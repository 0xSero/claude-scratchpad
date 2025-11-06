"""Integration with Tenderly for transaction simulation and debugging."""

import asyncio
from typing import Any

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class TenderlyClient:
    """Client for Tenderly API."""

    def __init__(
        self,
        access_key: str,
        account_slug: str,
        project_slug: str,
        api_base: str = "https://api.tenderly.co",
    ):
        """Initialize Tenderly client.

        Args:
            access_key: Tenderly access key
            account_slug: Account/username slug
            project_slug: Project slug
            api_base: API base URL
        """
        self.access_key = access_key
        self.account_slug = account_slug
        self.project_slug = project_slug
        self.api_base = api_base

        self.client = httpx.AsyncClient(
            base_url=api_base,
            headers={
                "X-Access-Key": access_key,
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def __aenter__(self) -> "TenderlyClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.client.aclose()

    # Simulation operations

    async def simulate_transaction(
        self,
        network_id: str,
        from_address: str,
        to_address: str,
        input_data: str,
        value: int = 0,
        gas: int | None = None,
        gas_price: int | None = None,
        block_number: int | None = None,
        save: bool = False,
    ) -> dict[str, Any]:
        """Simulate a transaction.

        Args:
            network_id: Network ID (e.g., "1" for mainnet)
            from_address: Sender address
            to_address: Contract address
            input_data: Transaction calldata (hex)
            value: ETH value in wei
            gas: Gas limit
            gas_price: Gas price in wei
            block_number: Block number to simulate at (None = latest)
            save: Save simulation to Tenderly dashboard

        Returns:
            Simulation result with trace, logs, and state changes
        """
        console.print("[cyan]Simulating transaction with Tenderly...[/cyan]")

        payload = {
            "network_id": network_id,
            "from": from_address,
            "to": to_address,
            "input": input_data,
            "value": str(value),
            "save": save,
        }

        if gas:
            payload["gas"] = gas
        if gas_price:
            payload["gas_price"] = str(gas_price)
        if block_number:
            payload["block_number"] = block_number

        endpoint = f"/api/v1/account/{self.account_slug}/project/{self.project_slug}/simulate"

        response = await self.client.post(endpoint, json=payload)
        response.raise_for_status()

        result = response.json()
        console.print("[green]✓ Simulation complete[/green]")

        return result

    async def simulate_bundle(
        self,
        network_id: str,
        transactions: list[dict[str, Any]],
        block_number: int | None = None,
    ) -> dict[str, Any]:
        """Simulate a bundle of transactions.

        Args:
            network_id: Network ID
            transactions: List of transaction dicts
            block_number: Block number to simulate at

        Returns:
            Bundle simulation result
        """
        console.print(f"[cyan]Simulating bundle of {len(transactions)} transactions...[/cyan]")

        payload = {
            "network_id": network_id,
            "transactions": transactions,
        }

        if block_number:
            payload["block_number"] = block_number

        endpoint = f"/api/v1/account/{self.account_slug}/project/{self.project_slug}/simulate-bundle"

        response = await self.client.post(endpoint, json=payload)
        response.raise_for_status()

        result = response.json()
        console.print("[green]✓ Bundle simulation complete[/green]")

        return result

    # Transaction analysis

    async def get_transaction(self, tx_hash: str, network_id: str) -> dict[str, Any]:
        """Get transaction details from Tenderly.

        Args:
            tx_hash: Transaction hash
            network_id: Network ID

        Returns:
            Transaction details with trace
        """
        endpoint = f"/api/v1/account/{self.account_slug}/project/{self.project_slug}/tx/{network_id}/{tx_hash}"

        response = await self.client.get(endpoint)
        response.raise_for_status()

        return response.json()

    async def get_transaction_trace(
        self, tx_hash: str, network_id: str
    ) -> dict[str, Any]:
        """Get detailed trace for a transaction.

        Args:
            tx_hash: Transaction hash
            network_id: Network ID

        Returns:
            Detailed trace with all calls and state changes
        """
        endpoint = f"/api/v1/account/{self.account_slug}/project/{self.project_slug}/tx/{network_id}/{tx_hash}/trace"

        response = await self.client.get(endpoint)
        response.raise_for_status()

        return response.json()

    # Contract operations

    async def verify_contract(
        self,
        network_id: str,
        contract_address: str,
        compiler_version: str,
        source_code: str,
        contract_name: str,
        optimization: bool = True,
        optimization_runs: int = 200,
    ) -> dict[str, Any]:
        """Verify a contract on Tenderly.

        Args:
            network_id: Network ID
            contract_address: Contract address
            compiler_version: Solidity compiler version
            source_code: Contract source code
            contract_name: Name of the contract
            optimization: Whether optimization was enabled
            optimization_runs: Number of optimization runs

        Returns:
            Verification result
        """
        console.print(f"[cyan]Verifying contract {contract_address}...[/cyan]")

        payload = {
            "config": {
                "compiler_version": compiler_version,
                "optimizations_used": optimization,
                "optimizations_count": optimization_runs,
            },
            "contracts": {
                contract_name: source_code,
            },
        }

        endpoint = f"/api/v1/account/{self.account_slug}/project/{self.project_slug}/contracts/{network_id}/{contract_address}/verify"

        response = await self.client.post(endpoint, json=payload)
        response.raise_for_status()

        result = response.json()
        console.print("[green]✓ Contract verified[/green]")

        return result

    async def get_contract(
        self, network_id: str, contract_address: str
    ) -> dict[str, Any]:
        """Get contract information from Tenderly.

        Args:
            network_id: Network ID
            contract_address: Contract address

        Returns:
            Contract information
        """
        endpoint = f"/api/v1/account/{self.account_slug}/project/{self.project_slug}/contracts/{network_id}/{contract_address}"

        response = await self.client.get(endpoint)
        response.raise_for_status()

        return response.json()

    # Alerts and monitoring

    async def create_alert(
        self,
        name: str,
        network_id: str,
        contract_address: str,
        alert_type: str,
        webhook_url: str | None = None,
    ) -> dict[str, Any]:
        """Create an alert for contract monitoring.

        Args:
            name: Alert name
            network_id: Network ID
            contract_address: Contract address to monitor
            alert_type: Type of alert (e.g., "function_call", "event")
            webhook_url: Optional webhook URL for notifications

        Returns:
            Created alert info
        """
        payload = {
            "name": name,
            "network_id": network_id,
            "target": {"address": contract_address},
            "alert_type": alert_type,
        }

        if webhook_url:
            payload["webhook"] = {"url": webhook_url}

        endpoint = f"/api/v1/account/{self.account_slug}/project/{self.project_slug}/alerts"

        response = await self.client.post(endpoint, json=payload)
        response.raise_for_status()

        return response.json()

    # Utility methods

    def format_simulation_result(self, result: dict[str, Any]) -> None:
        """Format and display simulation result.

        Args:
            result: Simulation result from Tenderly
        """
        transaction = result.get("transaction", {})
        trace = result.get("trace", [])

        # Summary table
        table = Table(title="Simulation Result")
        table.add_column("Property", style="cyan")
        table.add_column("Value")

        table.add_row("Status", "✅ Success" if transaction.get("status") else "❌ Failed")
        table.add_row("Gas Used", str(transaction.get("gas_used", "N/A")))
        table.add_row("Calls", str(len(trace)))

        if error := transaction.get("error_message"):
            table.add_row("Error", f"[red]{error}[/red]")

        console.print()
        console.print(table)
        console.print()

        # Show call trace summary
        if trace:
            console.print("[bold]Call Trace:[/bold]")
            for i, call in enumerate(trace[:10]):  # Show first 10 calls
                indent = "  " * call.get("depth", 0)
                function = call.get("function_name", "fallback")
                to = call.get("to", "")[:10] + "..."
                console.print(f"{indent}• {function} → {to}")

            if len(trace) > 10:
                console.print(f"  ... and {len(trace) - 10} more calls")
            console.print()

        # Show state changes
        if state_changes := result.get("state_changes", []):
            console.print(f"[bold]State Changes:[/bold] {len(state_changes)} objects modified")
            console.print()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()


def create_tenderly_client_from_config(config: dict[str, Any]) -> TenderlyClient:
    """Create Tenderly client from configuration dict.

    Args:
        config: Configuration with tenderly settings

    Returns:
        TenderlyClient instance
    """
    return TenderlyClient(
        access_key=config["access_key"],
        account_slug=config["account_slug"],
        project_slug=config["project_slug"],
        api_base=config.get("api_base", "https://api.tenderly.co"),
    )
