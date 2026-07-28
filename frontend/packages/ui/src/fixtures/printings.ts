import type { DeckCardPrinting } from "@/types/api";

const img = (id: string) => `https://cards.scryfall.io/large/front/${id[0]}/${id[1]}/${id}.jpg`;

export const cardPrintings: DeckCardPrinting[] = [
  {
    uuid: "d944340c-4fa8-5bd1-8abd-ad42cb1d2ae4",
    set_code: "2ED",
    set_name: "Unlimited Edition",
    number: "162",
    language: "English",
    is_default_printing: true,
    image_url: img("ff1b8fc5-604a-4449-a73d-861e53642a70"),
  },
  {
    uuid: "0aa4288b-47ee-5d3b-8b81-5479779a8b7b",
    set_code: "2X2",
    set_name: "Double Masters 2022",
    number: "117",
    language: "English",
    is_default_printing: true,
    image_url: img("f29ba16f-c8fb-42fe-aabf-87089cb214a7"),
  },
  {
    uuid: "190a854f-6657-59fb-a551-4bf99e4a5905",
    set_code: "2X2",
    set_name: "Double Masters 2022",
    number: "361",
    language: "English",
    is_default_printing: false,
    image_url: img("c8c8390f-4072-454f-8dc4-174919187a47"),
  },
  {
    uuid: "3995b117-80ba-5d3f-b57f-beb4055df545",
    set_code: "30A",
    set_name: "30th Anniversary Edition",
    number: "157",
    language: "English",
    is_default_printing: false,
    image_url: img("54be73dd-cb3b-411b-8f48-d12ca5183dee"),
  },
  {
    uuid: "7148e05b-25b6-5310-93f6-aae141a2077e",
    set_code: "4BB",
    set_name: "Fourth Edition Foreign Black Border",
    number: "208",
    language: "Japanese",
    is_default_printing: false,
    image_url: img("310de1ef-f1b6-4b61-9d6c-6b70382a7f95"),
  },
];
