import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { addToCollection, fetchCard, fetchCards, fetchCardTags, fetchKeywordFrequencies, updateRating } from "../api/cards"
import type { CardFilters } from "../types/filters"

export function useCards(filters: CardFilters, enabled = true) {
  return useQuery({
    queryKey: ["cards", filters],
    queryFn: () => fetchCards(filters),
    staleTime: 30_000,
    placeholderData: (prev) => prev,
    enabled,
  })
}

export function useCard(uuid: string | undefined) {
  return useQuery({
    queryKey: ["card", uuid],
    queryFn: () => fetchCard(uuid!),
    staleTime: 60_000,
    enabled: !!uuid,
  })
}

export function useCardTags(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["cardTags", params],
    queryFn: () => fetchCardTags(params),
    staleTime: 30_000,
  })
}

export function useKeywordFrequencies(params?: Record<string, string>, enabled = true) {
  return useQuery({
    queryKey: ["keywordFrequencies", params],
    queryFn: () => fetchKeywordFrequencies(params),
    staleTime: 30_000,
    enabled,
  })
}

export function useUpdateCollection() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (uuid: string) => addToCollection(uuid),
    onSuccess: (_, uuid) => {
      qc.invalidateQueries({ queryKey: ["card", uuid] })
    },
  })
}

export function useUpdateRating() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      uuid,
      rating,
    }: {
      uuid: string
      rating: Parameters<typeof updateRating>[1]
    }) => updateRating(uuid, rating),
    onSuccess: (_, { uuid }) => {
      qc.invalidateQueries({ queryKey: ["card", uuid] })
    },
  })
}
