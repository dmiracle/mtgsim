import type { PriceSummary } from "@/types/api";

export const priceSummaries: PriceSummary[] = [
  {
    uuid: "p1",
    name: "The One Ring",
    set_code: "LTR",
    rarity: "mythic",
    image_url: null,
    prices: { tcgplayer: 65.0, cardkingdom: 69.99 },
    average_usd: 65.0,
  },
  {
    uuid: "p2",
    name: "Ragavan, Nimble Pilferer",
    set_code: "MH2",
    rarity: "mythic",
    image_url: null,
    prices: { tcgplayer: 55.0, cardkingdom: 59.99 },
    average_usd: 55.0,
  },
  {
    uuid: "p3",
    name: "Wrenn and Six",
    set_code: "MH1",
    rarity: "mythic",
    image_url: null,
    prices: { tcgplayer: 48.0, cardkingdom: 49.99 },
    average_usd: 48.0,
  },
];
