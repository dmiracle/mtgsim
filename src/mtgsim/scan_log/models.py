"""SQLModel models for the scan logging database.

Tables:
- ScanAttempt: One row per scan with pipeline, result, and match info
- ScanTiming: Per-stage timing breakdown
- ScanParams: Parameter snapshot as JSON
- ScanMatchCandidate: Top N match candidates with scores
- LLMCall: Per-call LLM usage tracking (tokens, cost, latency)
"""

from datetime import UTC, datetime

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class ScanAttempt(SQLModel, table=True):
    """One row per card scan attempt."""

    __tablename__ = "scan_attempt"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    pipeline: str = Field(index=True)
    image_hash: str = Field(index=True)
    image_size_bytes: int = 0
    mime_type: str = ""
    extracted_name: str = ""
    raw_text: str = ""
    matched: bool = False
    match_type: str = "none"
    match_confidence: float | None = None
    matched_card_uuid: str | None = Field(default=None, index=True)
    matched_card_name: str | None = None
    added_to_collection: bool = False
    added_to_deck_id: int | None = None
    correct: bool | None = None
    notes: str | None = None


class ScanTiming(SQLModel, table=True):
    """Timing breakdown for a scan attempt."""

    __tablename__ = "scan_timing"

    id: int | None = Field(default=None, primary_key=True)
    scan_id: int = Field(foreign_key="scan_attempt.id", index=True)
    preprocess_ms: float = 0.0
    extract_ms: float = 0.0
    match_ms: float = 0.0
    total_ms: float = 0.0


class ScanParams(SQLModel, table=True):
    """Parameter snapshot for a scan attempt (stored as JSON)."""

    __tablename__ = "scan_params"

    id: int | None = Field(default=None, primary_key=True)
    scan_id: int = Field(foreign_key="scan_attempt.id", index=True)
    params_json: dict = Field(default_factory=dict, sa_column=Column(JSON))


class ScanMatchCandidate(SQLModel, table=True):
    """Top N match candidates for a scan attempt."""

    __tablename__ = "scan_match_candidate"

    id: int | None = Field(default=None, primary_key=True)
    scan_id: int = Field(foreign_key="scan_attempt.id", index=True)
    rank: int = 0
    card_name: str = ""
    card_uuid: str = ""
    score: float = 0.0
    component_scores_json: dict = Field(default_factory=dict, sa_column=Column(JSON))


class LLMCall(SQLModel, table=True):
    """One row per LLM API call."""

    __tablename__ = "llm_call"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    scan_id: int | None = Field(default=None, foreign_key="scan_attempt.id", index=True)
    provider: str = Field(index=True)
    model: str = Field(index=True)
    purpose: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    status: str = "success"
    error_message: str | None = None
    request_json: dict | None = Field(default=None, sa_column=Column(JSON))
    response_json: dict | None = Field(default=None, sa_column=Column(JSON))
