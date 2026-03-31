"""API router for card interactions."""

from fastapi import APIRouter, HTTPException, Query

from mtgsim.api.models.interaction import (
    InteractionCreateRequest,
    InteractionDetail,
    InteractionGraphResponse,
    InteractionListResponse,
    InteractionUpdateRequest,
)
from mtgsim.api.services.interaction_service import interaction_service

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("", response_model=InteractionDetail, status_code=201)
async def create_interaction(req: InteractionCreateRequest) -> InteractionDetail:
    if req.source_card_uuid == req.target_card_uuid:
        raise HTTPException(status_code=400, detail="source and target card must be different")
    result = await interaction_service.create_interaction(req)
    if not result:
        raise HTTPException(status_code=404, detail="one or both card UUIDs not found")
    return result


@router.get("", response_model=InteractionListResponse)
async def list_interactions(
    card_uuid: str | None = Query(None, description="Filter by card UUID"),
    type: str | None = Query(None, description="Filter by interaction type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> InteractionListResponse:
    return await interaction_service.list_interactions(
        card_uuid=card_uuid,
        interaction_type=type,
        page=page,
        limit=limit,
    )


@router.get("/graph/{card_uuid}", response_model=InteractionGraphResponse)
async def get_interaction_graph(
    card_uuid: str,
    depth: int = Query(1, ge=1, le=3, description="Traversal depth (max 3)"),
) -> InteractionGraphResponse:
    result = await interaction_service.get_interaction_graph(card_uuid, depth)
    if not result:
        raise HTTPException(status_code=404, detail="Card not found")
    return result


@router.get("/{interaction_id}", response_model=InteractionDetail)
async def get_interaction(interaction_id: int) -> InteractionDetail:
    result = await interaction_service.get_interaction(interaction_id)
    if not result:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return result


@router.put("/{interaction_id}", response_model=InteractionDetail)
async def update_interaction(interaction_id: int, req: InteractionUpdateRequest) -> InteractionDetail:
    result = await interaction_service.update_interaction(interaction_id, req)
    if not result:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return result


@router.delete("/{interaction_id}", status_code=204)
async def delete_interaction(interaction_id: int) -> None:
    deleted = await interaction_service.delete_interaction(interaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Interaction not found")
