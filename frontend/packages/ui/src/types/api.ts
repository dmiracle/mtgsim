// API response types derived from backend-definition.md

// --- Pagination ---

export type Pagination = {
  page: number;
  limit: number;
  total: number;
  pages: number;
};

// --- Decks ---

export type DeckSummary = {
  uuid: string;
  file: string;
  name: string;
  code: string;
  deck_type: string;
  card_count: number;
  colors: string[];
  price: number;
  release_date: string;
  legality: Record<string, boolean>;
  source: string;
};

export type DeckListResponse = {
  data: DeckSummary[];
  pagination: Pagination;
  filters: {
    sets: string[];
    formats: string[];
    color_combinations: string[];
  };
};

export type DeckCard = {
  uuid: string;
  name: string;
  count: number;
  board: string;
  mana_cost: string;
  mana_value: number;
  type: string;
  types: string[];
  colors: string[];
  rarity: string;
  tags: string[];
  text: string;
  price: number;
  image_url: string | null;
  owns_enough: boolean;
  owned_count: number;
  missing_count: number;
};

export type DeckStats = {
  total_cards: number;
  unique_cards: number;
  mana_curve: Record<string, number>;
  type_distribution: Record<string, number>;
  rarity_distribution: Record<string, number>;
  color_distribution: Record<string, number>;
  price_histogram: { range: string; count: number }[];
  keywords: {
    ability_words: Record<string, number>;
    keyword_abilities: Record<string, number>;
    keyword_actions: Record<string, number>;
  };
};

export type DeckDetail = {
  meta: {
    uuid: string;
    name: string;
    file: string;
    code: string;
    release_date: string;
    description: string | null;
    format: string | null;
    source: string;
  };
  legality: Record<string, boolean>;
  colors: string[];
  price: {
    total: number;
    tcgplayer: number;
    cardkingdom: number;
    cardsphere: number;
    cardmarket: number;
    mtgo: number;
  };
  commander: DeckCard[];
  main_board: DeckCard[];
  side_board: DeckCard[];
  stats: DeckStats;
};

export type UserDeckResponse = {
  uuid: string;
  id: number;
  name: string;
  description: string | null;
  format: string | null;
  source: string;
  card_count: number;
};

export type DeckImportResult = {
  deck_id: string;
  deck_name: string;
  total_cards: number;
  resolved: {
    name: string;
    matched_name: string;
    match_type: "exact" | "fuzzy" | "created";
    match_score: number;
    count: number;
  }[];
  legality: { format: string; legal: boolean; reason: string }[];
};

// --- Cards ---

export type CardSummary = {
  uuid: string;
  name: string;
  type: string;
  mana_cost: string;
  mana_value: number;
  rarity: string;
  set_code: string;
  /** Card colors (gold/hybrid both list all colors); absent on endpoints that don't serve it */
  colors?: string[];
  color_identity: string[];
  tags: string[];
  text: string;
  price: number;
  image_url: string | null;
  owns: boolean;
  wants: boolean;
  total_owned: number;
  total_wanted: number;
};

export type CardListResponse = {
  data: CardSummary[];
  pagination: Pagination;
};

export type CardPrice = {
  provider: string;
  finish: string;
  listing_type: string;
  price: number;
};

export type DeckCardPrinting = {
  uuid: string;
  set_code: string;
  set_name: string;
  number: string;
  language: string | null;
  is_default_printing: boolean;
  image_url: string | null;
};

export type CardPrinting = {
  set_code: string;
  set_name: string;
  uuid: string;
  rarity: string;
  number: string;
  image_url: string | null;
  owns: boolean;
  total_owned: number;
  price?: number;
};

export type CardCollection = {
  quantity_owned: number;
  quantity_owned_foil: number;
  quantity_owned_mtga: number;
  quantity_owned_mtga_foil: number;
  quantity_wanted: number;
  quantity_wanted_foil: number;
  condition: string | null;
  notes: string | null;
};

export type MtgaImportResult = {
  matched: number;
  created: number;
  updated: number;
  unmatched: string[];
};

export type QuadrantRating = {
  developing: number | null;
  ahead: number | null;
  behind: number | null;
  parity: number | null;
  notes: string | null;
};

export type CardDetail = {
  uuid: string;
  name: string;
  mana_cost: string;
  mana_value: number;
  type: string;
  types: string[];
  subtypes: string[];
  supertypes: string[];
  text: string;
  flavor_text: string | null;
  rarity: string;
  set_code: string;
  set_name: string;
  color_identity: string[];
  colors: string[];
  keywords: string[];
  tags: string[];
  power: string | null;
  toughness: string | null;
  loyalty: string | null;
  defense: string | null;
  artist: string;
  number: string;
  layout: string;
  finishes: string[];
  border_color: string;
  frame_version: string;
  is_reprint: boolean;
  is_reserved: boolean;
  is_promo: boolean;
  image_url: string | null;
  legalities: Record<string, string>;
  all_prices: CardPrice[];
  appears_in_decks: { file: string; name: string; count: number }[];
  other_printings: CardPrinting[];
  owns: boolean;
  wants: boolean;
  total_owned: number;
  total_wanted: number;
  collection: CardCollection | null;
  quadrant_rating: QuadrantRating | null;
};

export type TagCount = {
  tag: string;
  count: number;
};

export type KeywordFrequencies = {
  keyword_abilities: Record<string, number>;
  keyword_actions: Record<string, number>;
  ability_words: Record<string, number>;
};

// --- Sets ---

export type SetSummary = {
  code: string;
  name: string;
  type: string;
  release_date: string;
  base_set_size: number;
  total_set_size: number;
  block: string | null;
  keyrune_code: string;
  collection_stats: Record<string, number> | null;
};

export type SetListResponse = {
  data: SetSummary[];
  pagination: Pagination;
  filters: {
    types: string[];
    blocks: string[];
  };
};

export type SetCard = {
  uuid: string;
  name: string;
  mana_cost: string;
  mana_value: number;
  type: string;
  rarity: string;
  color_identity: string[];
  colors: string[];
  power: string | null;
  toughness: string | null;
  number: string;
  text: string;
  price: number;
  image_url: string | null;
  owns: boolean;
  wants: boolean;
  total_owned: number;
  total_wanted: number;
};

export type SetDetail = {
  meta: {
    code: string;
    name: string;
    type: string;
    release_date: string;
    base_set_size: number;
    total_set_size: number;
    block: string | null;
  };
  stats: {
    rarity_count: Record<string, number>;
    price: {
      total: number;
      tcgplayer: number;
      cardkingdom: number;
      cardsphere: number;
      cardmarket: number;
      mtgo: number;
    };
    keywords: KeywordFrequencies;
  };
  cards: {
    data: SetCard[];
    pagination: Pagination;
  };
};

// --- Card Stats (aggregated) ---

export type CardStatsResponse = {
  total: number;
  mana_curve: Record<string, number>;
  type_distribution: Record<string, number>;
  rarity_distribution: Record<string, number>;
  color_distribution: Record<string, number>;
  price_stats: {
    total: number;
    average: number;
    median: number;
    count_with_price: number;
  };
};

// --- Prices ---

export type PriceSummary = {
  uuid: string;
  name: string;
  set_code: string;
  rarity: string;
  image_url: string | null;
  prices: Record<string, number>;
  average_usd: number;
};

export type PriceListResponse = {
  data: PriceSummary[];
  pagination: Pagination;
  meta: {
    last_updated: string;
    total_cards_with_prices: number;
  };
};

// --- Stats ---

export type HomeStats = {
  total_decks: number;
  total_sets: number;
  total_cards: number;
  total_cards_with_prices: number;
  format_distribution: Record<string, number>;
  price_histogram: { range: string; count: number }[];
  recent_sets: { code: string; name: string; release_date: string }[];
  most_expensive_cards: { name: string; price: number; set_code: string }[];
};

// --- Boosters ---

export type BoosterCard = {
  uuid: string;
  name: string;
  set_code: string;
  rarity: string;
  slot: string;
  number: string;
  is_foil: boolean;
  image_url: string | null;
  mana_cost: string;
  mana_value: number;
  type_line: string;
  colors: string[];
};

export type BoosterPack = {
  set_code: string;
  set_name: string;
  booster_type: string;
  cards: BoosterCard[];
};

// --- Keywords ---

export type KeywordEntry = {
  term: string;
  definition: string;
};

export type KeywordsResponse = {
  keyword_abilities: KeywordEntry[];
  keyword_actions: KeywordEntry[];
  ability_words: KeywordEntry[];
};

// --- Similarity ---

export type SimilarCardSummary = {
  uuid: string;
  name: string;
  type: string;
  mana_cost: string;
  mana_value: number;
  rarity: string;
  set_code: string;
  color_identity: string[];
  image_url: string | null;
  owns: boolean;
  total_owned: number;
};

export type SimilarCardResult = {
  card: SimilarCardSummary;
  score: number;
  strategy_scores: Record<string, number>;
};

export type SimilarCardsResponse = {
  source: SimilarCardSummary;
  strategies_used: string[];
  results: SimilarCardResult[];
  total: number;
};

export type Strategy = {
  name: string;
  description: string;
};

// --- Feature Vectors ---

export type AggregateVectorResponse = {
  vector: number[];
  dimensions: number;
  dimension_names: string[];
  card_count: number;
};

export type CompactVectorCard = {
  uuid: string;
  name: string;
  vector: number[];
};

export type BatchCompactVectorResponse = {
  cards: CompactVectorCard[];
  dimensions: number;
  dimension_names: string[];
  total: number;
};

// --- Interactions ---

export type InteractionCard = {
  uuid: string;
  name: string;
  type_line: string;
  mana_cost: string;
  image_url: string | null;
};

export type Interaction = {
  id: number;
  source_card: InteractionCard;
  target_card: InteractionCard;
  interaction_type: string;
  is_bidirectional: boolean;
  description: string | null;
  strength: number | null;
  extra: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type InteractionListResponse = {
  data: Interaction[];
  pagination: Pagination;
};

export type CreateInteractionBody = {
  source_card_uuid: string;
  target_card_uuid: string;
  interaction_type: string;
  is_bidirectional?: boolean;
  description?: string;
  strength?: number;
};

export type InteractionGraphNode = {
  card: InteractionCard;
  interactions: Interaction[];
};

export type InteractionGraphResponse = {
  root_card: InteractionCard;
  depth: number;
  nodes: InteractionGraphNode[];
  total_interactions: number;
};

// --- User data (tags, notes, tier lists) ---

export type UserTagSummary = {
  tag: string;
  description: string | null;
  card_count: number;
};

export type TagCard = {
  uuid: string | null;
  name: string;
  type_line: string | null;
  mana_cost: string | null;
  set_code: string | null;
  image_url: string | null;
};

export type CardNote = {
  id: number;
  card_name: string;
  kind: string;
  title: string | null;
  body: string;
  extra: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type Tier =
  | "A+"
  | "A"
  | "A-"
  | "B+"
  | "B"
  | "B-"
  | "C+"
  | "C"
  | "C-"
  | "D+"
  | "D"
  | "D-"
  | "F";

export type TierListSummary = {
  id: number;
  name: string;
  description: string | null;
  set_code: string | null;
  format: string | null;
  extra: Record<string, unknown>;
  entry_count: number;
  created_at: string;
  updated_at: string;
};

export type TierEntry = {
  id: number;
  card_name: string;
  tier: string;
  position: number;
  note: string | null;
  card: TagCard | null;
};

export type TierListDetail = TierListSummary & {
  entries: TierEntry[];
};
