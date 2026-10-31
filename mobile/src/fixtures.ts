import type { Card, CardSet, TierList, UserTag } from "./types";

export const cards: Card[] = [
  {
    "uuid": "a0229777-3843-57e0-9911-cd640679a239",
    "name": "Andromedan Automatons",
    "type": "Artifact Creature — Android",
    "mana_cost": "{2}{W}",
    "mana_value": 3.0,
    "rarity": "common",
    "set_code": "TRK",
    "colors": [
      "W"
    ],
    "color_identity": [
      "W"
    ],
    "tags": [],
    "user_tags": [
      "removal-target",
      "top-common"
    ],
    "note_count": 0,
    "text": "When this creature enters, you may search your library for any number of cards named Andromedan Automatons, reveal them, put them into your hand, then shuffle.",
    "price": 0.12,
    "image_url": "https://cards.scryfall.io/large/front/f/c/fc386662-0fe3-432f-85a8-9a06e1274245.jpg?v=1",
    "owns": false,
    "wants": false,
    "number": "10"
  },
  {
    "uuid": "0d58d34f-8e7e-5866-8273-9dfe8fd7cfd9",
    "name": "Command Decision",
    "type": "Sorcery",
    "mana_cost": "{1}{W}",
    "mana_value": 2.0,
    "rarity": "common",
    "set_code": "TRK",
    "colors": [
      "W"
    ],
    "color_identity": [
      "W"
    ],
    "tags": [],
    "user_tags": [],
    "note_count": 1,
    "text": "Choose one —\n• Destroy target creature with power 4 or greater.\n• Draw a card.",
    "price": 0.25,
    "image_url": "https://cards.scryfall.io/large/front/9/f/9f1f789b-5c08-4a4d-b3a3-4d51ad9f1a4d.jpg?v=1",
    "owns": false,
    "wants": false,
    "number": "17"
  },
  {
    "uuid": "d7177fd9-68c7-52ba-94bf-5d17c1e7285e",
    "name": "DOT-7 Repair Squad",
    "type": "Artifact Creature — Robot",
    "mana_cost": "{3}{W}",
    "mana_value": 4.0,
    "rarity": "common",
    "set_code": "TRK",
    "colors": [
      "W"
    ],
    "color_identity": [
      "W"
    ],
    "tags": [],
    "user_tags": [],
    "note_count": 0,
    "text": "Flying\n{1}{W}: Untap target creature. Activate only as a sorcery and only once each turn.",
    "price": null,
    "image_url": "https://cards.scryfall.io/large/front/f/c/fca1528c-84cc-42d2-99ae-9f10f0e28743.jpg?v=1",
    "owns": false,
    "wants": false,
    "number": "24"
  },
  {
    "uuid": "1054964b-57ea-5b60-8f50-ba0566547ef7",
    "name": "Emergency Medical Hologram",
    "type": "Artifact Creature — Illusion Doctor",
    "mana_cost": "{W}",
    "mana_value": 1.0,
    "rarity": "common",
    "set_code": "TRK",
    "colors": [
      "W"
    ],
    "color_identity": [
      "W"
    ],
    "tags": [],
    "user_tags": [],
    "note_count": 0,
    "text": "When this creature enters, put a +1/+1 counter on target creature. You gain 1 life.",
    "price": null,
    "image_url": "https://cards.scryfall.io/large/front/d/d/dda6f965-cbdf-4dbc-b0b1-00c27e32f5f2.jpg?v=1",
    "owns": false,
    "wants": false,
    "number": "31"
  }
];

export const sets: CardSet[] = [
  { code: "TRK", name: "Star Trek", type: "expansion", release_date: "2026-11-13", total_set_size: 557 },
  { code: "TRC", name: "Star Trek Commander", type: "commander", release_date: "2026-11-13", total_set_size: 506 },
  { code: "MSH", name: "Marvel Super Heroes", type: "expansion", release_date: "2026-06-26", total_set_size: 334 },
  { code: "SOS", name: "Secrets of Strixhaven", type: "expansion", release_date: "2026-04-24", total_set_size: 341 },
];

export const userTags: UserTag[] = [
  { tag: "removal", card_count: 42 },
  { tag: "top-common", card_count: 12 },
  { tag: "build-around", card_count: 7 },
];

export const tierLists: TierList[] = [
  { id: 1, name: "TRK draft", set_code: "TRK", entry_count: 120 },
  { id: 2, name: "Cube staples", set_code: null, entry_count: 64 },
];
