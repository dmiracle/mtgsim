"""Price API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Query

from mtgsim.api.models.price import PriceDetail, PriceListResponse
from mtgsim.api.services.price_service import price_service

logger = logging.getLogger("mtgsim.api.routers.prices")

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
    """Search price data with filters."""
    logger.debug(f"search_prices: q={q} set={set} rarity={rarity} range=[{price_min},{price_max}] sort={sort}")
    result = await price_service.search_prices(
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
    logger.debug(f"search_prices: returning {len(result.data)} results, total={result.pagination.total}")
    return result


@router.get("/{uuid}", response_model=PriceDetail)
async def get_price(uuid: str) -> PriceDetail:
    """Get detailed price data for a card."""
    logger.debug(f"get_price: uuid={uuid}")
    price = await price_service.get_price(uuid)
    if price is None:
        raise HTTPException(status_code=404, detail=f"Price data not found: {uuid}")
    return price
