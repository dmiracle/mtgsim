"""Pydantic models for situational card evaluations."""

from pydantic import BaseModel, Field

Stars = int | None


class EvaluationSetCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    set_code: str | None = None


class EvaluationSetSummary(BaseModel):
    id: int
    name: str
    set_code: str | None = None
    entry_count: int = 0
    created_at: str
    updated_at: str


class CardEvaluation(BaseModel):
    """Stars (1-5) for how good the card is when developing, at parity, behind, and ahead; null = not rated."""

    card_name: str
    developing: Stars = Field(None, ge=1, le=5)
    parity: Stars = Field(None, ge=1, le=5)
    behind: Stars = Field(None, ge=1, le=5)
    ahead: Stars = Field(None, ge=1, le=5)


class EvaluationSetDetail(EvaluationSetSummary):
    entries: list[CardEvaluation] = []
