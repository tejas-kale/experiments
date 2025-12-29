"""Qwen-Image-Layered CLI for Runpod.

A CLI tool to run Qwen-Image-Layered on Runpod instances for image layer decomposition.
"""

from __future__ import annotations

import base64
import io
import os
import time
from pathlib import Path

import click
import requests
from dotenv import load_dotenv
from PIL import Image
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

# Load environment variables
load_dotenv()


class QwenRunpodClient:
    """Client for managing Qwen-Image-Layered on Runpod."""

    def __init__(self, api_key: str, endpoint_id: str):
        """Initialize the client with Runpod API key and endpoint ID.

        Args:
            api_key: Runpod API key
            endpoint_id: Runpod endpoint ID
        """
        self.api_key = api_key
        self.endpoint_id = endpoint_id
        self.endpoint_url = f"https://api.runpod.ai/v2/{endpoint_id}"

    def generate_layers(
        self,
        image_path: Path,
        num_layers: int = 4,
        resolution: int = 640,
        num_steps: int = 50,
        cfg_scale: float = 4.0,
    ) -> list[bytes]:
        """Generate image layers from input image.

        Args:
            image_path: Path to input image
            num_layers: Number of layers to generate (3, 4, or 8)
            resolution: Output resolution (640 or 1024)
            num_steps: Number of inference steps (default 50)
            cfg_scale: Classifier-free guidance scale (default 4.0)

        Returns:
            List of PNG image bytes for each layer
        """
        console.print(f"\n[yellow]Generating {num_layers} layers from {image_path.name}...[/yellow]")

        # Load and encode image
        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            image_b64 = base64.b64encode(buffer.getvalue()).decode()

        # Prepare request payload
        payload = {
            "input": {
                "image": image_b64,
                "num_layers": num_layers,
                "resolution": resolution,
                "num_inference_steps": num_steps,
                "true_cfg_scale": cfg_scale,
                "cfg_normalize": True,
                "use_en_prompt": True,
            }
        }

        # Send request
        console.print("[yellow]Sending request to Runpod...[/yellow]")
        response = requests.post(
            f"{self.endpoint_url}/run",
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=600,
        )

        if response.status_code != 200:
            raise RuntimeError(f"Request failed: {response.text}")

        result = response.json()
        job_id = result["id"]

        # Poll for results
        console.print(f"[yellow]Job submitted: {job_id}. Waiting for completion...[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing...", total=None)

            while True:
                status_response = requests.get(
                    f"{self.endpoint_url}/status/{job_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30,
                )

                if status_response.status_code == 200:
                    status_data = status_response.json()

                    if status_data["status"] == "COMPLETED":
                        progress.update(task, description="[green]Complete!")
                        console.print("[green]✓ Layers generated successfully[/green]")

                        # Decode layer images
                        layers = []
                        for layer_b64 in status_data["output"]["layers"]:
                            layer_bytes = base64.b64decode(layer_b64)
                            layers.append(layer_bytes)

                        return layers

                    elif status_data["status"] == "FAILED":
                        raise RuntimeError(f"Job failed: {status_data.get('error', 'Unknown error')}")

                time.sleep(3)


@click.group()
def cli() -> None:
    """Qwen-Image-Layered CLI for Runpod."""
    pass


@cli.command()
@click.argument("image_path", type=click.Path(exists=True, path_type=Path))
@click.option("--layers", "-l", default="4", type=click.Choice(["3", "4", "8"]), help="Number of layers")
@click.option("--resolution", "-r", default="640", type=click.Choice(["640", "1024"]), help="Output resolution")
@click.option("--steps", "-s", default=50, type=int, help="Number of inference steps")
@click.option("--cfg-scale", "-c", default=4.0, type=float, help="CFG scale")
@click.option("--output-dir", "-o", type=click.Path(path_type=Path), default=None, help="Output directory")
@click.option("--endpoint-id", type=str, default=None, help="Runpod endpoint ID (optional, uses env var if not provided)")
def generate(
    image_path: Path,
    layers: str,
    resolution: str,
    steps: int,
    cfg_scale: float,
    output_dir: Path | None,
    endpoint_id: str | None,
) -> None:
    """Generate layered images from an input image."""
    # Display banner
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Qwen-Image-Layered[/bold cyan]\n"
        "[dim]Image Layer Decomposition on Runpod[/dim]",
        border_style="cyan",
    ))

    # Validate API key
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        console.print("[red]✗ RUNPOD_API_KEY not found in environment[/red]")
        console.print("[yellow]Please set it in .env file or environment variables[/yellow]")
        return

    # Get endpoint ID
    if endpoint_id is None:
        endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")

    if not endpoint_id:
        console.print("[red]✗ RUNPOD_ENDPOINT_ID not found[/red]")
        console.print("[yellow]Please set it in .env file or pass --endpoint-id[/yellow]")
        console.print("[yellow]Create an endpoint at: https://www.runpod.io/console/serverless[/yellow]")
        return

    # Setup output directory
    if output_dir is None:
        output_dir = Path.cwd() / "qwen_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Display parameters
    table = Table(title="Generation Parameters", show_header=False)
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_row("Input Image", str(image_path))
    table.add_row("Layers", layers)
    table.add_row("Resolution", f"{resolution}px")
    table.add_row("Inference Steps", str(steps))
    table.add_row("CFG Scale", str(cfg_scale))
    table.add_row("Endpoint ID", endpoint_id)
    table.add_row("Output Directory", str(output_dir))
    console.print(table)

    # Initialize client
    client = QwenRunpodClient(api_key, endpoint_id)

    try:
        # Generate layers
        layer_images = client.generate_layers(
            image_path=image_path,
            num_layers=int(layers),
            resolution=int(resolution),
            num_steps=steps,
            cfg_scale=cfg_scale,
        )

        # Save layers
        console.print(f"\n[yellow]Saving {len(layer_images)} layers to {output_dir}...[/yellow]")
        for i, layer_bytes in enumerate(layer_images):
            output_path = output_dir / f"layer_{i:02d}.png"
            with open(output_path, "wb") as f:
                f.write(layer_bytes)
            console.print(f"[green]✓ Saved {output_path.name}[/green]")

        console.print(f"\n[bold green]✓ All layers saved to {output_dir}[/bold green]\n")

    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]\n")
        raise


if __name__ == "__main__":
    cli()
