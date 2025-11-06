"""CLI commands for viewing analysis history."""

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .storage import get_db

console = Console()


@click.group()
def history() -> None:
    """View analysis history and past results."""
    pass


@history.command()
@click.option("--project", "-p", help="Filter by project name")
@click.option("--limit", "-l", default=20, help="Number of entries to show")
def show(project: str | None, limit: int) -> None:
    """Show analysis history.

    Example:
        ai-crypto history show
        ai-crypto history show --project my-project --limit 10
    """
    db = get_db()

    # Get project ID if specified
    project_id = None
    if project:
        proj = db.get_project_by_name(project)
        if not proj:
            console.print(f"[red]Project '{project}' not found[/red]")
            return
        project_id = proj.id

    # Get history
    entries = db.get_history(project_id=project_id, limit=limit)

    if not entries:
        console.print("[yellow]No history entries found[/yellow]")
        return

    # Display as table
    table = Table(title=f"Analysis History{f' - {project}' if project else ''}")
    table.add_column("Date", style="dim")
    table.add_column("Project", style="cyan")
    table.add_column("Action", style="bold")
    table.add_column("Details")

    for entry in entries:
        # Get project name
        proj = db.get_project(entry.project_id) if entry.project_id else None
        proj_name = proj.name if proj else "N/A"

        # Format date
        date = entry.created_at.strftime("%Y-%m-%d %H:%M")

        # Get details summary
        details_summary = ""
        if "contract" in entry.details:
            details_summary = entry.details["contract"]
        elif "tx_hash" in entry.details:
            details_summary = entry.details["tx_hash"][:16] + "..."

        table.add_row(date, proj_name, entry.action, details_summary)

    console.print()
    console.print(table)
    console.print()


@history.command()
@click.argument("analysis_id", type=int)
def view(analysis_id: int) -> None:
    """View full analysis result by ID.

    Example:
        ai-crypto history view 42
    """
    db = get_db()
    analysis = db.get_analysis(analysis_id)

    if not analysis:
        console.print(f"[red]Analysis {analysis_id} not found[/red]")
        return

    # Get project and contract info
    proj = db.get_project(analysis.project_id)
    contract = db.get_contract(analysis.contract_id) if analysis.contract_id else None

    # Display header
    console.print()
    console.print(
        Panel.fit(
            f"""[bold cyan]Analysis #{analysis_id}[/bold cyan]

[bold]Type:[/bold] {analysis.analysis_type.value}
[bold]Project:[/bold] {proj.name if proj else 'N/A'}
[bold]Contract:[/bold] {contract.name if contract else 'N/A'}
[bold]Model:[/bold] {analysis.model}
[bold]Date:[/bold] {analysis.created_at.strftime("%Y-%m-%d %H:%M:%S")}
[bold]Duration:[/bold] {analysis.duration:.2f}s
{f'[bold]Severity:[/bold] {analysis.severity}' if analysis.severity else ''}
{f'[bold]Findings:[/bold] {analysis.findings_count}' if analysis.findings_count > 0 else ''}
""",
            border_style="cyan",
        )
    )
    console.print()

    # Display summary if available
    if analysis.summary:
        console.print(Panel(analysis.summary, title="Summary", border_style="yellow"))
        console.print()

    # Display full result
    console.print(
        Panel(
            Markdown(analysis.result),
            title="Analysis Result",
            border_style="green",
            padding=(1, 2),
        )
    )
    console.print()


@history.command()
@click.argument("project_name")
@click.option("--type", "-t", help="Filter by analysis type")
@click.option("--limit", "-l", default=10, help="Number of results to show")
def analyses(project_name: str, type: str | None, limit: int) -> None:
    """List analyses for a project.

    Example:
        ai-crypto history analyses my-project
        ai-crypto history analyses my-project --type security --limit 5
    """
    db = get_db()

    # Get project
    proj = db.get_project_by_name(project_name)
    if not proj:
        console.print(f"[red]Project '{project_name}' not found[/red]")
        return

    # Parse analysis type if provided
    analysis_type = None
    if type:
        from .storage import AnalysisType

        try:
            analysis_type = AnalysisType(type)
        except ValueError:
            console.print(f"[red]Invalid analysis type: {type}[/red]")
            console.print(f"Valid types: {', '.join([t.value for t in AnalysisType])}")
            return

    # Get analyses
    analyses_list = db.list_analyses(
        project_id=proj.id,  # type: ignore
        analysis_type=analysis_type,
        limit=limit,
    )

    if not analyses_list:
        console.print("[yellow]No analyses found[/yellow]")
        return

    # Display as table
    table = Table(title=f"Analyses - {project_name}")
    table.add_column("ID", style="dim")
    table.add_column("Type", style="cyan")
    table.add_column("Contract")
    table.add_column("Summary")
    table.add_column("Date")
    table.add_column("Severity")

    for analysis in analyses_list:
        contract = db.get_contract(analysis.contract_id) if analysis.contract_id else None
        contract_name = contract.name if contract else "N/A"

        # Truncate summary
        summary = analysis.summary
        if len(summary) > 60:
            summary = summary[:57] + "..."

        # Format severity with color
        severity = ""
        if analysis.severity:
            color = {"high": "red", "medium": "yellow", "low": "blue", "info": "cyan"}.get(
                analysis.severity.lower(), "white"
            )
            severity = f"[{color}]{analysis.severity.upper()}[/{color}]"

        table.add_row(
            str(analysis.id),
            analysis.analysis_type.value,
            contract_name,
            summary,
            analysis.created_at.strftime("%m/%d %H:%M"),
            severity,
        )

    console.print()
    console.print(table)
    console.print()
    console.print(f"[dim]Tip: View full analysis with 'ai-crypto history view <id>'[/dim]")
    console.print()


@history.command()
@click.argument("project_name")
def stats(project_name: str) -> None:
    """Show project statistics.

    Example:
        ai-crypto history stats my-project
    """
    db = get_db()

    # Get project
    proj = db.get_project_by_name(project_name)
    if not proj:
        console.print(f"[red]Project '{project_name}' not found[/red]")
        return

    # Get all analyses
    all_analyses = db.list_analyses(proj.id, limit=1000)  # type: ignore

    # Count by type
    from collections import Counter

    type_counts = Counter(a.analysis_type.value for a in all_analyses)

    # Count by severity (for security analyses)
    severity_counts = Counter(
        a.severity for a in all_analyses if a.severity
    )

    # Total findings
    total_findings = sum(a.findings_count for a in all_analyses)

    # Display stats
    console.print()
    console.print(Panel.fit(
        f"""[bold cyan]Statistics - {project_name}[/bold cyan]

[bold]Total Analyses:[/bold] {len(all_analyses)}
[bold]Total Findings:[/bold] {total_findings}

[bold]Analyses by Type:[/bold]
{chr(10).join(f"  • {t}: {c}" for t, c in type_counts.most_common())}

{f'''[bold]Security Findings:[/bold]
{chr(10).join(f"  • {s.upper()}: {c}" for s, c in severity_counts.most_common())}''' if severity_counts else ''}
""",
        border_style="cyan",
    ))
    console.print()
