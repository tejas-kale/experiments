"""Qwen-Image-Layered CLI for Runpod."""

from __future__ import annotations

import os
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .client import QwenImageLayeredClient
from .config import Config
from .runpod_manager import RunpodManager

console = Console()


@click.group()
def cli() -> None:
    """Qwen-Image-Layered CLI for image layer decomposition on Runpod."""
    pass


@cli.command()
@click.option(
    "--api-key",
    type=str,
    default=None,
    help="Runpod API key (or set RUNPOD_API_KEY env var)",
)
@click.option(
    "--docker-image",
    type=str,
    default="runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
    help="Base Docker image for Runpod template",
)
@click.option(
    "--gpu-type",
    type=str,
    default="NVIDIA RTX 3090",
    help="GPU type to use",
)
def configure(
    api_key: str | None,
    docker_image: str,
    gpu_type: str,
) -> None:
    """Configure Runpod endpoint for Qwen-Image-Layered."""
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]Qwen-Image-Layered Configuration[/bold cyan]\n"
            "[dim]Setting up Runpod serverless endpoint[/dim]",
            border_style="cyan",
        )
    )

    # Get API key
    if api_key is None:
        api_key = os.getenv("RUNPOD_API_KEY")

    if not api_key:
        console.print("[red]✗ RUNPOD_API_KEY not found[/red]")
        console.print(
            "[yellow]Please set it as an environment variable or pass --api-key[/yellow]"
        )
        console.print(
            "[yellow]Get your API key from: https://www.runpod.io/console/user/settings[/yellow]"
        )
        return

    # Initialize config and manager
    config = Config()
    manager = RunpodManager(api_key)

    try:
        # Create template
        template_name = "qwen-image-layered"
        console.print(f"\n[yellow]Creating Runpod template: {template_name}...[/yellow]")

        template_id = manager.create_template(
            name=template_name,
            docker_image=docker_image,
            container_disk_gb=80,
            env_vars={"HF_HOME": "/app/hf_cache"},
        )

        # Create endpoint
        endpoint_name = "qwen-image-layered"
        console.print(f"\n[yellow]Creating Runpod endpoint: {endpoint_name}...[/yellow]")

        endpoint_id = manager.create_endpoint(
            name=endpoint_name,
            template_id=template_id,
            gpu_type_id=gpu_type,
            min_workers=0,
            max_workers=1,
            idle_timeout=5,
        )

        # Save configuration
        config.set("api_key", api_key)
        config.set("endpoint_id", endpoint_id)
        config.set("template_id", template_id)
        config.set("docker_image", docker_image)
        config.set("gpu_type", gpu_type)

        # Display success
        console.print("\n[bold green]✓ Configuration complete![/bold green]\n")

        table = Table(title="Configuration Summary", show_header=False)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="yellow")
        table.add_row("Template ID", template_id)
        table.add_row("Endpoint ID", endpoint_id)
        table.add_row("Docker Image", docker_image)
        table.add_row("GPU Type", gpu_type)
        table.add_row("Config File", str(config.config_file))
        console.print(table)

        console.print(
            "\n[green]You can now use the 'generate' command to decompose images![/green]\n"
        )

    except Exception as e:
        console.print(f"\n[red]✗ Configuration failed: {e}[/red]\n")
        raise


@cli.command()
@click.argument("image_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--layers",
    "-l",
    default="4",
    type=click.Choice(["3", "4", "8"]),
    help="Number of layers",
)
@click.option(
    "--resolution",
    "-r",
    default="640",
    type=click.Choice(["640", "1024"]),
    help="Output resolution",
)
@click.option("--steps", "-s", default=50, type=int, help="Number of inference steps")
@click.option("--cfg-scale", "-c", default=4.0, type=float, help="CFG scale")
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory",
)
def generate(
    image_path: Path,
    layers: str,
    resolution: str,
    steps: int,
    cfg_scale: float,
    output_dir: Path | None,
) -> None:
    """Generate layered images from an input image."""
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]Qwen-Image-Layered[/bold cyan]\n"
            "[dim]Image Layer Decomposition on Runpod[/dim]",
            border_style="cyan",
        )
    )

    # Load configuration
    config = Config()

    if not config.is_configured():
        console.print("[red]✗ Not configured[/red]")
        console.print(
            "[yellow]Please run 'qwen-image-layered configure' first[/yellow]"
        )
        return

    api_key = config.get_api_key()
    endpoint_id = config.get_endpoint_id()

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
    client = QwenImageLayeredClient(api_key, endpoint_id)

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
        console.print(
            f"\n[yellow]Saving {len(layer_images)} layers to {output_dir}...[/yellow]"
        )
        for i, layer_bytes in enumerate(layer_images):
            output_path = output_dir / f"layer_{i:02d}.png"
            with open(output_path, "wb") as f:
                f.write(layer_bytes)
            console.print(f"[green]✓ Saved {output_path.name}[/green]")

        console.print(
            f"\n[bold green]✓ All layers saved to {output_dir}[/bold green]\n"
        )

    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]\n")
        raise


@cli.command()
def info() -> None:
    """Display configuration information."""
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]Configuration Information[/bold cyan]",
            border_style="cyan",
        )
    )

    config = Config()

    if not config.is_configured():
        console.print("\n[yellow]Not configured yet[/yellow]")
        console.print(
            "[dim]Run 'qwen-image-layered configure' to set up[/dim]\n"
        )
        return

    table = Table(show_header=False)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_row("API Key", config.get_api_key()[:20] + "..." if config.get_api_key() else "Not set")
    table.add_row("Endpoint ID", config.get_endpoint_id() or "Not set")
    table.add_row("Template ID", config.get_template_id() or "Not set")
    table.add_row("Docker Image", config.get_docker_image() or "Not set")
    table.add_row("GPU Type", config.get_gpu_type())
    table.add_row("Config File", str(config.config_file))

    console.print(table)
    console.print()


if __name__ == "__main__":
    cli()
