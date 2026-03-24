"""Flashcard study API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Query

from mtgsim.api.models.flashcards import (
    CollectionInfo,
    DeleteCollectionResponse,
    FlashcardQuestion,
    GenerateRequest,
    GenerateResponse,
    ReviewRequest,
    ReviewResponse,
    StudyStats,
)
from mtgsim.api.services.flashcard_service import flashcard_service

logger = logging.getLogger("mtgsim.api.routers.flashcards")

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_flashcards(req: GenerateRequest) -> GenerateResponse:
    """Generate flashcards for a user from MTG data.

    Card types: keyword_definition, card_oracle, card_mana_cost, card_stats.
    Set-based types (card_oracle, card_mana_cost, card_stats) require set_code.
    """
    if req.card_type in ("card_oracle", "card_mana_cost", "card_stats") and not req.set_code:
        raise HTTPException(status_code=400, detail="set_code required for card-based flashcards")

    return await flashcard_service.generate(
        user_id=req.user_id,
        card_type=req.card_type,
        set_code=req.set_code,
        rarity=req.rarity,
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

    Rating scale (SM-2): 0=complete blackout, 1=incorrect but remembered on seeing answer,
    2=incorrect but easy recall, 3=correct with difficulty, 4=correct, 5=perfect.
    """
    return await flashcard_service.record_review(
        user_id=req.user_id,
        flashcard_id=req.flashcard_id,
        rating=req.rating,
        response_time_ms=req.response_time_ms,
    )


@router.get("/collections", response_model=list[CollectionInfo])
async def list_collections(
    user_id: str = Query(..., description="User ID"),
) -> list[CollectionInfo]:
    """List flashcard collections for a user."""
    return await flashcard_service.get_collections(user_id=user_id)


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
