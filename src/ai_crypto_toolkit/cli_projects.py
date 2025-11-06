"""CLI commands for project management."""

import asyncio
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .integrations.foundry import FoundryIntegration
from .storage import Project, get_db
from .storage.database import compute_source_hash

console = Console()


@click.group()
def project() -> None:
    """Manage projects and contracts."""
    pass


@project.command()
@click.argument("name")
@click.argument("path", type=click.Path())
@click.option("--description", "-d", help="Project description")
@click.option("--foundry", is_flag=True, help="This is a Foundry project")
def init(name: str, path: str, description: str | None, foundry: bool) -> None:
    """Initialize a new project.

    Example:
        ai-crypto project init my-defi-project ./contracts
        ai-crypto project init foundry-proj ./foundry --foundry
    """
    db = get_db()

    # Check if project already exists
    if db.get_project_by_name(name):
        console.print(f"[red]Project '{name}' already exists[/red]")
        return

    # Check if it's a Foundry project
    project_path = Path(path).resolve()
    is_foundry = foundry or (project_path / "foundry.toml").exists()

    foundry_config = None
    if is_foundry:
        foundry_config = str(project_path / "foundry.toml")

    # Create project
    proj = Project(
        name=name,
        description=description or "",
        path=str(project_path),
        is_foundry_project=is_foundry,
        foundry_config=foundry_config,
    )

    db.create_project(proj)

    console.print()
    console.print(
        Panel.fit(
            f"[green]✓[/green] Project initialized\n\n"
            f"Name: [cyan]{name}[/cyan]\n"
            f"Path: {project_path}\n"
            f"Type: {'Foundry' if is_foundry else 'Standard'} project",
            title="[bold green]Project Created[/bold green]",
            border_style="green",
        )
    )
    console.print()

    # If Foundry project, scan contracts
    if is_foundry:
        _scan_foundry_contracts(proj)


@project.command("list")
def list_projects() -> None:
    """List all projects.

    Example:
        ai-crypto project list
    """
    db = get_db()
    projects = db.list_projects()

    if not projects:
        console.print("[yellow]No projects found. Create one with 'ai-crypto project init'[/yellow]")
        return

    table = Table(title="Projects")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="cyan bold")
    table.add_column("Type")
    table.add_column("Contracts")
    table.add_column("Updated")

    for proj in projects:
        contracts = db.list_contracts(proj.id)  # type: ignore
        proj_type = "Foundry" if proj.is_foundry_project else "Standard"
        updated = proj.updated_at.strftime("%Y-%m-%d %H:%M")

        table.add_row(
            str(proj.id),
            proj.name,
            proj_type,
            str(len(contracts)),
            updated,
        )

    console.print()
    console.print(table)
    console.print()


@project.command()
@click.argument("name")
def show(name: str) -> None:
    """Show project details.

    Example:
        ai-crypto project show my-project
    """
    db = get_db()
    proj = db.get_project_by_name(name)

    if not proj:
        console.print(f"[red]Project '{name}' not found[/red]")
        return

    # Get contracts
    contracts = db.list_contracts(proj.id)  # type: ignore

    # Get recent analyses
    analyses = db.list_analyses(proj.id, limit=5)  # type: ignore

    # Display project info
    console.print()
    console.print(
        Panel(
            f"""[bold cyan]Project: {proj.name}[/bold cyan]

[bold]Description:[/bold]
{proj.description or 'No description'}

[bold]Path:[/bold] {proj.path}
[bold]Type:[/bold] {'Foundry' if proj.is_foundry_project else 'Standard'} project
[bold]Created:[/bold] {proj.created_at.strftime("%Y-%m-%d %H:%M")}
[bold]Updated:[/bold] {proj.updated_at.strftime("%Y-%m-%d %H:%M")}

[bold]Contracts:[/bold] {len(contracts)}
[bold]Analyses:[/bold] {len(analyses)}
""",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()

    # Show contracts
    if contracts:
        contracts_table = Table(title="Contracts")
        contracts_table.add_column("ID", style="dim")
        contracts_table.add_column("Name", style="cyan")
        contracts_table.add_column("Path")
        contracts_table.add_column("Updated")

        for contract in contracts[:10]:  # Show first 10
            contracts_table.add_row(
                str(contract.id),
                contract.name,
                contract.path,
                contract.updated_at.strftime("%Y-%m-%d"),
            )

        console.print(contracts_table)
        console.print()

    # Show recent analyses
    if analyses:
        analyses_table = Table(title="Recent Analyses")
        analyses_table.add_column("Type", style="cyan")
        analyses_table.add_column("Summary")
        analyses_table.add_column("Date")

        for analysis in analyses:
            analyses_table.add_row(
                analysis.analysis_type.value,
                analysis.summary[:50] + "..." if len(analysis.summary) > 50 else analysis.summary,
                analysis.created_at.strftime("%Y-%m-%d %H:%M"),
            )

        console.print(analyses_table)
        console.print()


@project.command()
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this project?")
def delete(name: str) -> None:
    """Delete a project.

    Example:
        ai-crypto project delete my-project
    """
    db = get_db()
    proj = db.get_project_by_name(name)

    if not proj:
        console.print(f"[red]Project '{name}' not found[/red]")
        return

    db.delete_project(proj.id)  # type: ignore
    console.print(f"[green]✓ Project '{name}' deleted[/green]")


@project.command()
@click.argument("name")
def scan(name: str) -> None:
    """Scan project and update contracts.

    Example:
        ai-crypto project scan my-project
    """
    db = get_db()
    proj = db.get_project_by_name(name)

    if not proj:
        console.print(f"[red]Project '{name}' not found[/red]")
        return

    if proj.is_foundry_project:
        _scan_foundry_contracts(proj)
    else:
        _scan_standard_contracts(proj)


def _scan_foundry_contracts(proj: Project) -> None:
    """Scan Foundry project for contracts."""
    console.print(f"[cyan]Scanning Foundry project: {proj.name}[/cyan]")

    db = get_db()
    foundry = FoundryIntegration(proj.path)

    contracts_found = foundry.get_contracts()
    console.print(f"[green]Found {len(contracts_found)} contracts[/green]")

    for contract_info in contracts_found:
        # Read source
        contract_path = Path(proj.path) / contract_info["path"]
        source = contract_path.read_text()
        source_hash = compute_source_hash(source)

        # Check if exists
        existing = db.get_contract_by_path(proj.id, contract_info["path"])  # type: ignore

        if existing:
            # Update if changed
            if existing.source_hash != source_hash:
                existing.source_hash = source_hash
                db.update_contract(existing)
                console.print(f"  Updated: {contract_info['name']}")
        else:
            # Create new
            from .storage import Contract

            contract = Contract(
                project_id=proj.id,  # type: ignore
                name=contract_info["name"],
                path=contract_info["path"],
                source_hash=source_hash,
            )
            db.create_contract(contract)
            console.print(f"  Added: {contract_info['name']}")

    console.print("[green]✓ Scan complete[/green]")


def _scan_standard_contracts(proj: Project) -> None:
    """Scan standard project for .sol files."""
    console.print(f"[cyan]Scanning project: {proj.name}[/cyan]")

    db = get_db()
    project_path = Path(proj.path)

    sol_files = list(project_path.rglob("*.sol"))
    console.print(f"[green]Found {len(sol_files)} Solidity files[/green]")

    for sol_file in sol_files:
        rel_path = str(sol_file.relative_to(project_path))
        source = sol_file.read_text()
        source_hash = compute_source_hash(source)

        # Check if exists
        existing = db.get_contract_by_path(proj.id, rel_path)  # type: ignore

        if existing:
            if existing.source_hash != source_hash:
                existing.source_hash = source_hash
                db.update_contract(existing)
                console.print(f"  Updated: {sol_file.name}")
        else:
            from .storage import Contract

            contract = Contract(
                project_id=proj.id,  # type: ignore
                name=sol_file.stem,
                path=rel_path,
                source_hash=source_hash,
            )
            db.create_contract(contract)
            console.print(f"  Added: {sol_file.name}")

    console.print("[green]✓ Scan complete[/green]")
