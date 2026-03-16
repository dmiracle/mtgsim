"""Booster pack API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Query

from mtgsim.booster import BoosterPack, generate_booster

logger = logging.getLogger("mtgsim.api.routers.boosters")

router = APIRouter(prefix="/boosters", tags=["boosters"])


@router.get("/{set_code}", response_model=BoosterPack)
async def open_booster(
    set_code: str,
    type: str | None = Query(None, pattern="^(play|draft)$", description="Booster type (auto-detects if omitted)"),
) -> BoosterPack:
    """Generate a random booster pack from a set.

    Uses Play Booster rules for 2024+ sets, Draft Booster for older sets.
    """
    try:
        return generate_booster(set_code.upper(), booster_type=type)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{set_code}/batch")
async def open_boosters(
    set_code: str,
    count: int = Query(6, ge=1, le=36, description="Number of packs to open"),
    type: str | None = Query(None, pattern="^(play|draft)$", description="Booster type"),
) -> list[BoosterPack]:
    """Generate multiple booster packs from a set (e.g., for sealed/draft)."""
    try:
        return [generate_booster(set_code.upper(), booster_type=type) for _ in range(count)]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
