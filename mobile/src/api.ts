import { keepPreviousData, useQuery } from "@tanstack/react-query";
import type { Filters } from "./filters";
import type { Card, CardSet, Page, TierList, UserTag } from "./types";

export const PAGE_SIZE = 100;

async function get<T>(path: string, params: Record<string, string | number> = {}): Promise<T> {
  const query = new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]));
  const res = await fetch(`/api${path}?${query}`);
  return res.json();
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
