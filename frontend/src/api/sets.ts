import type { SetFilters } from "../types/filters"
import type { SetDetail, SetListResponse } from "../types/set"
import { apiFetch } from "./client"

export function fetchSets(filters: SetFilters) {
  return apiFetch<SetListResponse>("/sets", filters as Record<string, unknown>)
}

export function fetchSet(code: string, params?: Record<string, unknown>) {
  return apiFetch<SetDetail>(`/sets/${code}`, params)
}
