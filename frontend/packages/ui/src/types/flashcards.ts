// Flashcard API types from flashcard-backend-definition.md

export type GenerateRequest = {
  user_id: string;
  card_type: "keyword_definition" | "card_oracle" | "card_mana_cost" | "card_stats" | "card_rarity" | "card_recall";
  set_code?: string;
  rarity?: string;
  collection_name?: string;
};

export type GenerateResponse = {
  created: number;
  collection: string;
};

export type KeywordQuestion = {
  card_type: "keyword_definition";
  keyword: string;
  keyword_type: string;
};

export type CardOracleQuestion = {
  card_type: "card_oracle";
  card_name: string;
  set_code: string;
  image_url: string | null;
};

export type CardManaCostQuestion = {
  card_type: "card_mana_cost";
  card_name: string;
  oracle_text: string;
  type_line: string;
};

export type CardStatsQuestion = {
  card_type: "card_stats";
  card_name: string;
  oracle_text: string;
  type_line: string;
};

export type CardRecallQuestion = {
  card_type: "card_recall";
  card_name: string;
  uuid: string;
  set_code: string;
  image_url: string | null;
};

export type FlashcardQuestionData =
  | KeywordQuestion
  | CardOracleQuestion
  | CardManaCostQuestion
  | CardStatsQuestion
  | CardRecallQuestion;

export type FlashcardAnswer = {
  definition?: string;
  oracle_text?: string;
  mana_cost?: string;
  mana_value?: number;
  type_line?: string;
  power?: string;
  toughness?: string;
  rarity?: string;
  image_url?: string;
};

export type FlashcardQuestion = {
  flashcard_id: number;
  question: FlashcardQuestionData;
  answer?: FlashcardAnswer | null;
  collection: string | null;
};

export type AspectRating = "green" | "yellow" | "red";

export type ReviewRequest = {
  user_id: string;
  flashcard_id: number;
  rating?: number;
  aspect_ratings?: Record<string, AspectRating>;
  response_time_ms: number;
};

export type ReviewResponse = {
  next_review_at: string | null;
  interval: number;
  ease_factor: number;
};

export type CollectionInfo = {
  id: number;
  name: string;
  card_count: number;
};

// Analytics types

export type ReviewHistoryEntry = {
  date: string;
  reviews: number;
  average_rating: number | null;
  average_response_ms: number | null;
  new_cards_learned: number;
};

export type ReviewHistory = {
  buckets: ReviewHistoryEntry[];
  granularity: "hourly" | "daily";
  days: number;
};

export type CardDifficultyItem = {
  flashcard_id: number;
  question: Record<string, unknown>;
  ease_factor: number;
  interval: number;
  repetitions: number;
  total_reviews: number;
};

export type CardDifficulty = {
  hardest: CardDifficultyItem[];
  easiest: CardDifficultyItem[];
};

export type CollectionAnalytics = {
  id: number;
  name: string;
  card_count: number;
  cards_reviewed: number;
  completion_pct: number;
  win_rate: number;
  average_ease: number;
  cards_due: number;
};

export type SessionAnalytics = {
  total_study_time_ms: number;
  avg_cards_per_minute: number;
  accuracy_by_card_type: Record<string, number>;
};

export type RetentionBucket = {
  interval_label: string;
  total_reviews: number;
  passed: number;
  pass_rate: number;
};

export type RetentionAnalytics = {
  buckets: RetentionBucket[];
};

export type KeywordAnalyticsItem = {
  keyword: string;
  ease_factor: number;
  total_reviews: number;
  pass_rate: number;
};

export type KeywordAnalytics = {
  hardest: KeywordAnalyticsItem[];
  easiest: KeywordAnalyticsItem[];
};

export type StudyStats = {
  total_cards: number;
  cards_due: number;
  cards_new: number;
  reviews_today: number;
  collections: CollectionInfo[];
  // Extended SRS metrics (optional — backend may not return these yet)
  cards_learning?: number;
  cards_young?: number;
  cards_mature?: number;
  average_ease?: number;
  total_reviews?: number;
  streak_days?: number;
  due_tomorrow?: number;
  due_this_week?: number;
};
