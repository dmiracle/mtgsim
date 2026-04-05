"""Deck API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from mtgsim.api.models.deck import DeckDetail, DeckListResponse, DeckSummary
from mtgsim.api.services.deck_service import deck_service

logger = logging.getLogger("mtgsim.api.routers.decks")

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("", response_model=DeckListResponse)
async def list_decks(
    q: str | None = Query(None, description="Search by deck name or code"),
    format: str | None = Query(None, description="Filter by format legality"),
    set: str | None = Query(None, description="Filter by set code"),
    type: str | None = Query(None, description="Filter by deck type (60, 100)"),
    colors: str | None = Query(None, description="Filter by color identity (e.g., 'WU', 'BRG')"),
    colors_mode: str = Query(
        "subset", pattern="^(subset|exact|any)$", description="Color match: subset (default), exact, any"
    ),
    card_count_min: int | None = Query(None, ge=0, description="Minimum card count"),
    card_count_max: int | None = Query(None, ge=0, description="Maximum card count"),
    price_min: float | None = Query(None, ge=0, description="Minimum deck price"),
    price_max: float | None = Query(None, ge=0, description="Maximum deck price"),
    source: str | None = Query(None, description="Deck source (precon, user, import, test, ...)"),
    sort: str = Query("name", description="Sort field"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> DeckListResponse:
    """
    List and filter decks with pagination.

    - **q**: Search deck names and codes
    - **format**: Filter by format legality (standard, pioneer, modern, legacy, vintage, commander)
    - **set**: Filter by set code
    - **type**: Filter by deck size (60 for standard, 100 for commander)
    - **colors**: Filter by color identity (e.g., "WU" for white-blue decks)
    - **card_count_min/card_count_max**: Filter by card count range
    - **price_min/price_max**: Filter by deck price range
    - **source**: Filter by deck source (precon=preconstructed, user=user-created)
    - **sort**: Sort by name, release_date, card_count, price, colors
    - **order**: Sort order (asc, desc)
    """
    color_list = list(colors.upper()) if colors else None

    logger.debug(f"list_decks: q={q} format={format} set={set} type={type} colors={color_list} sort={sort}")
    return await deck_service.list_decks(
        q=q,
        format=format,
        set_code=set,
        deck_type=type,
        colors=color_list,
        colors_mode=colors_mode,
        card_count_min=card_count_min,
        card_count_max=card_count_max,
        price_min=price_min,
        price_max=price_max,
        source=source,
        sort=sort,
        order=order,
        page=page,
        limit=limit,
    )


@router.get("/pinned", response_model=list[DeckSummary])
async def list_pinned_decks() -> list[DeckSummary]:
    """Get all pinned decks with full summaries, in pin order."""
    return await deck_service.get_pinned_decks()


@router.post("/pinned/{file}")
async def pin_deck(file: str) -> dict:
    """Pin a deck by file identifier."""
    newly_pinned = await deck_service.pin_deck(file)
    return {"status": "pinned", "created": newly_pinned}


@router.delete("/pinned/{file:path}")
async def unpin_deck(file: str) -> dict:
    """Unpin a deck by file identifier."""
    was_pinned = await deck_service.unpin_deck(file)
    if not was_pinned:
        raise HTTPException(status_code=404, detail=f"Deck not pinned: {file}")
    return {"status": "unpinned"}


@router.get("/{file}", response_model=DeckDetail)
async def get_deck(file: str) -> DeckDetail:
    """
    Get full deck details including cards and statistics.

    Returns complete deck information with:
    - Deck metadata (name, code, release date)
    - Format legality
    - Color identity
    - Price breakdown by source
    - All cards (commander, main board, sideboard) with ownership status
    - Statistics (mana curve, type distribution, keywords)
    """
    logger.debug(f"get_deck: file={file}")
    deck = await deck_service.get_deck(file)
    if deck is None:
        raise HTTPException(status_code=404, detail=f"Deck not found: {file}")
    logger.debug(f"get_deck: found deck '{deck.meta.name}' with {len(deck.main_board)} main board cards")
    return deck


class DeckImportRequest(BaseModel):
    text: str
    name: str


class DeckCreateRequest(BaseModel):
    name: str
    description: str | None = None
    format: str | None = None


class DeckUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    format: str | None = None


class AddCardRequest(BaseModel):
    card_uuid: str
    count: int = 1
    board: str = "main"


class UserDeckResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    format: str | None = None
    source: str = "user"
    card_count: int = 0


@router.post("/import")
async def import_deck(req: DeckImportRequest) -> dict:
    """Import a deck from MTGA export format. Auto-detects format legality."""
    from mtgsim.deck_import import import_mtga_deck

    result = import_mtga_deck(text=req.text, name=req.name)
    return result.model_dump()


@router.post("/create")
async def create_deck(req: DeckCreateRequest) -> UserDeckResponse:
    """Create a new empty user deck."""
    deck = await deck_service.create_user_deck(name=req.name, description=req.description, format=req.format)
    return UserDeckResponse(**deck)


@router.get("/user/list")
async def list_user_decks() -> list[UserDeckResponse]:
    """List all user-created decks (lightweight, for deck picker)."""
    result = await deck_service.list_decks(source="user", limit=100)
    import_result = await deck_service.list_decks(source="import", limit=100)
    decks = []
    for d in result.data + import_result.data:
        fmt = None
        if d.legality:
            for f in ["standard", "pioneer", "modern", "legacy", "vintage", "commander"]:
                if getattr(d.legality, f, False):
                    fmt = f
                    break
        decks.append(
            UserDeckResponse(
                id=int(d.file) if d.file.isdigit() else 0,
                name=d.name,
                format=fmt,
                source=d.source or "user",
                card_count=d.card_count,
            )
        )
    return decks


@router.post("/{deck_id}/cards")
async def add_card_to_deck(deck_id: int, req: AddCardRequest) -> dict:
    """Add a card to a user deck."""
    result = await deck_service.add_card_to_deck(
        deck_id=deck_id,
        card_uuid=req.card_uuid,
        count=req.count,
        board=req.board,
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Deck not found: {deck_id}")
    return result


@router.delete("/{deck_id}/cards/{card_uuid}")
async def remove_card_from_deck(
    deck_id: int,
    card_uuid: str,
    board: str | None = Query(None),
) -> dict:
    """Remove a card from a user deck."""
    success = await deck_service.remove_card_from_deck(deck_id=deck_id, card_uuid=card_uuid, board=board)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found in deck")
    return {"status": "removed"}


@router.post("/{file}/duplicate", response_model=UserDeckResponse)
async def duplicate_deck(file: str) -> UserDeckResponse:
    """Duplicate any deck (user or precon) as a new user deck."""
    result = await deck_service.duplicate_deck(file)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Deck not found: {file}")
    return UserDeckResponse(**result)


@router.patch("/{deck_id}", response_model=UserDeckResponse)
async def update_deck(deck_id: int, req: DeckUpdateRequest) -> UserDeckResponse:
    """Update a user deck's metadata (name, description, format)."""
    result = await deck_service.update_user_deck(
        deck_id=deck_id, name=req.name, description=req.description, format=req.format
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Deck not found: {deck_id}")
    return UserDeckResponse(**result)


@router.delete("/{deck_id}")
async def delete_deck(deck_id: int) -> dict:
    """Delete a user deck."""
    success = await deck_service.delete_user_deck(deck_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Deck not found: {deck_id}")
    return {"status": "deleted"}


@router.get("/{file}/raw")
async def get_deck_raw(file: str) -> dict:
    """Get raw deck JSON for developer inspection."""
    data = await deck_service.get_deck_raw(file)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Deck not found: {file}")
    return data
