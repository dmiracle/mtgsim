"""API router for user card tags."""

from fastapi import APIRouter, HTTPException, Query, Response

from mtgsim.api.data.user_tags import user_tags_data
from mtgsim.api.models.common import Pagination
from mtgsim.api.models.user_tag import (
    TagAssignment,
    TagAssignmentRequest,
    TagCardsResponse,
    TagDefinitionRequest,
    TagListResponse,
    TagSummary,
)

router = APIRouter(prefix="/user-tags", tags=["user-tags"])


def _pagination(page: int, limit: int, total: int) -> Pagination:
    return Pagination(page=page, limit=limit, total=total, pages=(total + limit - 1) // limit if limit else 0)


@router.get("", response_model=TagListResponse)
async def list_tags(
    q: str | None = Query(None, description="Substring filter on tag"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> TagListResponse:
    """List the user tag vocabulary with card counts and optional descriptions."""
    data, total = user_tags_data.list_tags(q=q, page=page, limit=limit)
    return TagListResponse(data=data, pagination=_pagination(page, limit, total))


@router.get("/cards", response_model=TagCardsResponse)
async def cards_for_tag(
    tag: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> TagCardsResponse:
    """List cards bearing a tag, as default-printing summaries."""
    data, total = user_tags_data.cards_for_tag(tag, page=page, limit=limit)
    return TagCardsResponse(tag=tag, data=data, pagination=_pagination(page, limit, total))


@router.post("/assignments", response_model=TagAssignment)
async def assign_tag(req: TagAssignmentRequest, response: Response) -> TagAssignment:
    """Assign a tag to a card by name. 201 on create, 200 if already assigned."""
    result = user_tags_data.assign(req.card_name, req.tag)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Card not found: {req.card_name}")
    assignment, created = result
    response.status_code = 201 if created else 200
    return TagAssignment(**assignment)


@router.delete("/assignments", status_code=204)
async def unassign_tag(card_name: str = Query(..., min_length=1), tag: str = Query(..., min_length=1)) -> None:
    if not user_tags_data.unassign(card_name, tag):
        raise HTTPException(status_code=404, detail="Assignment not found")


@router.put("/{tag}", response_model=TagSummary)
async def set_tag_definition(tag: str, req: TagDefinitionRequest) -> TagSummary:
    """Create or update the definition for a tag."""
    return TagSummary(**user_tags_data.set_definition(tag, req.description))


@router.delete("/{tag}", status_code=204)
async def delete_tag(tag: str) -> None:
    """Remove a tag entirely: its definition and all assignments."""
    if not user_tags_data.delete_tag(tag):
        raise HTTPException(status_code=404, detail=f"Tag not found: {tag}")
