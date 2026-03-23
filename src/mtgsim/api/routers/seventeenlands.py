"""17Lands API endpoints."""

import logging

from fastapi import APIRouter, Query

from mtgsim.api.models.seventeenlands import (
    DatasetListResponse,
    DraftPickListResponse,
    ExpansionSummary,
    GameListResponse,
    ReplayListResponse,
)
from mtgsim.api.services.seventeenlands_service import seventeenlands_service

logger = logging.getLogger("mtgsim.api.routers.seventeenlands")

router = APIRouter(prefix="/17lands", tags=["17lands"])


@router.get("/datasets", response_model=DatasetListResponse)
async def list_datasets(
    expansion: str | None = Query(None, description="Filter by expansion code"),
    format: str | None = Query(None, description="Filter by event format"),
    has_draft: bool | None = Query(None, description="Has draft data"),
    has_game: bool | None = Query(None, description="Has game data"),
    has_replay: bool | None = Query(None, description="Has replay data"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> DatasetListResponse:
    """List available 17Lands public datasets."""
    return await seventeenlands_service.list_datasets(
        expansion=expansion,
        format=format,
        has_draft=has_draft,
        has_game=has_game,
        has_replay=has_replay,
        page=page,
        limit=limit,
    )


@router.get("/expansions", response_model=list[ExpansionSummary])
async def list_expansions() -> list[ExpansionSummary]:
    """List expansions with available 17Lands data."""
    return await seventeenlands_service.list_expansions()


@router.get("/drafts", response_model=DraftPickListResponse)
async def list_draft_picks(
    expansion: str | None = Query(None, description="Filter by expansion"),
    event_type: str | None = Query(None, description="Filter by event type"),
    card_name: str | None = Query(None, description="Filter by picked card name"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> DraftPickListResponse:
    """List draft picks from ingested 17Lands data."""
    return await seventeenlands_service.list_draft_picks(
        expansion=expansion,
        event_type=event_type,
        card_name=card_name,
        page=page,
        limit=limit,
    )


@router.get("/games", response_model=GameListResponse)
async def list_games(
    expansion: str | None = Query(None, description="Filter by expansion"),
    event_type: str | None = Query(None, description="Filter by event type"),
    won: bool | None = Query(None, description="Filter by win/loss"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> GameListResponse:
    """List games from ingested 17Lands data."""
    return await seventeenlands_service.list_games(
        expansion=expansion,
        event_type=event_type,
        won=won,
        page=page,
        limit=limit,
    )


@router.get("/replays", response_model=ReplayListResponse)
async def list_replays(
    expansion: str | None = Query(None, description="Filter by expansion"),
    format: str | None = Query(None, description="Filter by format"),
    won: bool | None = Query(None, description="Filter by win/loss"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> ReplayListResponse:
    """List game replays from ingested 17Lands data."""
    return await seventeenlands_service.list_replays(
        expansion=expansion,
        format=format,
        won=won,
        page=page,
        limit=limit,
    )
