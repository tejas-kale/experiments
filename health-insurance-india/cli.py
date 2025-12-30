"""CLI for Health Insurance India - Query policies using AI agents"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
import sys
from pathlib import Path

from agents.insurance_agent import InsuranceAgent
from services.document_service import DocumentService
from services.policy_service import PolicyService
from models.database import init_db, get_db
from utils.config import Config

app = typer.Typer(
    name="health-insurance",
    help="Health Insurance India CLI - Query policies using AI agents",
    add_completion=False
)
console = Console()
config = Config()

# Initialize agent
try:
    agent = InsuranceAgent(api_key=config.anthropic_api_key)
except Exception as e:
    agent = None


@app.command()
def chat(
    policy: str = typer.Option(None, "--policy", "-p", help="Focus on specific policy")
):
    """Start interactive chat with insurance agent"""
    
    if not agent:
        console.print("[red]Error: ANTHROPIC_API_KEY not configured[/red]")
        console.print("[yellow]Set ANTHROPIC_API_KEY environment variable[/yellow]")
        return
    
    console.print(Panel.fit(
        "[bold cyan]Health Insurance Agent[/bold cyan]\n"
        "[dim]Powered by Anthropic Agents SDK[/dim]",
        subtitle="Type 'exit' or 'quit' to end conversation"
    ))
    
    if policy:
        console.print(f"\n[yellow]Focused on:[/yellow] {policy}\n")
    
    console.print("[dim]Ask me anything about health insurance policies![/dim]\n")
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            
            if not user_input.strip():
                continue
            
            # Show thinking indicator
            with console.status("[bold yellow]Agent is thinking..."):
                response = agent.chat(user_input)
            
            # Display response
            console.print(f"\n[bold green]Agent:[/bold green]")
            console.print(Markdown(response))
            
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Interrupted. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error:[/red] {str(e)}")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask"),
    policy: str = typer.Option(None, "--policy", "-p", help="Focus on specific policy")
):
    """Ask a single question (non-interactive)"""
    
    if not agent:
        console.print("[red]Error: ANTHROPIC_API_KEY not configured[/red]")
        return
    
    with console.status("[bold yellow]Thinking..."):
        response = agent.chat(question)
    
    console.print(Panel(
        Markdown(response),
        title="[bold green]Answer[/bold green]",
        border_style="green"
    ))


@app.command()
def add_document(
    path: str = typer.Argument(..., help="Path or URL to insurance document"),
    insurer: str = typer.Option(None, "--insurer", "-i", help="Insurer name"),
    product: str = typer.Option(None, "--product", "-p", help="Product name"),
    auto_extract: bool = typer.Option(True, help="Automatically extract metadata")
):
    """Add a user insurance document"""
    
    console.print(Panel.fit(
        "[bold cyan]Add Document[/bold cyan]",
        subtitle="Upload your insurance policy"
    ))
    
    db = get_db()
    doc_service = DocumentService(db)
    
    with console.status("[bold yellow]Processing document..."):
        try:
            # Add document
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


@app.command()
def list_documents():
    """List all documents in the database"""
    
    db = get_db()
    doc_service = DocumentService(db)
    documents = doc_service.list_all()
    
    if not documents:
        console.print("[yellow]No documents found[/yellow]")
        return
    
    table = Table(title="Insurance Documents", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Insurer", style="green")
    table.add_column("Product", style="blue")
    table.add_column("Type", style="yellow")
    table.add_column("Pages", justify="right")
    
    for doc in documents:
        table.add_row(
            str(doc.id),
            doc.insurer_name,
            doc.product_name or "N/A",
            doc.document_type or "N/A",
            str(doc.page_count or 0)
        )
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(documents)} documents[/dim]")


@app.command()
def list_policies():
    """List all policies in the database"""
    
    db = get_db()
    policy_service = PolicyService(db)
    policies = policy_service.list_all()
    
    if not policies:
        console.print("[yellow]No policies found[/yellow]")
        console.print("[dim]Add policies using the database or collectors[/dim]")
        return
    
    table = Table(title="Insurance Policies", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Insurer", style="green")
    table.add_column("Product", style="blue")
    table.add_column("UIN", style="yellow")
    table.add_column("Sum Insured Range", justify="right")
    
    for policy in policies:
        si_range = f"₹{(policy.min_sum_insured or 0)/100000:.1f}L - ₹{(policy.max_sum_insured or 0)/100000:.1f}L"
        table.add_row(
            str(policy.id),
            policy.insurer_name,
            policy.product_name,
            policy.uin_number or "N/A",
            si_range
        )
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(policies)} policies[/dim]")


@app.command()
def compare(
    policies: str = typer.Argument(..., help="Policies to compare (comma-separated)"),
    aspects: str = typer.Option(None, "--aspects", "-a", help="Aspects to compare")
):
    """Compare multiple insurance policies"""
    
    if not agent:
        console.print("[red]Error: ANTHROPIC_API_KEY not configured[/red]")
        return
    
    policy_list = [p.strip() for p in policies.split(",")]
    aspect_list = [a.strip() for a in aspects.split(",")] if aspects else None
    
    question = f"Compare these policies: {', '.join(policy_list)}"
    if aspect_list:
        question += f" focusing on: {', '.join(aspect_list)}"
    
    with console.status("[bold yellow]Comparing policies..."):
        response = agent.chat(question)
    
    console.print(Panel(
        Markdown(response),
        title="[bold cyan]Policy Comparison[/bold cyan]",
        border_style="cyan"
    ))


@app.command()
def summarize(
    policy: str = typer.Option(..., "--policy", "-p", help="Policy to summarize")
):
    """Get a summary of a specific policy"""
    
    if not agent:
        console.print("[red]Error: ANTHROPIC_API_KEY not configured[/red]")
        return
    
    question = f"Provide a comprehensive summary of {policy} including key features, exclusions, waiting periods, and important warnings."
    
    with console.status("[bold yellow]Generating summary..."):
        response = agent.chat(question)
    
    console.print(Panel(
        Markdown(response),
        title=f"[bold cyan]{policy} Summary[/bold cyan]",
        border_style="cyan"
    ))


# Database commands
db_app = typer.Typer(help="Database operations")
app.add_typer(db_app, name="db")


@db_app.command("init")
def db_init():
    """Initialize database"""
    console.print("[yellow]Initializing database...[/yellow]")
    init_db()
    console.print("[green]✓ Database initialized![/green]")
    console.print(f"[dim]Location: {config.database_path}[/dim]")


@db_app.command("status")
def db_status():
    """Show database statistics"""
    db = get_db()
    
    # Get counts
    policy_count = PolicyService(db).count()
    doc_count = DocumentService(db).count()
    
    table = Table(title="Database Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")
    
    table.add_row("Policies", str(policy_count))
    table.add_row("Documents", str(doc_count))
    
    if config.database_path.exists():
        db_size = config.database_path.stat().st_size / 1024
        table.add_row("Database Size", f"{db_size:.2f} KB")
    
    console.print(table)


@db_app.command("add-sample")
def db_add_sample():
    """Add sample policies for testing"""
    console.print("[yellow]Adding sample policies...[/yellow]")
    
    db = get_db()
    policy_service = PolicyService(db)
    
    # Sample policies
    samples = [
        {
            "insurer_name": "Star Health Insurance",
            "product_name": "Star Comprehensive",
            "uin_number": "SHAHLIP21374V022021",
            "min_sum_insured": 500000,
            "max_sum_insured": 2500000,
            "min_age": 18,
            "max_age": 65,
            "waiting_periods": {
                "initial": "30 days",
                "pre_existing": "48 months",
                "specific_diseases": "24 months"
            },
            "key_features": [
                "Cashless treatment at network hospitals",
                "Pre and post hospitalization coverage",
                "No room rent capping",
                "Annual health checkup"
            ],
            "major_exclusions": [
                "Pre-existing diseases (first 48 months)",
                "Cosmetic surgery",
                "Obesity treatment",
                "Experimental treatments"
            ],
            "optional_covers": ["Maternity", "Critical Illness", "Personal Accident"],
            "network_hospitals": 14000,
            "key_warnings": ["Read waiting period carefully", "Room rent sub-limits may apply"]
        },
        {
            "insurer_name": "HDFC ERGO",
            "product_name": "Optima Secure",
            "uin_number": "HDFHLIP21374V012021",
            "min_sum_insured": 300000,
            "max_sum_insured": 5000000,
            "min_age": 18,
            "max_age": 65,
            "waiting_periods": {
                "initial": "30 days",
                "pre_existing": "36 months",
                "specific_diseases": "24 months"
            },
            "key_features": [
                "Restore benefit",
                "No room rent capping",
                "Unlimited automatic recharge",
                "Wellness benefits"
            ],
            "major_exclusions": [
                "War and terrorism",
                "Self-inflicted injury",
                "Drug abuse",
                "Adventure sports"
            ],
            "optional_covers": ["OPD Cover", "Maternity", "Dental"],
            "network_hospitals": 12000,
            "key_warnings": ["Copayment for senior citizens", "Zone-based pricing"]
        }
    ]
    
    for sample in samples:
        try:
            policy_service.create(**sample)
            console.print(f"[green]✓[/green] Added {sample['product_name']}")
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] {sample['product_name']}: {str(e)}")
    
    console.print("\n[green]Sample policies added successfully![/green]")


if __name__ == "__main__":
    app()
