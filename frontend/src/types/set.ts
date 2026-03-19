import type { KeywordCounts, Pagination } from "./common"

export interface SetSummary {
  code: string
  name: string
  type: string
  release_date: string
  base_set_size: number
  total_set_size: number
  block: string | null
  keyrune_code: string | null
  collection_stats: Record<string, number> | null
}

export interface SetListResponse {
  data: SetSummary[]
  pagination: Pagination
  filters: {
    types: string[]
    blocks: string[]
  }
}

export interface SetCard {
  uuid: string
  name: string
  mana_cost: string | null
  mana_value: number
  type: string
  rarity: string
  color_identity: string[]
  colors: string[]
  power: string | null
  toughness: string | null
  number: string
  text: string | null
  price: number | null
  image_url: string | null
  owns: boolean
  wants: boolean
  total_owned: number
  total_wanted: number
}

export interface SetStats {
  rarity_count: Record<string, number>
  price: {
    total: number
    tcgplayer: number | null
    cardkingdom: number | null
    cardsphere: number | null
    cardmarket: number | null
    mtgo: number | null
  }
  keywords: KeywordCounts
}

export interface SetMeta {
  code: string
  name: string
  type: string
  release_date: string
  base_set_size: number
  total_set_size: number
  block: string | null
}

export interface SetDetail {
  meta: SetMeta
  stats: SetStats
  cards: {
    data: SetCard[]
    pagination: Pagination
  }
}
