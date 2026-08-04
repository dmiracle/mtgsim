"""Pydantic models for user card tags."""

from pydantic import BaseModel, Field

from mtgsim.api.models.common import Pagination


class TagSummary(BaseModel):
    tag: str
    description: str | None = None
    card_count: int = 0


class TagListResponse(BaseModel):
    data: list[TagSummary]
    pagination: Pagination


class TagCardSummary(BaseModel):
    uuid: str | None = None
    name: str
    type_line: str | None = None
    mana_cost: str | None = None
    set_code: str | None = None
    image_url: str | None = None


class TagCardsResponse(BaseModel):
    tag: str
    data: list[TagCardSummary]
    pagination: Pagination


class TagAssignmentRequest(BaseModel):
    card_name: str = Field(min_length=1)
    tag: str = Field(min_length=1, max_length=60)


class TagAssignment(BaseModel):
    card_name: str
    tag: str


class TagDefinitionRequest(BaseModel):
    description: str = Field(min_length=1)
