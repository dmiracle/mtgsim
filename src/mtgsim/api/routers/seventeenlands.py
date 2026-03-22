"""17Lands API endpoints."""

import logging

from fastapi import APIRouter, Query

from mtgsim.api.models.seventeenlands import (
    DatasetListResponse,
    ExpansionSummary,
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
