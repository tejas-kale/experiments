"""Runpod management utilities for creating and managing serverless endpoints."""

from __future__ import annotations

import requests
from rich.console import Console

console = Console()


class RunpodManager:
    """Manages Runpod templates and endpoints via GraphQL API."""

    GRAPHQL_URL = "https://api.runpod.io/graphql"

    def __init__(self, api_key: str):
        """Initialize Runpod manager.

        Args:
            api_key: Runpod API key
        """
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}

    def _make_request(self, query: str, variables: dict | None = None) -> dict:
        """Make a GraphQL request to Runpod API.

        Args:
            query: GraphQL query string
            variables: Optional query variables

        Returns:
            Response data dictionary
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(
            self.GRAPHQL_URL,
            json=payload,
            headers=self.headers,
            params={"api_key": self.api_key},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def create_template(
        self,
        name: str,
        docker_image: str,
        container_disk_gb: int = 50,
        env_vars: dict[str, str] | None = None,
        handler_url: str | None = None,
    ) -> str:
        """Create a Runpod template.

        Args:
            name: Template name
            docker_image: Docker image to use
            container_disk_gb: Container disk size in GB
            env_vars: Optional environment variables
            handler_url: URL to download handler.py from (optional)

        Returns:
            Template ID
        """
        console.print(f"[yellow]Creating Runpod template: {name}...[/yellow]")

        env_list = []
        if env_vars:
            env_list = [{"key": k, "value": v} for k, v in env_vars.items()]

        # Build start command using base64 encoding to avoid quoting issues
        if handler_url:
            start_command = (
                f"bash -c 'pip install --no-cache-dir git+https://github.com/huggingface/diffusers "
                f"transformers>=4.51.3 accelerate torch>=2.4.0 torchvision pillow runpod && "
                f"wget -O handler.py {handler_url} && "
                f"python handler.py'"
            )
        else:
            # Base64 encode the handler to avoid all quoting issues
            import base64 as b64

            handler_code = """\"\"\"Runpod handler for Qwen-Image-Layered inference.

This script runs on the Runpod instance and handles inference requests.
\"\"\"

from __future__ import annotations

import base64
import io
from typing import Any

import runpod
import torch

# Workaround for diffusers expecting torch.xpu to exist
if not hasattr(torch, "xpu"):
    class MockXPU:
        def is_available(self):
            return False
        def device_count(self):
            return 0
        def empty_cache(self):
            pass
        def __getattr__(self, name):
            def dummy(*args, **kwargs):
                return None
            return dummy
    torch.xpu = MockXPU()

from diffusers import QwenImageLayeredPipeline
from PIL import Image


# Global pipeline (loaded once on cold start)
pipeline: QwenImageLayeredPipeline | None = None


def load_model() -> QwenImageLayeredPipeline:
    \"\"\"Load the Qwen-Image-Layered model.

    Returns:
        Loaded pipeline instance
    \"\"\"
    global pipeline

    if pipeline is None:
        print("Loading Qwen-Image-Layered model...")

        pipeline = QwenImageLayeredPipeline.from_pretrained(
            "Qwen/Qwen-Image-Layered",
            torch_dtype=torch.bfloat16,  # Use bf16 for better quality
        )
        pipeline.enable_sequential_cpu_offload()

        print("Model loaded successfully!")

    return pipeline


def handler(job: dict[str, Any]) -> dict[str, Any]:
    \"\"\"Handle inference requests.

    Args:
        job: Job input containing image and parameters

    Returns:
        Dictionary with generated layers
    \"\"\"
    try:
        job_input = job["input"]

        # Decode input image
        image_b64 = job_input["image"]
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        # Get parameters
        num_layers = job_input.get("num_layers", 4)
        resolution = job_input.get("resolution", 640)
        num_inference_steps = job_input.get("num_inference_steps", 50)
        true_cfg_scale = job_input.get("true_cfg_scale", 4.0)
        cfg_normalize = job_input.get("cfg_normalize", True)
        use_en_prompt = job_input.get("use_en_prompt", True)

        # Load model
        pipe = load_model()

        # Run inference
        print(f"Generating {num_layers} layers...")

        with torch.inference_mode():
            output = pipe(
                image=image,
                generator=torch.Generator(device="cuda").manual_seed(777),
                true_cfg_scale=true_cfg_scale,
                negative_prompt=" ",
                num_inference_steps=num_inference_steps,
                layers=num_layers,
                resolution=resolution,
                cfg_normalize=cfg_normalize,
                use_en_prompt=use_en_prompt,
            )

        # Encode output layers as base64
        layers_b64 = []
        for layer_image in output.images[0]:
            buffer = io.BytesIO()
            layer_image.save(buffer, format="PNG")
            layer_b64 = base64.b64encode(buffer.getvalue()).decode()
            layers_b64.append(layer_b64)

        print(f"Successfully generated {len(layers_b64)} layers")

        return {"layers": layers_b64}

    except Exception as e:
        print(f"Error during inference: {e}")
        return {"error": str(e)}


# Start the serverless worker
runpod.serverless.start({"handler": handler})
"""
            handler_b64 = b64.b64encode(handler_code.encode()).decode()

            start_command = (
                f"bash -c 'pip install --no-cache-dir git+https://github.com/huggingface/diffusers "
                f"transformers>=4.51.3 accelerate torch>=2.4.0 torchvision pillow runpod && "
                f"echo {handler_b64} | base64 -d > handler.py && "
                f"python handler.py'"
            )

        query = """
        mutation SaveTemplate($input: SaveTemplateInput!) {
            saveTemplate(input: $input) {
                id
                name
            }
        }
        """

        variables = {
            "input": {
                "name": name,
                "imageName": docker_image,
                "dockerArgs": start_command,
                "containerDiskInGb": container_disk_gb,
                "volumeInGb": 0,
                "volumeMountPath": "",
                "ports": "",
                "env": env_list,
                "isServerless": True,
            }
        }

        result = self._make_request(query, variables)

        if "errors" in result:
            raise RuntimeError(f"Failed to create template: {result['errors']}")

        template_id = result["data"]["saveTemplate"]["id"]
        console.print(f"[green]✓ Template created: {template_id}[/green]")

        return template_id

    def create_endpoint(
        self,
        name: str,
        template_id: str,
        gpu_type_id: str = "NVIDIA RTX 3090",
        min_workers: int = 0,
        max_workers: int = 1,
        idle_timeout: int = 5,
    ) -> str:
        """Create a Runpod serverless endpoint.

        Args:
            name: Endpoint name
            template_id: Template ID to use
            gpu_type_id: GPU type identifier (e.g., "AMPERE_16", "NVIDIA RTX 3090")
            min_workers: Minimum workers (0 for auto-scaling)
            max_workers: Maximum workers
            idle_timeout: Idle timeout in seconds

        Returns:
            Endpoint ID
        """
        console.print(f"[yellow]Creating Runpod endpoint: {name}...[/yellow]")

        query = """
        mutation SaveEndpoint($input: EndpointInput!) {
            saveEndpoint(input: $input) {
                id
                name
                gpuIds
                workersMin
                workersMax
                idleTimeout
            }
        }
        """

        variables = {
            "input": {
                "name": name,
                "templateId": template_id,
                "gpuIds": gpu_type_id,
                "workersMin": min_workers,
                "workersMax": max_workers,
                "idleTimeout": idle_timeout,
                "scalerType": "QUEUE_DELAY",
                "scalerValue": 4,
            }
        }

        result = self._make_request(query, variables)

        if "errors" in result:
            raise RuntimeError(f"Failed to create endpoint: {result['errors']}")

        endpoint_id = result["data"]["saveEndpoint"]["id"]
        console.print(f"[green]✓ Endpoint created: {endpoint_id}[/green]")

        return endpoint_id

    def get_gpu_types(self) -> list[dict]:
        """Get available GPU types.

        Returns:
            List of GPU type dictionaries
        """
        query = """
        query GpuTypes {
            gpuTypes {
                id
                displayName
                memoryInGb
            }
        }
        """

        result = self._make_request(query)

        if "errors" in result:
            raise RuntimeError(f"Failed to get GPU types: {result['errors']}")

        return result["data"]["gpuTypes"]

    def list_endpoints(self) -> list[dict]:
        """List all serverless endpoints.

        Returns:
            List of endpoint dictionaries
        """
        query = """
        query Endpoints {
            myself {
                serverlessEndpoints {
                    id
                    name
                    templateId
                }
            }
        }
        """

        result = self._make_request(query)

        if "errors" in result:
            raise RuntimeError(f"Failed to list endpoints: {result['errors']}")

        return result["data"]["myself"]["serverlessEndpoints"]

    def delete_endpoint(self, endpoint_id: str) -> None:
        """Delete a serverless endpoint.

        Args:
            endpoint_id: Endpoint ID to delete
        """
        console.print(f"[yellow]Deleting endpoint: {endpoint_id}...[/yellow]")

        query = """
        mutation DeleteServerlessEndpoint($input: DeleteServerlessEndpointInput!) {
            deleteServerlessEndpoint(input: $input)
        }
        """

        variables = {"input": {"endpointId": endpoint_id}}

        result = self._make_request(query, variables)

        if "errors" in result:
            raise RuntimeError(f"Failed to delete endpoint: {result['errors']}")

        console.print("[green]✓ Endpoint deleted[/green]")
