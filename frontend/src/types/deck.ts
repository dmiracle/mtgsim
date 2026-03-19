import type { HistogramBucket, KeywordCounts, Pagination } from "./common"

export interface DeckSummary {
  file: string
  name: string
  code: string | null
  deck_type: string | null
  card_count: number
  colors: string[]
  price: number | null
  release_date: string | null
  legality: Record<string, boolean>
  source: string
}

export interface DeckListResponse {
  data: DeckSummary[]
  pagination: Pagination
  filters: {
    sets: string[]
    formats: string[]
    color_combinations: string[]
  }
}

export interface DeckCard {
  uuid: string
  name: string
  count: number
  board: string
  mana_cost: string | null
  mana_value: number
  type: string
  types: string[]
  colors: string[]
  rarity: string
  tags: string[]
  text: string | null
  price: number | null
  image_url: string | null
  owns_enough: boolean
  owned_count: number
  missing_count: number
}

export interface DeckMeta {
  name: string
  file: string
  code: string | null
  release_date: string | null
  description: string | null
  format: string | null
  source: string
}

export interface DeckLegality {
  standard: boolean
  pioneer: boolean
  modern: boolean
  legacy: boolean
  vintage: boolean
  commander: boolean
  brawl: boolean
  historic: boolean
  pauper: boolean
}

export interface DeckPrice {
  total: number
  tcgplayer: number | null
  cardkingdom: number | null
  cardsphere: number | null
  cardmarket: number | null
  mtgo: number | null
}

export interface DeckStats {
  total_cards: number
  unique_cards: number
  mana_curve: Record<string, number>
  type_distribution: Record<string, number>
  rarity_distribution: Record<string, number>
  color_distribution: Record<string, number>
  price_histogram: HistogramBucket[]
  keywords: KeywordCounts
}

export interface DeckDetail {
  meta: DeckMeta
  legality: DeckLegality
  colors: string[]
  price: DeckPrice
  commander: DeckCard[]
  main_board: DeckCard[]
  side_board: DeckCard[]
  stats: DeckStats
}

export interface UserDeckResponse {
  id: number
  name: string
  description: string | null
  format: string | null
  source: string
  card_count: number
}

export interface DeckImportResult {
  deck_id: string
  deck_name: string
  total_cards: number
  resolved: {
    name: string
    matched_name: string
    match_type: "exact" | "fuzzy" | "created"
    match_score: number
    count: number
  }[]
  legality: {
    format: string
    legal: boolean
    reason: string | null
  }[]
}
