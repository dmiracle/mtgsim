"""API router for pairwise card rankings."""

from fastapi import APIRouter, HTTPException, Query

from mtgsim.api.data.rankings import rankings_data
from mtgsim.api.models.ranking import (
    RankingCreateRequest,
    RankingDetail,
    RankingExclusionRequest,
    RankingRoundRequest,
    RankingRoundResponse,
    RankingSummary,
)

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.post("", response_model=RankingSummary, status_code=201)
async def create_ranking(req: RankingCreateRequest) -> RankingSummary:
    return RankingSummary(**rankings_data.create_ranking(req.name, req.filters))


@router.get("", response_model=list[RankingSummary])
async def list_rankings() -> list[RankingSummary]:
    return [RankingSummary(**r) for r in rankings_data.list_rankings()]


@router.get("/{ranking_id}", response_model=RankingDetail)
async def get_ranking(ranking_id: int) -> RankingDetail:
    result = rankings_data.get_ranking(ranking_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Ranking not found: {ranking_id}")
    return RankingDetail(**result)


@router.post("/{ranking_id}/rounds", response_model=RankingRoundResponse)
async def add_round(ranking_id: int, req: RankingRoundRequest) -> RankingRoundResponse:
    """Record a ranked round (best first) as pairwise comparisons."""
    if len(set(req.ordered_card_names)) != len(req.ordered_card_names):
        raise HTTPException(status_code=422, detail="Card names in a round must be distinct")
    added = rankings_data.add_round(ranking_id, req.ordered_card_names)
    if added is None:
        raise HTTPException(status_code=404, detail=f"Ranking not found: {ranking_id}")
    return RankingRoundResponse(comparisons_added=added)


@router.post("/{ranking_id}/exclusions", status_code=204)
async def exclude_card(ranking_id: int, req: RankingExclusionRequest) -> None:
    """Leave a card out of the ranking: it no longer appears in rounds or results."""
    if rankings_data.exclude_card(ranking_id, req.card_name) is None:
        raise HTTPException(status_code=404, detail=f"Ranking not found: {ranking_id}")


@router.delete("/{ranking_id}/exclusions", status_code=204)
async def restore_card(ranking_id: int, card_name: str = Query(...)) -> None:
    if not rankings_data.restore_card(ranking_id, card_name):
        raise HTTPException(status_code=404, detail=f"Card not excluded from ranking {ranking_id}: {card_name}")


@router.delete("/{ranking_id}", status_code=204)
async def delete_ranking(ranking_id: int) -> None:
    if not rankings_data.delete_ranking(ranking_id):
        raise HTTPException(status_code=404, detail=f"Ranking not found: {ranking_id}")
