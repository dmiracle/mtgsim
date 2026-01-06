"""Price API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from mtgsim.api.models.price import PriceDetail, PriceListResponse
from mtgsim.api.services.price_service import price_service

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("", response_model=PriceListResponse)
async def search_prices(
    q: str | None = Query(None, description="Search by card name"),
    set: str | None = Query(None, description="Filter by set code"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    price_min: float | None = Query(None, ge=0, description="Minimum price"),
    price_max: float | None = Query(None, ge=0, description="Maximum price"),
    sort: str = Query("average_usd", description="Sort field"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> PriceListResponse:
    """
    Search price data with filters.

    - **q**: Search card names
    - **set**: Filter by set code
    - **rarity**: Filter by rarity
    - **price_min/price_max**: Filter by price range
    - **sort**: Sort by price source (tcgplayer, cardkingdom, etc.) or average_usd
    - **order**: Sort order (asc, desc)

    Returns cards with prices from all sources and calculated average USD price.
    """
    return await price_service.search_prices(
        q=q,
        set_code=set,
        rarity=rarity,
        price_min=price_min,
        price_max=price_max,
        sort=sort,
        order=order,
        page=page,
        limit=limit,
    )


@router.get("/{uuid}", response_model=PriceDetail)
async def get_price(uuid: str) -> PriceDetail:
    """
    Get detailed price data for a card.

    Returns comprehensive price information:
    - Paper prices (TCGplayer, Card Kingdom, Cardsphere, Cardmarket)
    - MTGO prices (Cardhoarder)
    - Retail and buylist prices
    - Normal and foil variants
    - Price history (if available)
    """
    price = await price_service.get_price(uuid)
    if price is None:
        raise HTTPException(status_code=404, detail=f"Price data not found: {uuid}")
    return price
