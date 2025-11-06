"""Transaction analysis and explanation using local LLMs and Web3."""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from web3 import Web3

from ..llm.client import LLMClient

console = Console()


async def explain_transaction(
    llm_client: LLMClient,
    tx_hash: str,
    rpc_url: str,
    verbose: bool = False,
) -> tuple[dict[str, Any], str]:
    """Fetch transaction data and explain what it does.

    Args:
        llm_client: LLM client for explanation
        tx_hash: Transaction hash
        rpc_url: Ethereum RPC URL
        verbose: Include detailed technical info

    Returns:
        Tuple of (transaction data, explanation)
    """
    # Connect to Ethereum
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to RPC: {rpc_url}")

    # Display header
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]Analyzing Transaction[/bold cyan]: {tx_hash}",
        border_style="cyan"
    ))
    console.print()

    # Fetch transaction
    console.print("[yellow]Fetching transaction data...[/yellow]")
    tx = w3.eth.get_transaction(tx_hash)
    receipt = w3.eth.get_transaction_receipt(tx_hash)

    # Build transaction data dict
    tx_data = {
        "hash": tx_hash,
        "from": tx["from"],
        "to": tx["to"],
        "value": tx["value"],
        "gas": tx["gas"],
        "gas_used": receipt["gasUsed"],
        "gas_price": tx.get("gasPrice", 0),
        "block_number": tx["blockNumber"],
        "input": tx["input"].hex(),
        "status": receipt["status"],
    }

    if verbose:
        console.print("[cyan]Transaction data fetched. Analyzing with AI...[/cyan]")
        console.print()

    # Get AI explanation
    explanation = await llm_client.explain_transaction(tx_data)

    return tx_data, explanation


def format_transaction_explanation(
    tx_data: dict[str, Any],
    explanation: str,
    verbose: bool = False,
) -> None:
    """Format and display transaction explanation.

    Args:
        tx_data: Transaction data dictionary
        explanation: Explanation from LLM
        verbose: Include detailed technical info
    """
    # Display basic transaction info
    if verbose:
        table = Table(title="Transaction Details", show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        table.add_row("Hash", str(tx_data["hash"]))
        table.add_row("From", str(tx_data["from"]))
        table.add_row("To", str(tx_data["to"]))
        table.add_row("Value", f"{Web3.from_wei(tx_data['value'], 'ether')} ETH")
        table.add_row("Gas Used", str(tx_data["gas_used"]))
        table.add_row("Block", str(tx_data["block_number"]))
        table.add_row("Status", "✅ Success" if tx_data["status"] == 1 else "❌ Failed")

        console.print(table)
        console.print()

    # Display AI explanation
    console.print(Panel(
        Markdown(explanation),
        title="[bold green]Transaction Explanation[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))
    console.print()
