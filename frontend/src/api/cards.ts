import type { CardDetail, CardListResponse } from "../types/card"
import type { CardFilters } from "../types/filters"
import { apiFetch } from "./client"

export function fetchCards(filters: CardFilters) {
  return apiFetch<CardListResponse>("/cards", filters as Record<string, unknown>)
}

export function fetchCard(uuid: string) {
  return apiFetch<CardDetail>(`/cards/${uuid}`)
}

export function fetchCardTags(params?: Record<string, string>) {
  return apiFetch<{ tag: string; count: number }[]>("/cards/tags", params)
}

export function fetchKeywordFrequencies(params?: Record<string, string>) {
  return apiFetch<{
    keyword_abilities: Record<string, number>
    keyword_actions: Record<string, number>
    ability_words: Record<string, number>
  }>("/cards/keyword-frequencies", params)
}

export function addToCollection(uuid: string) {
  return apiFetch<{ success: boolean; message: string }>(
    `/cards/${uuid}/collection`,
    undefined,
    "POST",
  )
}

export function updateRating(
  uuid: string,
  rating: {
    developing: number | null
    ahead: number | null
    behind: number | null
    parity: number | null
    notes: string | null
  },
) {
  return apiFetch<typeof rating>(`/cards/${uuid}/rating`, undefined, "PUT", rating)
}
