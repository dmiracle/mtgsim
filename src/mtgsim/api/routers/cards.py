"""Card API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from mtgsim.api.models.card import CardDetail, CardListResponse
from mtgsim.api.services.card_service import card_service

router = APIRouter(prefix="/cards", tags=["cards"])


class CollectionResponse(BaseModel):
    """Response for collection management operations."""
    success: bool
    message: str
    card: dict | None = None


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
    scope: str = Query("user", pattern="^(user|reference|combined)$", description="Search scope"),
) -> CardListResponse:
    """
    Search cards with filters and scope control.

    - **q**: Search card names (minimum 2 characters recommended)
    - **set**: Filter by set code
    - **rarity**: Filter by rarity (common, uncommon, rare, mythic)
    - **type**: Filter by card type (Creature, Instant, Sorcery, etc.)
    - **colors**: Filter by color identity (e.g., "WU", "BRG")
    - **price_min/price_max**: Filter by price range
    - **sort**: Sort by name, price, mana_value
    - **order**: Sort order (asc, desc)
    - **scope**: Search scope (user=collection only, reference=all available, combined=both)
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
        scope=scope,
    )


@router.get("/{uuid}", response_model=CardDetail)
async def get_card(
    uuid: str,
    scope: str = Query("user", pattern="^(user|reference|combined)$", description="Search scope"),
) -> CardDetail:
    """
    Get full card details with scope control.

    Returns complete card information with:
    - Card data (name, type, text, stats)
    - Prices from all sources (if in collection)
    - Format legalities
    - Deck appearances
    - Other printings
    
    - **scope**: Search scope (user=collection only, reference=all available, combined=both)
    """
    card = await card_service.get_card(uuid, scope=scope)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card not found: {uuid}")
    return card


@router.post("/{uuid}/collection", response_model=CollectionResponse)
async def add_card_to_collection(uuid: str) -> CollectionResponse:
    """
    Add a card from reference tables to user's collection.
    
    This endpoint allows users to add cards from the complete MTGJSON reference
    database to their personal collection in the domain database.
    
    - **uuid**: The UUID of the card to add to collection
    
    Returns success/failure status and details about the operation.
    """
    result = await card_service.add_card_to_collection(uuid)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return CollectionResponse(**result)


@router.delete("/{uuid}/collection", response_model=CollectionResponse)
async def remove_card_from_collection(uuid: str) -> CollectionResponse:
    """
    Remove a card from user's collection.
    
    This endpoint removes a card from the user's personal collection in the
    domain database. The card will still be available in reference tables.
    
    - **uuid**: The UUID of the card to remove from collection
    
    Returns success/failure status and details about the operation.
    """
    result = await card_service.remove_card_from_collection(uuid)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return CollectionResponse(**result)
