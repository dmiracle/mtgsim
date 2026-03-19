import type { Pagination } from "./common"

export interface PriceSummary {
  uuid: string
  name: string
  set_code: string
  rarity: string
  image_url: string | null
  prices: Record<string, number>
  average_usd: number
}

export interface PriceListResponse {
  data: PriceSummary[]
  pagination: Pagination
  meta: {
    last_updated: string | null
    total_cards_with_prices: number
  }
}
