"""Migration tracking and logging models for the domain database."""

from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class MigrationStatus(str, Enum):
    """Status of a migration operation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class MigrationType(str, Enum):
    """Type of migration operation."""

    REFERENCE_SYNC = "reference_sync"
    ENTITY_ADD = "entity_add"
    BULK_IMPORT = "bulk_import"
    SCHEMA_UPDATE = "schema_update"
    DATA_CLEANUP = "data_cleanup"


class MigrationLog(SQLModel, table=True):
    """Track migration operations and their status."""

    __tablename__ = "migration_log"

    id: int | None = Field(default=None, primary_key=True)

    # Migration identification
    migration_type: MigrationType = Field(index=True)
    source_name: str = Field(index=True)  # e.g., 'mtgjson', 'tcgplayer', 'scryfall'
    operation_name: str = Field(index=True)  # e.g., 'sync_cards', 'add_card', 'sync_sets'

    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    completed_at: datetime | None = None
    duration_seconds: float | None = None

    # Status tracking
    status: MigrationStatus = Field(default=MigrationStatus.PENDING, index=True)
    error_message: str | None = None
    error_details: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Progress tracking
    total_items: int | None = None
    processed_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0

    # Operation details
    parameters: dict = Field(default_factory=dict, sa_column=Column(JSON))
    result_summary: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Rollback information
    rollback_data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    can_rollback: bool = True

    # Metadata
    version: str | None = None  # Version of the migration system
    fingerprint: str | None = None  # Hash of source data for change detection

    def mark_started(self) -> None:
        """Mark migration as started."""
        self.status = MigrationStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()

    def mark_completed(self, result_summary: dict | None = None) -> None:
        """Mark migration as completed."""
        self.status = MigrationStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        if result_summary:
            self.result_summary = result_summary

    def mark_failed(self, error_message: str, error_details: dict | None = None) -> None:
        """Mark migration as failed."""
        self.status = MigrationStatus.FAILED
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.error_message = error_message
        if error_details:
            self.error_details = error_details

    def update_progress(self, processed: int, failed: int = 0, skipped: int = 0) -> None:
        """Update progress counters."""
        self.processed_items = processed
        self.failed_items = failed
        self.skipped_items = skipped


class SchemaVersion(SQLModel, table=True):
    """Track domain database schema versions."""

    __tablename__ = "schema_version"

    id: int | None = Field(default=None, primary_key=True)
    version: str = Field(unique=True, index=True)
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    description: str | None = None
    migration_script: str | None = None  # SQL or Python script that was applied
    checksum: str | None = None  # Checksum of the migration script


class DataIntegrityCheck(SQLModel, table=True):
    """Track data integrity validation results."""

    __tablename__ = "data_integrity_check"

    id: int | None = Field(default=None, primary_key=True)

    # Check identification
    check_name: str = Field(index=True)
    table_name: str = Field(index=True)
    check_type: str = Field(index=True)  # 'foreign_key', 'unique', 'not_null', 'custom'

    # Timing
    executed_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Results
    passed: bool = Field(index=True)
    error_count: int = 0
    warning_count: int = 0

    # Details
    error_details: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    warning_details: list[dict] = Field(default_factory=list, sa_column=Column(JSON))

    # Context
    migration_log_id: int | None = Field(default=None, foreign_key="migration_log.id")
    parameters: dict = Field(default_factory=dict, sa_column=Column(JSON))
