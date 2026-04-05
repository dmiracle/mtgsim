"""Query functions for the scan log database."""

from sqlalchemy import Integer, cast
from sqlmodel import Session, col, func, select

from mtgsim.scan_log.db import get_engine
from mtgsim.scan_log.models import (
    LLMCall,
    ScanAttempt,
    ScanBatch,
    ScanMatchCandidate,
    ScanParams,
    ScanTiming,
)


def get_scan_list(
    q: str | None = None,
    pipeline: str | None = None,
    matched: bool | None = None,
    correct: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """Get paginated scan history with optional filters."""
    with Session(get_engine()) as session:
        query = select(ScanAttempt)
        count_query = select(func.count(ScanAttempt.id))

        if q:
            search = f"%{q}%"
            name_filter = ScanAttempt.extracted_name.like(search) | ScanAttempt.matched_card_name.like(search)
            query = query.where(name_filter)
            count_query = count_query.where(name_filter)
        if pipeline:
            query = query.where(ScanAttempt.pipeline == pipeline)
            count_query = count_query.where(ScanAttempt.pipeline == pipeline)
        if matched is not None:
            query = query.where(ScanAttempt.matched == matched)
            count_query = count_query.where(ScanAttempt.matched == matched)
        if correct is not None:
            query = query.where(ScanAttempt.correct == correct)
            count_query = count_query.where(ScanAttempt.correct == correct)

        total = session.exec(count_query).one()
        attempts = session.exec(query.order_by(col(ScanAttempt.created_at).desc()).offset(offset).limit(limit)).all()

        results = []
        for a in attempts:
            timing = session.exec(select(ScanTiming).where(ScanTiming.scan_id == a.id)).first()
            results.append(
                {
                    "id": a.id,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                    "pipeline": a.pipeline,
                    "extracted_name": a.extracted_name,
                    "matched": a.matched,
                    "match_type": a.match_type,
                    "match_confidence": a.match_confidence,
                    "matched_card_name": a.matched_card_name,
                    "correct": a.correct,
                    "total_ms": timing.total_ms if timing else None,
                }
            )

        return results, total


def get_scan_detail(scan_id: int) -> dict | None:
    """Get full detail for a single scan attempt."""
    with Session(get_engine()) as session:
        attempt = session.exec(select(ScanAttempt).where(ScanAttempt.id == scan_id)).first()
        if not attempt:
            return None

        timing = session.exec(select(ScanTiming).where(ScanTiming.scan_id == scan_id)).first()
        params = session.exec(select(ScanParams).where(ScanParams.scan_id == scan_id)).first()
        candidates = session.exec(
            select(ScanMatchCandidate).where(ScanMatchCandidate.scan_id == scan_id).order_by(ScanMatchCandidate.rank)
        ).all()
        llm_calls = session.exec(select(LLMCall).where(LLMCall.scan_id == scan_id)).all()

        return {
            "id": attempt.id,
            "created_at": attempt.created_at.isoformat() if attempt.created_at else None,
            "pipeline": attempt.pipeline,
            "image_hash": attempt.image_hash,
            "image_size_bytes": attempt.image_size_bytes,
            "mime_type": attempt.mime_type,
            "extracted_name": attempt.extracted_name,
            "raw_text": attempt.raw_text,
            "matched": attempt.matched,
            "match_type": attempt.match_type,
            "match_confidence": attempt.match_confidence,
            "matched_card_uuid": attempt.matched_card_uuid,
            "matched_card_name": attempt.matched_card_name,
            "added_to_collection": attempt.added_to_collection,
            "added_to_deck_id": attempt.added_to_deck_id,
            "correct": attempt.correct,
            "notes": attempt.notes,
            "timing": {
                "preprocess_ms": timing.preprocess_ms,
                "extract_ms": timing.extract_ms,
                "match_ms": timing.match_ms,
                "total_ms": timing.total_ms,
            }
            if timing
            else None,
            "params": params.params_json if params else None,
            "candidates": [
                {
                    "rank": c.rank,
                    "card_name": c.card_name,
                    "card_uuid": c.card_uuid,
                    "score": c.score,
                    "component_scores": c.component_scores_json,
                }
                for c in candidates
            ],
            "llm_calls": [
                {
                    "provider": lc.provider,
                    "model": lc.model,
                    "prompt_tokens": lc.prompt_tokens,
                    "completion_tokens": lc.completion_tokens,
                    "total_tokens": lc.total_tokens,
                    "cost_usd": lc.cost_usd,
                    "latency_ms": lc.latency_ms,
                    "status": lc.status,
                    "error_message": lc.error_message,
                }
                for lc in llm_calls
            ],
        }


def get_summary_stats() -> dict:
    """Get aggregate stats across all scans."""
    with Session(get_engine()) as session:
        total = session.exec(select(func.count(ScanAttempt.id))).one()
        matched = session.exec(select(func.count(ScanAttempt.id)).where(ScanAttempt.matched.is_(True))).one()
        labeled = session.exec(select(func.count(ScanAttempt.id)).where(ScanAttempt.correct.is_not(None))).one()
        correct = session.exec(select(func.count(ScanAttempt.id)).where(ScanAttempt.correct.is_(True))).one()

        # Per-pipeline breakdown
        pipeline_rows = session.exec(
            select(
                ScanAttempt.pipeline,
                func.count(ScanAttempt.id),
                func.sum(cast(ScanAttempt.matched, Integer)),
            ).group_by(ScanAttempt.pipeline)
        ).all()

        pipelines = {}
        for pipe, count, match_count in pipeline_rows:
            pipelines[pipe] = {"total": count, "matched": match_count or 0}

        # Avg timing per pipeline
        timing_rows = session.exec(
            select(
                ScanAttempt.pipeline,
                func.avg(ScanTiming.total_ms),
                func.avg(ScanTiming.extract_ms),
                func.avg(ScanTiming.match_ms),
            )
            .join(ScanTiming, ScanTiming.scan_id == ScanAttempt.id)
            .group_by(ScanAttempt.pipeline)
        ).all()

        for pipe, avg_total, avg_extract, avg_match in timing_rows:
            if pipe in pipelines:
                pipelines[pipe]["avg_total_ms"] = round(avg_total or 0, 1)
                pipelines[pipe]["avg_extract_ms"] = round(avg_extract or 0, 1)
                pipelines[pipe]["avg_match_ms"] = round(avg_match or 0, 1)

        return {
            "total_scans": total,
            "total_matched": matched,
            "total_labeled": labeled,
            "total_correct": correct,
            "accuracy": round(correct / labeled * 100, 1) if labeled > 0 else None,
            "match_rate": round(matched / total * 100, 1) if total > 0 else None,
            "pipelines": pipelines,
        }


def get_llm_cost_stats() -> dict:
    """Get LLM cost and usage statistics."""
    with Session(get_engine()) as session:
        total_calls = session.exec(select(func.count(LLMCall.id))).one()
        total_cost = session.exec(select(func.sum(LLMCall.cost_usd))).one() or 0
        total_tokens = session.exec(select(func.sum(LLMCall.total_tokens))).one() or 0

        # Per-model breakdown
        model_rows = session.exec(
            select(
                LLMCall.provider,
                LLMCall.model,
                func.count(LLMCall.id),
                func.sum(LLMCall.prompt_tokens),
                func.sum(LLMCall.completion_tokens),
                func.sum(LLMCall.cost_usd),
                func.avg(LLMCall.latency_ms),
            ).group_by(LLMCall.provider, LLMCall.model)
        ).all()

        models = []
        for provider, model, count, prompt_tok, comp_tok, cost, avg_lat in model_rows:
            models.append(
                {
                    "provider": provider,
                    "model": model,
                    "calls": count,
                    "prompt_tokens": prompt_tok or 0,
                    "completion_tokens": comp_tok or 0,
                    "total_cost_usd": round(cost or 0, 4),
                    "avg_latency_ms": round(avg_lat or 0, 1),
                }
            )

        errors = session.exec(select(func.count(LLMCall.id)).where(LLMCall.status == "error")).one()

        return {
            "total_calls": total_calls,
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "error_count": errors,
            "models": models,
        }


def label_scan(scan_id: int, correct: bool, notes: str | None = None) -> bool:
    """Label a scan as correct or incorrect. Returns True if scan exists."""
    with Session(get_engine()) as session:
        attempt = session.exec(select(ScanAttempt).where(ScanAttempt.id == scan_id)).first()
        if not attempt:
            return False
        attempt.correct = correct
        if notes is not None:
            attempt.notes = notes
        session.add(attempt)
        session.commit()
        return True


def get_batch_list() -> list[dict]:
    """List all batch scan jobs, newest first."""
    with Session(get_engine()) as session:
        batches = session.exec(select(ScanBatch).order_by(col(ScanBatch.created_at).desc())).all()
        return [
            {
                "id": b.id,
                "created_at": b.created_at.isoformat() if b.created_at else None,
                "completed_at": b.completed_at.isoformat() if b.completed_at else None,
                "status": b.status,
                "source_dir": b.source_dir,
                "total_images": b.total_images,
                "processed": b.processed,
                "matched_openai": b.matched_openai,
                "matched_tesseract": b.matched_tesseract,
                "agreed": b.agreed,
                "added_to_collection": b.added_to_collection,
                "total_cost_usd": b.total_cost_usd,
                "total_time_s": b.total_time_s,
            }
            for b in batches
        ]


def get_batch_detail(batch_id: int) -> dict | None:
    """Get full detail for a batch scan job, including per-image results."""
    with Session(get_engine()) as session:
        batch = session.exec(select(ScanBatch).where(ScanBatch.id == batch_id)).first()
        if not batch:
            return None

        # Get all scans in this batch, grouped by image_hash
        scans = session.exec(
            select(ScanAttempt)
            .where(ScanAttempt.batch_id == batch_id)
            .order_by(ScanAttempt.image_hash, ScanAttempt.pipeline)
        ).all()

        # Group by image_hash
        images: dict[str, dict] = {}
        for s in scans:
            if s.image_hash not in images:
                images[s.image_hash] = {"image_hash": s.image_hash, "pipelines": {}}
            images[s.image_hash]["pipelines"][s.pipeline] = {
                "scan_id": s.id,
                "extracted_name": s.extracted_name,
                "matched": s.matched,
                "match_type": s.match_type,
                "match_confidence": s.match_confidence,
                "matched_card_name": s.matched_card_name,
                "added_to_collection": s.added_to_collection,
            }

        return {
            "id": batch.id,
            "created_at": batch.created_at.isoformat() if batch.created_at else None,
            "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
            "status": batch.status,
            "source_dir": batch.source_dir,
            "total_images": batch.total_images,
            "processed": batch.processed,
            "matched_openai": batch.matched_openai,
            "matched_tesseract": batch.matched_tesseract,
            "agreed": batch.agreed,
            "added_to_collection": batch.added_to_collection,
            "total_cost_usd": batch.total_cost_usd,
            "total_time_s": batch.total_time_s,
            "summary": batch.summary_json,
            "images": list(images.values()),
        }
