"""Configuration management for AI Crypto Toolkit."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Configuration for local LLM API."""

    api_base: str = Field(default="http://localhost:8000/v1")
    model: str = Field(default="gpt-3.5-turbo")  # Default for compatibility
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, gt=0)
    timeout: int = Field(default=300, gt=0)
    stream: bool = Field(default=True)
    api_key: str = Field(default="dummy-key")  # Most local APIs don't need real keys


class EthereumConfig(BaseModel):
    """Configuration for Ethereum RPC access."""

    rpc_url: str = Field(default="http://localhost:8545")
    timeout: int = Field(default=30, gt=0)


class SecurityConfig(BaseModel):
    """Configuration for security analysis."""

    check_reentrancy: bool = Field(default=True)
    check_overflow: bool = Field(default=True)
    check_access_control: bool = Field(default=True)
    check_delegatecall: bool = Field(default=True)
    check_tx_origin: bool = Field(default=True)
    check_unchecked_calls: bool = Field(default=True)
    custom_patterns: list[str] = Field(default_factory=list)


class Config(BaseModel):
    """Main configuration for AI Crypto Toolkit."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    ethereum: EthereumConfig = Field(default_factory=EthereumConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)


def load_config(config_path: str | None = None) -> Config:
    """Load configuration from file or environment variables.

    Priority (highest to lowest):
    1. Explicit config file path
    2. Environment variables (LLM_API_BASE, LLM_MODEL, etc.)
    3. ~/.ai-crypto-toolkit/config.yaml
    4. Default values
    """
    config_dict: dict[str, Any] = {}

    # Try to load from file
    if config_path:
        config_file = Path(config_path)
    else:
        config_file = Path.home() / ".ai-crypto-toolkit" / "config.yaml"

    if config_file.exists():
        with open(config_file) as f:
            config_dict = yaml.safe_load(f) or {}

    # Override with environment variables
    llm_config = config_dict.get("llm", {})
    if api_base := os.getenv("LLM_API_BASE"):
        llm_config["api_base"] = api_base
    if model := os.getenv("LLM_MODEL"):
        llm_config["model"] = model
    if temperature := os.getenv("LLM_TEMPERATURE"):
        llm_config["temperature"] = float(temperature)
    if max_tokens := os.getenv("LLM_MAX_TOKENS"):
        llm_config["max_tokens"] = int(max_tokens)
    if api_key := os.getenv("LLM_API_KEY"):
        llm_config["api_key"] = api_key

    if llm_config:
        config_dict["llm"] = llm_config

    eth_config = config_dict.get("ethereum", {})
    if rpc_url := os.getenv("ETH_RPC_URL"):
        eth_config["rpc_url"] = rpc_url

    if eth_config:
        config_dict["ethereum"] = eth_config

    return Config(**config_dict)


def create_default_config(path: str | None = None) -> Path:
    """Create a default configuration file."""
    if path:
        config_path = Path(path)
    else:
        config_path = Path.home() / ".ai-crypto-toolkit" / "config.yaml"

    config_path.parent.mkdir(parents=True, exist_ok=True)

    default_config = """# AI Crypto Toolkit Configuration

llm:
  # Point to your local LLM API (vLLM, TabbyAPI, LM Studio, etc.)
  api_base: "http://localhost:8000/v1"

  # Model name (whatever your local API uses)
  model: "Qwen/Qwen2.5-Coder-32B-Instruct"

  # Temperature for code analysis (lower = more deterministic)
  temperature: 0.1

  # Max tokens for responses
  max_tokens: 4000

  # Request timeout (seconds)
  timeout: 300

  # Enable streaming (recommended for real-time feedback)
  stream: true

  # API key (most local APIs don't need this, use "dummy-key")
  api_key: "dummy-key"

ethereum:
  # Ethereum RPC URL (for transaction analysis)
  rpc_url: "http://localhost:8545"
  # Or use a service: "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"

  timeout: 30

security:
  # Which security checks to enable
  check_reentrancy: true
  check_overflow: true
  check_access_control: true
  check_delegatecall: true
  check_tx_origin: true
  check_unchecked_calls: true

  # Add custom vulnerability patterns (regex)
  custom_patterns: []
"""

    with open(config_path, "w") as f:
        f.write(default_config)

    return config_path
