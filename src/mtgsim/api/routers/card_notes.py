"""API router for user card notes."""

from fastapi import APIRouter, HTTPException, Query

from mtgsim.api.data.card_notes import card_notes_data
from mtgsim.api.models.card_note import (
    CardNoteCreateRequest,
    CardNoteDetail,
    CardNoteListResponse,
    CardNoteUpdateRequest,
)
from mtgsim.api.models.common import Pagination

router = APIRouter(prefix="/card-notes", tags=["card-notes"])


@router.post("", response_model=CardNoteDetail, status_code=201)
async def create_note(req: CardNoteCreateRequest) -> CardNoteDetail:
    result = card_notes_data.create_note(
        card_name=req.card_name, body=req.body, kind=req.kind, title=req.title, extra=req.extra
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Card not found: {req.card_name}")
    return CardNoteDetail(**result)


@router.get("", response_model=CardNoteListResponse)
async def list_notes(
    card_name: str | None = Query(None),
    kind: str | None = Query(None),
    q: str | None = Query(None, description="Substring search over title and body"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> CardNoteListResponse:
    data, total = card_notes_data.list_notes(card_name=card_name, kind=kind, q=q, page=page, limit=limit)
    pages = (total + limit - 1) // limit if limit else 0
    return CardNoteListResponse(data=data, pagination=Pagination(page=page, limit=limit, total=total, pages=pages))


@router.get("/{note_id}", response_model=CardNoteDetail)
async def get_note(note_id: int) -> CardNoteDetail:
    result = card_notes_data.get_note(note_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Note not found: {note_id}")
    return CardNoteDetail(**result)


@router.patch("/{note_id}", response_model=CardNoteDetail)
async def update_note(note_id: int, req: CardNoteUpdateRequest) -> CardNoteDetail:
    result = card_notes_data.update_note(note_id, **req.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Note not found: {note_id}")
    return CardNoteDetail(**result)


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: int) -> None:
    if not card_notes_data.delete_note(note_id):
        raise HTTPException(status_code=404, detail=f"Note not found: {note_id}")
