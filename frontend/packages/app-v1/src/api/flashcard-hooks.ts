import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type {
  GenerateRequest,
  GenerateResponse,
  FlashcardQuestion,
  ReviewRequest,
  ReviewResponse,
  CollectionInfo,
  StudyStats,
  ReviewHistory,
  CardDifficulty,
  CollectionAnalytics,
  SessionAnalytics,
  RetentionAnalytics,
  KeywordAnalytics,
} from "@/types/flashcards";

export function useFlashcardStats(userId: string) {
  return useQuery({
    queryKey: ["flashcards", "stats", userId],
    queryFn: () => apiFetch<StudyStats>(`/flashcards/stats?user_id=${userId}`),
    enabled: !!userId,
  });
}

export function useFlashcardCollections(userId: string) {
  return useQuery({
    queryKey: ["flashcards", "collections", userId],
    queryFn: () => apiFetch<CollectionInfo[]>(`/flashcards/collections?user_id=${userId}`),
    enabled: !!userId,
  });
}

export function useNextFlashcard(userId: string, collection?: string) {
  const params = new URLSearchParams({ user_id: userId });
  if (collection) params.set("collection", collection);
  return useQuery({
    queryKey: ["flashcards", "next", userId, collection],
    queryFn: () => apiFetch<FlashcardQuestion | null>(`/flashcards/next?${params}`),
    enabled: !!userId,
    staleTime: 0,
    gcTime: 0,
  });
}

export function useGenerateFlashcards() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (req: GenerateRequest) =>
      apiFetch<GenerateResponse>("/flashcards/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["flashcards"] });
    },
  });
}

export function useDeleteCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ collectionId, userId }: { collectionId: number; userId: string }) =>
      apiFetch(`/flashcards/collections/${collectionId}?user_id=${userId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["flashcards"] });
    },
  });
}

export function useRecordReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (req: ReviewRequest) =>
      apiFetch<ReviewResponse>("/flashcards/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
      }),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ["flashcards", "next", vars.user_id] });
      qc.invalidateQueries({ queryKey: ["flashcards", "stats", vars.user_id] });
    },
  });
}

// --- Analytics ---

export function useReviewHistory(userId: string, granularity: "daily" | "hourly" = "hourly") {
  return useQuery({
    queryKey: ["flashcards", "analytics", "review-history", userId, granularity],
    queryFn: () => apiFetch<ReviewHistory>(`/flashcards/analytics/review-history?user_id=${userId}&granularity=${granularity}`),
    enabled: !!userId,
  });
}

export function useCardDifficulty(userId: string) {
  return useQuery({
    queryKey: ["flashcards", "analytics", "card-difficulty", userId],
    queryFn: () => apiFetch<CardDifficulty>(`/flashcards/analytics/card-difficulty?user_id=${userId}`),
    enabled: !!userId,
  });
}

export function useCollectionAnalytics(userId: string) {
  return useQuery({
    queryKey: ["flashcards", "analytics", "collections", userId],
    queryFn: () => apiFetch<CollectionAnalytics[]>(`/flashcards/analytics/collections?user_id=${userId}`),
    enabled: !!userId,
  });
}

export function useSessionAnalytics(userId: string) {
  return useQuery({
    queryKey: ["flashcards", "analytics", "sessions", userId],
    queryFn: () => apiFetch<SessionAnalytics>(`/flashcards/analytics/sessions?user_id=${userId}`),
    enabled: !!userId,
  });
}

export function useRetentionAnalytics(userId: string) {
  return useQuery({
    queryKey: ["flashcards", "analytics", "retention", userId],
    queryFn: () => apiFetch<RetentionAnalytics>(`/flashcards/analytics/retention?user_id=${userId}`),
    enabled: !!userId,
  });
}

export function useKeywordAnalytics(userId: string) {
  return useQuery({
    queryKey: ["flashcards", "analytics", "keywords", userId],
    queryFn: () => apiFetch<KeywordAnalytics>(`/flashcards/analytics/keywords?user_id=${userId}`),
    enabled: !!userId,
  });
}
