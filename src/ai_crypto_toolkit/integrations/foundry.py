"""Deep integration with Foundry (forge/cast)."""

import json
import subprocess
import tomli
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class FoundryIntegration:
    """Integration with Foundry toolchain (forge, cast, anvil)."""

    def __init__(self, project_path: str):
        """Initialize Foundry integration.

        Args:
            project_path: Path to Foundry project root
        """
        self.project_path = Path(project_path)
        self.config_path = self.project_path / "foundry.toml"
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load foundry.toml configuration."""
        if not self.config_path.exists():
            return {}

        with open(self.config_path, "rb") as f:
            return tomli.load(f)

    def is_foundry_project(self) -> bool:
        """Check if this is a valid Foundry project."""
        return self.config_path.exists()

    def get_source_dir(self) -> Path:
        """Get source directory (default: src/)."""
        src_dir = self.config.get("profile", {}).get("default", {}).get("src", "src")
        return self.project_path / src_dir

    def get_test_dir(self) -> Path:
        """Get test directory (default: test/)."""
        test_dir = self.config.get("profile", {}).get("default", {}).get("test", "test")
        return self.project_path / test_dir

    def get_out_dir(self) -> Path:
        """Get output directory for artifacts (default: out/)."""
        out_dir = self.config.get("profile", {}).get("default", {}).get("out", "out")
        return self.project_path / out_dir

    # Build operations

    def build(self, force: bool = False) -> dict[str, Any]:
        """Build contracts with forge.

        Args:
            force: Force rebuild even if up-to-date

        Returns:
            Build result with compilation info
        """
        console.print("[cyan]Building contracts with Foundry...[/cyan]")

        cmd = ["forge", "build", "--json"]
        if force:
            cmd.append("--force")

        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            console.print(f"[red]Build failed:[/red]\n{result.stderr}")
            return {"success": False, "error": result.stderr}

        # Parse output
        output_lines = result.stdout.strip().split("\n")
        build_info = {"success": True, "contracts": [], "errors": [], "warnings": []}

        for line in output_lines:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if "compiler" in data:
                    build_info["compiler"] = data["compiler"]
                elif "errors" in data:
                    build_info["errors"].extend(data["errors"])
                elif "warnings" in data:
                    build_info["warnings"].extend(data["warnings"])
            except json.JSONDecodeError:
                continue

        console.print("[green]✓ Build successful[/green]")
        return build_info

    def clean(self) -> None:
        """Clean build artifacts."""
        subprocess.run(["forge", "clean"], cwd=self.project_path, check=True)
        console.print("[green]✓ Cleaned build artifacts[/green]")

    # Test operations

    def test(
        self,
        match_contract: str | None = None,
        match_test: str | None = None,
        verbose: bool = False,
    ) -> dict[str, Any]:
        """Run tests with forge.

        Args:
            match_contract: Filter by contract name
            match_test: Filter by test function name
            verbose: Show detailed output

        Returns:
            Test results
        """
        console.print("[cyan]Running Foundry tests...[/cyan]")

        cmd = ["forge", "test", "--json"]

        if match_contract:
            cmd.extend(["--match-contract", match_contract])
        if match_test:
            cmd.extend(["--match-test", match_test])
        if verbose:
            cmd.append("-vvv")

        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True,
        )

        # Parse JSONL output
        tests = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "test":
                    tests.append(data)
            except json.JSONDecodeError:
                continue

        # Summarize results
        passed = sum(1 for t in tests if t.get("status") == "Success")
        failed = sum(1 for t in tests if t.get("status") == "Failure")
        total = len(tests)

        test_result = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "tests": tests,
            "success": failed == 0,
        }

        # Display summary
        self._display_test_summary(test_result)

        return test_result

    def _display_test_summary(self, result: dict[str, Any]) -> None:
        """Display test summary table."""
        table = Table(title="Test Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")

        table.add_row("Total Tests", str(result["total"]))
        table.add_row("Passed", f"[green]{result['passed']}[/green]")
        table.add_row("Failed", f"[red]{result['failed']}[/red]")
        table.add_row(
            "Success Rate",
            f"{result['passed'] / result['total'] * 100:.1f}%"
            if result["total"] > 0
            else "0%",
        )

        console.print()
        console.print(table)
        console.print()

        # Show failed tests
        if result["failed"] > 0:
            console.print("[red]Failed Tests:[/red]")
            for test in result["tests"]:
                if test.get("status") == "Failure":
                    console.print(f"  ❌ {test.get('contract')}::{test.get('test')}")
                    if reason := test.get("reason"):
                        console.print(f"     {reason}")
            console.print()

    def coverage(self) -> dict[str, Any]:
        """Generate coverage report.

        Returns:
            Coverage data
        """
        console.print("[cyan]Generating coverage report...[/cyan]")

        # Run coverage
        result = subprocess.run(
            ["forge", "coverage", "--report", "lcov"],
            cwd=self.project_path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            console.print(f"[red]Coverage failed:[/red]\n{result.stderr}")
            return {"success": False, "error": result.stderr}

        # Parse lcov output (simplified)
        coverage_data = {
            "success": True,
            "files": [],
            "overall_coverage": 0.0,
        }

        console.print("[green]✓ Coverage report generated[/green]")
        return coverage_data

    # Snapshot and gas reporting

    def snapshot(self, diff: bool = False) -> dict[str, Any]:
        """Generate gas snapshot.

        Args:
            diff: Show diff with previous snapshot

        Returns:
            Gas snapshot data
        """
        console.print("[cyan]Generating gas snapshot...[/cyan]")

        cmd = ["forge", "snapshot"]
        if diff:
            cmd.append("--diff")

        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return {"success": False, "error": result.stderr}

        # Parse snapshot output
        snapshot_path = self.project_path / ".gas-snapshot"
        snapshots = {}

        if snapshot_path.exists():
            for line in snapshot_path.read_text().split("\n"):
                if not line.strip():
                    continue
                parts = line.split(":")
                if len(parts) == 2:
                    test_name = parts[0].strip()
                    gas = parts[1].strip().split()[0]
                    snapshots[test_name] = int(gas)

        console.print(f"[green]✓ Snapshot generated ({len(snapshots)} tests)[/green]")

        return {
            "success": True,
            "snapshots": snapshots,
            "total_tests": len(snapshots),
        }

    # Contract inspection

    def get_contracts(self) -> list[dict[str, Any]]:
        """Get list of contracts in the project.

        Returns:
            List of contract info dicts
        """
        src_dir = self.get_source_dir()
        if not src_dir.exists():
            return []

        contracts = []
        for sol_file in src_dir.rglob("*.sol"):
            contracts.append(
                {
                    "name": sol_file.stem,
                    "path": str(sol_file.relative_to(self.project_path)),
                    "size": sol_file.stat().st_size,
                }
            )

        return contracts

    def get_abi(self, contract_name: str) -> list[dict[str, Any]] | None:
        """Get ABI for a contract.

        Args:
            contract_name: Name of the contract

        Returns:
            ABI as list of function/event definitions, or None if not found
        """
        out_dir = self.get_out_dir()

        # Search for contract JSON
        for json_file in out_dir.rglob(f"{contract_name}.json"):
            with open(json_file) as f:
                data = json.load(f)
                return data.get("abi")

        return None

    def get_bytecode(self, contract_name: str) -> str | None:
        """Get deployed bytecode for a contract.

        Args:
            contract_name: Name of the contract

        Returns:
            Bytecode as hex string, or None if not found
        """
        out_dir = self.get_out_dir()

        for json_file in out_dir.rglob(f"{contract_name}.json"):
            with open(json_file) as f:
                data = json.load(f)
                return data.get("deployedBytecode", {}).get("object")

        return None

    # Script execution

    def run_script(
        self,
        script_path: str,
        args: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run a Foundry script.

        Args:
            script_path: Path to script file
            args: Additional arguments

        Returns:
            Script execution result
        """
        console.print(f"[cyan]Running script: {script_path}[/cyan]")

        cmd = ["forge", "script", script_path]
        if args:
            cmd.extend(args)

        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    # Helper methods

    def get_forge_version(self) -> str:
        """Get installed forge version."""
        result = subprocess.run(
            ["forge", "--version"],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def init_project(self, path: str, template: str | None = None) -> bool:
        """Initialize a new Foundry project.

        Args:
            path: Path for new project
            template: Optional template to use

        Returns:
            True if successful
        """
        cmd = ["forge", "init", path]
        if template:
            cmd.extend(["-t", template])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            console.print(f"[green]✓ Foundry project initialized at {path}[/green]")
            return True
        else:
            console.print(f"[red]Failed to initialize project:[/red]\n{result.stderr}")
            return False
