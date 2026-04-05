"""Similarity search response models."""

from pydantic import BaseModel

from mtgsim.api.models.card import CardSummary


class SimilarCardResult(BaseModel):
    """A card with similarity scores."""

    card: CardSummary
    score: float
    strategy_scores: dict[str, float] = {}


class SimilarCardsResponse(BaseModel):
    """Response from the similarity search endpoint."""

    source: CardSummary
    strategies_used: list[str]
    results: list[SimilarCardResult]
    total: int


class StrategyInfo(BaseModel):
    """Metadata about an available similarity strategy."""

    name: str
    description: str
