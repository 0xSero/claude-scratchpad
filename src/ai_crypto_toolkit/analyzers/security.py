"""Security vulnerability scanning using local LLMs and static analysis."""

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from ..llm.client import LLMClient
from ..llm.prompts import get_vulnerability_hints

console = Console()


class SecurityFinding:
    """Represents a security finding."""

    def __init__(
        self,
        severity: str,
        title: str,
        description: str,
        location: str | None = None,
        fix: str | None = None,
    ):
        self.severity = severity.upper()
        self.title = title
        self.description = description
        self.location = location
        self.fix = fix

    @property
    def severity_color(self) -> str:
        """Get color for severity level."""
        colors = {
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "blue",
            "INFO": "cyan",
        }
        return colors.get(self.severity, "white")


async def audit_contract(
    llm_client: LLMClient,
    contract_path: str,
    severity_filter: str | None = None,
    context: str | None = None,
) -> str:
    """Audit a smart contract for security vulnerabilities.

    Args:
        llm_client: LLM client for analysis
        contract_path: Path to Solidity contract file
        severity_filter: Only show findings of this severity or higher
        context: Optional additional context

    Returns:
        Audit result
    """
    # Read contract code
    path = Path(contract_path)
    if not path.exists():
        raise FileNotFoundError(f"Contract not found: {contract_path}")

    code = path.read_text()

    # Display header
    console.print()
    console.print(Panel.fit(
        f"[bold red]Security Audit[/bold red]: {path.name}",
        border_style="red"
    ))
    console.print()

    # Quick pattern-based checks
    hints = get_vulnerability_hints(code)
    if hints:
        console.print("[yellow]⚡ Quick Pattern Checks:[/yellow]")
        for hint in hints:
            console.print(f"  • {hint}")
        console.print()
        console.print("[cyan]Running deep AI analysis...[/cyan]")
        console.print()

    # Perform deep AI analysis
    audit_context = context or ""
    if hints:
        audit_context += f"\n\nQuick checks found: {', '.join(hints)}"

    result = await llm_client.analyze_code(
        code=code,
        analysis_type="security",
        context=audit_context,
    )

    return result


def format_security_audit(audit: str, contract_name: str) -> None:
    """Format and display security audit results.

    Args:
        audit: Audit result from LLM
        contract_name: Name of the audited contract
    """
    console.print()
    console.print(Panel(
        Markdown(audit),
        title=f"[bold red]🛡️  Security Audit: {contract_name}[/bold red]",
        border_style="red",
        padding=(1, 2),
    ))
    console.print()


def display_security_summary(findings: list[SecurityFinding]) -> None:
    """Display a summary table of security findings.

    Args:
        findings: List of security findings
    """
    table = Table(title="Security Findings Summary")
    table.add_column("Severity", style="bold")
    table.add_column("Issue")
    table.add_column("Location")

    for finding in findings:
        table.add_row(
            f"[{finding.severity_color}]{finding.severity}[/{finding.severity_color}]",
            finding.title,
            finding.location or "N/A",
        )

    console.print(table)
    console.print()
