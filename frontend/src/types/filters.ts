export interface CardFilters {
  q?: string
  text?: string
  sets?: string
  rarity?: string
  type?: string
  colors?: string
  format?: string
  keywords?: string
  tags?: string
  owns?: boolean
  unique?: boolean
  sort?: string
  order?: string
  page?: number
  limit?: number
}

export interface DeckFilters {
  q?: string
  format?: string
  source?: string
  set?: string
  colors?: string
  card_count_min?: number
  card_count_max?: number
  price_min?: number
  price_max?: number
  sort?: string
  order?: string
  page?: number
  limit?: number
}

export interface SetFilters {
  q?: string
  type?: string
  sort?: string
  order?: string
  page?: number
  limit?: number
}

export interface PriceFilters {
  q?: string
  set?: string
  price_min?: number
  price_max?: number
  sort?: string
  order?: string
  page?: number
  limit?: number
}
