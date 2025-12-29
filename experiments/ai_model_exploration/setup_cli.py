"""Runpod Setup CLI - Create and manage templates and endpoints.

This CLI tool helps you set up Runpod serverless endpoints for both
Qwen-Image-Layered and Chatterbox TTS experiments.
"""

from __future__ import annotations

import os
from pathlib import Path

import click
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()
load_dotenv()

RUNPOD_GRAPHQL_URL = "https://api.runpod.io/graphql"


class RunpodSetupClient:
    """Client for managing Runpod templates and endpoints via GraphQL API."""

    def __init__(self, api_key: str):
        """Initialize the client.

        Args:
            api_key: Runpod API key
        """
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json", "Authorization": api_key}

    def graphql_query(self, query: str, variables: dict | None = None) -> dict:
        """Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Optional query variables

        Returns:
            Query response data
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(
            RUNPOD_GRAPHQL_URL, json=payload, headers=self.headers, timeout=30
        )

        if response.status_code != 200:
            raise RuntimeError(f"GraphQL request failed: {response.text}")

        result = response.json()

        if "errors" in result:
            raise RuntimeError(f"GraphQL errors: {result['errors']}")

        return result.get("data", {})

    def create_template(
        self,
        name: str,
        image_name: str,
        docker_start_cmd: str,
        container_disk_gb: int = 20,
        env_vars: dict | None = None,
    ) -> str:
        """Create a new template.

        Args:
            name: Template name
            image_name: Docker image name
            docker_start_cmd: Start command
            container_disk_gb: Container disk size in GB
            env_vars: Environment variables

        Returns:
            Template ID
        """
        query = """
        mutation SaveTemplate($input: SaveTemplateInput!) {
            saveTemplate(input: $input) {
                id
                name
            }
        }
        """

        env_list = []
        if env_vars:
            env_list = [{"key": k, "value": v} for k, v in env_vars.items()]

        variables = {
            "input": {
                "name": name,
                "imageName": image_name,
                "dockerArgs": "",
                "containerDiskInGb": container_disk_gb,
                "volumeInGb": 0,
                "volumeMountPath": "",
                "ports": "",
                "env": env_list,
                "startSsh": False,
                "startJupyter": False,
                "isServerless": True,
                "dockerStartCmd": docker_start_cmd,
            }
        }

        result = self.graphql_query(query, variables)
        template = result.get("saveTemplate", {})

        if not template:
            raise RuntimeError("Failed to create template")

        console.print(f"[green]✓ Template created: {template['name']} (ID: {template['id']})[/green]")
        return template["id"]

    def list_templates(self) -> list[dict]:
        """List all templates.

        Returns:
            List of templates
        """
        query = """
        query {
            myself {
                serverlessTemplates {
                    id
                    name
                    imageName
                    dockerStartCmd
                }
            }
        }
        """

        result = self.graphql_query(query)
        return result.get("myself", {}).get("serverlessTemplates", [])

    def create_endpoint(
        self,
        name: str,
        template_id: str,
        gpu_ids: str = "AMPERE_16",
        workers_min: int = 0,
        workers_max: int = 1,
        idle_timeout: int = 5,
        execution_timeout: int = 600,
    ) -> dict:
        """Create a serverless endpoint.

        Args:
            name: Endpoint name
            template_id: Template ID to use
            gpu_ids: GPU type ID (e.g., "AMPERE_16" for RTX 3060 Ti)
            workers_min: Minimum workers (0 for auto-scale)
            workers_max: Maximum workers
            idle_timeout: Idle timeout in seconds
            execution_timeout: Max execution time in seconds

        Returns:
            Endpoint data with ID and URL
        """
        query = """
        mutation SaveEndpoint($input: EndpointInput!) {
            saveEndpoint(input: $input) {
                id
                name
                aiKey
            }
        }
        """

        variables = {
            "input": {
                "name": name,
                "templateId": template_id,
                "gpuIds": gpu_ids,
                "workersMin": workers_min,
                "workersMax": workers_max,
                "idleTimeout": idle_timeout,
                "executionTimeout": execution_timeout,
                "networkVolumeId": None,
            }
        }

        result = self.graphql_query(query, variables)
        endpoint = result.get("saveEndpoint", {})

        if not endpoint:
            raise RuntimeError("Failed to create endpoint")

        console.print(f"[green]✓ Endpoint created: {endpoint['name']}[/green]")
        console.print(f"[cyan]  Endpoint ID: {endpoint['id']}[/cyan]")

        return {
            "id": endpoint["id"],
            "name": endpoint["name"],
            "url": f"https://api.runpod.ai/v2/{endpoint['id']}",
        }

    def list_endpoints(self) -> list[dict]:
        """List all serverless endpoints.

        Returns:
            List of endpoints
        """
        query = """
        query {
            myself {
                endpoints {
                    id
                    name
                    templateId
                    gpuIds
                    workersMin
                    workersMax
                }
            }
        }
        """

        result = self.graphql_query(query)
        return result.get("myself", {}).get("endpoints", [])


# GPU ID mappings
GPU_MAPPINGS = {
    "RTX 3060 Ti (8GB)": "AMPERE_16",
    "RTX 3060 (12GB)": "AMPERE_12",
    "RTX 3090 (24GB)": "AMPERE_24",
    "RTX 4060 (8GB)": "ADA_16",
    "RTX 4090 (24GB)": "ADA_24",
    "RTX A5000 (24GB)": "AMPERE_A5000",
}


@click.group()
def cli() -> None:
    """Runpod Setup CLI for AI Model Experiments."""
    pass


@cli.command()
def setup_chatterbox() -> None:
    """Set up Chatterbox TTS template and endpoint."""
    console.print()
    console.print(Panel.fit(
        "[bold magenta]Chatterbox TTS Setup[/bold magenta]\n"
        "[dim]Create Runpod template and endpoint[/dim]",
        border_style="magenta",
    ))

    # Get API key
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        console.print("[red]✗ RUNPOD_API_KEY not found in .env[/red]")
        api_key = Prompt.ask("\nEnter your Runpod API key")

    client = RunpodSetupClient(api_key)

    # Create template
    console.print("\n[yellow]Step 1: Creating template...[/yellow]")

    template_name = "chatterbox-tts"
    docker_image = "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04"
    start_cmd = (
        "pip install chatterbox-tts runpod && "
        "wget -O handler.py https://raw.githubusercontent.com/tejas-kale/experiments/main/"
        "experiments/ai_model_exploration/chatterbox_tts/runpod_handler.py && "
        "python handler.py"
    )

    try:
        template_id = client.create_template(
            name=template_name,
            image_name=docker_image,
            docker_start_cmd=start_cmd,
            container_disk_gb=15,
        )
    except Exception as e:
        console.print(f"[red]✗ Failed to create template: {e}[/red]")
        return

    # Select GPU
    console.print("\n[yellow]Step 2: Select GPU type[/yellow]")
    console.print("[dim]Recommended: RTX 3060 Ti (8GB) @ $0.14/hour[/dim]\n")

    table = Table()
    table.add_column("Option", style="cyan")
    table.add_column("GPU", style="yellow")
    table.add_column("VRAM", style="green")
    table.add_column("Cost/Hour", style="magenta")

    for i, (gpu_name, _) in enumerate(GPU_MAPPINGS.items(), 1):
        vram = gpu_name.split("(")[1].split(")")[0]
        cost = {"8GB": "$0.14-0.16", "12GB": "$0.18", "24GB": "$0.24-0.44"}
        table.add_row(str(i), gpu_name.split("(")[0].strip(), vram, cost.get(vram, "N/A"))

    console.print(table)

    gpu_choice = Prompt.ask("\nSelect GPU", choices=["1", "2", "3", "4", "5", "6"], default="1")
    gpu_name = list(GPU_MAPPINGS.keys())[int(gpu_choice) - 1]
    gpu_id = GPU_MAPPINGS[gpu_name]

    # Create endpoint
    console.print("\n[yellow]Step 3: Creating endpoint...[/yellow]")

    try:
        endpoint = client.create_endpoint(
            name="chatterbox-tts",
            template_id=template_id,
            gpu_ids=gpu_id,
            workers_min=0,
            workers_max=1,
            idle_timeout=5,
            execution_timeout=600,
        )
    except Exception as e:
        console.print(f"[red]✗ Failed to create endpoint: {e}[/red]")
        return

    # Update .env file
    console.print("\n[yellow]Step 4: Updating .env file...[/yellow]")

    env_path = Path("chatterbox_tts/.env")
    env_content = f"RUNPOD_API_KEY={api_key}\nRUNPOD_ENDPOINT_ID={endpoint['id']}\n"

    env_path.write_text(env_content)
    console.print(f"[green]✓ Saved credentials to {env_path}[/green]")

    # Summary
    console.print("\n" + "="*60)
    console.print("[bold green]✓ Chatterbox TTS setup complete![/bold green]")
    console.print("="*60)
    console.print(f"\n[cyan]Endpoint ID:[/cyan] {endpoint['id']}")
    console.print(f"[cyan]Endpoint URL:[/cyan] {endpoint['url']}")
    console.print(f"[cyan]GPU:[/cyan] {gpu_name}")
    console.print("\n[yellow]Test it:[/yellow]")
    console.print('  cd chatterbox_tts')
    console.print('  python cli.py speak "Hello world!" --exaggeration 1.5')
    console.print()


@cli.command()
def setup_qwen() -> None:
    """Set up Qwen-Image-Layered template and endpoint."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Qwen-Image-Layered Setup[/bold cyan]\n"
        "[dim]Create Runpod template and endpoint[/dim]",
        border_style="cyan",
    ))

    # Get API key
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        console.print("[red]✗ RUNPOD_API_KEY not found in .env[/red]")
        api_key = Prompt.ask("\nEnter your Runpod API key")

    client = RunpodSetupClient(api_key)

    # Create template
    console.print("\n[yellow]Step 1: Creating template...[/yellow]")

    template_name = "qwen-image-layered"
    docker_image = "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04"
    start_cmd = (
        "pip install git+https://github.com/huggingface/diffusers transformers>=4.51.3 torch torchvision runpod && "
        "wget -O handler.py https://raw.githubusercontent.com/tejas-kale/experiments/main/"
        "experiments/ai_model_exploration/qwen_image_layered/runpod_handler.py && "
        "python handler.py"
    )

    try:
        template_id = client.create_template(
            name=template_name,
            image_name=docker_image,
            docker_start_cmd=start_cmd,
            container_disk_gb=25,
        )
    except Exception as e:
        console.print(f"[red]✗ Failed to create template: {e}[/red]")
        return

    # Select GPU (must be 24GB for Qwen)
    console.print("\n[yellow]Step 2: Select GPU type[/yellow]")
    console.print("[dim]Note: Qwen requires 24GB VRAM minimum[/dim]")
    console.print("[dim]Recommended: RTX 3090 (24GB) @ $0.24/hour[/dim]\n")

    gpu_24gb_options = {
        "RTX 3090 (24GB)": "AMPERE_24",
        "RTX 4090 (24GB)": "ADA_24",
        "RTX A5000 (24GB)": "AMPERE_A5000",
    }

    table = Table()
    table.add_column("Option", style="cyan")
    table.add_column("GPU", style="yellow")
    table.add_column("Cost/Hour (est)", style="magenta")

    costs = ["$0.24", "$0.44", "$0.34"]
    for i, (gpu_name, _) in enumerate(gpu_24gb_options.items(), 1):
        table.add_row(str(i), gpu_name, costs[i-1])

    console.print(table)

    gpu_choice = Prompt.ask("\nSelect GPU", choices=["1", "2", "3"], default="1")
    gpu_name = list(gpu_24gb_options.keys())[int(gpu_choice) - 1]
    gpu_id = gpu_24gb_options[gpu_name]

    # Create endpoint
    console.print("\n[yellow]Step 3: Creating endpoint...[/yellow]")

    try:
        endpoint = client.create_endpoint(
            name="qwen-image-layered",
            template_id=template_id,
            gpu_ids=gpu_id,
            workers_min=0,
            workers_max=1,
            idle_timeout=5,
            execution_timeout=600,
        )
    except Exception as e:
        console.print(f"[red]✗ Failed to create endpoint: {e}[/red]")
        return

    # Update .env file
    console.print("\n[yellow]Step 4: Updating .env file...[/yellow]")

    env_path = Path("qwen_image_layered/.env")
    env_content = f"RUNPOD_API_KEY={api_key}\nRUNPOD_ENDPOINT_ID={endpoint['id']}\n"

    env_path.write_text(env_content)
    console.print(f"[green]✓ Saved credentials to {env_path}[/green]")

    # Summary
    console.print("\n" + "="*60)
    console.print("[bold green]✓ Qwen-Image-Layered setup complete![/bold green]")
    console.print("="*60)
    console.print(f"\n[cyan]Endpoint ID:[/cyan] {endpoint['id']}")
    console.print(f"[cyan]Endpoint URL:[/cyan] {endpoint['url']}")
    console.print(f"[cyan]GPU:[/cyan] {gpu_name}")
    console.print("\n[yellow]Test it:[/yellow]")
    console.print('  cd qwen_image_layered')
    console.print('  python cli.py generate your_image.jpg --layers 4')
    console.print()


@cli.command()
def list_templates() -> None:
    """List all templates."""
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        console.print("[red]✗ RUNPOD_API_KEY not found in .env[/red]")
        return

    client = RunpodSetupClient(api_key)

    try:
        templates = client.list_templates()

        if not templates:
            console.print("[yellow]No templates found[/yellow]")
            return

        table = Table(title="Runpod Templates")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="yellow")
        table.add_column("Image", style="green")

        for template in templates:
            table.add_row(
                template["id"],
                template["name"],
                template.get("imageName", "N/A"),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@cli.command()
def list_endpoints() -> None:
    """List all endpoints."""
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        console.print("[red]✗ RUNPOD_API_KEY not found in .env[/red]")
        return

    client = RunpodSetupClient(api_key)

    try:
        endpoints = client.list_endpoints()

        if not endpoints:
            console.print("[yellow]No endpoints found[/yellow]")
            return

        table = Table(title="Runpod Endpoints")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="yellow")
        table.add_column("GPU", style="green")
        table.add_column("Workers", style="magenta")

        for endpoint in endpoints:
            table.add_row(
                endpoint["id"],
                endpoint["name"],
                endpoint.get("gpuIds", "N/A"),
                f"{endpoint.get('workersMin', 0)}-{endpoint.get('workersMax', 1)}",
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


if __name__ == "__main__":
    cli()
