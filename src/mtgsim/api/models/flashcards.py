"""Flashcard Pydantic request/response models."""

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    user_id: str
    card_type: str  # keyword_definition, card_oracle, card_mana_cost, card_stats
    set_code: str | None = None
    rarity: str | None = None
    collection_name: str | None = None


class GenerateResponse(BaseModel):
    created: int
    collection: str


class FlashcardQuestion(BaseModel):
    flashcard_id: int
    question: dict
    answer: dict | None = None
    collection: str | None = None


class ReviewRequest(BaseModel):
    user_id: str
    flashcard_id: int
    rating: int = Field(ge=0, le=5)
    response_time_ms: int = Field(ge=0)


class ReviewResponse(BaseModel):
    next_review_at: str | None = None
    interval: int
    ease_factor: float


class CollectionInfo(BaseModel):
    id: int
    name: str
    card_count: int


class MergeCollectionsRequest(BaseModel):
    user_id: str
    collection_ids: list[int] = Field(min_length=1)
    name: str
    delete_originals: bool = False


class MergeCollectionsResponse(BaseModel):
    collection: CollectionInfo
    merged_from: int
    delete_originals: bool


class DeleteCollectionResponse(BaseModel):
    deleted: bool
    collection: str
    cards_removed: int


class StudyStats(BaseModel):
    total_cards: int
    cards_due: int
    cards_new: int
    reviews_today: int
    collections: list[CollectionInfo]
