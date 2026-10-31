import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Filters } from "./filters";
import type { Card, CardSet, Page, Ranking, RankingDetail, TierList, TierListDetail, UserTag } from "./types";

export const PAGE_SIZE = 100;

async function get<T>(path: string, params: Record<string, string | number> = {}): Promise<T> {
  const query = new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]));
  const res = await fetch(`/api${path}?${query}`);
  return res.json();
}

async function send(method: string, path: string, body?: unknown) {
  const res = await fetch(`/api${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  return res.status === 204 ? null : res.json();
}

export function useSets(q: string) {
  return useQuery({
    queryKey: ["sets", q],
    queryFn: () => get<Page<CardSet>>("/sets", { q, limit: 50, sort: "release_date", order: "desc" }),
    placeholderData: keepPreviousData,
  });
}

export function useUserTags() {
  return useQuery({ queryKey: ["user-tags"], queryFn: () => get<Page<UserTag>>("/user-tags", { limit: 100 }) });
}

export function useTierLists() {
  return useQuery({ queryKey: ["tier-lists"], queryFn: () => get<Page<TierList>>("/tier-lists", { limit: 100 }) });
}

export function useCardCount(filters: Filters) {
  return useQuery({
    queryKey: ["card-count", filters],
    queryFn: () => get<Page<Card>>("/cards", { ...filters, limit: 1 }),
    select: (page) => page.pagination.total,
    placeholderData: keepPreviousData,
  });
}

export function cardPageQuery(filters: Filters, page: number) {
  return {
    queryKey: ["cards", filters, page],
    queryFn: () => get<Page<Card>>("/cards", { ...filters, page, limit: PAGE_SIZE }),
  };
}

export function useCardPage(filters: Filters, page: number) {
  return useQuery({ ...cardPageQuery(filters, page), placeholderData: keepPreviousData });
}

export function useTierList(id: string | undefined) {
  return useQuery({
    queryKey: ["tier-list", id],
    queryFn: () => get<TierListDetail>(`/tier-lists/${id}`),
    enabled: !!id,
  });
}

export function useCreateTierList() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: { name: string; set_code?: string }) => send("POST", "/tier-lists", body) as Promise<TierList>,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tier-lists"] }),
  });
}

// tier = null removes the card's grade from the list.
export function useSetGrade(listId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ cardName, tier }: { cardName: string; tier: string | null }) =>
      tier
        ? send("PUT", `/tier-lists/${listId}/entries`, { card_name: cardName, tier })
        : send("DELETE", `/tier-lists/${listId}/entries?${new URLSearchParams({ card_name: cardName })}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tier-list", listId] });
      queryClient.invalidateQueries({ queryKey: ["tier-lists"] });
    },
  });
}

// Rankings cover every card a filter matches, so the pool is capped to stay rankable.
export const RANKING_POOL_MAX = 600;

export function rankingPoolFilters(filters: Filters): Filters {
  const { grade_list: _g, not_in_tier_list: _n, i: _i, ...rest } = filters;
  return { ...rest, unique: "true", sort: "name", order: "asc" };
}

export function useRankingPool(filters: Filters | undefined) {
  return useQuery({
    queryKey: ["ranking-pool", filters],
    enabled: !!filters,
    queryFn: async () => {
      const cards: Card[] = [];
      for (let page = 1; ; page++) {
        const result = await get<Page<Card>>("/cards", { ...rankingPoolFilters(filters!), page, limit: PAGE_SIZE });
        if (result.pagination.total > RANKING_POOL_MAX) return { cards: [], total: result.pagination.total };
        cards.push(...result.data);
        if (page >= result.pagination.pages) return { cards, total: result.pagination.total };
      }
    },
  });
}

export function useRankings() {
  return useQuery({ queryKey: ["rankings"], queryFn: () => get<Ranking[]>("/rankings") });
}

export function useRanking(id: string | undefined) {
  return useQuery({ queryKey: ["ranking", id], queryFn: () => get<RankingDetail>(`/rankings/${id}`) });
}

export function useCreateRanking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: { name: string; filters: Filters }) => send("POST", "/rankings", body) as Promise<Ranking>,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rankings"] }),
  });
}

export function useDeleteRanking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => send("DELETE", `/rankings/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rankings"] }),
  });
}

export function useSubmitRound(id: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (orderedNames: string[]) =>
      send("POST", `/rankings/${id}/rounds`, { ordered_card_names: orderedNames }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ranking", id] });
      queryClient.invalidateQueries({ queryKey: ["rankings"] });
    },
  });
}
