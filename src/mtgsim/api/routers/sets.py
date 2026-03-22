"""Set API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Query

from mtgsim.api.models.set import SetDetail, SetListResponse
from mtgsim.api.services.set_service import set_service

logger = logging.getLogger("mtgsim.api.routers.sets")

router = APIRouter(prefix="/sets", tags=["sets"])


@router.get("", response_model=SetListResponse)
async def list_sets(
    q: str | None = Query(None, description="Search by set name or code"),
    type: str | None = Query(None, description="Filter by set type"),
    block: str | None = Query(None, description="Filter by block name"),
    has_owned_cards: bool | None = Query(None, description="Filter to sets with owned cards"),
    sort: str = Query("release_date", description="Sort field"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> SetListResponse:
    """
    List and filter sets with pagination.

    - **q**: Search set names and codes
    - **type**: Filter by set type (core, expansion, masters, commander, etc.)
    - **block**: Filter by block name
    - **has_owned_cards**: Filter to sets with owned cards (true) or without (false)
    - **sort**: Sort by name, release_date, size
    - **order**: Sort order (asc, desc)
    """
    logger.debug(f"list_sets: q={q} type={type} block={block} sort={sort} order={order} page={page} limit={limit}")
    return await set_service.list_sets(
        q=q,
        set_type=type,
        block=block,
        has_owned_cards=has_owned_cards,
        sort=sort,
        order=order,
        page=page,
        limit=limit,
    )


@router.get("/{code}", response_model=SetDetail)
async def get_set(
    code: str,
    rarity: str | None = Query(None, description="Filter cards by rarity"),
    colors: str | None = Query(None, description="Filter cards by colors (e.g. WUB)"),
    type: str | None = Query(None, description="Filter cards by type"),
    text: str | None = Query(None, description="Filter cards by oracle text"),
    tags: str | None = Query(None, description="Filter by oracle tags (comma-separated)"),
    owns: bool | None = Query(None, description="Filter by ownership (true=owned, false=not owned)"),
    wants: bool | None = Query(None, description="Filter by want status"),
    format: str | None = Query(None, description="Filter by format legality (standard, modern, pauper, etc.)"),
    sort: str = Query("number", description="Sort field (name, number, mana_value, rarity, price)"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    unique: bool = Query(False, description="Show only one printing per card name"),
    price_mode: str = Query("min", pattern="^(min|max)$", description="Price mode: min (cheapest) or max"),
    card_page: int = Query(1, ge=1, description="Card page number"),
    card_limit: int = Query(50, ge=1, le=100, description="Cards per page"),
) -> SetDetail:
    """
    Get full set details including cards and statistics.

    Returns complete set information with:
    - Set metadata (name, code, type, release date, sizes)
    - Statistics (rarity breakdown, keywords)
    - Paginated card list (filterable by rarity, color, type, ownership)
    """
    color_list = list(colors.upper()) if colors else None
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    logger.debug(f"get_set: code={code} rarity={rarity} colors={color_list} type={type} sort={sort}")
    set_data = await set_service.get_set(
        code=code,
        rarity=rarity,
        colors=color_list,
        card_type=type,
        text=text,
        tags=tag_list,
        owns=owns,
        wants=wants,
        format_legal=format,
        sort=sort,
        order=order,
        unique=unique,
        price_mode=price_mode,
        card_page=card_page,
        card_limit=card_limit,
    )
    if set_data is None:
        raise HTTPException(status_code=404, detail=f"Set not found: {code}")
    return set_data


@router.get("/{code}/raw")
async def get_set_raw(code: str) -> dict:
    """
    Get raw set JSON for developer inspection.

    Returns the set data in raw format.
    """
    data = await set_service.get_set_raw(code)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Set not found: {code}")
    return data
