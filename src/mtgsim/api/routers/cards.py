"""Card API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from mtgsim.api.models.card import CardDetail, CardListResponse
from mtgsim.api.services.card_service import card_service

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("", response_model=CardListResponse)
async def search_cards(
    q: str | None = Query(None, description="Search by card name"),
    set: str | None = Query(None, description="Filter by set code"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    type: str | None = Query(None, description="Filter by card type"),
    colors: str | None = Query(None, description="Filter by color identity"),
    price_min: float | None = Query(None, ge=0, description="Minimum price"),
    price_max: float | None = Query(None, ge=0, description="Maximum price"),
    sort: str = Query("name", description="Sort field"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> CardListResponse:
    """
    Search cards with filters.

    - **q**: Search card names (minimum 2 characters recommended)
    - **set**: Filter by set code
    - **rarity**: Filter by rarity (common, uncommon, rare, mythic)
    - **type**: Filter by card type (Creature, Instant, Sorcery, etc.)
    - **colors**: Filter by color identity (e.g., "WU", "BRG")
    - **price_min/price_max**: Filter by price range
    - **sort**: Sort by name, price, mana_value
    - **order**: Sort order (asc, desc)
    """
    color_list = list(colors.upper()) if colors else None

    return await card_service.search_cards(
        q=q,
        set_code=set,
        rarity=rarity,
        card_type=type,
        colors=color_list,
        price_min=price_min,
        price_max=price_max,
        sort=sort,
        order=order,
        page=page,
        limit=limit,
    )


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
    """
    card = await card_service.get_card(uuid)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card not found: {uuid}")
    return card
