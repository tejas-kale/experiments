"""Qwen-Image-Layered client for Runpod inference."""

from __future__ import annotations

import base64
import io
import time
from pathlib import Path

import requests
from PIL import Image
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class QwenImageLayeredClient:
    """Client for managing Qwen-Image-Layered inference on Runpod."""

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
            num_steps: Number of inference steps
            cfg_scale: Classifier-free guidance scale

        Returns:
            List of PNG image bytes for each layer
        """
        console.print(
            f"\n[yellow]Generating {num_layers} layers from {image_path.name}...[/yellow]"
        )

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
        console.print(
            f"[yellow]Job submitted: {job_id}. Waiting for completion...[/yellow]"
        )

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
                        raise RuntimeError(
                            f"Job failed: {status_data.get('error', 'Unknown error')}"
                        )

                time.sleep(3)
