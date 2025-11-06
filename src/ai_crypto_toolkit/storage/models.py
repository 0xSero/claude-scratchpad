"""Data models for storage layer."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AnalysisType(str, Enum):
    """Types of analysis that can be performed."""

    CONTRACT = "contract"
    SECURITY = "security"
    GAS = "gas"
    TRANSACTION = "transaction"
    FUZZING = "fuzzing"
    FOUNDRY_TEST = "foundry_test"
    TENDERLY_SIM = "tenderly_sim"


class Project(BaseModel):
    """A project containing multiple contracts."""

    id: int | None = None
    name: str
    description: str = ""
    path: str  # Root path of the project
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Foundry project settings
    foundry_config: str | None = None  # Path to foundry.toml
    is_foundry_project: bool = False

    # Tenderly settings
    tenderly_project: str | None = None
    tenderly_username: str | None = None


class Contract(BaseModel):
    """A smart contract within a project."""

    id: int | None = None
    project_id: int
    name: str
    path: str  # Relative to project path
    source_hash: str  # Hash of contract source
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Compilation info
    compiler_version: str | None = None
    deployed_address: str | None = None
    deployment_network: str | None = None


class Analysis(BaseModel):
    """An analysis result for a contract."""

    id: int | None = None
    project_id: int
    contract_id: int | None = None  # Null for tx analysis
    analysis_type: AnalysisType
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Analysis metadata
    model: str  # LLM model used
    duration: float  # Seconds
    cost: float = 0.0  # Estimated cost (for tracking)

    # Results
    result: str  # Main analysis result (markdown)
    summary: str = ""  # Short summary for listings
    severity: str | None = None  # For security analysis: high/medium/low
    findings_count: int = 0  # Number of findings
    metadata: dict[str, Any] = Field(default_factory=dict)

    # For transaction analysis
    tx_hash: str | None = None
    network: str | None = None

    # For fuzzing/testing
    test_results: dict[str, Any] | None = None


class HistoryEntry(BaseModel):
    """A history entry for tracking activity."""

    id: int | None = None
    project_id: int | None = None
    analysis_id: int | None = None
    action: str  # "analyze", "audit", "fuzz", etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    details: dict[str, Any] = Field(default_factory=dict)
