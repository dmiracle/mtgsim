"""Common models used across the API."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Pagination(BaseModel):
    """Pagination metadata."""

    page: int = Field(ge=1, description="Current page number")
    limit: int = Field(ge=1, le=100, description="Items per page")
    total: int = Field(ge=0, description="Total number of items")
    pages: int = Field(ge=0, description="Total number of pages")


class PaginatedResponse(BaseModel, Generic[T]):
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
