"""CLI entry point for secure-runpod-chat."""

import os
import sys
import signal
import atexit
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

from .utils import (
    get_model_info,
    estimate_model_size_gb,
    determine_gpu_requirements,
    is_vision_model,
    format_cost,
    confirm_action,
    validate_api_key,
)
from .runpod_manager import RunPodManager
from .ssh_client import SSHClient
from .model_deployer import ModelDeployer
from .chat_interface import ChatInterface

console = Console()

# Global references for cleanup
runpod_manager: Optional[RunPodManager] = None
ssh_client: Optional[SSHClient] = None


def cleanup_handler(signum=None, frame=None):
    """Handle cleanup on exit or interrupt."""
    console.print("\n[yellow]Cleaning up...[/yellow]")

    # Cleanup SSH
    if ssh_client:
        try:
            # Clear logs and temporary files
            console.print("[cyan]Clearing remote logs and temporary files...[/cyan]")
            ssh_client.cleanup_remote_files([
                "/root/model_server.log",
                "/root/model_server.py",
                "/root/uploads/*",
                "/root/images/*",
                "/tmp/*",
                "~/.cache/huggingface/*",
            ])
            ssh_client.close()
        except:
            pass

    # Cleanup RunPod instance
    if runpod_manager:
        try:
            runpod_manager.cleanup()

            # Verify termination
            console.print("[cyan]Verifying instance termination...[/cyan]")
            if runpod_manager.verify_termination():
                console.print("[green]Instance successfully terminated[/green]")
            else:
                console.print("[yellow]Warning: Could not verify instance termination[/yellow]")
        except:
            pass

    if signum:
        sys.exit(0)


@click.command()
@click.option(
    "--model",
    "-m",
    required=True,
    help="HuggingFace model ID (e.g., meta-llama/Llama-3.2-11B-Vision-Instruct)",
)
@click.option(
    "--gpu-type",
    "-g",
    default=None,
    help="GPU type to use (optional, auto-detected if not specified)",
)
@click.option(
    "--max-cost-per-hour",
    "-c",
    type=float,
    default=None,
    help="Maximum cost per hour in dollars",
)
@click.option(
    "--disk-size",
    "-d",
    type=int,
    default=50,
    help="Disk size in GB (default: 50)",
)
@click.option(
    "--quantize",
    "-q",
    is_flag=True,
    help="Use 4-bit quantization to reduce GPU requirements",
)
@click.option(
    "--no-history",
    is_flag=True,
    help="Disable encrypted chat history saving",
)
@click.option(
    "--use-vllm/--no-vllm",
    default=True,
    help="Use vLLM for optimized inference (default: True)",
)
def main(
    model: str,
    gpu_type: Optional[str],
    max_cost_per_hour: Optional[float],
    disk_size: int,
    quantize: bool,
    no_history: bool,
    use_vllm: bool,
):
    """Secure RunPod Chat - Privacy-focused CLI for running HuggingFace models on RunPod.

    Example:
        secure-runpod-chat --model meta-llama/Llama-3.2-11B-Vision-Instruct
    """
    global runpod_manager, ssh_client

    # Load environment variables
    load_dotenv()

    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    atexit.register(cleanup_handler)

    try:
        # Validate API key
        api_key = validate_api_key(os.getenv("RUNPOD_API_KEY"))

        # Display banner
        console.print(Panel(
            "[bold cyan]Secure RunPod Chat[/bold cyan]\n"
            "Privacy-focused CLI for running HuggingFace models on RunPod",
            border_style="cyan",
        ))

        # Get model information
        console.print(f"\n[cyan]Fetching model information for {model}...[/cyan]")
        model_info = get_model_info(model)

        if not model_info:
            console.print("[red]Could not fetch model information. Proceeding anyway...[/red]")

        # Determine if vision model
        is_vision = is_vision_model(model_info)

        # Estimate model size
        console.print("[cyan]Estimating model size...[/cyan]")
        model_size_gb = estimate_model_size_gb(model)
        console.print(f"Estimated model size: [bold]{model_size_gb:.1f} GB[/bold]")

        # Determine GPU requirements
        if not gpu_type:
            console.print("[cyan]Determining GPU requirements...[/cyan]")
            gpu_type, gpu_count = determine_gpu_requirements(model_size_gb, is_vision)
            console.print(f"Recommended GPU: [bold]{gpu_count}x {gpu_type}[/bold]")
        else:
            gpu_count = 1

        # Display cost estimate
        # Note: Actual costs vary, these are estimates
        gpu_costs = {
            "NVIDIA RTX A4000": 0.34,
            "NVIDIA RTX A5000": 0.44,
            "NVIDIA A40": 0.79,
            "NVIDIA RTX A6000": 0.79,
            "NVIDIA A100": 1.89,
            "NVIDIA A100 80GB": 2.19,
        }
        estimated_cost = gpu_costs.get(gpu_type, 1.0) * gpu_count
        console.print(f"\nEstimated cost: [bold yellow]{format_cost(estimated_cost)}[/bold yellow]")

        if max_cost_per_hour and estimated_cost > max_cost_per_hour:
            console.print(f"[red]Estimated cost (${estimated_cost:.4f}/hr) exceeds maximum (${max_cost_per_hour:.4f}/hr)[/red]")
            if not confirm_action("Continue anyway?", default=False):
                return

        # Confirm before creating instance
        if not confirm_action("\nCreate RunPod instance?", default=True):
            console.print("[yellow]Aborted[/yellow]")
            return

        # Create RunPod instance
        runpod_manager = RunPodManager(api_key)
        instance_info = runpod_manager.create_instance(
            gpu_type=gpu_type,
            gpu_count=gpu_count,
            disk_size=disk_size,
        )

        # Get SSH connection info
        ssh_info = runpod_manager.get_ssh_connection_info()

        # Connect via SSH
        ssh_client = SSHClient(
            host=ssh_info["host"],
            port=ssh_info["port"],
            username=ssh_info["username"],
        )

        if not ssh_client.connect():
            console.print("[red]Failed to connect via SSH[/red]")
            return

        # Deploy model
        deployer = ModelDeployer(ssh_client)
        if not deployer.deploy_model(
            model_id=model,
            is_vision=is_vision,
            use_vllm=use_vllm and not is_vision,  # vLLM doesn't support all vision models
            quantize=quantize,
        ):
            console.print("[red]Failed to deploy model[/red]")
            return

        # Start model server
        if not deployer.start_model_server():
            console.print("[red]Failed to start model server[/red]")
            return

        # Display actual cost
        actual_cost = runpod_manager.get_cost_per_hour()
        if actual_cost > 0:
            console.print(f"\n[bold green]Actual cost: {format_cost(actual_cost)}[/bold green]")

        # Start chat interface
        chat = ChatInterface(
            ssh_client=ssh_client,
            model_deployer=deployer,
            model_id=model,
            is_vision=is_vision,
            save_history=not no_history,
        )

        chat.run()
        chat.cleanup()

        # Cleanup will be handled by atexit

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        cleanup_handler()

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        cleanup_handler()
        sys.exit(1)


if __name__ == "__main__":
    main()
