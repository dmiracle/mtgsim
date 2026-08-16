"""Pydantic models for user tier lists."""

from typing import Literal

from pydantic import BaseModel, Field

from mtgsim.api.models.common import Pagination
from mtgsim.api.models.user_tag import TagCardSummary

Tier = Literal["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"]


class TierListCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    set_code: str | None = Field(default=None, max_length=8)
    format: str | None = Field(default=None, max_length=40)


class TierListUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    set_code: str | None = Field(default=None, max_length=8)
    format: str | None = Field(default=None, max_length=40)


class TierListSummary(BaseModel):
    id: int
    name: str
    description: str | None = None
    set_code: str | None = None
    format: str | None = None
    extra: dict = {}
    entry_count: int = 0
    created_at: str
    updated_at: str


class TierListListResponse(BaseModel):
    data: list[TierListSummary]
    pagination: Pagination


class TierEntryRequest(BaseModel):
    card_name: str = Field(min_length=1)
    tier: Tier
    position: int | None = Field(default=None, ge=0)
    note: str | None = None


class TierEntry(BaseModel):
    id: int
    card_name: str
    tier: str
    position: int
    note: str | None = None
    card: TagCardSummary | None = None


class TierListDetail(TierListSummary):
    entries: list[TierEntry] = []


class TierReorderRequest(BaseModel):
    tier: Tier
    ordered_card_names: list[str] = Field(min_length=1)


class TierReorderResponse(BaseModel):
    tier: str
    card_names: list[str]
