// Filters are kept as the exact query params of GET /api/cards, so the same
// object drives the form, the review URL, and the API request.
export type Filters = Record<string, string>;

export const DEFAULT_FILTERS: Filters = { sort: "number", order: "asc" };

export const RARITIES = ["common", "uncommon", "rare", "mythic"];
export const COLORS = ["W", "U", "B", "R", "G"];
export const MANA_VALUES = ["0", "1", "2", "3", "4", "5", "6", "7"];
export const FORMATS = ["standard", "pioneer", "modern", "legacy", "vintage", "commander", "brawl", "historic", "pauper"];
export const TIERS = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"];

export const SORTS = [
  { value: "number", label: "Collector #" },
  { value: "name", label: "Name" },
  { value: "mana_value", label: "Mana value" },
  { value: "price", label: "Price" },
  { value: "rarity", label: "Rarity" },
  { value: "color", label: "Color" },
  { value: "set_code", label: "Set" },
  { value: "tier", label: "Tier" },
];

export function listParam(filters: Filters, key: string): string[] {
  return filters[key] ? filters[key].split(",") : [];
}

export function setParam(filters: Filters, key: string, value: string): Filters {
  const next = { ...filters, [key]: value };
  if (!value) delete next[key];
  return next;
}

export function toggleInList(filters: Filters, key: string, value: string): Filters {
  const list = listParam(filters, key);
  const next = list.includes(value) ? list.filter((v) => v !== value) : [...list, value];
  return setParam(filters, key, next.join(","));
}

const STORAGE_KEY = "mtgsim-mobile-filters";
export const LAST_REVIEW_KEY = "mtgsim-mobile-last-review";

export function loadFilters(): Filters {
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved ? JSON.parse(saved) : DEFAULT_FILTERS;
}

export function saveFilters(filters: Filters) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(filters));
}
