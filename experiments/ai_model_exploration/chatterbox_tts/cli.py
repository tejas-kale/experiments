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
from pydub import AudioSegment
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

# Load environment variables
load_dotenv()


def preprocess_text(text: str) -> str:
    """Preprocess text for better TTS quality.

    Args:
        text: Raw input text

    Returns:
        Cleaned text suitable for TTS
    """
    lines = text.split('\n')
    paragraphs = []
    current_paragraph = []

    for line in lines:
        # Strip leading/trailing whitespace
        cleaned_line = line.strip()

        if not cleaned_line:
            # Empty line = paragraph break
            if current_paragraph:
                # Join lines in current paragraph
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
        else:
            current_paragraph.append(cleaned_line)

    # Add final paragraph
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))

    # Join paragraphs with double newline
    result = '\n\n'.join(paragraphs)

    # Normalize multiple spaces to single space
    import re
    result = re.sub(r' +', ' ', result)

    return result


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


def adjust_speed(audio: AudioSegment, speed: float) -> AudioSegment:
    """Adjust audio playback speed.

    Args:
        audio: Input audio segment
        speed: Speed multiplier (0.5 = half speed, 2.0 = double speed)

    Returns:
        Speed-adjusted audio segment
    """
    # Change frame rate to adjust speed
    sound_with_altered_frame_rate = audio._spawn(
        audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)}
    )
    # Convert back to original frame rate to maintain pitch
    return sound_with_altered_frame_rate.set_frame_rate(audio.frame_rate)


def convert_to_mp3(
    wav_path: Path, mp3_path: Path, bitrate: str = "192k", speed: float = 1.0
) -> None:
    """Convert WAV file to MP3.

    Args:
        wav_path: Path to input WAV file
        mp3_path: Path to output MP3 file
        bitrate: MP3 bitrate (default: 192k)
        speed: Speed multiplier (default: 1.0)
    """
    console.print(f"[yellow]Converting to MP3 (bitrate: {bitrate})...[/yellow]")

    audio = AudioSegment.from_wav(str(wav_path))

    # Adjust speed if needed
    if speed != 1.0:
        console.print(f"[yellow]Adjusting speed ({speed}x)...[/yellow]")
        audio = adjust_speed(audio, speed)

    audio.export(str(mp3_path), format="mp3", bitrate=bitrate)

    console.print(f"[green]✓ MP3 saved to {mp3_path}[/green]")


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
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
def preprocess(input_file: Path, output_file: Path) -> None:
    """Preprocess a text file and save the cleaned version.

    This command only preprocesses the text without synthesizing speech.
    Useful for reviewing what will be sent to Chatterbox.
    """
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Text Preprocessing[/bold cyan]\n"
        "[dim]Clean formatting for TTS[/dim]",
        border_style="cyan",
    ))

    # Read input
    console.print(f"\n[cyan]Reading {input_file}...[/cyan]")
    raw_text = input_file.read_text(encoding="utf-8").strip()

    if not raw_text:
        console.print("[red]✗ File is empty[/red]")
        return

    # Preprocess
    console.print(f"[yellow]Preprocessing...[/yellow]")
    cleaned_text = preprocess_text(raw_text)

    # Save
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(cleaned_text, encoding="utf-8")

    # Show stats
    table = Table(title="Preprocessing Results", show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_row("Original length", f"{len(raw_text)} characters")
    table.add_row("Cleaned length", f"{len(cleaned_text)} characters")
    table.add_row("Change", f"{len(cleaned_text) - len(raw_text):+d} characters")
    table.add_row("Output file", str(output_file))
    console.print()
    console.print(table)

    console.print(f"\n[bold green]✓ Preprocessed text saved to {output_file}[/bold green]\n")


@cli.command()
@click.argument("text", type=str, required=False)
@click.option("--file", "-F", type=click.Path(exists=True, path_type=Path), help="Read text from file")
@click.option("--save-preprocessed", type=click.Path(path_type=Path), help="Save preprocessed text to file")
@click.option("--exaggeration", "-e", default=1.0, type=float, help="Emotion exaggeration (0.25-2.0)")
@click.option("--cfg-weight", "-c", default=0.7, type=float, help="CFG weight (0.0-1.0)")
@click.option("--temperature", "-t", default=1.0, type=float, help="Temperature (0.05-5.0)")
@click.option("--speed", "-s", default=0.85, type=float, help="Playback speed (0.5-2.0, default 0.85 for slower)")
@click.option("--voice", "-v", default="default", help="Voice name")
@click.option("--output", "-o", type=click.Path(path_type=Path), default=None, help="Output file path")
@click.option("--format", "-f", type=click.Choice(["wav", "mp3"]), default="wav", help="Output format (wav or mp3)")
@click.option("--bitrate", "-b", default="192k", help="MP3 bitrate (e.g., 128k, 192k, 320k)")
@click.option("--play/--no-play", default=True, help="Auto-play audio after generation")
@click.option("--endpoint-id", type=str, default=None, help="Runpod endpoint ID (optional, uses env var if not provided)")
def speak(
    text: str | None,
    file: Path | None,
    save_preprocessed: Path | None,
    exaggeration: float,
    cfg_weight: float,
    temperature: float,
    speed: float,
    voice: str,
    output: Path | None,
    format: str,
    bitrate: str,
    play: bool,
    endpoint_id: str | None,
) -> None:
    """Synthesize speech from text or file."""
    # Display banner
    console.print()
    console.print(Panel.fit(
        "[bold magenta]Chatterbox TTS[/bold magenta]\n"
        "[dim]Text-to-Speech Synthesis on Runpod[/dim]",
        border_style="magenta",
    ))

    # Get text from argument or file
    if text and file:
        console.print("[red]✗ Cannot specify both text and --file[/red]")
        console.print("[yellow]Use either: 'python cli.py speak \"text\"' or 'python cli.py speak --file text.txt'[/yellow]")
        return

    if not text and not file:
        console.print("[red]✗ Must provide either text or --file[/red]")
        console.print("[yellow]Usage: 'python cli.py speak \"text\"' or 'python cli.py speak --file text.txt'[/yellow]")
        return

    if file:
        console.print(f"[cyan]Reading text from {file}...[/cyan]")
        raw_text = file.read_text(encoding="utf-8").strip()
        if not raw_text:
            console.print("[red]✗ File is empty[/red]")
            return

        # Preprocess text to clean formatting issues
        text = preprocess_text(raw_text)
        console.print(f"[green]✓ Loaded {len(text)} characters from file[/green]")
        console.print(f"[dim]Preprocessed: removed formatting/indentation[/dim]")

        # Save preprocessed text if requested
        if save_preprocessed:
            save_preprocessed.parent.mkdir(parents=True, exist_ok=True)
            save_preprocessed.write_text(text, encoding="utf-8")
            console.print(f"[green]✓ Saved preprocessed text to {save_preprocessed}[/green]")

        console.print()

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
        ext = "mp3" if format == "mp3" else "wav"
        output = Path.cwd() / "chatterbox_output" / f"speech_{int(time.time())}.{ext}"
    output.parent.mkdir(parents=True, exist_ok=True)

    # Ensure output has correct extension
    if format == "mp3" and not str(output).endswith(".mp3"):
        output = output.with_suffix(".mp3")
    elif format == "wav" and not str(output).endswith(".wav"):
        output = output.with_suffix(".wav")

    # Display parameters
    table = Table(title="Synthesis Parameters", show_header=False)
    table.add_column("Parameter", style="magenta")
    table.add_column("Value", style="yellow")
    if file:
        table.add_row("Input Source", f"File: {file.name}")
    table.add_row("Text Length", f"{len(text)} characters")
    table.add_row("Exaggeration", str(exaggeration))
    table.add_row("CFG Weight", str(cfg_weight))
    table.add_row("Temperature", str(temperature))
    table.add_row("Speed", f"{speed}x")
    table.add_row("Voice", voice)
    table.add_row("Format", format.upper())
    if format == "mp3":
        table.add_row("Bitrate", bitrate)
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

        # Save audio (always starts as WAV from Runpod)
        temp_wav = output.with_suffix(".wav.temp")
        console.print(f"\n[yellow]Saving audio...[/yellow]")
        with open(temp_wav, "wb") as f:
            f.write(audio_bytes)

        # Process audio (speed adjustment)
        if speed != 1.0 or format == "mp3":
            audio = AudioSegment.from_wav(str(temp_wav))

            # Adjust speed
            if speed != 1.0:
                console.print(f"[yellow]Adjusting speed to {speed}x...[/yellow]")
                audio = adjust_speed(audio, speed)

            # Export in final format
            if format == "mp3":
                console.print(f"[yellow]Converting to MP3 (bitrate: {bitrate})...[/yellow]")
                audio.export(str(output), format="mp3", bitrate=bitrate)
            else:
                # Save as WAV with speed adjustment
                audio.export(str(output), format="wav")

            # Remove temp file
            temp_wav.unlink()
            console.print(f"[green]✓ Audio saved to {output}[/green]")
        else:
            # No processing needed, just rename temp to final
            temp_wav.rename(output)
            console.print(f"[green]✓ Audio saved to {output}[/green]")

        final_output = output

        # Play audio
        if play:
            console.print("\n[yellow]Playing audio...[/yellow]")
            play_audio(final_output)

        console.print(f"\n[bold green]✓ Synthesis complete![/bold green]\n")

    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]\n")
        raise


if __name__ == "__main__":
    cli()
