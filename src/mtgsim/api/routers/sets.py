"""Set API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from mtgsim.api.models.set import SetDetail, SetListResponse
from mtgsim.api.services.set_service import set_service

router = APIRouter(prefix="/sets", tags=["sets"])


@router.get("", response_model=SetListResponse)
async def list_sets(
    q: str | None = Query(None, description="Search by set name or code"),
    type: str | None = Query(None, description="Filter by set type"),
    block: str | None = Query(None, description="Filter by block name"),
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
    - **sort**: Sort by name, release_date, size
    - **order**: Sort order (asc, desc)
    """
    return await set_service.list_sets(
        q=q,
        set_type=type,
        block=block,
        sort=sort,
        order=order,
        page=page,
        limit=limit,
    )


@router.get("/{code}", response_model=SetDetail)
async def get_set(
    code: str,
    rarity: str | None = Query(None, description="Filter cards by rarity"),
    color: str | None = Query(None, description="Filter cards by color"),
    type: str | None = Query(None, description="Filter cards by type"),
    card_page: int = Query(1, ge=1, description="Card page number"),
    card_limit: int = Query(50, ge=1, le=100, description="Cards per page"),
) -> SetDetail:
    """
    Get full set details including cards and statistics.

    Returns complete set information with:
    - Set metadata (name, code, type, release date, sizes)
    - Statistics (rarity breakdown, prices, keywords, word frequencies)
    - Paginated card list (filterable by rarity, color, type)
    """
    set_data = await set_service.get_set(
        code=code,
        rarity=rarity,
        color=color,
        card_type=type,
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

    Returns the original MTGJSON set file format.
    """
    data = await set_service.get_set_raw(code)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Set not found: {code}")
    return data
