"""Database layer using SQLite."""

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import Analysis, AnalysisType, Contract, HistoryEntry, Project


class Database:
    """SQLite database for storing projects, contracts, and analysis history."""

    def __init__(self, db_path: str | None = None):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file. Defaults to ~/.ai-crypto-toolkit/db.sqlite
        """
        if db_path is None:
            db_path = str(Path.home() / ".ai-crypto-toolkit" / "db.sqlite")

        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        cursor = self.conn.cursor()

        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                foundry_config TEXT,
                is_foundry_project INTEGER DEFAULT 0,
                tenderly_project TEXT,
                tenderly_username TEXT
            )
        """)

        # Contracts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                compiler_version TEXT,
                deployed_address TEXT,
                deployment_network TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE(project_id, path)
            )
        """)

        # Analyses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                contract_id INTEGER,
                analysis_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                model TEXT NOT NULL,
                duration REAL NOT NULL,
                cost REAL DEFAULT 0,
                result TEXT NOT NULL,
                summary TEXT,
                severity TEXT,
                findings_count INTEGER DEFAULT 0,
                metadata TEXT,
                tx_hash TEXT,
                network TEXT,
                test_results TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
            )
        """)

        # History table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                analysis_id INTEGER,
                action TEXT NOT NULL,
                created_at TEXT NOT NULL,
                details TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
            )
        """)

        # Indexes for common queries
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_contracts_project ON contracts(project_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_analyses_project ON analyses(project_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_analyses_contract ON analyses(contract_id)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_project ON history(project_id)")

        self.conn.commit()

    # Project operations

    def create_project(self, project: Project) -> Project:
        """Create a new project."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO projects (name, description, path, created_at, updated_at,
                                  metadata, foundry_config, is_foundry_project,
                                  tenderly_project, tenderly_username)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                project.name,
                project.description,
                project.path,
                project.created_at.isoformat(),
                project.updated_at.isoformat(),
                json.dumps(project.metadata),
                project.foundry_config,
                1 if project.is_foundry_project else 0,
                project.tenderly_project,
                project.tenderly_username,
            ),
        )
        self.conn.commit()
        project.id = cursor.lastrowid
        return project

    def get_project(self, project_id: int) -> Project | None:
        """Get project by ID."""
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return self._row_to_project(row) if row else None

    def get_project_by_name(self, name: str) -> Project | None:
        """Get project by name."""
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM projects WHERE name = ?", (name,)).fetchone()
        return self._row_to_project(row) if row else None

    def list_projects(self) -> list[Project]:
        """List all projects."""
        cursor = self.conn.cursor()
        rows = cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()
        return [self._row_to_project(row) for row in rows]

    def update_project(self, project: Project) -> None:
        """Update project."""
        project.updated_at = datetime.utcnow()
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE projects
            SET description=?, path=?, updated_at=?, metadata=?,
                foundry_config=?, is_foundry_project=?,
                tenderly_project=?, tenderly_username=?
            WHERE id=?
        """,
            (
                project.description,
                project.path,
                project.updated_at.isoformat(),
                json.dumps(project.metadata),
                project.foundry_config,
                1 if project.is_foundry_project else 0,
                project.tenderly_project,
                project.tenderly_username,
                project.id,
            ),
        )
        self.conn.commit()

    def delete_project(self, project_id: int) -> None:
        """Delete project (cascades to contracts and analyses)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()

    # Contract operations

    def create_contract(self, contract: Contract) -> Contract:
        """Create a new contract."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO contracts (project_id, name, path, source_hash, created_at,
                                   updated_at, metadata, compiler_version,
                                   deployed_address, deployment_network)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                contract.project_id,
                contract.name,
                contract.path,
                contract.source_hash,
                contract.created_at.isoformat(),
                contract.updated_at.isoformat(),
                json.dumps(contract.metadata),
                contract.compiler_version,
                contract.deployed_address,
                contract.deployment_network,
            ),
        )
        self.conn.commit()
        contract.id = cursor.lastrowid
        return contract

    def get_contract(self, contract_id: int) -> Contract | None:
        """Get contract by ID."""
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,)).fetchone()
        return self._row_to_contract(row) if row else None

    def get_contract_by_path(self, project_id: int, path: str) -> Contract | None:
        """Get contract by project and path."""
        cursor = self.conn.cursor()
        row = cursor.execute(
            "SELECT * FROM contracts WHERE project_id = ? AND path = ?", (project_id, path)
        ).fetchone()
        return self._row_to_contract(row) if row else None

    def list_contracts(self, project_id: int) -> list[Contract]:
        """List all contracts in a project."""
        cursor = self.conn.cursor()
        rows = cursor.execute(
            "SELECT * FROM contracts WHERE project_id = ? ORDER BY name", (project_id,)
        ).fetchall()
        return [self._row_to_contract(row) for row in rows]

    def update_contract(self, contract: Contract) -> None:
        """Update contract."""
        contract.updated_at = datetime.utcnow()
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE contracts
            SET name=?, path=?, source_hash=?, updated_at=?, metadata=?,
                compiler_version=?, deployed_address=?, deployment_network=?
            WHERE id=?
        """,
            (
                contract.name,
                contract.path,
                contract.source_hash,
                contract.updated_at.isoformat(),
                json.dumps(contract.metadata),
                contract.compiler_version,
                contract.deployed_address,
                contract.deployment_network,
                contract.id,
            ),
        )
        self.conn.commit()

    # Analysis operations

    def create_analysis(self, analysis: Analysis) -> Analysis:
        """Create a new analysis."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO analyses (project_id, contract_id, analysis_type, created_at,
                                  model, duration, cost, result, summary, severity,
                                  findings_count, metadata, tx_hash, network, test_results)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                analysis.project_id,
                analysis.contract_id,
                analysis.analysis_type.value,
                analysis.created_at.isoformat(),
                analysis.model,
                analysis.duration,
                analysis.cost,
                analysis.result,
                analysis.summary,
                analysis.severity,
                analysis.findings_count,
                json.dumps(analysis.metadata),
                analysis.tx_hash,
                analysis.network,
                json.dumps(analysis.test_results) if analysis.test_results else None,
            ),
        )
        self.conn.commit()
        analysis.id = cursor.lastrowid
        return analysis

    def get_analysis(self, analysis_id: int) -> Analysis | None:
        """Get analysis by ID."""
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        return self._row_to_analysis(row) if row else None

    def list_analyses(
        self,
        project_id: int,
        contract_id: int | None = None,
        analysis_type: AnalysisType | None = None,
        limit: int = 50,
    ) -> list[Analysis]:
        """List analyses with optional filters."""
        cursor = self.conn.cursor()

        query = "SELECT * FROM analyses WHERE project_id = ?"
        params: list[Any] = [project_id]

        if contract_id:
            query += " AND contract_id = ?"
            params.append(contract_id)

        if analysis_type:
            query += " AND analysis_type = ?"
            params.append(analysis_type.value)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        rows = cursor.execute(query, params).fetchall()
        return [self._row_to_analysis(row) for row in rows]

    # History operations

    def add_history(self, entry: HistoryEntry) -> HistoryEntry:
        """Add history entry."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO history (project_id, analysis_id, action, created_at, details)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                entry.project_id,
                entry.analysis_id,
                entry.action,
                entry.created_at.isoformat(),
                json.dumps(entry.details),
            ),
        )
        self.conn.commit()
        entry.id = cursor.lastrowid
        return entry

    def get_history(
        self, project_id: int | None = None, limit: int = 50
    ) -> list[HistoryEntry]:
        """Get history entries."""
        cursor = self.conn.cursor()

        if project_id:
            query = "SELECT * FROM history WHERE project_id = ? ORDER BY created_at DESC LIMIT ?"
            rows = cursor.execute(query, (project_id, limit)).fetchall()
        else:
            query = "SELECT * FROM history ORDER BY created_at DESC LIMIT ?"
            rows = cursor.execute(query, (limit,)).fetchall()

        return [self._row_to_history(row) for row in rows]

    # Helper methods

    def _row_to_project(self, row: sqlite3.Row) -> Project:
        """Convert database row to Project model."""
        return Project(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            path=row["path"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            foundry_config=row["foundry_config"],
            is_foundry_project=bool(row["is_foundry_project"]),
            tenderly_project=row["tenderly_project"],
            tenderly_username=row["tenderly_username"],
        )

    def _row_to_contract(self, row: sqlite3.Row) -> Contract:
        """Convert database row to Contract model."""
        return Contract(
            id=row["id"],
            project_id=row["project_id"],
            name=row["name"],
            path=row["path"],
            source_hash=row["source_hash"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            compiler_version=row["compiler_version"],
            deployed_address=row["deployed_address"],
            deployment_network=row["deployment_network"],
        )

    def _row_to_analysis(self, row: sqlite3.Row) -> Analysis:
        """Convert database row to Analysis model."""
        return Analysis(
            id=row["id"],
            project_id=row["project_id"],
            contract_id=row["contract_id"],
            analysis_type=AnalysisType(row["analysis_type"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            model=row["model"],
            duration=row["duration"],
            cost=row["cost"],
            result=row["result"],
            summary=row["summary"] or "",
            severity=row["severity"],
            findings_count=row["findings_count"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            tx_hash=row["tx_hash"],
            network=row["network"],
            test_results=json.loads(row["test_results"]) if row["test_results"] else None,
        )

    def _row_to_history(self, row: sqlite3.Row) -> HistoryEntry:
        """Convert database row to HistoryEntry model."""
        return HistoryEntry(
            id=row["id"],
            project_id=row["project_id"],
            analysis_id=row["analysis_id"],
            action=row["action"],
            created_at=datetime.fromisoformat(row["created_at"]),
            details=json.loads(row["details"]) if row["details"] else {},
        )

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


# Global database instance
_db: Database | None = None


def get_db() -> Database:
    """Get global database instance."""
    global _db
    if _db is None:
        _db = Database()
    return _db


def compute_source_hash(source: str) -> str:
    """Compute hash of contract source code."""
    return hashlib.sha256(source.encode()).hexdigest()
