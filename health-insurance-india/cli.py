#!/usr/bin/env python3
"""Health Insurance India CLI - Query policies using AI agents"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich import box
from typing import Optional
import sys
from pathlib import Path

from agents.insurance_agent import InsuranceAgent
from collectors.base_collector import CollectorFactory
from services.document_service import DocumentService
from services.policy_service import PolicyService
from models.database import init_db, get_db, close_db
from models.schemas import DocumentCreate
from utils.config import Config
from utils.logger import get_logger

# Initialize
app = typer.Typer(
    name="health-insurance",
    help="🏥 Health Insurance India CLI - Query policies using AI agents",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()
logger = get_logger(__name__)

# Initialize config
try:
    Config.validate()
except ValueError as e:
    console.print(f"[red]Configuration Error:[/red] {e}")
    console.print("\n[yellow]Please set ANTHROPIC_API_KEY in .env file or environment[/yellow]")
    sys.exit(1)

# Initialize agent
try:
    agent = InsuranceAgent(api_key=Config.ANTHROPIC_API_KEY)
except Exception as e:
    console.print(f"[red]Failed to initialize agent:[/red] {e}")
    agent = None


@app.command()
def collect(
    insurer: Optional[str] = typer.Option(None, "--insurer", help="Specific insurer to collect from"),
    all_insurers: bool = typer.Option(False, "--all", help="Collect from all insurers")
):
    """📥 Collect insurance policy documents from insurers"""

    console.print(Panel.fit(
        "[bold cyan]Document Collection[/bold cyan]",
        subtitle="Fetching policy documents from insurers",
        border_style="cyan"
    ))

    if all_insurers:
        insurers = CollectorFactory.list_all()
        console.print(f"\n[yellow]Collecting from {len(insurers)} insurers...[/yellow]\n")
    elif insurer:
        insurers = [insurer]
    else:
        console.print("[red]Error:[/red] Specify --insurer or --all")
        console.print("[dim]Example: python cli.py collect --all[/dim]")
        return

    db = get_db()
    doc_service = DocumentService(db)
    total_collected = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        for ins in insurers:
            task = progress.add_task(f"Collecting from {ins}...", total=None)

            try:
                collector = CollectorFactory.create(ins)
                documents = collector.collect()

                # Save to database
                for doc in documents:
                    if doc.get('text'):  # Only save new documents
                        try:
                            doc_data = DocumentCreate(
                                insurer_name=doc['insurer'],
                                product_name=doc['product'],
                                document_type=doc['document_type'],
                                file_path=doc['file_path'],
                                source_url=doc.get('source_url'),
                                is_user_uploaded=False
                            )
                            doc_service.create(doc_data)
                            total_collected += 1
                        except Exception as e:
                            logger.error(f"Failed to save document: {e}")

                progress.update(task, description=f"[green]✓[/green] {ins}: {len(documents)} documents")
                console.print(f"[green]✓[/green] {ins}: Collected {len(documents)} documents")

            except Exception as e:
                progress.update(task, description=f"[red]✗[/red] {ins}: Failed")
                console.print(f"[red]✗[/red] {ins}: {str(e)}")

    close_db(db)
    console.print(f"\n[bold green]Collection complete! Added {total_collected} new documents to database[/bold green]")


@app.command()
def add_document(
    path: str = typer.Argument(..., help="Path or URL to insurance document"),
    insurer: Optional[str] = typer.Option(None, "--insurer", help="Insurer name"),
    product: Optional[str] = typer.Option(None, "--product", help="Product name"),
    auto_extract: bool = typer.Option(True, "--auto-extract/--no-extract", help="Auto-extract metadata")
):
    """📄 Add a user insurance document"""

    console.print(Panel.fit(
        "[bold cyan]Add Document[/bold cyan]",
        subtitle="Upload your insurance policy",
        border_style="cyan"
    ))

    db = get_db()
    doc_service = DocumentService(db)

    with console.status("[bold yellow]Processing document..."):
        try:
            doc_id = doc_service.add_user_document(
                path=path,
                insurer=insurer,
                product=product,
                auto_extract=auto_extract
            )

            console.print(f"\n[green]✓[/green] Document added successfully!")
            console.print(f"[dim]Document ID: {doc_id}[/dim]")

        except Exception as e:
            console.print(f"\n[red]✗ Error:[/red] {str(e)}")

    close_db(db)


@app.command()
def list_documents():
    """📋 List all documents in the database"""

    db = get_db()
    doc_service = DocumentService(db)
    documents = doc_service.list_all()

    table = Table(
        title="📚 Insurance Documents",
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED
    )
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Insurer", style="green")
    table.add_column("Product", style="blue")
    table.add_column("Type", style="yellow")
    table.add_column("Pages", justify="right")
    table.add_column("User Upload", justify="center")

    for doc in documents:
        table.add_row(
            str(doc.id),
            doc.insurer_name,
            doc.product_name or "N/A",
            doc.document_type or "N/A",
            str(doc.page_count) if doc.page_count else "?",
            "✓" if doc.is_user_uploaded else ""
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(documents)} documents[/dim]")

    close_db(db)


@app.command()
def chat(
    policy: Optional[str] = typer.Option(None, "--policy", help="Focus on specific policy")
):
    """💬 Start interactive chat with insurance agent"""

    if not agent:
        console.print("[red]Agent not initialized. Please check your ANTHROPIC_API_KEY[/red]")
        return

    console.print(Panel.fit(
        "[bold cyan]🤖 Health Insurance Agent[/bold cyan]\n"
        "[dim]Powered by Anthropic Claude[/dim]",
        subtitle="Type 'exit' or 'quit' to end conversation",
        border_style="cyan"
    ))

    if policy:
        console.print(f"\n[yellow]Focused on:[/yellow] {policy}\n")

    console.print("[dim]Ask me anything about health insurance policies![/dim]\n")

    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")

            if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
                console.print("\n[yellow]👋 Goodbye! Stay healthy![/yellow]")
                break

            if not user_input.strip():
                continue

            # Special commands
            if user_input.lower() == 'reset':
                agent.reset_conversation()
                console.print("[yellow]Conversation reset[/yellow]")
                continue

            # Show thinking indicator
            with console.status("[bold yellow]🤔 Agent is thinking..."):
                response = agent.chat(user_input)

            # Display response
            console.print(f"\n[bold green]🤖 Agent:[/bold green]")
            console.print(Markdown(response))

        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Interrupted. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error:[/red] {str(e)}")
            logger.error(f"Chat error: {e}")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask")
):
    """❓ Ask a single question (non-interactive)"""

    if not agent:
        console.print("[red]Agent not initialized. Please check your ANTHROPIC_API_KEY[/red]")
        return

    with console.status("[bold yellow]🤔 Thinking..."):
        response = agent.chat(question, reset_history=True)

    console.print(Panel(
        Markdown(response),
        title="[bold green]Answer[/bold green]",
        border_style="green"
    ))


@app.command()
def compare(
    policies: str = typer.Argument(..., help="Policies to compare (comma-separated)"),
    aspects: Optional[str] = typer.Option(None, "--aspects", help="Aspects to compare (comma-separated)")
):
    """⚖️  Compare multiple insurance policies"""

    if not agent:
        console.print("[red]Agent not initialized. Please check your ANTHROPIC_API_KEY[/red]")
        return

    policy_list = [p.strip() for p in policies.split(",")]
    aspect_list = [a.strip() for a in aspects.split(",")] if aspects else None

    question = f"Compare these policies in detail: {', '.join(policy_list)}"
    if aspect_list:
        question += f" focusing on: {', '.join(aspect_list)}"

    with console.status("[bold yellow]📊 Comparing policies..."):
        response = agent.chat(question, reset_history=True)

    console.print(Panel(
        Markdown(response),
        title="[bold cyan]Policy Comparison[/bold cyan]",
        border_style="cyan"
    ))


@app.command()
def summarize(
    policy: str = typer.Option(..., "--policy", help="Policy to summarize")
):
    """📝 Get a summary of a specific policy"""

    if not agent:
        console.print("[red]Agent not initialized. Please check your ANTHROPIC_API_KEY[/red]")
        return

    question = f"Provide a comprehensive summary of {policy} including key features, exclusions, waiting periods, and important warnings. Present it in a clear, structured format."

    with console.status("[bold yellow]📋 Generating summary..."):
        response = agent.chat(question, reset_history=True)

    console.print(Panel(
        Markdown(response),
        title=f"[bold cyan]{policy} Summary[/bold cyan]",
        border_style="cyan"
    ))


@app.command()
def serve(
    port: int = typer.Option(8000, "--port", help="Port to run on"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
    host: str = typer.Option("0.0.0.0", "--host", help="Host to bind to")
):
    """🚀 Start FastAPI server for API access"""

    console.print(Panel.fit(
        "[bold cyan]Starting API Server[/bold cyan]\n"
        f"[dim]http://{host}:{port}[/dim]\n"
        f"[dim]Docs: http://{host}:{port}/docs[/dim]",
        subtitle="Press Ctrl+C to stop",
        border_style="cyan"
    ))

    import uvicorn

    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


@app.command()
def list_insurers():
    """🏢 List supported insurers"""

    insurers = CollectorFactory.list_all()

    table = Table(
        title="Supported Insurers",
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED
    )
    table.add_column("Insurer", style="cyan")
    table.add_column("Status", style="green")

    for insurer in insurers:
        table.add_row(insurer.replace('_', ' ').title(), "✓ Active")

    console.print(table)


@app.command()
def list_policies():
    """📋 List all policies in database"""

    db = get_db()
    policy_service = PolicyService(db)
    policies = policy_service.list_all()

    if not policies:
        console.print("[yellow]No policies in database. Run collection first:[/yellow]")
        console.print("[dim]  python cli.py collect --all[/dim]")
        close_db(db)
        return

    table = Table(
        title="📋 Insurance Policies",
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED
    )
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Insurer", style="green")
    table.add_column("Product", style="blue")
    table.add_column("UIN", style="yellow")
    table.add_column("Sum Insured Range", style="magenta")

    for policy in policies:
        si_range = "N/A"
        if policy.min_sum_insured:
            si_range = f"₹{policy.min_sum_insured:,} - ₹{policy.max_sum_insured:,}"

        table.add_row(
            str(policy.id),
            policy.insurer_name,
            policy.product_name,
            policy.uin_number or "N/A",
            si_range
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(policies)} policies[/dim]")

    close_db(db)


# Database commands
db_app = typer.Typer(help="🗄️  Database operations")
app.add_typer(db_app, name="db")


@db_app.command("init")
def db_init():
    """Initialize database"""
    console.print("[yellow]Initializing database...[/yellow]")
    init_db()
    console.print("[green]✓ Database initialized![/green]")


@db_app.command("status")
def db_status():
    """Show database statistics"""

    db = get_db()
    policy_service = PolicyService(db)
    doc_service = DocumentService(db)

    policy_count = policy_service.count()
    doc_count = doc_service.count()

    db_path = Config.DATA_DIR / "policies.db"
    db_size = db_path.stat().st_size / 1024 if db_path.exists() else 0

    table = Table(
        title="Database Status",
        box=box.ROUNDED
    )
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")

    table.add_row("Policies", str(policy_count))
    table.add_row("Documents", str(doc_count))
    table.add_row("Database Size", f"{db_size:.2f} KB")
    table.add_row("Location", str(db_path))

    console.print(table)

    close_db(db)


@db_app.command("reset")
def db_reset():
    """Reset database (WARNING: Deletes all data)"""

    if Confirm.ask("[red]⚠️  Are you sure? This will delete all data![/red]"):
        console.print("[yellow]Resetting database...[/yellow]")

        # Drop and recreate
        db_path = Config.DATA_DIR / "policies.db"
        if db_path.exists():
            db_path.unlink()

        init_db()
        console.print("[green]✓ Database reset complete![/green]")
    else:
        console.print("[yellow]Cancelled.[/yellow]")


@app.callback()
def main():
    """
    🏥 Health Insurance India CLI

    Query and compare Indian health insurance policies using AI agents.
    """
    pass


if __name__ == "__main__":
    app()
