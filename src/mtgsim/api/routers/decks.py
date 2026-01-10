"""Deck API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from mtgsim.api.models.deck import DeckDetail, DeckListResponse
from mtgsim.api.services.deck_service import deck_service

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("", response_model=DeckListResponse)
async def list_decks(
    q: str | None = Query(None, description="Search by deck name or code"),
    format: str | None = Query(None, description="Filter by format legality"),
    set: str | None = Query(None, description="Filter by set code"),
    type: str | None = Query(None, description="Filter by deck type (60, 100)"),
    colors: str | None = Query(None, description="Filter by color identity (e.g., 'WU', 'BRG')"),
    card_count_min: int | None = Query(None, ge=0, description="Minimum card count"),
    card_count_max: int | None = Query(None, ge=0, description="Maximum card count"),
    price_min: float | None = Query(None, ge=0, description="Minimum deck price"),
    price_max: float | None = Query(None, ge=0, description="Maximum deck price"),
    source: str | None = Query(None, pattern="^(precon|user)$", description="Deck source (precon or user)"),
    sort: str = Query("name", description="Sort field"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> DeckListResponse:
    """
    List and filter decks with pagination.

    - **q**: Search deck names and codes
    - **format**: Filter by format legality (standard, pioneer, modern, legacy, vintage, commander)
    - **set**: Filter by set code
    - **type**: Filter by deck size (60 for standard, 100 for commander)
    - **colors**: Filter by color identity (e.g., "WU" for white-blue decks)
    - **card_count_min/card_count_max**: Filter by card count range
    - **price_min/price_max**: Filter by deck price range
    - **source**: Filter by deck source (precon=preconstructed, user=user-created)
    - **sort**: Sort by name, release_date, card_count, price, colors
    - **order**: Sort order (asc, desc)
    """
    color_list = list(colors.upper()) if colors else None

    return await deck_service.list_decks(
        q=q,
        format=format,
        set_code=set,
        deck_type=type,
        colors=color_list,
        card_count_min=card_count_min,
        card_count_max=card_count_max,
        price_min=price_min,
        price_max=price_max,
        source=source,
        sort=sort,
        order=order,
        page=page,
        limit=limit,
    )


@router.get("/{file}", response_model=DeckDetail)
async def get_deck(file: str) -> DeckDetail:
    """
    Get full deck details including cards and statistics.

    Returns complete deck information with:
    - Deck metadata (name, code, release date)
    - Format legality
    - Color identity
    - Price breakdown by source
    - All cards (commander, main board, sideboard) with ownership status
    - Statistics (mana curve, type distribution, keywords)
    """
    deck = await deck_service.get_deck(file)
    if deck is None:
        raise HTTPException(status_code=404, detail=f"Deck not found: {file}")
    return deck


@router.get("/{file}/raw")
async def get_deck_raw(file: str) -> dict:
    """
    Get raw deck JSON for developer inspection.

    Returns the deck data in raw format.
    """
    data = await deck_service.get_deck_raw(file)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Deck not found: {file}")
    return data
