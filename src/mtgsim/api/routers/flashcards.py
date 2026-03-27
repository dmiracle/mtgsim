"""Flashcard study API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Query

from mtgsim.api.models.flashcards import (
    CardDifficultyResponse,
    CollectionBreakdown,
    CollectionInfo,
    DeleteCollectionResponse,
    FlashcardQuestion,
    GenerateRequest,
    GenerateResponse,
    KeywordInsightsResponse,
    MergeCollectionsRequest,
    MergeCollectionsResponse,
    RetentionCurveResponse,
    ReviewHistoryResponse,
    ReviewRequest,
    ReviewResponse,
    SessionAnalytics,
    StudyStats,
)
from mtgsim.api.services import flashcard_analytics
from mtgsim.api.services.flashcard_service import flashcard_service

logger = logging.getLogger("mtgsim.api.routers.flashcards")

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_flashcards(req: GenerateRequest) -> GenerateResponse:
    """Generate flashcards for a user from MTG data.

    Card types: keyword_definition, card_oracle, card_mana_cost, card_stats, card_recall.
    Set-based types require set_code.
    """
    if req.card_type in ("card_oracle", "card_mana_cost", "card_stats", "card_recall") and not req.set_code:
        raise HTTPException(status_code=400, detail="set_code required for card-based flashcards")

    return await flashcard_service.generate(
        user_id=req.user_id,
        card_type=req.card_type,
        set_code=req.set_code,
        rarity=req.rarity,
        collection_name=req.collection_name,
    )


@router.get("/next", response_model=FlashcardQuestion | None)
async def get_next_flashcard(
    user_id: str = Query(..., description="User ID"),
    collection: str | None = Query(None, description="Collection name to study from"),
) -> FlashcardQuestion | None:
    """Get the next flashcard to study.

    Uses SM-2 scheduling with randomization among due/new cards to avoid
    returning the same card repeatedly.

    Returns null if no cards are available (all reviewed, none generated).
    """
    return await flashcard_service.get_next(user_id=user_id, collection=collection)


@router.post("/review", response_model=ReviewResponse)
async def record_review(req: ReviewRequest) -> ReviewResponse:
    """Record a flashcard review.

    Accepts either a single `rating` (0-5 SM-2 scale) or `aspect_ratings`
    (dict of aspect → green/yellow/red). When aspect_ratings is provided,
    the effective SM-2 rating is derived from the worst aspect
    (green=5, yellow=3, red=1).
    """
    metadata = None
    if req.aspect_ratings:
        metadata = {"aspect_ratings": req.aspect_ratings}

    return await flashcard_service.record_review(
        user_id=req.user_id,
        flashcard_id=req.flashcard_id,
        rating=req.effective_rating(),
        response_time_ms=req.response_time_ms,
        metadata=metadata,
    )


@router.get("/collections", response_model=list[CollectionInfo])
async def list_collections(
    user_id: str = Query(..., description="User ID"),
) -> list[CollectionInfo]:
    """List flashcard collections for a user."""
    return await flashcard_service.get_collections(user_id=user_id)


@router.post("/collections/merge", response_model=MergeCollectionsResponse)
async def merge_collections(req: MergeCollectionsRequest) -> MergeCollectionsResponse:
    """Merge multiple collections into a single named collection.

    Copies all flashcards from source collections into a new/existing collection.
    Set delete_originals=true to remove source collections after merge.
    """
    result = await flashcard_service.merge_collections(
        user_id=req.user_id,
        collection_ids=req.collection_ids,
        name=req.name,
        delete_originals=req.delete_originals,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="One or more source collections not found")
    return result


@router.delete("/collections/{collection_id}", response_model=DeleteCollectionResponse)
async def delete_collection(
    collection_id: int,
    user_id: str = Query(..., description="User ID"),
) -> DeleteCollectionResponse:
    """Delete a flashcard collection and its orphaned flashcards."""
    result = await flashcard_service.delete_collection(user_id=user_id, collection_id=collection_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    return result


@router.get("/stats", response_model=StudyStats)
async def get_study_stats(
    user_id: str = Query(..., description="User ID"),
) -> StudyStats:
    """Get study statistics for a user."""
    return await flashcard_service.get_stats(user_id=user_id)


# =============================================================================
# Analytics endpoints
# =============================================================================


@router.get("/analytics/review-history", response_model=ReviewHistoryResponse)
async def review_history(
    user_id: str = Query(..., description="User ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    granularity: str = Query("daily", pattern="^(daily|hourly)$", description="Bucket granularity"),
) -> ReviewHistoryResponse:
    """Review counts, ratings, and response times bucketed by time.

    Granularity:
    - **daily** (default): one bucket per day
    - **hourly**: one bucket per hour (days × 24 buckets)
    """
    return await flashcard_analytics.get_review_history(user_id, days=days, granularity=granularity)


@router.get("/analytics/card-difficulty", response_model=CardDifficultyResponse)
async def card_difficulty(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(10, ge=1, le=50, description="Cards per list"),
) -> CardDifficultyResponse:
    """Hardest, easiest, and most-reviewed cards."""
    return await flashcard_analytics.get_card_difficulty(user_id, limit=limit)


@router.get("/analytics/collections", response_model=list[CollectionBreakdown])
async def collection_breakdown(
    user_id: str = Query(..., description="User ID"),
) -> list[CollectionBreakdown]:
    """Per-collection stats: completion, win rate, ease, cards due."""
    return await flashcard_analytics.get_collection_breakdown(user_id)


@router.get("/analytics/sessions", response_model=SessionAnalytics)
async def session_analytics(
    user_id: str = Query(..., description="User ID"),
) -> SessionAnalytics:
    """Study time, review velocity, and accuracy by card type."""
    return await flashcard_analytics.get_session_analytics(user_id)


@router.get("/analytics/retention", response_model=RetentionCurveResponse)
async def retention_curve(
    user_id: str = Query(..., description="User ID"),
) -> RetentionCurveResponse:
    """Pass rate by interval bucket (retention curve)."""
    return await flashcard_analytics.get_retention_curve(user_id)


@router.get("/analytics/keywords", response_model=KeywordInsightsResponse)
async def keyword_insights(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(10, ge=1, le=50, description="Keywords per list"),
) -> KeywordInsightsResponse:
    """Hardest and easiest keywords by ease factor."""
    return await flashcard_analytics.get_keyword_insights(user_id, limit=limit)
