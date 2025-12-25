"""Interactive chat interface for secure-runpod-chat."""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from cryptography.fernet import Fernet
from .ssh_client import SSHClient
from .model_deployer import ModelDeployer
from .utils import sanitize_path

console = Console()


class ChatInterface:
    """Interactive chat interface."""

    def __init__(
        self,
        ssh_client: SSHClient,
        model_deployer: ModelDeployer,
        model_id: str,
        is_vision: bool = False,
        save_history: bool = True,
    ):
        """Initialize chat interface.

        Args:
            ssh_client: Connected SSH client
            model_deployer: Model deployer instance
            model_id: HuggingFace model ID
            is_vision: Whether model supports vision
            save_history: Whether to save chat history
        """
        self.ssh = ssh_client
        self.deployer = model_deployer
        self.model_id = model_id
        self.is_vision = is_vision
        self.save_history = save_history
        self.history: List[Dict] = []
        self.history_file: Optional[Path] = None
        self.encryption_key: Optional[bytes] = None

        if save_history:
            self._setup_history()

    def _setup_history(self):
        """Setup encrypted chat history."""
        # Create history directory
        history_dir = Path.home() / ".secure-runpod-chat" / "history"
        history_dir.mkdir(parents=True, exist_ok=True)

        # Create encryption key if not exists
        key_file = history_dir / ".key"
        if key_file.exists():
            self.encryption_key = key_file.read_bytes()
        else:
            self.encryption_key = Fernet.generate_key()
            key_file.write_bytes(self.encryption_key)
            key_file.chmod(0o600)  # Restrict permissions

        # Create history file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = self.model_id.replace("/", "_")
        self.history_file = history_dir / f"{model_name}_{timestamp}.enc"

    def _save_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Save message to history.

        Args:
            role: Message role (user/assistant)
            content: Message content
            metadata: Optional metadata
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        self.history.append(message)

        if self.save_history and self.history_file and self.encryption_key:
            try:
                # Encrypt and save
                fernet = Fernet(self.encryption_key)
                history_json = json.dumps(self.history, indent=2)
                encrypted_data = fernet.encrypt(history_json.encode())
                self.history_file.write_bytes(encrypted_data)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not save history: {e}[/yellow]")

    def show_help(self):
        """Show help message."""
        help_text = """
## Available Commands

- `/help` - Show this help message
- `/upload <local_path>` - Upload a file to the instance
- `/download <remote_path> [local_path]` - Download a file from the instance
- `/image <path>` - Include an image in your message (vision models only)
- `/clear` - Clear chat history
- `/cost` - Show current instance cost
- `/exit` - Exit and terminate the instance
- `/quit` - Same as /exit

## Tips

- For vision models, use `/image <path>` before your message
- Files are uploaded to `/root/uploads/` on the instance
- Use Ctrl+C to interrupt long responses
- Chat history is encrypted and saved locally
"""
        console.print(Panel(Markdown(help_text), title="Help", border_style="cyan"))

    def handle_upload_command(self, args: str) -> bool:
        """Handle /upload command.

        Args:
            args: Command arguments

        Returns:
            True if successful
        """
        if not args:
            console.print("[red]Usage: /upload <local_path>[/red]")
            return False

        local_path = args.strip()
        if not os.path.exists(local_path):
            console.print(f"[red]File not found: {local_path}[/red]")
            return False

        # Create uploads directory on remote
        self.ssh.execute_command("mkdir -p /root/uploads")

        # Upload file
        filename = os.path.basename(local_path)
        remote_path = f"/root/uploads/{filename}"

        if self.ssh.upload_file(local_path, remote_path):
            console.print(f"[green]File uploaded to {remote_path}[/green]")
            return True

        return False

    def handle_download_command(self, args: str) -> bool:
        """Handle /download command.

        Args:
            args: Command arguments

        Returns:
            True if successful
        """
        if not args:
            console.print("[red]Usage: /download <remote_path> [local_path][/red]")
            return False

        parts = args.strip().split(maxsplit=1)
        remote_path = parts[0]

        if len(parts) > 1:
            local_path = parts[1]
        else:
            local_path = os.path.basename(remote_path)

        # Check if remote file exists
        if not self.ssh.file_exists(remote_path):
            console.print(f"[red]Remote file not found: {remote_path}[/red]")
            return False

        # Download file
        if self.ssh.download_file(remote_path, local_path):
            console.print(f"[green]File downloaded to {local_path}[/green]")
            return True

        return False

    def handle_image_command(self, args: str) -> Optional[str]:
        """Handle /image command.

        Args:
            args: Command arguments

        Returns:
            Path to uploaded image or None
        """
        if not self.is_vision:
            console.print("[yellow]This model does not support vision inputs[/yellow]")
            return None

        if not args:
            console.print("[red]Usage: /image <path>[/red]")
            return None

        image_path = args.strip()
        if not os.path.exists(image_path):
            console.print(f"[red]Image not found: {image_path}[/red]")
            return None

        # Upload image
        self.ssh.execute_command("mkdir -p /root/images")
        filename = os.path.basename(image_path)
        remote_path = f"/root/images/{filename}"

        if self.ssh.upload_file(image_path, remote_path):
            console.print(f"[green]Image uploaded. Include it in your next message.[/green]")
            return remote_path

        return None

    def run(self):
        """Run the interactive chat interface."""
        # Display welcome message
        console.print(Panel(
            f"[bold cyan]Secure RunPod Chat[/bold cyan]\n\n"
            f"Model: {self.model_id}\n"
            f"Vision support: {'Yes' if self.is_vision else 'No'}\n\n"
            f"Type /help for available commands\n"
            f"Type /exit to quit and terminate instance",
            border_style="cyan",
        ))

        current_image: Optional[str] = None

        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    command_parts = user_input[1:].split(maxsplit=1)
                    command = command_parts[0].lower()
                    args = command_parts[1] if len(command_parts) > 1 else ""

                    if command in ["exit", "quit"]:
                        if console.input("\n[yellow]Terminate instance and exit? (y/N): [/yellow]").lower() == 'y':
                            break
                        continue

                    elif command == "help":
                        self.show_help()
                        continue

                    elif command == "upload":
                        self.handle_upload_command(args)
                        continue

                    elif command == "download":
                        self.handle_download_command(args)
                        continue

                    elif command == "image":
                        current_image = self.handle_image_command(args)
                        continue

                    elif command == "clear":
                        self.history = []
                        console.print("[green]Chat history cleared[/green]")
                        continue

                    elif command == "cost":
                        # This would need to be passed from the main CLI
                        console.print("[yellow]Cost information not available in this context[/yellow]")
                        continue

                    else:
                        console.print(f"[red]Unknown command: /{command}[/red]")
                        console.print("[dim]Type /help for available commands[/dim]")
                        continue

                # Save user message
                self._save_message("user", user_input, {"image": current_image})

                # Send to model
                console.print("\n[bold cyan]Assistant[/bold cyan]")

                with console.status("[cyan]Thinking...[/cyan]"):
                    response = self.deployer.send_chat_message(
                        prompt=user_input,
                        image_path=current_image,
                    )

                if response:
                    console.print(response)
                    self._save_message("assistant", response)
                else:
                    console.print("[red]Failed to get response from model[/red]")

                # Clear current image after use
                current_image = None

            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Use /exit to quit.[/yellow]")
                continue

            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                continue

        console.print("\n[cyan]Exiting chat interface...[/cyan]")

    def cleanup(self):
        """Cleanup resources."""
        if self.history and self.save_history:
            console.print("[cyan]Chat history saved[/cyan]")
