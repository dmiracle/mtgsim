const WUBRG: Record<string, string> = { W: "0", U: "1", B: "2", R: "3", G: "4" };

/** Mirrors the backend color_sort_key: mono W,U,B,R,G first, then pairs/triples/
 * 4/5-color (WUBRG-lexicographic within a size), colorless last. Gold and hybrid
 * cards of the same colors share a key. */
export function colorSortKey(colors: string[]): string {
  const digits = colors
    .map((c) => WUBRG[c])
    .filter((d) => d !== undefined)
    .sort();
  if (digits.length === 0) return "6";
  return `${digits.length}${digits.join("")}`;
}
