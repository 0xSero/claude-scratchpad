"""Gas optimization analysis using local LLMs."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from ..llm.client import LLMClient

console = Console()


async def optimize_gas(
    llm_client: LLMClient,
    contract_path: str,
    context: str | None = None,
) -> str:
    """Analyze contract for gas optimization opportunities.

    Args:
        llm_client: LLM client for analysis
        contract_path: Path to Solidity contract file
        context: Optional additional context

    Returns:
        Optimization suggestions
    """
    # Read contract code
    path = Path(contract_path)
    if not path.exists():
        raise FileNotFoundError(f"Contract not found: {contract_path}")

    code = path.read_text()

    # Display header
    console.print()
    console.print(Panel.fit(
        f"[bold green]⚡ Gas Optimization Analysis[/bold green]: {path.name}",
        border_style="green"
    ))
    console.print()

    # Perform analysis
    result = await llm_client.analyze_code(
        code=code,
        analysis_type="gas",
        context=context,
    )

    return result


def format_gas_optimization(optimization: str, contract_name: str) -> None:
    """Format and display gas optimization results.

    Args:
        optimization: Optimization result from LLM
        contract_name: Name of the analyzed contract
    """
    console.print()
    console.print(Panel(
        Markdown(optimization),
        title=f"[bold green]⚡ Gas Optimization: {contract_name}[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))
    console.print()
