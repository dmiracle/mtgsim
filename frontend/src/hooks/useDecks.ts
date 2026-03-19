import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { addCardToDeck, createDeck, fetchDeck, fetchDecks, fetchUserDecks, importDeck } from "../api/decks"
import type { DeckFilters } from "../types/filters"

export function useDecks(filters: DeckFilters) {
  return useQuery({
    queryKey: ["decks", filters],
    queryFn: () => fetchDecks(filters),
    staleTime: 30_000,
    placeholderData: (prev) => prev,
  })
}

export function useDeck(file: string | undefined) {
  return useQuery({
    queryKey: ["deck", file],
    queryFn: () => fetchDeck(file!),
    staleTime: 60_000,
    enabled: !!file,
  })
}

export function useUserDecks() {
  return useQuery({
    queryKey: ["userDecks"],
    queryFn: fetchUserDecks,
    staleTime: 30_000,
  })
}

export function useCreateDeck() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createDeck,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["userDecks"] })
      qc.invalidateQueries({ queryKey: ["decks"] })
    },
  })
}

export function useImportDeck() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: importDeck,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["decks"] })
    },
  })
}

export function useAddCardToDeck() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ deckId, ...data }: { deckId: number; card_uuid: string; count?: number; board?: string }) =>
      addCardToDeck(deckId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["userDecks"] })
    },
  })
}
