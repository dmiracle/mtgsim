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


@router.get("", response_model=CardListResponse)
async def search_cards(
    q: str | None = Query(None, description="Search by card name"),
    set: str | None = Query(None, description="Filter by set code"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    type: str | None = Query(None, description="Filter by card type"),
    colors: str | None = Query(None, description="Filter by color identity"),
    price_min: float | None = Query(None, ge=0, description="Minimum price"),
    price_max: float | None = Query(None, ge=0, description="Maximum price"),
    owns: bool | None = Query(None, description="Filter by ownership (true=owned, false=not owned)"),
    wants: bool | None = Query(None, description="Filter by want status (true=wanted, false=not wanted)"),
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
    - **owns**: Filter by ownership (true=owned only, false=not owned only)
    - **wants**: Filter by want status (true=wanted only, false=not wanted only)
    - **sort**: Sort by name, price, mana_value
    - **order**: Sort order (asc, desc)
    """
    color_list = list(colors.upper()) if colors else None

    logger.debug(f"search_cards: q={q} set={set} rarity={rarity} type={type} colors={color_list}")
    return await card_service.search_cards(
        q=q,
        set_code=set,
        rarity=rarity,
        card_type=type,
        colors=color_list,
        price_min=price_min,
        price_max=price_max,
        owns=owns,
        wants=wants,
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
    """
    Remove a card from user's collection.

    - **uuid**: The UUID of the card to remove from collection

    Returns success/failure status and details about the operation.
    """
    result = await card_service.remove_card_from_collection(uuid)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return CollectionResponse(**result)
