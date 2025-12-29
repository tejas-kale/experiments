"""Chatterbox TTS CLI for Runpod.

A CLI tool to run Chatterbox TTS on Runpod instances for text-to-speech synthesis.
"""

from __future__ import annotations

import base64
import os
import platform
import subprocess
import time
from pathlib import Path

import click
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

# Load environment variables
load_dotenv()


class ChatterboxRunpodClient:
    """Client for managing Chatterbox TTS on Runpod."""

    def __init__(self, api_key: str, endpoint_id: str):
        """Initialize the client with Runpod API key and endpoint ID.

        Args:
            api_key: Runpod API key
            endpoint_id: Runpod endpoint ID
        """
        self.api_key = api_key
        self.endpoint_id = endpoint_id
        self.endpoint_url = f"https://api.runpod.ai/v2/{endpoint_id}"

    def synthesize_speech(
        self,
        text: str,
        exaggeration: float = 1.0,
        cfg_weight: float = 0.7,
        temperature: float = 1.0,
        voice: str = "default",
    ) -> bytes:
        """Synthesize speech from text.

        Args:
            text: Input text to synthesize
            exaggeration: Emotion exaggeration (0.25-2.0)
            cfg_weight: Classifier-free guidance weight (0.0-1.0)
            temperature: Sampling temperature (0.05-5.0)
            voice: Voice name (default or custom)

        Returns:
            WAV audio bytes
        """
        console.print(f"\n[yellow]Synthesizing speech...[/yellow]")
        console.print(f"[dim]Text: {text[:100]}{'...' if len(text) > 100 else ''}[/dim]")

        # Prepare request payload
        payload = {
            "input": {
                "text": text,
                "exaggeration": exaggeration,
                "cfg_weight": cfg_weight,
                "temperature": temperature,
                "voice": voice,
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
                        console.print("[green]✓ Speech synthesized successfully[/green]")

                        # Decode audio
                        audio_b64 = status_data["output"]["audio"]
                        audio_bytes = base64.b64decode(audio_b64)
                        return audio_bytes

                    elif status_data["status"] == "FAILED":
                        raise RuntimeError(f"Job failed: {status_data.get('error', 'Unknown error')}")

                time.sleep(2)


def play_audio(audio_path: Path) -> None:
    """Play audio file using system default player.

    Args:
        audio_path: Path to audio file
    """
    try:
        system = platform.system()

        if system == "Darwin":  # macOS
            subprocess.run(["afplay", str(audio_path)], check=True)
        elif system == "Linux":
            subprocess.run(["aplay", str(audio_path)], check=True)
        elif system == "Windows":
            os.startfile(str(audio_path))
        else:
            console.print(f"[yellow]Audio saved to {audio_path}. Please play manually.[/yellow]")

    except Exception as e:
        console.print(f"[yellow]Could not auto-play audio: {e}[/yellow]")
        console.print(f"[yellow]Audio saved to {audio_path}[/yellow]")


@click.group()
def cli() -> None:
    """Chatterbox TTS CLI for Runpod."""
    pass


@cli.command()
@click.argument("text", type=str)
@click.option("--exaggeration", "-e", default=1.0, type=float, help="Emotion exaggeration (0.25-2.0)")
@click.option("--cfg-weight", "-c", default=0.7, type=float, help="CFG weight (0.0-1.0)")
@click.option("--temperature", "-t", default=1.0, type=float, help="Temperature (0.05-5.0)")
@click.option("--voice", "-v", default="default", help="Voice name")
@click.option("--output", "-o", type=click.Path(path_type=Path), default=None, help="Output file path")
@click.option("--play/--no-play", default=True, help="Auto-play audio after generation")
@click.option("--endpoint-id", type=str, default=None, help="Runpod endpoint ID (optional, uses env var if not provided)")
def speak(
    text: str,
    exaggeration: float,
    cfg_weight: float,
    temperature: float,
    voice: str,
    output: Path | None,
    play: bool,
    endpoint_id: str | None,
) -> None:
    """Synthesize speech from text."""
    # Display banner
    console.print()
    console.print(Panel.fit(
        "[bold magenta]Chatterbox TTS[/bold magenta]\n"
        "[dim]Text-to-Speech Synthesis on Runpod[/dim]",
        border_style="magenta",
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

    # Setup output path
    if output is None:
        output = Path.cwd() / "chatterbox_output" / f"speech_{int(time.time())}.wav"
    output.parent.mkdir(parents=True, exist_ok=True)

    # Display parameters
    table = Table(title="Synthesis Parameters", show_header=False)
    table.add_column("Parameter", style="magenta")
    table.add_column("Value", style="yellow")
    table.add_row("Text Length", f"{len(text)} characters")
    table.add_row("Exaggeration", str(exaggeration))
    table.add_row("CFG Weight", str(cfg_weight))
    table.add_row("Temperature", str(temperature))
    table.add_row("Voice", voice)
    table.add_row("Endpoint ID", endpoint_id)
    table.add_row("Output File", str(output))
    console.print(table)

    # Initialize client
    client = ChatterboxRunpodClient(api_key, endpoint_id)

    try:
        # Synthesize speech
        audio_bytes = client.synthesize_speech(
            text=text,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            temperature=temperature,
            voice=voice,
        )

        # Save audio
        console.print(f"\n[yellow]Saving audio to {output}...[/yellow]")
        with open(output, "wb") as f:
            f.write(audio_bytes)
        console.print(f"[green]✓ Audio saved to {output}[/green]")

        # Play audio
        if play:
            console.print("\n[yellow]Playing audio...[/yellow]")
            play_audio(output)

        console.print(f"\n[bold green]✓ Synthesis complete![/bold green]\n")

    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]\n")
        raise


if __name__ == "__main__":
    cli()
