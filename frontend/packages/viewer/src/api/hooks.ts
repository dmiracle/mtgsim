import { useQuery, useQueries, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, buildParams } from "./client";
import type {
  HomeStats,
  DeckSummary,
  DeckListResponse,
  DeckDetail,
  UserDeckResponse,
  DeckImportResult,
  CardListResponse,
  CardStatsResponse,
  CardDetail,
  TagCount,
  KeywordFrequencies,
  KeywordsResponse,
  SetListResponse,
  SetDetail,
  PriceListResponse,
  BoosterPack,
  QuadrantRating,
  SimilarCardsResponse,
  Strategy,
  AggregateVectorResponse,
  DeckCardPrinting,
} from "@/types/api";

// --- Stats ---

export function useHomeStats() {
  return useQuery({
    queryKey: ["stats", "home"],
    queryFn: () => apiFetch<HomeStats>("/stats/home"),
  });
}

// --- Decks ---

export function useDecks(params: Record<string, string | number | boolean | null | undefined>) {
  return useQuery({
    queryKey: ["decks", params],
    queryFn: () => apiFetch<DeckListResponse>(`/decks${buildParams(params)}`),
  });
}

export function useDeck(file: string) {
  return useQuery({
    queryKey: ["deck", file],
    queryFn: () => apiFetch<DeckDetail>(`/decks/${file}`),
    enabled: !!file,
  });
}

export function useUserDecks() {
  return useQuery({
    queryKey: ["decks", "user"],
    queryFn: () => apiFetch<UserDeckResponse[]>("/decks/user/list"),
  });
}

export function useCreateDeck() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { name: string; format: string | null; description: string | null }) =>
      apiFetch<UserDeckResponse>("/decks/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["decks"] });
    },
  });
}

export function useImportDeck() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { text: string; name: string }) =>
      apiFetch<DeckImportResult>("/decks/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["decks"] });
    },
  });
}

// --- Pinned Decks ---

export function usePinnedDecksQuery() {
  return useQuery({
    queryKey: ["decks", "pinned"],
    queryFn: () => apiFetch<DeckSummary[]>("/decks/pinned"),
    staleTime: 0,
    refetchOnMount: "always",
  });
}

export function usePinDeck() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (uuid: string) =>
      apiFetch(`/decks/pinned/${uuid}`, { method: "POST" }),
    onMutate: async (uuid) => {
      await qc.cancelQueries({ queryKey: ["decks", "pinned"] });
      const prev = qc.getQueryData<DeckSummary[]>(["decks", "pinned"]);
      qc.setQueryData<DeckSummary[]>(["decks", "pinned"], (old) => {
        if (!old) return [];
        if (old.some((d) => d.uuid === uuid)) return old;
        return [...old, { uuid, file: "", name: "", code: "", deck_type: "", card_count: 0, colors: [], price: 0, release_date: "", legality: {}, source: "" }];
      });
      return { prev };
    },
    onError: (_err, _uuid, context) => {
      if (context?.prev) qc.setQueryData(["decks", "pinned"], context.prev);
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["decks", "pinned"] });
    },
  });
}

export function useUnpinDeck() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (uuid: string) =>
      apiFetch(`/decks/pinned/${uuid}`, { method: "DELETE" }),
    onMutate: async (uuid) => {
      await qc.cancelQueries({ queryKey: ["decks", "pinned"] });
      const prev = qc.getQueryData<DeckSummary[]>(["decks", "pinned"]);
      qc.setQueryData<DeckSummary[]>(["decks", "pinned"], (old) =>
        old ? old.filter((d) => d.uuid !== uuid) : [],
      );
      return { prev };
    },
    onError: (_err, _uuid, context) => {
      if (context?.prev) qc.setQueryData(["decks", "pinned"], context.prev);
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["decks", "pinned"] });
    },
  });
}

export function useUpdateDeck() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ deckId, ...body }: { deckId: number; name?: string; intended_format?: string | null }) =>
      apiFetch<UserDeckResponse>(`/decks/${deckId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }),
    onSuccess: (_, { deckId }) => {
      qc.invalidateQueries({ queryKey: ["decks"] });
      qc.invalidateQueries({ queryKey: ["deck", String(deckId)] });
    },
  });
}

export function useDeleteDeck() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (deckId: number) =>
      apiFetch(`/decks/${deckId}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["decks"] });
    },
  });
}

export function useDuplicateDeck() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (deckId: number) =>
      apiFetch<UserDeckResponse>(`/decks/${deckId}/duplicate`, { method: "POST" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["decks"] });
    },
  });
}

export function useAddCardToDeck() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ deckId, ...body }: { deckId: number; card_uuid: string; count: number; board: string }) =>
      apiFetch(`/decks/${deckId}/cards`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["decks"] });
      qc.invalidateQueries({ queryKey: ["deck"] });
    },
  });
}

export function useRemoveCardFromDeck() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ deckId, cardUuid, count }: { deckId: number; cardUuid: string; count?: number }) =>
      apiFetch(`/decks/${deckId}/cards/${cardUuid}${count ? `?count=${count}` : ""}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["decks"] });
      qc.invalidateQueries({ queryKey: ["deck"] });
    },
  });
}

// --- Cards ---

export function useCards(params: Record<string, string | number | boolean | null | undefined>) {
  const hasFilter = Object.values(params).some((v) => v !== undefined && v !== null && v !== "");
  return useQuery({
    queryKey: ["cards", params],
    queryFn: () => apiFetch<CardListResponse>(`/cards${buildParams(params)}`),
    enabled: hasFilter,
    placeholderData: (prev) => prev,
  });
}

export function useCardStats(params: Record<string, string | number | boolean | null | undefined>) {
  const hasFilter = Object.values(params).some((v) => v !== undefined && v !== null && v !== "");
  return useQuery({
    queryKey: ["cards", "stats", params],
    queryFn: () => apiFetch<CardStatsResponse>(`/cards/stats${buildParams(params)}`),
    enabled: hasFilter,
    placeholderData: (prev) => prev,
  });
}

export function useCard(uuid: string) {
  return useQuery({
    queryKey: ["card", uuid],
    queryFn: () => apiFetch<CardDetail>(`/cards/${uuid}`),
    enabled: !!uuid,
  });
}

export function useCardTags(params: Record<string, string | undefined>) {
  return useQuery({
    queryKey: ["cards", "tags", params],
    queryFn: () => apiFetch<TagCount[]>(`/cards/tags${buildParams(params)}`),
  });
}

export function useKeywordFrequencies(params: Record<string, string | undefined>) {
  return useQuery({
    queryKey: ["cards", "keyword-frequencies", params],
    queryFn: () => apiFetch<KeywordFrequencies>(`/cards/keyword-frequencies${buildParams(params)}`),
  });
}

export function useAddToCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (uuid: string) =>
      apiFetch(`/cards/${uuid}/collection`, { method: "POST" }),
    onSuccess: (_, uuid) => {
      qc.invalidateQueries({ queryKey: ["card", uuid] });
    },
  });
}

export function useSaveRating() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ uuid, ...rating }: QuadrantRating & { uuid: string }) =>
      apiFetch(`/cards/${uuid}/rating`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(rating),
      }),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ["card", vars.uuid] });
    },
  });
}

// --- Sets ---

export function useSets(params: Record<string, string | number | boolean | null | undefined>) {
  return useQuery({
    queryKey: ["sets", params],
    queryFn: () => apiFetch<SetListResponse>(`/sets${buildParams(params)}`),
  });
}

export function useSet(code: string, cardParams?: Record<string, string | number | boolean | null | undefined>) {
  return useQuery({
    queryKey: ["set", code, cardParams],
    queryFn: () => apiFetch<SetDetail>(`/sets/${code}${buildParams(cardParams ?? {})}`),
    enabled: !!code,
    placeholderData: (prev) => prev,
  });
}

// --- Prices ---

export function usePrices(params: Record<string, string | number | boolean | null | undefined>) {
  return useQuery({
    queryKey: ["prices", params],
    queryFn: () => apiFetch<PriceListResponse>(`/prices${buildParams(params)}`),
  });
}

// --- Boosters ---

export function useOpenPacks() {
  return useMutation({
    mutationFn: ({ setCode, count, type }: { setCode: string; count: number; type?: string }) => {
      const params = buildParams({ type, count: count > 1 ? count : undefined });
      const path = count > 1
        ? `/boosters/${setCode}/batch${params}`
        : `/boosters/${setCode}${params}`;
      return apiFetch<BoosterPack | BoosterPack[]>(path);
    },
  });
}

// --- Keywords ---

export function useKeywords() {
  return useQuery({
    queryKey: ["keywords"],
    queryFn: () => apiFetch<KeywordsResponse>("/keywords"),
    staleTime: Infinity,
  });
}

// --- Similarity ---

export function useSimilarCards(
  uuid: string,
  strategies: string[],
  filters?: Record<string, string | number | boolean | null | undefined>,
  limit: number = 20,
) {
  const params = buildParams({
    strategies: strategies.length > 0 ? strategies.join(",") : undefined,
    limit,
    ...filters,
  });
  return useQuery({
    queryKey: ["cards", "similar", uuid, strategies, filters, limit],
    queryFn: () => apiFetch<SimilarCardsResponse>(`/cards/${uuid}/similar${params}`),
    enabled: !!uuid && strategies.length > 0,
  });
}

export function useStrategies() {
  return useQuery({
    queryKey: ["cards", "similar", "strategies"],
    queryFn: () => apiFetch<Strategy[]>("/cards/similar/strategies"),
    staleTime: Infinity,
  });
}

// --- Feature Vectors ---

export function useAggregateVector(params: Record<string, string | number | boolean | null | undefined>) {
  const hasFilter = Object.values(params).some((v) => v !== undefined && v !== null && v !== "");
  return useQuery({
    queryKey: ["cards", "features", "aggregate", params],
    queryFn: () => apiFetch<AggregateVectorResponse>(`/cards/features/aggregate${buildParams(params)}`),
    enabled: hasFilter,
    placeholderData: (prev) => prev,
  });
}

export function useCardVector(uuid: string) {
  return useQuery({
    queryKey: ["cards", "features", "compact", uuid],
    queryFn: () => apiFetch<AggregateVectorResponse>(`/cards/${uuid}/features/compact`),
    enabled: !!uuid,
  });
}

export function useDeckVector(file: string) {
  return useQuery({
    queryKey: ["decks", "features", file],
    queryFn: () => apiFetch<AggregateVectorResponse>(`/decks/${file}/features`),
    enabled: !!file,
  });
}

export function useDeckVectors(files: string[]) {
  return useQueries({
    queries: files.map((file) => ({
      queryKey: ["decks", "features", file],
      queryFn: () => apiFetch<AggregateVectorResponse>(`/decks/${file}/features`),
      enabled: !!file,
      staleTime: 60_000,
    })),
    combine: (results) => {
      const map: Record<string, AggregateVectorResponse> = {};
      for (let i = 0; i < files.length; i++) {
        if (results[i].data) map[files[i]] = results[i].data!;
      }
      return map;
    },
  });
}

// --- Printings ---

export function usePrintings(uuid: string) {
  return useQuery({
    queryKey: ["cards", uuid, "printings"],
    queryFn: () => apiFetch<DeckCardPrinting[]>(`/cards/${uuid}/printings`),
    enabled: !!uuid,
    staleTime: 300_000,
  });
}

export function useSetPrinting() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ deckId, cardUuid, printingUuid }: { deckId: number; cardUuid: string; printingUuid: string }) =>
      apiFetch(`/decks/${deckId}/cards/${cardUuid}/printing`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ printing_uuid: printingUuid }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["decks"] });
      qc.invalidateQueries({ queryKey: ["deck"] });
    },
  });
}
