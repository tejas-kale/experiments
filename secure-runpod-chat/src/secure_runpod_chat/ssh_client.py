"""SSH client for secure communication with RunPod instances."""

import os
import time
import paramiko
from typing import Optional, Tuple, List
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn

console = Console()


class SSHClient:
    """Secure SSH client for RunPod instances."""

    def __init__(self, host: str, port: int, username: str = "root"):
        """Initialize SSH client.

        Args:
            host: SSH host
            port: SSH port
            username: SSH username
        """
        self.host = host
        self.port = port
        self.username = username
        self.client: Optional[paramiko.SSHClient] = None
        self.sftp: Optional[paramiko.SFTPClient] = None

    def connect(self, timeout: int = 60, max_retries: int = 5) -> bool:
        """Connect to SSH server with retries.

        Args:
            timeout: Connection timeout in seconds
            max_retries: Maximum number of connection attempts

        Returns:
            True if connected successfully
        """
        console.print(f"\n[cyan]Connecting to {self.host}:{self.port}...[/cyan]")

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        for attempt in range(max_retries):
            try:
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    timeout=timeout,
                    look_for_keys=False,
                    allow_agent=False,
                    password="",  # RunPod instances typically use key-based auth or no password
                    auth_timeout=timeout,
                )

                console.print(f"[green]Connected successfully![/green]")
                self.sftp = self.client.open_sftp()
                return True

            except paramiko.AuthenticationException:
                # Try without password
                try:
                    self.client.connect(
                        hostname=self.host,
                        port=self.port,
                        username=self.username,
                        timeout=timeout,
                        look_for_keys=False,
                        allow_agent=False,
                    )
                    console.print(f"[green]Connected successfully![/green]")
                    self.sftp = self.client.open_sftp()
                    return True
                except Exception as e:
                    console.print(f"[yellow]Authentication attempt {attempt + 1}/{max_retries} failed[/yellow]")

            except Exception as e:
                console.print(f"[yellow]Connection attempt {attempt + 1}/{max_retries} failed: {e}[/yellow]")

            if attempt < max_retries - 1:
                time.sleep(5)

        console.print("[red]Failed to connect after multiple attempts[/red]")
        return False

    def execute_command(
        self, command: str, timeout: Optional[int] = None, stream_output: bool = False
    ) -> Tuple[int, str, str]:
        """Execute command on remote server.

        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            stream_output: Whether to stream output in real-time

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not self.client:
            raise RuntimeError("Not connected to SSH server")

        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)

            if stream_output:
                # Stream output in real-time
                stdout_lines = []
                stderr_lines = []

                # Read stdout
                for line in stdout:
                    line = line.strip()
                    if line:
                        console.print(line)
                        stdout_lines.append(line)

                # Read stderr
                for line in stderr:
                    line = line.strip()
                    if line:
                        console.print(f"[yellow]{line}[/yellow]")
                        stderr_lines.append(line)

                exit_code = stdout.channel.recv_exit_status()
                return exit_code, "\n".join(stdout_lines), "\n".join(stderr_lines)
            else:
                # Get all output at once
                stdout_str = stdout.read().decode("utf-8")
                stderr_str = stderr.read().decode("utf-8")
                exit_code = stdout.channel.recv_exit_status()

                return exit_code, stdout_str, stderr_str

        except Exception as e:
            console.print(f"[red]Error executing command: {e}[/red]")
            return -1, "", str(e)

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to remote server.

        Args:
            local_path: Local file path
            remote_path: Remote file path

        Returns:
            True if successful
        """
        if not self.sftp:
            raise RuntimeError("SFTP not initialized")

        try:
            local_file = Path(local_path)
            if not local_file.exists():
                console.print(f"[red]Local file not found: {local_path}[/red]")
                return False

            file_size = local_file.stat().st_size

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Uploading {local_file.name}...", total=file_size
                )

                def callback(transferred, total):
                    progress.update(task, completed=transferred)

                self.sftp.put(local_path, remote_path, callback=callback)

            console.print(f"[green]Uploaded {local_path} to {remote_path}[/green]")
            return True

        except Exception as e:
            console.print(f"[red]Error uploading file: {e}[/red]")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file from remote server.

        Args:
            remote_path: Remote file path
            local_path: Local file path

        Returns:
            True if successful
        """
        if not self.sftp:
            raise RuntimeError("SFTP not initialized")

        try:
            # Get remote file size
            file_stat = self.sftp.stat(remote_path)
            file_size = file_stat.st_size

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Downloading {os.path.basename(remote_path)}...", total=file_size
                )

                def callback(transferred, total):
                    progress.update(task, completed=transferred)

                self.sftp.get(remote_path, local_path, callback=callback)

            console.print(f"[green]Downloaded {remote_path} to {local_path}[/green]")
            return True

        except Exception as e:
            console.print(f"[red]Error downloading file: {e}[/red]")
            return False

    def list_files(self, remote_path: str) -> List[str]:
        """List files in remote directory.

        Args:
            remote_path: Remote directory path

        Returns:
            List of file names
        """
        if not self.sftp:
            raise RuntimeError("SFTP not initialized")

        try:
            return self.sftp.listdir(remote_path)
        except Exception as e:
            console.print(f"[red]Error listing files: {e}[/red]")
            return []

    def file_exists(self, remote_path: str) -> bool:
        """Check if remote file exists.

        Args:
            remote_path: Remote file path

        Returns:
            True if file exists
        """
        if not self.sftp:
            raise RuntimeError("SFTP not initialized")

        try:
            self.sftp.stat(remote_path)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def cleanup_remote_files(self, patterns: List[str]) -> bool:
        """Clean up remote files matching patterns.

        Args:
            patterns: List of file patterns to delete

        Returns:
            True if successful
        """
        if not self.client:
            return False

        try:
            for pattern in patterns:
                command = f"rm -rf {pattern}"
                exit_code, stdout, stderr = self.execute_command(command)

                if exit_code == 0:
                    console.print(f"[green]Cleaned up {pattern}[/green]")
                else:
                    console.print(f"[yellow]Failed to clean up {pattern}: {stderr}[/yellow]")

            return True

        except Exception as e:
            console.print(f"[red]Error during cleanup: {e}[/red]")
            return False

    def close(self):
        """Close SSH connection."""
        if self.sftp:
            try:
                self.sftp.close()
            except:
                pass

        if self.client:
            try:
                self.client.close()
            except:
                pass

        console.print("[cyan]SSH connection closed[/cyan]")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
