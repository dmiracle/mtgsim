"""API router for user tier lists."""

from fastapi import APIRouter, HTTPException, Query, Response

from mtgsim.api.data.tier_lists import tier_lists_data
from mtgsim.api.models.common import Pagination
from mtgsim.api.models.tier_list import (
    TierEntry,
    TierEntryRequest,
    TierListCreateRequest,
    TierListDetail,
    TierListListResponse,
    TierListSummary,
    TierListUpdateRequest,
    TierReorderRequest,
    TierReorderResponse,
)

router = APIRouter(prefix="/tier-lists", tags=["tier-lists"])


@router.post("", response_model=TierListSummary, status_code=201)
async def create_tier_list(req: TierListCreateRequest) -> TierListSummary:
    return TierListSummary(**tier_lists_data.create_list(**req.model_dump()))


@router.get("", response_model=TierListListResponse)
async def list_tier_lists(
    set_code: str | None = Query(None),
    format: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> TierListListResponse:
    data, total = tier_lists_data.list_lists(set_code=set_code, format=format, page=page, limit=limit)
    pages = (total + limit - 1) // limit if limit else 0
    return TierListListResponse(data=data, pagination=Pagination(page=page, limit=limit, total=total, pages=pages))


@router.get("/{list_id}", response_model=TierListDetail)
async def get_tier_list(list_id: int) -> TierListDetail:
    result = tier_lists_data.get_list(list_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Tier list not found: {list_id}")
    return TierListDetail(**result)


@router.patch("/{list_id}", response_model=TierListSummary)
async def update_tier_list(list_id: int, req: TierListUpdateRequest) -> TierListSummary:
    result = tier_lists_data.update_list(list_id, **req.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Tier list not found: {list_id}")
    return TierListSummary(**result)


@router.delete("/{list_id}", status_code=204)
async def delete_tier_list(list_id: int) -> None:
    if not tier_lists_data.delete_list(list_id):
        raise HTTPException(status_code=404, detail=f"Tier list not found: {list_id}")


@router.put("/{list_id}/entries", response_model=TierEntry)
async def upsert_entry(list_id: int, req: TierEntryRequest, response: Response) -> TierEntry:
    """Add a card to the list, or move it (tier/position) if already present."""
    result = tier_lists_data.upsert_entry(
        list_id, card_name=req.card_name, tier=req.tier, position=req.position, note=req.note
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Tier list or card not found")
    entry, created = result
    response.status_code = 201 if created else 200
    return TierEntry(**entry)


@router.delete("/{list_id}/entries", status_code=204)
async def remove_entry(list_id: int, card_name: str = Query(..., min_length=1)) -> None:
    if not tier_lists_data.remove_entry(list_id, card_name):
        raise HTTPException(status_code=404, detail="Entry not found")


@router.post("/{list_id}/entries/reorder", response_model=TierReorderResponse)
async def reorder_tier(list_id: int, req: TierReorderRequest) -> TierReorderResponse:
    result = tier_lists_data.reorder_tier(list_id, req.tier, req.ordered_card_names)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Tier list not found: {list_id}")
    return TierReorderResponse(**result)
