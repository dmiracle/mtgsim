import type { PriceFilters } from "../types/filters"
import type { PriceListResponse } from "../types/price"
import { apiFetch } from "./client"

export function fetchPrices(filters: PriceFilters) {
  return apiFetch<PriceListResponse>("/prices", filters as Record<string, unknown>)
}
