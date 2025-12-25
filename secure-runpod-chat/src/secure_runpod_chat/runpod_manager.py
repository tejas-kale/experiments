"""RunPod instance management."""

import time
import atexit
from typing import Dict, Optional
import runpod
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

console = Console()


class RunPodManager:
    """Manages RunPod GPU instance lifecycle."""

    def __init__(self, api_key: str):
        """Initialize RunPod manager.

        Args:
            api_key: RunPod API key
        """
        self.api_key = api_key
        runpod.api_key = api_key
        self.pod_id: Optional[str] = None
        self.pod_info: Optional[Dict] = None

        # Register cleanup on exit
        atexit.register(self.cleanup)

    def create_instance(
        self,
        gpu_type: str,
        gpu_count: int = 1,
        disk_size: int = 50,
        docker_image: str = "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel",
        cloud_type: str = "SECURE",
    ) -> Dict:
        """Create a RunPod GPU instance.

        Args:
            gpu_type: GPU type to use
            gpu_count: Number of GPUs
            disk_size: Disk size in GB
            docker_image: Docker image to use
            cloud_type: Cloud type (SECURE, COMMUNITY, or ALL)

        Returns:
            Instance information dictionary
        """
        console.print(f"\n[cyan]Creating RunPod instance...[/cyan]")
        console.print(f"  GPU: {gpu_count}x {gpu_type}")
        console.print(f"  Disk: {disk_size}GB")
        console.print(f"  Image: {docker_image}")

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Finding available GPU...", total=None)

                # Create pod
                pod = runpod.create_pod(
                    name="secure-runpod-chat",
                    image_name=docker_image,
                    gpu_type_id=self._get_gpu_type_id(gpu_type),
                    cloud_type=cloud_type,
                    gpu_count=gpu_count,
                    volume_in_gb=disk_size,
                    container_disk_in_gb=disk_size,
                    ports="22/tcp",
                    env={
                        "JUPYTER_DISABLE_PASSWORDS": "1",
                    },
                )

                if not pod:
                    raise RuntimeError("Failed to create pod")

                self.pod_id = pod.get("id")
                progress.update(task, description=f"Instance created: {self.pod_id}")

                # Wait for instance to be ready
                progress.update(task, description="Waiting for instance to start...")
                self.pod_info = self._wait_for_instance_ready(self.pod_id)

            # Display instance information
            self._display_instance_info()

            return self.pod_info

        except Exception as e:
            console.print(f"[red]Error creating instance: {e}[/red]")
            if self.pod_id:
                self.cleanup()
            raise

    def _get_gpu_type_id(self, gpu_name: str) -> str:
        """Convert GPU name to RunPod GPU type ID.

        Args:
            gpu_name: Human-readable GPU name

        Returns:
            RunPod GPU type ID
        """
        # Mapping of GPU names to RunPod IDs
        gpu_mapping = {
            "NVIDIA RTX A4000": "NVIDIA RTX A4000",
            "NVIDIA RTX A5000": "NVIDIA RTX A5000",
            "NVIDIA A40": "NVIDIA A40",
            "NVIDIA RTX A6000": "NVIDIA RTX A6000",
            "NVIDIA A100": "NVIDIA A100 80GB PCIe",
            "NVIDIA A100 80GB": "NVIDIA A100 80GB PCIe",
        }

        return gpu_mapping.get(gpu_name, gpu_name)

    def _wait_for_instance_ready(self, pod_id: str, timeout: int = 300) -> Dict:
        """Wait for instance to be ready.

        Args:
            pod_id: Pod ID
            timeout: Maximum time to wait in seconds

        Returns:
            Pod information

        Raises:
            TimeoutError: If instance doesn't start within timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                pod = runpod.get_pod(pod_id)

                if not pod:
                    raise RuntimeError(f"Pod {pod_id} not found")

                status = pod.get("desiredStatus")

                if status == "RUNNING":
                    # Additional check for SSH connectivity
                    runtime = pod.get("runtime", {})
                    if runtime and runtime.get("ports"):
                        return pod

                time.sleep(5)

            except Exception as e:
                console.print(f"[yellow]Waiting for instance... ({e})[/yellow]")
                time.sleep(5)

        raise TimeoutError(f"Instance did not start within {timeout} seconds")

    def _display_instance_info(self):
        """Display instance information in a table."""
        if not self.pod_info:
            return

        runtime = self.pod_info.get("runtime", {})
        machine = self.pod_info.get("machine", {})

        table = Table(title="RunPod Instance Information", show_header=True)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Instance ID", self.pod_id or "N/A")
        table.add_row("Status", self.pod_info.get("desiredStatus", "UNKNOWN"))
        table.add_row("GPU Type", machine.get("gpuDisplayName", "N/A"))
        table.add_row("GPU Count", str(machine.get("gpuCount", 0)))
        table.add_row("Cost per Hour", f"${runtime.get('uptimeInSeconds', 0) * runtime.get('gpuCostPerHour', 0) / 3600:.4f}")

        # Get SSH connection info
        ports = runtime.get("ports", [])
        if ports:
            ssh_port = next((p for p in ports if p.get("privatePort") == 22), None)
            if ssh_port:
                public_ip = ssh_port.get("ip", "N/A")
                public_port = ssh_port.get("publicPort", "N/A")
                table.add_row("SSH Host", f"{public_ip}:{public_port}")

        console.print(table)

    def get_ssh_connection_info(self) -> Dict[str, str]:
        """Get SSH connection information.

        Returns:
            Dictionary with host, port, and username
        """
        if not self.pod_info:
            raise RuntimeError("No active instance")

        runtime = self.pod_info.get("runtime", {})
        ports = runtime.get("ports", [])

        if not ports:
            raise RuntimeError("No SSH port available")

        ssh_port = next((p for p in ports if p.get("privatePort") == 22), None)
        if not ssh_port:
            raise RuntimeError("SSH port not found")

        return {
            "host": ssh_port.get("ip"),
            "port": int(ssh_port.get("publicPort")),
            "username": "root",  # RunPod default
        }

    def get_cost_per_hour(self) -> float:
        """Get current cost per hour.

        Returns:
            Cost in dollars per hour
        """
        if not self.pod_info:
            return 0.0

        runtime = self.pod_info.get("runtime", {})
        return runtime.get("costPerHr", 0.0)

    def terminate_instance(self, pod_id: Optional[str] = None) -> bool:
        """Terminate the RunPod instance.

        Args:
            pod_id: Pod ID to terminate (uses self.pod_id if not provided)

        Returns:
            True if successful
        """
        target_pod_id = pod_id or self.pod_id

        if not target_pod_id:
            console.print("[yellow]No instance to terminate[/yellow]")
            return False

        try:
            console.print(f"\n[cyan]Terminating instance {target_pod_id}...[/cyan]")

            runpod.stop_pod(target_pod_id)
            time.sleep(2)  # Wait a bit before deleting

            runpod.terminate_pod(target_pod_id)

            console.print(f"[green]Instance {target_pod_id} terminated successfully[/green]")

            if target_pod_id == self.pod_id:
                self.pod_id = None
                self.pod_info = None

            return True

        except Exception as e:
            console.print(f"[red]Error terminating instance: {e}[/red]")
            return False

    def cleanup(self):
        """Cleanup resources on exit."""
        if self.pod_id:
            console.print("\n[yellow]Cleaning up instance...[/yellow]")
            self.terminate_instance()

    def verify_termination(self, pod_id: Optional[str] = None) -> bool:
        """Verify that instance has been terminated.

        Args:
            pod_id: Pod ID to verify (uses self.pod_id if not provided)

        Returns:
            True if instance is terminated
        """
        target_pod_id = pod_id or self.pod_id

        if not target_pod_id:
            return True

        try:
            pod = runpod.get_pod(target_pod_id)
            return pod is None or pod.get("desiredStatus") in ["EXITED", "STOPPED"]
        except:
            return True  # If we can't get pod info, assume it's terminated
