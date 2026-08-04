"""Pydantic models for user card notes."""

from pydantic import BaseModel, Field

from mtgsim.api.models.common import Pagination


class CardNoteCreateRequest(BaseModel):
    card_name: str = Field(min_length=1)
    body: str = Field(min_length=1)
    kind: str = Field(default="note", max_length=40)
    title: str | None = None
    extra: dict = {}


class CardNoteUpdateRequest(BaseModel):
    body: str | None = Field(default=None, min_length=1)
    kind: str | None = Field(default=None, max_length=40)
    title: str | None = None
    extra: dict | None = None


class CardNoteDetail(BaseModel):
    id: int
    card_name: str
    kind: str
    title: str | None = None
    body: str
    extra: dict = {}
    created_at: str
    updated_at: str


class CardNoteListResponse(BaseModel):
    data: list[CardNoteDetail]
    pagination: Pagination
