"""Scan logging database engine, session management, and logging functions."""

import hashlib
import logging

from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

from mtgsim.scan_log.models import (
    LLMCall,
    ScanAttempt,
    ScanMatchCandidate,
    ScanParams,
    ScanTiming,
)

logger = logging.getLogger("mtgsim.scan_log")

_engine = None


# Cost per 1M tokens: (provider, model) -> (input_cost, output_cost)
# Update as pricing changes. Models not listed default to 0.
LLM_PRICING = {
    ("openai", "gpt-4o"): (2.50, 10.00),
    ("openai", "gpt-4o-mini"): (0.15, 0.60),
    ("openai", "gpt-4-turbo"): (10.00, 30.00),
    ("openai", "gpt-4.1"): (2.00, 8.00),
    ("openai", "gpt-4.1-mini"): (0.40, 1.60),
    ("openai", "gpt-4.1-nano"): (0.10, 0.40),
    ("openai", "o3"): (2.00, 8.00),
    ("openai", "o4-mini"): (1.10, 4.40),
    ("anthropic", "claude-sonnet-4-20250514"): (3.00, 15.00),
    ("anthropic", "claude-opus-4-20250514"): (15.00, 75.00),
    ("anthropic", "claude-haiku-3-20250414"): (0.80, 4.00),
}


def _get_db_path() -> str:
    # Check env var directly (for test isolation) before falling back to settings
    import os

    env_path = os.environ.get("SCAN_LOG_DB_PATH")
    if env_path:
        return env_path

    from mtgsim.settings import settings

    if settings.scan_log_db_path:
        return settings.scan_log_db_path
    from mtgdb.config import MTGDB_HOME

    return str(MTGDB_HOME / "scan_log.sqlite")


def get_engine():
    global _engine
    if _engine is None:
        db_path = _get_db_path()
        _engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        SQLModel.metadata.create_all(_engine, tables=[
            ScanAttempt.__table__,
            ScanTiming.__table__,
            ScanParams.__table__,
            ScanMatchCandidate.__table__,
            LLMCall.__table__,
        ])
        logger.info(f"Scan log DB initialized at {db_path}")
    return _engine


def get_session() -> Session:
    return Session(get_engine())


def close_db():
    global _engine
    if _engine:
        _engine.dispose()
        _engine = None


def image_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def estimate_cost(provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate USD cost from token counts using the pricing table."""
    key = (provider, model)
    if key not in LLM_PRICING:
        return 0.0
    input_rate, output_rate = LLM_PRICING[key]
    return (prompt_tokens * input_rate + completion_tokens * output_rate) / 1_000_000


def log_scan(
    pipeline: str,
    image_data: bytes,
    mime_type: str,
    extracted_name: str,
    raw_text: str,
    matched: bool,
    match_type: str,
    match_confidence: float | None,
    matched_card_uuid: str | None,
    matched_card_name: str | None,
    added_to_collection: bool,
    added_to_deck_id: int | None,
    timing: dict[str, float] | None = None,
    params: dict | None = None,
    candidates: list[dict] | None = None,
) -> int:
    """Log a scan attempt. Returns the scan_attempt.id."""
    with get_session() as session:
        attempt = ScanAttempt(
            pipeline=pipeline,
            image_hash=image_hash(image_data),
            image_size_bytes=len(image_data),
            mime_type=mime_type,
            extracted_name=extracted_name,
            raw_text=raw_text,
            matched=matched,
            match_type=match_type,
            match_confidence=match_confidence,
            matched_card_uuid=matched_card_uuid,
            matched_card_name=matched_card_name,
            added_to_collection=added_to_collection,
            added_to_deck_id=added_to_deck_id,
        )
        session.add(attempt)
        session.flush()
        scan_id = attempt.id

        if timing:
            session.add(ScanTiming(scan_id=scan_id, **timing))

        if params:
            session.add(ScanParams(scan_id=scan_id, params_json=params))

        if candidates:
            for i, cand in enumerate(candidates):
                session.add(ScanMatchCandidate(
                    scan_id=scan_id,
                    rank=i + 1,
                    card_name=cand.get("card_name", ""),
                    card_uuid=cand.get("card_uuid", ""),
                    score=cand.get("score", 0.0),
                    component_scores_json=cand.get("component_scores", {}),
                ))

        session.commit()
        logger.debug(f"Logged scan attempt {scan_id}: {extracted_name} ({pipeline})")
        return scan_id


def log_llm_call(
    provider: str,
    model: str,
    purpose: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: float,
    status: str = "success",
    scan_id: int | None = None,
    error_message: str | None = None,
    request_json: dict | None = None,
    response_json: dict | None = None,
) -> int:
    """Log an LLM API call. Returns the llm_call.id."""
    cost = estimate_cost(provider, model, prompt_tokens, completion_tokens)

    with get_session() as session:
        call = LLMCall(
            scan_id=scan_id,
            provider=provider,
            model=model,
            purpose=purpose,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message,
            request_json=request_json,
            response_json=response_json,
        )
        session.add(call)
        session.commit()
        logger.debug(
            f"Logged LLM call {call.id}: {provider}/{model} "
            f"{prompt_tokens}+{completion_tokens} tokens, ${cost:.4f}"
        )
        return call.id
