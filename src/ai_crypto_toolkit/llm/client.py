"""LLM client for interacting with local AI models via OpenAI-compatible APIs."""

import asyncio
from typing import Any, AsyncIterator

import httpx
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from ..config import LLMConfig

console = Console()


class LLMClient:
    """Client for local LLM APIs (vLLM, TabbyAPI, LM Studio, etc.)."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.api_base,
            timeout=config.timeout,
            headers={"Authorization": f"Bearer {config.api_key}"},
        )

    async def __aenter__(self) -> "LLMClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.client.aclose()

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stream: bool | None = None,
    ) -> str:
        """Send a completion request to the local LLM.

        Args:
            prompt: The user prompt
            system: Optional system message
            temperature: Override config temperature
            max_tokens: Override config max_tokens
            stream: Override config stream setting

        Returns:
            Complete response text
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": stream if stream is not None else self.config.stream,
        }

        if payload["stream"]:
            return await self._stream_completion(payload)
        else:
            return await self._complete(payload)

    async def _complete(self, payload: dict[str, Any]) -> str:
        """Non-streaming completion."""
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _stream_completion(self, payload: dict[str, Any]) -> str:
        """Streaming completion with real-time display."""
        full_response = ""

        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()

            with Live(console=console, refresh_per_second=10) as live:
                async for line in response.aiter_lines():
                    if not line.strip() or line.strip() == "data: [DONE]":
                        continue

                    if line.startswith("data: "):
                        try:
                            import json

                            data = json.loads(line[6:])
                            if content := data["choices"][0]["delta"].get("content"):
                                full_response += content
                                live.update(Markdown(full_response))
                        except (json.JSONDecodeError, KeyError):
                            continue

        return full_response

    async def analyze_code(
        self,
        code: str,
        analysis_type: str,
        context: str | None = None,
    ) -> str:
        """Analyze code with appropriate system prompt.

        Args:
            code: The code to analyze
            analysis_type: Type of analysis (contract, security, gas, etc.)
            context: Additional context for the analysis

        Returns:
            Analysis result
        """
        from .prompts import get_analysis_prompt, get_system_prompt

        system = get_system_prompt(analysis_type)
        prompt = get_analysis_prompt(analysis_type, code, context)

        return await self.complete(prompt, system=system)

    async def explain_transaction(
        self,
        tx_data: dict[str, Any],
        contract_abi: list[dict[str, Any]] | None = None,
    ) -> str:
        """Explain what a transaction does in plain English.

        Args:
            tx_data: Transaction data (hash, from, to, input, etc.)
            contract_abi: Optional contract ABI for better decoding

        Returns:
            Human-readable explanation
        """
        from .prompts import get_transaction_prompt

        prompt = get_transaction_prompt(tx_data, contract_abi)
        system = "You are an expert at explaining blockchain transactions in simple terms."

        return await self.complete(prompt, system=system)

    async def check_health(self) -> bool:
        """Check if the LLM API is accessible and responding.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try a simple completion
            response = await self.complete(
                "Respond with just 'OK'",
                system="You are a test assistant.",
                stream=False,
                max_tokens=10,
            )
            return "ok" in response.lower()
        except Exception as e:
            console.print(f"[red]LLM health check failed: {e}[/red]")
            return False


async def test_llm_connection(config: LLMConfig) -> bool:
    """Test connection to local LLM API.

    Args:
        config: LLM configuration

    Returns:
        True if connection successful, False otherwise
    """
    async with LLMClient(config) as client:
        return await client.check_health()
