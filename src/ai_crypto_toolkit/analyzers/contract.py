"""Smart contract analysis using local LLMs."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from ..llm.client import LLMClient

console = Console()


async def analyze_contract(
    llm_client: LLMClient,
    contract_path: str,
    context: str | None = None,
) -> str:
    """Analyze a smart contract and provide insights.

    Args:
        llm_client: LLM client for analysis
        contract_path: Path to Solidity contract file
        context: Optional additional context

    Returns:
        Analysis result
    """
    # Read contract code
    path = Path(contract_path)
    if not path.exists():
        raise FileNotFoundError(f"Contract not found: {contract_path}")

    code = path.read_text()

    # Display header
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]Analyzing Contract[/bold cyan]: {path.name}",
        border_style="cyan"
    ))
    console.print()

    # Perform analysis
    result = await llm_client.analyze_code(
        code=code,
        analysis_type="contract",
        context=context,
    )

    return result


def format_contract_analysis(analysis: str, contract_name: str) -> None:
    """Format and display contract analysis results.

    Args:
        analysis: Analysis result from LLM
        contract_name: Name of the analyzed contract
    """
    console.print()
    console.print(Panel(
        Markdown(analysis),
        title=f"[bold green]Contract Analysis: {contract_name}[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))
    console.print()
