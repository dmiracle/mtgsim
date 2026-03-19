import { useQuery } from "@tanstack/react-query"
import { fetchSet, fetchSets } from "../api/sets"
import type { SetFilters } from "../types/filters"
import type { SetSummary } from "../types/set"

export function useSets(filters: SetFilters) {
  return useQuery({
    queryKey: ["sets", filters],
    queryFn: () => fetchSets(filters),
    staleTime: 30_000,
    placeholderData: (prev) => prev,
  })
}

export function useSet(code: string | undefined, params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ["set", code, params],
    queryFn: () => fetchSet(code!, params),
    staleTime: 60_000,
    enabled: !!code,
  })
}

export function useAllSets() {
  return useQuery({
    queryKey: ["allSets"],
    queryFn: async () => {
      const allSets: SetSummary[] = []
      let page = 1
      while (true) {
        const res = await fetchSets({ limit: 100, page, sort: "release_date", order: "desc" })
        allSets.push(...res.data)
        if (page >= res.pagination.pages) break
        page++
      }
      return allSets
    },
    staleTime: Infinity,
  })
}
