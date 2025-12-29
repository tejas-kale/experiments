"""Indian Health Insurance Assistant CLI.

A simple CLI interface for the Indian Health Insurance Assistant.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import box


def display_banner() -> None:
    """Display the application banner."""
    console = Console()

    title = Text()
    title.append("╔═══════════════════════════════════════════════════╗\n", style="bold cyan")
    title.append("║                                                   ║\n", style="bold cyan")
    title.append("║     ", style="bold cyan")
    title.append("Indian Health Insurance Assistant", style="bold yellow")
    title.append("     ║\n", style="bold cyan")
    title.append("║                                                   ║\n", style="bold cyan")
    title.append("╚═══════════════════════════════════════════════════╝", style="bold cyan")

    console.print()
    console.print(title)
    console.print()

    welcome_panel = Panel(
        "[bold white]Welcome to your personal health insurance assistant for India![/bold white]\n"
        "[dim]Type your questions about health insurance policies and get expert guidance.[/dim]\n\n"
        "[italic cyan]Commands:[/italic cyan] Type 'exit' or 'quit' to leave",
        title="[bold green]About[/bold green]",
        border_style="green",
        box=box.ROUNDED,
    )
    console.print(welcome_panel)
    console.print()


def chat_loop() -> None:
    """Run the main chat loop."""
    console = Console()

    while True:
        try:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")

            if user_input.lower() in ["exit", "quit"]:
                console.print("\n[bold green]Thank you for using Indian Health Insurance Assistant. Goodbye![/bold green]\n")
                break

            if not user_input.strip():
                continue

            # Placeholder response
            response = "Hi Tejas. This application is still WIP."
            console.print(f"[bold magenta]Assistant[/bold magenta]: {response}\n")

        except KeyboardInterrupt:
            console.print("\n\n[bold yellow]Interrupted. Goodbye![/bold yellow]\n")
            break
        except EOFError:
            console.print("\n\n[bold green]Goodbye![/bold green]\n")
            break


def main() -> None:
    """Main entry point for the CLI application."""
    display_banner()
    chat_loop()


if __name__ == "__main__":
    main()
