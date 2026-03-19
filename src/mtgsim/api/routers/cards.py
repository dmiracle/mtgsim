"""Card API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from mtgsim.api.models.card import CardDetail, CardListResponse
from mtgsim.api.services.card_service import card_service

logger = logging.getLogger("mtgsim.api.routers.cards")

router = APIRouter(prefix="/cards", tags=["cards"])


class CollectionResponse(BaseModel):
    """Response for collection management operations."""

    success: bool
    message: str
    card: dict | None = None


class QuadrantRatingRequest(BaseModel):
    developing: float | None = None
    ahead: float | None = None
    behind: float | None = None
    parity: float | None = None
    notes: str | None = None


class QuadrantRatingResponse(BaseModel):
    developing: float | None = None
    ahead: float | None = None
    behind: float | None = None
    parity: float | None = None
    notes: str | None = None


@router.get("", response_model=CardListResponse)
async def search_cards(
    q: str | None = Query(None, description="Search by card name"),
    text: str | None = Query(None, description="Filter by oracle text"),
    set: str | None = Query(None, description="Filter by set code"),
    sets: str | None = Query(None, description="Filter by multiple set codes (comma-separated)"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    type: str | None = Query(None, description="Filter by card type"),
    colors: str | None = Query(None, description="Filter by color identity"),
    format: str | None = Query(None, description="Filter by format legality (standard, modern, etc.)"),
    keywords: str | None = Query(None, description="Filter by keywords (comma-separated)"),
    tags: str | None = Query(None, description="Filter by oracle tags (comma-separated, e.g. mana-dork,ramp)"),
    price_min: float | None = Query(None, ge=0, description="Minimum price"),
    price_max: float | None = Query(None, ge=0, description="Maximum price"),
    owns: bool | None = Query(None, description="Filter by ownership"),
    wants: bool | None = Query(None, description="Filter by want status"),
    unique: bool = Query(False, description="Show only one printing per card name"),
    sort: str = Query("name", description="Sort field"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> CardListResponse:
    """Search cards with filters."""
    color_list = list(colors.upper()) if colors else None
    set_code_list = [s.strip() for s in sets.split(",") if s.strip()] if sets else None
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else None
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None

    logger.debug(f"search_cards: q={q} set={set} format={format} rarity={rarity}")
    return await card_service.search_cards(
        q=q,
        text=text,
        set_code=set,
        set_codes=set_code_list,
        rarity=rarity,
        card_type=type,
        colors=color_list,
        format_legal=format,
        keywords=keyword_list,
        tags=tag_list,
        price_min=price_min,
        price_max=price_max,
        owns=owns,
        wants=wants,
        unique=unique,
        sort=sort,
        order=order,
        page=page,
        limit=limit,
    )


@router.get("/tags")
async def get_tags(
    set: str | None = Query(None, description="Filter by set code"),
    format: str | None = Query(None, description="Filter by format legality"),
    colors: str | None = Query(None, description="Filter by colors (e.g. WUB)"),
    type: str | None = Query(None, description="Filter by card type"),
    rarity: str | None = Query(None, description="Filter by rarity"),
) -> list[dict]:
    """Get available oracle tags with card counts, optionally filtered."""
    from mtgsim.api.data import cards_data

    color_list = list(colors.upper()) if colors else None
    return cards_data.get_available_tags(
        set_code=set,
        format_legal=format,
        colors=color_list,
        card_type=type,
        rarity=rarity,
    )


@router.get("/keyword-frequencies")
async def get_keyword_frequencies(
    set: str | None = Query(None, description="Filter by set code"),
    sets: str | None = Query(None, description="Filter by multiple set codes (comma-separated)"),
    format: str | None = Query(None, description="Filter by format legality"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    colors: str | None = Query(None, description="Filter by colors (e.g. WUB)"),
    type: str | None = Query(None, description="Filter by card type"),
) -> dict:
    """Get keyword frequencies for filtered cards, categorized by type."""
    from mtgsim.api.data import cards_data
    from mtgsim.api.data.keywords import keywords_data

    set_code_list = [s.strip() for s in sets.split(",") if s.strip()] if sets else None
    color_list = list(colors.upper()) if colors else None
    freq = cards_data.get_keyword_frequencies(
        set_code=set,
        set_codes=set_code_list,
        format_legal=format,
        rarity=rarity,
        colors=color_list,
        card_type=type,
    )
    return keywords_data.categorize_keyword_freq(freq)


@router.get("/{uuid}", response_model=CardDetail)
async def get_card(uuid: str) -> CardDetail:
    """
    Get full card details.

    Returns complete card information with:
    - Card data (name, type, text, stats)
    - Prices from all sources
    - Format legalities
    - Deck appearances
    - Other printings
    - Collection status (owns, wants, quantities)
    """
    logger.debug(f"get_card: uuid={uuid}")
    card = await card_service.get_card(uuid)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card not found: {uuid}")
    logger.debug(f"get_card: found '{card.name}' ({card.set_code})")
    return card


@router.post("/{uuid}/collection", response_model=CollectionResponse)
async def add_card_to_collection(
    uuid: str,
    quantity_owned: int = Query(1, ge=0, description="Quantity owned (non-foil)"),
    quantity_owned_foil: int = Query(0, ge=0, description="Quantity owned (foil)"),
    quantity_wanted: int = Query(0, ge=0, description="Quantity wanted (non-foil)"),
    quantity_wanted_foil: int = Query(0, ge=0, description="Quantity wanted (foil)"),
) -> CollectionResponse:
    """
    Add a card to user's collection.

    - **uuid**: The UUID of the card to add to collection
    - **quantity_owned**: Number of non-foil copies owned
    - **quantity_owned_foil**: Number of foil copies owned
    - **quantity_wanted**: Number of non-foil copies wanted
    - **quantity_wanted_foil**: Number of foil copies wanted

    Returns success/failure status and details about the operation.
    """
    result = await card_service.add_card_to_collection(
        card_uuid=uuid,
        quantity_owned=quantity_owned,
        quantity_owned_foil=quantity_owned_foil,
        quantity_wanted=quantity_wanted,
        quantity_wanted_foil=quantity_wanted_foil,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return CollectionResponse(**result)


@router.delete("/{uuid}/collection", response_model=CollectionResponse)
async def remove_card_from_collection(uuid: str) -> CollectionResponse:
    """Remove a card from user's collection."""
    result = await card_service.remove_card_from_collection(uuid)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return CollectionResponse(**result)


@router.put("/{uuid}/rating", response_model=QuadrantRatingResponse)
async def set_quadrant_rating(uuid: str, req: QuadrantRatingRequest) -> QuadrantRatingResponse:
    """Set quadrant theory rating for a card (developing, ahead, behind, parity)."""
    from mtgsim.api.data import cards_data

    result = cards_data.set_quadrant_rating(
        card_uuid=uuid,
        developing=req.developing,
        ahead=req.ahead,
        behind=req.behind,
        parity=req.parity,
        notes=req.notes,
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Card not found: {uuid}")
    return QuadrantRatingResponse(**result)


@router.get("/{uuid}/rating", response_model=QuadrantRatingResponse)
async def get_quadrant_rating(uuid: str) -> QuadrantRatingResponse:
    """Get quadrant theory rating for a card."""
    from mtgsim.api.data import cards_data

    result = cards_data.get_quadrant_rating(uuid)
    if result is None:
        return QuadrantRatingResponse()
    return QuadrantRatingResponse(**result)
