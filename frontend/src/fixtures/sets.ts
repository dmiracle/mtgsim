import type { SetSummary, SetDetail } from "@/types/api";

export const setSummaries: SetSummary[] = [
  {
    code: "MH2",
    name: "Modern Horizons 2",
    type: "draft_innovation",
    release_date: "2021-06-18",
    base_set_size: 303,
    total_set_size: 531,
    block: null,
    keyrune_code: "MH2",
    collection_stats: null,
  },
  {
    code: "ONE",
    name: "Phyrexia: All Will Be One",
    type: "expansion",
    release_date: "2023-02-03",
    base_set_size: 271,
    total_set_size: 453,
    block: null,
    keyrune_code: "ONE",
    collection_stats: null,
  },
  {
    code: "DMU",
    name: "Dominaria United",
    type: "expansion",
    release_date: "2022-09-09",
    base_set_size: 281,
    total_set_size: 436,
    block: null,
    keyrune_code: "DMU",
    collection_stats: null,
  },
];

export const setDetail: SetDetail = {
  meta: {
    code: "MH2",
    name: "Modern Horizons 2",
    type: "draft_innovation",
    release_date: "2021-06-18",
    base_set_size: 303,
    total_set_size: 531,
    block: null,
  },
  stats: {
    rarity_count: {
      common: 101,
      uncommon: 100,
      rare: 78,
      mythic: 24,
    },
    price: {
      total: 2450.0,
      tcgplayer: 2450.0,
      cardkingdom: 2600.0,
      cardsphere: 2200.0,
      cardmarket: 2100.0,
      mtgo: 180.0,
    },
    keywords: {
      keyword_abilities: { flying: 32, trample: 18, deathtouch: 15 },
      keyword_actions: { destroy: 22, exile: 18, create: 45 },
      ability_words: { delirium: 8, domain: 0 },
    },
  },
  cards: {
    data: [],
    pagination: { page: 1, limit: 50, total: 303, pages: 7 },
  },
};
