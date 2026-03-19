import type { Pagination } from "./common"

export interface CardSummary {
  uuid: string
  name: string
  type: string
  mana_cost: string | null
  mana_value: number
  rarity: string
  set_code: string
  color_identity: string[]
  tags: string[]
  text: string | null
  price: number | null
  image_url: string | null
  owns: boolean
  wants: boolean
  total_owned: number
  total_wanted: number
}

export interface CardListResponse {
  data: CardSummary[]
  pagination: Pagination
}

export interface CardPriceEntry {
  provider: string
  finish: string
  listing_type: string
  price: number
}

export interface CardPrinting {
  set_code: string
  set_name: string
  uuid: string
  rarity: string
  number: string
  image_url: string | null
  owns: boolean
  total_owned: number
}

export interface CardAppearance {
  file: string
  name: string
  count: number
}

export interface CollectionInfo {
  quantity_owned: number
  quantity_owned_foil: number
  quantity_wanted: number
  quantity_wanted_foil: number
  condition: string | null
  notes: string | null
}

export interface QuadrantRating {
  developing: number | null
  ahead: number | null
  behind: number | null
  parity: number | null
  notes: string | null
}

export interface CardDetail {
  uuid: string
  name: string
  mana_cost: string | null
  mana_value: number
  type: string
  types: string[]
  subtypes: string[]
  supertypes: string[]
  text: string | null
  flavor_text: string | null
  rarity: string
  set_code: string
  set_name: string
  color_identity: string[]
  colors: string[]
  keywords: string[]
  tags: string[]
  power: string | null
  toughness: string | null
  loyalty: string | null
  defense: string | null
  artist: string | null
  number: string | null
  layout: string | null
  finishes: string[]
  border_color: string | null
  frame_version: string | null
  is_reprint: boolean
  is_reserved: boolean
  is_promo: boolean
  image_url: string | null
  legalities: Record<string, string>
  all_prices: CardPriceEntry[]
  appears_in_decks: CardAppearance[]
  other_printings: CardPrinting[]
  owns: boolean
  wants: boolean
  total_owned: number
  total_wanted: number
  collection: CollectionInfo | null
  quadrant_rating: QuadrantRating | null
}
