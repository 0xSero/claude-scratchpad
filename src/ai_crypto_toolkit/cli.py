"""CLI interface for AI Crypto Toolkit."""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from .analyzers.contract import analyze_contract, format_contract_analysis
from .analyzers.fuzzing import fuzz_and_analyze, generate_property_tests
from .analyzers.gas import format_gas_optimization, optimize_gas
from .analyzers.security import audit_contract, format_security_audit
from .analyzers.transaction import explain_transaction, format_transaction_explanation
from .cli_history import history
from .cli_projects import project
from .config import Config, create_default_config, load_config
from .llm.client import LLMClient, test_llm_connection

console = Console()


@click.group()
@click.version_option(version="0.1.0")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to config file",
)
@click.pass_context
def cli(ctx: click.Context, config: str | None) -> None:
    """AI Crypto Toolkit - Analyze smart contracts using local LLMs.

    Built for independence. Use your own hardware, your own models, your own rules.
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)


@cli.command()
@click.argument("contract_path", type=click.Path(exists=True))
@click.option(
    "--context",
    "-x",
    help="Additional context for analysis",
)
@click.pass_context
def analyze(ctx: click.Context, contract_path: str, context: str | None) -> None:
    """Analyze a smart contract and explain what it does.

    Example:
        ai-crypto analyze contracts/MyToken.sol
    """
    config: Config = ctx.obj["config"]

    async def run() -> None:
        async with LLMClient(config.llm) as client:
            result = await analyze_contract(client, contract_path, context)
            format_contract_analysis(result, Path(contract_path).name)

    asyncio.run(run())


@cli.command()
@click.argument("contract_path", type=click.Path(exists=True))
@click.option(
    "--severity",
    "-s",
    type=click.Choice(["high", "medium", "low", "info"], case_sensitive=False),
    help="Filter by minimum severity",
)
@click.option(
    "--context",
    "-x",
    help="Additional context for audit",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed output",
)
@click.pass_context
def audit(
    ctx: click.Context,
    contract_path: str,
    severity: str | None,
    context: str | None,
    verbose: bool,
) -> None:
    """Audit a smart contract for security vulnerabilities.

    Example:
        ai-crypto audit contracts/DeFi.sol --severity high
    """
    config: Config = ctx.obj["config"]

    async def run() -> None:
        async with LLMClient(config.llm) as client:
            result = await audit_contract(client, contract_path, severity, context)
            format_security_audit(result, Path(contract_path).name)

    asyncio.run(run())


@cli.command()
@click.argument("tx_hash")
@click.option(
    "--network",
    "-n",
    default="ethereum",
    help="Network name (uses RPC from config)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed transaction info",
)
@click.pass_context
def tx(ctx: click.Context, tx_hash: str, network: str, verbose: bool) -> None:
    """Explain what a transaction does in plain English.

    Example:
        ai-crypto tx 0x1234...5678 --network ethereum
    """
    config: Config = ctx.obj["config"]

    async def run() -> None:
        async with LLMClient(config.llm) as client:
            tx_data, explanation = await explain_transaction(
                client,
                tx_hash,
                config.ethereum.rpc_url,
                verbose,
            )
            format_transaction_explanation(tx_data, explanation, verbose)

    asyncio.run(run())


@cli.command()
@click.argument("contract_path", type=click.Path(exists=True))
@click.option(
    "--context",
    "-x",
    help="Additional context for optimization",
)
@click.pass_context
def optimize(ctx: click.Context, contract_path: str, context: str | None) -> None:
    """Analyze contract for gas optimization opportunities.

    Example:
        ai-crypto optimize contracts/Storage.sol
    """
    config: Config = ctx.obj["config"]

    async def run() -> None:
        async with LLMClient(config.llm) as client:
            result = await optimize_gas(client, contract_path, context)
            format_gas_optimization(result, Path(contract_path).name)

    asyncio.run(run())


@cli.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(),
    help="Where to create config file (default: ~/.ai-crypto-toolkit/config.yaml)",
)
def init(path: str | None) -> None:
    """Create a default configuration file.

    Example:
        ai-crypto init
        ai-crypto init --path ./my-config.yaml
    """
    config_path = create_default_config(path)
    console.print()
    console.print(
        Panel.fit(
            f"[green]✓[/green] Configuration file created at:\n[cyan]{config_path}[/cyan]\n\n"
            "Edit this file to point to your local LLM API.",
            title="[bold green]Setup Complete[/bold green]",
            border_style="green",
        )
    )
    console.print()


@cli.command()
@click.pass_context
def test(ctx: click.Context) -> None:
    """Test connection to your local LLM API.

    Example:
        ai-crypto test
    """
    config: Config = ctx.obj["config"]

    console.print()
    console.print("[cyan]Testing connection to LLM API...[/cyan]")
    console.print(f"[dim]API Base: {config.llm.api_base}[/dim]")
    console.print(f"[dim]Model: {config.llm.model}[/dim]")
    console.print()

    async def run() -> None:
        success = await test_llm_connection(config.llm)
        console.print()
        if success:
            console.print(
                Panel.fit(
                    "[green]✓ Connection successful![/green]\n\n"
                    "Your local LLM is responding correctly.",
                    title="[bold green]Test Passed[/bold green]",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel.fit(
                    "[red]✗ Connection failed[/red]\n\n"
                    "Check that:\n"
                    "1. Your LLM server is running\n"
                    "2. The API base URL is correct\n"
                    "3. The API is accessible\n\n"
                    f"Current config: {config.llm.api_base}",
                    title="[bold red]Test Failed[/bold red]",
                    border_style="red",
                )
            )
            sys.exit(1)
        console.print()

    asyncio.run(run())


@cli.command()
@click.argument("contract_path", type=click.Path(exists=True))
@click.option(
    "--tool",
    "-t",
    type=click.Choice(["echidna", "foundry"], case_sensitive=False),
    default="echidna",
    help="Fuzzing tool to use",
)
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Fuzzer config file (optional)",
)
@click.pass_context
def fuzz(
    ctx: click.Context,
    contract_path: str,
    tool: str,
    config_file: str | None,
) -> None:
    """Run AI-powered fuzzing analysis.

    Runs property-based fuzzing (Echidna or Foundry) and uses AI to analyze
    any failures found.

    Example:
        ai-crypto fuzz examples/VulnerableBank.sol --tool echidna
        ai-crypto fuzz contracts/Token.sol --tool foundry
    """
    config: Config = ctx.obj["config"]

    async def run() -> None:
        async with LLMClient(config.llm) as client:
            result, analysis = await fuzz_and_analyze(
                client,
                contract_path,
                tool=tool.lower(),
                config_path=config_file,
            )

            # Display AI analysis
            from rich.markdown import Markdown
            from rich.panel import Panel

            console.print()
            console.print(Panel(
                Markdown(analysis),
                title=f"[bold magenta]🔬 AI Analysis of Fuzzing Results[/bold magenta]",
                border_style="magenta",
                padding=(1, 2),
            ))
            console.print()

    asyncio.run(run())


@cli.command()
@click.argument("contract_path", type=click.Path(exists=True))
@click.option(
    "--tool",
    "-t",
    type=click.Choice(["echidna", "foundry"], case_sensitive=False),
    default="echidna",
    help="Target fuzzing tool",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file for generated tests",
)
@click.pass_context
def gentest(
    ctx: click.Context,
    contract_path: str,
    tool: str,
    output: str | None,
) -> None:
    """Generate property-based tests using AI.

    Uses AI to analyze your contract and generate comprehensive invariant tests
    for Echidna or Foundry fuzzing.

    Example:
        ai-crypto gentest examples/SecureToken.sol --tool echidna
        ai-crypto gentest contracts/DeFi.sol --tool foundry -o test/Properties.t.sol
    """
    config: Config = ctx.obj["config"]

    async def run() -> None:
        contract_code = Path(contract_path).read_text()

        async with LLMClient(config.llm) as client:
            tests = await generate_property_tests(
                client,
                contract_code,
                tool=tool.lower(),
            )

            # Display generated tests
            from rich.markdown import Markdown
            from rich.panel import Panel
            from rich.syntax import Syntax

            console.print()
            console.print(Panel(
                Markdown(tests),
                title=f"[bold green]Generated {tool.title()} Property Tests[/bold green]",
                border_style="green",
                padding=(1, 2),
            ))
            console.print()

            # Save to file if requested
            if output:
                Path(output).write_text(tests)
                console.print(f"[green]✓ Tests saved to: {output}[/green]")
                console.print()

    asyncio.run(run())


@cli.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show current configuration.

    Example:
        ai-crypto info
    """
    config: Config = ctx.obj["config"]

    console.print()
    console.print(
        Panel(
            f"""[bold cyan]LLM Configuration[/bold cyan]
API Base: {config.llm.api_base}
Model: {config.llm.model}
Temperature: {config.llm.temperature}
Max Tokens: {config.llm.max_tokens}
Stream: {config.llm.stream}

[bold cyan]Ethereum Configuration[/bold cyan]
RPC URL: {config.ethereum.rpc_url}

[bold cyan]Security Checks Enabled[/bold cyan]
Reentrancy: {config.security.check_reentrancy}
Overflow: {config.security.check_overflow}
Access Control: {config.security.check_access_control}
Delegatecall: {config.security.check_delegatecall}
TX Origin: {config.security.check_tx_origin}
Unchecked Calls: {config.security.check_unchecked_calls}
""",
            title="[bold]AI Crypto Toolkit Configuration[/bold]",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()


# Register command groups
cli.add_command(project)
cli.add_command(history)


def main() -> None:
    """Main entry point for CLI."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
