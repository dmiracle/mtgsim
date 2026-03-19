import type { HistogramBucket } from "../types/common"
import { apiFetch } from "./client"

export interface HomeStats {
  total_decks: number
  total_sets: number
  total_cards: number
  total_cards_with_prices: number
  format_distribution: Record<string, number>
  price_histogram: HistogramBucket[]
  recent_sets: { code: string; name: string; release_date: string }[]
  most_expensive_cards: { name: string; price: number; set_code: string }[]
}

export function fetchHomeStats() {
  return apiFetch<HomeStats>("/stats/home")
}
