import type { HomeStats } from "@/types/api";

export const homeStats: HomeStats = {
  total_decks: 42,
  total_sets: 156,
  total_cards: 28500,
  total_cards_with_prices: 25000,
  format_distribution: {
    modern: 12,
    commander: 15,
    standard: 5,
    legacy: 4,
    pioneer: 3,
    vintage: 2,
    pauper: 1,
  },
  price_histogram: [
    { range: "$0-50", count: 8 },
    { range: "$50-100", count: 12 },
    { range: "$100-200", count: 10 },
    { range: "$200-500", count: 7 },
    { range: "$500+", count: 5 },
  ],
  recent_sets: [
    { code: "OTJ", name: "Outlaws of Thunder Junction", release_date: "2024-04-19" },
    { code: "MKM", name: "Murders at Karlov Manor", release_date: "2024-02-09" },
    { code: "LCI", name: "The Lost Caverns of Ixalan", release_date: "2023-11-17" },
  ],
  most_expensive_cards: [
    { name: "The One Ring", price: 65.0, set_code: "LTR" },
    { name: "Ragavan, Nimble Pilferer", price: 55.0, set_code: "MH2" },
    { name: "Wrenn and Six", price: 48.0, set_code: "MH1" },
    { name: "Force of Negation", price: 42.0, set_code: "MH1" },
    { name: "Solitude", price: 38.0, set_code: "MH2" },
  ],
};
