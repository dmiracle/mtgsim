const RARITY_RANK: Record<string, number> = { common: 0, uncommon: 1, rare: 2, mythic: 3 };

/** Mirrors the backend rarity_order(): common < uncommon < rare < mythic < other. */
export function rarityRank(rarity: string | null | undefined): number {
  return RARITY_RANK[rarity ?? ""] ?? 4;
}
