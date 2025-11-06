"""AI-powered fuzzing integration with Echidna and Foundry."""

import asyncio
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from ..llm.client import LLMClient

console = Console()


class FuzzingResult:
    """Represents results from a fuzzing session."""

    def __init__(
        self,
        tool: str,
        contract: str,
        properties_tested: int,
        properties_passed: int,
        properties_failed: int,
        failures: list[dict[str, Any]],
        duration: float,
    ):
        self.tool = tool
        self.contract = contract
        self.properties_tested = properties_tested
        self.properties_passed = properties_passed
        self.properties_failed = properties_failed
        self.failures = failures
        self.duration = duration

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.properties_tested == 0:
            return 0.0
        return (self.properties_passed / self.properties_tested) * 100


async def run_echidna(
    contract_path: str,
    config_path: str | None = None,
) -> FuzzingResult:
    """Run Echidna fuzzer on a contract.

    Args:
        contract_path: Path to contract file
        config_path: Optional Echidna config file

    Returns:
        FuzzingResult with fuzzing outcomes
    """
    console.print("[cyan]Running Echidna fuzzer...[/cyan]")

    cmd = ["echidna", contract_path, "--format", "json"]
    if config_path:
        cmd.extend(["--config", config_path])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        # Parse Echidna JSON output
        output = result.stdout
        data = json.loads(output) if output.strip() else {}

        failures = []
        properties_tested = 0
        properties_passed = 0

        for test in data.get("tests", []):
            properties_tested += 1
            if test.get("passed"):
                properties_passed += 1
            else:
                failures.append({
                    "property": test.get("name"),
                    "seed": test.get("seed"),
                    "callSequence": test.get("callSequence", []),
                    "error": test.get("error"),
                })

        return FuzzingResult(
            tool="Echidna",
            contract=Path(contract_path).name,
            properties_tested=properties_tested,
            properties_passed=properties_passed,
            properties_failed=len(failures),
            failures=failures,
            duration=data.get("duration", 0),
        )

    except subprocess.TimeoutExpired:
        console.print("[yellow]Echidna timeout - fuzzing took too long[/yellow]")
        raise
    except FileNotFoundError:
        console.print("[red]Echidna not found. Install with: pip install echidna-parade[/red]")
        raise
    except json.JSONDecodeError:
        console.print("[yellow]Could not parse Echidna output[/yellow]")
        # Return empty result
        return FuzzingResult(
            tool="Echidna",
            contract=Path(contract_path).name,
            properties_tested=0,
            properties_passed=0,
            properties_failed=0,
            failures=[],
            duration=0,
        )


async def run_foundry_fuzz(
    contract_path: str,
    test_contract: str | None = None,
) -> FuzzingResult:
    """Run Foundry fuzzing tests.

    Args:
        contract_path: Path to contract file
        test_contract: Optional specific test contract to run

    Returns:
        FuzzingResult with fuzzing outcomes
    """
    console.print("[cyan]Running Foundry fuzzer...[/cyan]")

    cmd = ["forge", "test", "--json"]
    if test_contract:
        cmd.extend(["--match-contract", test_contract])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=Path(contract_path).parent,
        )

        # Parse Foundry JSON output
        output = result.stdout
        failures = []
        properties_tested = 0
        properties_passed = 0

        # Parse each line as JSON (Foundry outputs JSONL)
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "test":
                    properties_tested += 1
                    if data.get("status") == "Success":
                        properties_passed += 1
                    else:
                        failures.append({
                            "property": data.get("test"),
                            "contract": data.get("contract"),
                            "reason": data.get("reason"),
                            "counterexample": data.get("counterexample"),
                        })
            except json.JSONDecodeError:
                continue

        return FuzzingResult(
            tool="Foundry",
            contract=Path(contract_path).name,
            properties_tested=properties_tested,
            properties_passed=properties_passed,
            properties_failed=len(failures),
            failures=failures,
            duration=0,  # Foundry doesn't report total duration easily
        )

    except subprocess.TimeoutExpired:
        console.print("[yellow]Foundry timeout - fuzzing took too long[/yellow]")
        raise
    except FileNotFoundError:
        console.print("[red]Foundry not found. Install from: https://getfoundry.sh/[/red]")
        raise


async def analyze_fuzzing_results(
    llm_client: LLMClient,
    result: FuzzingResult,
    contract_code: str,
) -> str:
    """Use AI to analyze fuzzing failures and suggest fixes.

    Args:
        llm_client: LLM client for analysis
        result: Fuzzing results
        contract_code: The contract source code

    Returns:
        AI analysis and recommendations
    """
    if not result.failures:
        return "✅ All properties passed! No issues found during fuzzing."

    # Build prompt with failure details
    failures_text = ""
    for i, failure in enumerate(result.failures, 1):
        failures_text += f"\n### Failure {i}: {failure.get('property', 'Unknown')}\n"

        if call_seq := failure.get("callSequence"):
            failures_text += f"**Call Sequence**: {call_seq}\n"

        if reason := failure.get("reason"):
            failures_text += f"**Reason**: {reason}\n"

        if error := failure.get("error"):
            failures_text += f"**Error**: {error}\n"

        if seed := failure.get("seed"):
            failures_text += f"**Seed**: {seed}\n"

    prompt = f"""Analyze these fuzzing failures from {result.tool}:

**Contract**: {result.contract}
**Properties Tested**: {result.properties_tested}
**Failures**: {result.properties_failed}

{failures_text}

**Contract Code**:
```solidity
{contract_code}
```

For each failure, provide:
1. **What Went Wrong**: Explain the failure in plain English
2. **Root Cause**: Why did the property fail?
3. **Security Implications**: Is this a vulnerability or just a property issue?
4. **Fix**: Concrete code changes to address the issue
5. **Better Properties**: Suggest improved invariant tests

Be specific and actionable. Use code examples."""

    system = """You are an expert at analyzing fuzzing results and smart contract invariants.
Your job is to explain failures clearly and suggest concrete fixes."""

    return await llm_client.complete(prompt, system=system)


async def generate_property_tests(
    llm_client: LLMClient,
    contract_code: str,
    tool: str = "echidna",
) -> str:
    """Generate property-based tests using AI.

    Args:
        llm_client: LLM client
        contract_code: Contract source code
        tool: Target fuzzing tool (echidna or foundry)

    Returns:
        Generated test code
    """
    console.print(f"[cyan]Generating {tool} property tests with AI...[/cyan]")

    if tool == "echidna":
        test_format = """Echidna property format:
```solidity
function echidna_property_name() public returns (bool) {
    // Your invariant here
    return true;  // Should always be true
}
```"""
    else:  # foundry
        test_format = """Foundry fuzz test format:
```solidity
function testFuzz_PropertyName(uint256 x, address user) public {
    // Your invariant test here
    assertEq(expected, actual);
}
```"""

    prompt = f"""Generate comprehensive property-based tests for this contract:

```solidity
{contract_code}
```

Create tests for {tool} that verify:
1. **Balance Invariants**: Total balances never exceed expected values
2. **Access Control**: Only authorized addresses can perform privileged actions
3. **State Consistency**: Related state variables stay consistent
4. **Mathematical Properties**: Arithmetic operations are correct
5. **Edge Cases**: Boundary conditions are handled properly

{test_format}

Generate 5-10 meaningful properties that would catch real bugs.
Include comments explaining what each property checks."""

    system = """You are an expert at property-based testing for smart contracts.
Generate comprehensive, meaningful invariants that would catch real vulnerabilities."""

    return await llm_client.complete(prompt, system=system)


def format_fuzzing_results(result: FuzzingResult) -> None:
    """Display fuzzing results in a formatted table.

    Args:
        result: Fuzzing results to display
    """
    # Summary table
    table = Table(title=f"{result.tool} Fuzzing Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold")

    table.add_row("Contract", result.contract)
    table.add_row("Properties Tested", str(result.properties_tested))
    table.add_row("Passed", f"[green]{result.properties_passed}[/green]")
    table.add_row("Failed", f"[red]{result.properties_failed}[/red]")
    table.add_row("Success Rate", f"{result.success_rate:.1f}%")
    if result.duration > 0:
        table.add_row("Duration", f"{result.duration:.2f}s")

    console.print()
    console.print(table)
    console.print()

    # Failure details
    if result.failures:
        console.print(Panel.fit(
            f"[red]Found {len(result.failures)} failing properties[/red]",
            border_style="red"
        ))


async def fuzz_and_analyze(
    llm_client: LLMClient,
    contract_path: str,
    tool: str = "echidna",
    config_path: str | None = None,
) -> tuple[FuzzingResult, str]:
    """Run fuzzing and AI analysis in one go.

    Args:
        llm_client: LLM client for analysis
        contract_path: Path to contract
        tool: Fuzzing tool to use (echidna or foundry)
        config_path: Optional config file

    Returns:
        Tuple of (fuzzing result, AI analysis)
    """
    # Display header
    console.print()
    console.print(Panel.fit(
        f"[bold magenta]AI-Powered Fuzzing[/bold magenta]: {Path(contract_path).name}",
        border_style="magenta"
    ))
    console.print()

    # Run fuzzer
    if tool == "echidna":
        result = await run_echidna(contract_path, config_path)
    elif tool == "foundry":
        result = await run_foundry_fuzz(contract_path)
    else:
        raise ValueError(f"Unknown fuzzing tool: {tool}")

    # Display results
    format_fuzzing_results(result)

    # AI analysis of failures
    if result.failures:
        console.print("[cyan]Analyzing failures with AI...[/cyan]")
        console.print()

        contract_code = Path(contract_path).read_text()
        analysis = await analyze_fuzzing_results(llm_client, result, contract_code)

        return result, analysis

    return result, "✅ All properties passed! No failures to analyze."
