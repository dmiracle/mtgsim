"""Pydantic models for pairwise card rankings."""

from pydantic import BaseModel, Field


class RankingCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    filters: dict[str, str] = {}


class RankingSummary(BaseModel):
    id: int
    name: str
    filters: dict[str, str] = {}
    comparison_count: int = 0
    created_at: str
    updated_at: str


class RankingComparison(BaseModel):
    winner_name: str
    loser_name: str


class RankingDetail(RankingSummary):
    comparisons: list[RankingComparison] = []
    excluded_names: list[str] = []


class RankingExclusionRequest(BaseModel):
    card_name: str = Field(min_length=1)


class RankingRoundRequest(BaseModel):
    ordered_card_names: list[str] = Field(min_length=2, max_length=8, description="Best first")


class RankingRoundResponse(BaseModel):
    comparisons_added: int
