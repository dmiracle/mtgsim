import { useQuery } from "@tanstack/react-query"
import { fetchPrices } from "../api/prices"
import type { PriceFilters } from "../types/filters"

export function usePrices(filters: PriceFilters) {
  return useQuery({
    queryKey: ["prices", filters],
    queryFn: () => fetchPrices(filters),
    staleTime: 30_000,
    placeholderData: (prev) => prev,
  })
}
