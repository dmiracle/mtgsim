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


# =============================================================================
# Analytics models
# =============================================================================


class ReviewBucket(BaseModel):
    date: str
    reviews: int
    average_rating: float | None = None
    average_response_ms: int | None = None
    new_cards_learned: int = 0


# Keep old name as alias for backwards compat
DailyReviewStats = ReviewBucket


class ReviewHistoryResponse(BaseModel):
    buckets: list[ReviewBucket]
    granularity: str
    days: int


class CardDifficulty(BaseModel):
    flashcard_id: int
    question: dict
    ease_factor: float
    interval: int
    repetitions: int
    total_reviews: int


class CardDifficultyResponse(BaseModel):
    hardest: list[CardDifficulty]
    easiest: list[CardDifficulty]
    most_reviewed: list[CardDifficulty]


class CollectionBreakdown(BaseModel):
    id: int
    name: str
    card_count: int
    cards_reviewed: int
    completion_pct: float
    win_rate: float | None = None
    average_ease: float | None = None
    cards_due: int = 0


class SessionAnalytics(BaseModel):
    total_study_time_ms: int
    avg_cards_per_minute: float | None = None
    accuracy_by_card_type: dict[str, float]


class RetentionBucket(BaseModel):
    interval_label: str
    total_reviews: int
    passed: int
    pass_rate: float


class RetentionCurveResponse(BaseModel):
    buckets: list[RetentionBucket]


class KeywordInsight(BaseModel):
    keyword: str
    ease_factor: float
    total_reviews: int
    pass_rate: float


class KeywordInsightsResponse(BaseModel):
    hardest: list[KeywordInsight]
    easiest: list[KeywordInsight]


class StudyStats(BaseModel):
    total_cards: int
    cards_due: int
    cards_new: int
    reviews_today: int
    collections: list[CollectionInfo]
    # Mastery distribution
    cards_learning: int = 0
    cards_young: int = 0
    cards_mature: int = 0
    # Performance
    average_ease: float = 2.5
    total_reviews: int = 0
    streak_days: int = 0
    # Forecast
    due_tomorrow: int = 0
    due_this_week: int = 0
