import type { DeckDetail, DeckImportResult, DeckListResponse, UserDeckResponse } from "../types/deck"
import type { DeckFilters } from "../types/filters"
import { apiFetch } from "./client"

export function fetchDecks(filters: DeckFilters) {
  return apiFetch<DeckListResponse>("/decks", filters as Record<string, unknown>)
}

export function fetchDeck(file: string) {
  return apiFetch<DeckDetail>(`/decks/${file}`)
}

export function fetchUserDecks() {
  return apiFetch<UserDeckResponse[]>("/decks/user/list")
}

export function createDeck(data: { name: string; format?: string | null; description?: string | null }) {
  return apiFetch<UserDeckResponse>("/decks/create", undefined, "POST", data)
}

export function importDeck(data: { text: string; name: string }) {
  return apiFetch<DeckImportResult>("/decks/import", undefined, "POST", data)
}

export function addCardToDeck(
  deckId: number,
  data: { card_uuid: string; count?: number; board?: string },
) {
  return apiFetch<unknown>(`/decks/${deckId}/cards`, undefined, "POST", data)
}
