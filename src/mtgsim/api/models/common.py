"""Common models used across the API."""

from typing import TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Pagination(BaseModel):
    """Pagination metadata."""

    page: int = Field(ge=1, description="Current page number")
    limit: int = Field(ge=1, le=100, description="Items per page")
    total: int = Field(ge=0, description="Total number of items")
    pages: int = Field(ge=0, description="Total number of pages")


class PaginatedResponse[T](BaseModel):
    """Generic paginated response wrapper."""

    data: list[T]
    pagination: Pagination


class ErrorDetail(BaseModel):
    """Error detail information."""

    code: str
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: ErrorDetail


class HistogramBucket(BaseModel):
    """Single bucket in a histogram."""

    range: str
    count: int


class WordFrequency(BaseModel):
    """Word frequency for word clouds."""

    word: str
    count: int


class KeywordCounts(BaseModel):
    """Keyword frequency counts by category."""

    ability_words: dict[str, int] = Field(default_factory=dict)
    keyword_abilities: dict[str, int] = Field(default_factory=dict)
    keyword_actions: dict[str, int] = Field(default_factory=dict)


class CollectionStatus(BaseModel):
    """User's collection status for an item."""

    owns: bool = False
    wants: bool = False
    total_owned: int = 0
    total_wanted: int = 0


class CollectionDetail(BaseModel):
    """Detailed collection quantities."""

    quantity_owned: int = 0
    quantity_owned_foil: int = 0
    quantity_wanted: int = 0
    quantity_wanted_foil: int = 0
    condition: str | None = None
    notes: str | None = None
