import type { CardNote, TagCard, TierListDetail, TierListSummary, UserTagSummary } from "@/types/api";

export const userTags: UserTagSummary[] = [
  { tag: "removal", description: "Cleanly answers a resolved threat.", card_count: 12 },
  { tag: "wincon", description: "A primary way the deck closes the game.", card_count: 7 },
  { tag: "card-advantage", description: null, card_count: 9 },
  { tag: "enabler", description: "Sets up a payoff card elsewhere in the deck.", card_count: 5 },
  { tag: "sacrifice-outlet", description: null, card_count: 4 },
  { tag: "graveyard-hate", description: "Punishes graveyard-centric strategies.", card_count: 3 },
];

const bolt: TagCard = {
  uuid: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  name: "Lightning Bolt",
  type_line: "Instant",
  mana_cost: "{R}",
  set_code: "M10",
  image_url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",
};

const counterspell: TagCard = {
  uuid: "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  name: "Counterspell",
  type_line: "Instant",
  mana_cost: "{U}{U}",
  set_code: "MH2",
  image_url: "https://cards.scryfall.io/normal/front/1/9/1920dae4-fb92-4f19-ae4b-eb3276b8571e.jpg",
};

const tarmogoyf: TagCard = {
  uuid: "c3d4e5f6-a7b8-9012-cdef-123456789012",
  name: "Tarmogoyf",
  type_line: "Creature — Lhurgoyf",
  mana_cost: "{1}{G}",
  set_code: "MH2",
  image_url: "https://cards.scryfall.io/normal/front/6/9/69daba76-96e8-4bcc-ab79-2f00189ad8fb.jpg",
};

const goblinGuide: TagCard = {
  uuid: "d4e5f6a7-b8c9-0123-def1-234567890123",
  name: "Goblin Guide",
  type_line: "Creature — Goblin Scout",
  mana_cost: "{R}",
  set_code: "ZEN",
  image_url: "https://cards.scryfall.io/normal/front/3/6/363339db-0caa-437c-98b0-ef6a7ed81e6e.jpg",
};

const eidolon: TagCard = {
  uuid: "e5f6a7b8-c9d0-1234-ef12-345678901234",
  name: "Eidolon of the Great Revel",
  type_line: "Enchantment Creature — Spirit",
  mana_cost: "{R}{R}",
  set_code: "JOU",
  image_url: null,
};

const cutDown: TagCard = {
  uuid: "f6a7b8c9-d0e1-2345-f123-456789012345",
  name: "Cut Down",
  type_line: "Instant",
  mana_cost: "{B}",
  set_code: "DMU",
  image_url: null,
};

export const cardNotes: CardNote[] = [
  {
    id: 1,
    card_name: "Lightning Bolt",
    kind: "note",
    title: "Sequencing",
    body: "Hold for the opposing one-drop in racing matchups; face damage is the fallback, not the default.",
    extra: {},
    created_at: "2026-08-01T09:00:00Z",
    updated_at: "2026-08-10T14:30:00Z",
  },
  {
    id: 2,
    card_name: "Lightning Bolt",
    kind: "sideboard",
    title: null,
    body: "Comes out against decks with no relevant creatures — it is the worst card in the control matchup.",
    extra: {},
    created_at: "2026-08-05T11:00:00Z",
    updated_at: "2026-08-05T11:00:00Z",
  },
  {
    id: 3,
    card_name: "Lightning Bolt",
    kind: "combo-line",
    title: "Eidolon math",
    body: "With Eidolon of the Great Revel on the battlefield each Bolt is effectively 5 damage split 3/2.",
    extra: {},
    created_at: "2026-08-12T08:15:00Z",
    updated_at: "2026-08-12T08:15:00Z",
  },
];

export const tierListSummaries: TierListSummary[] = [
  {
    id: 1,
    name: "DMU Limited",
    description: "Draft pick order for Dominaria United.",
    set_code: "DMU",
    format: "draft",
    extra: {},
    entry_count: 6,
    created_at: "2026-08-01T09:00:00Z",
    updated_at: "2026-08-14T16:00:00Z",
  },
  {
    id: 2,
    name: "Burn staples",
    description: null,
    set_code: null,
    format: "modern",
    extra: {},
    entry_count: 12,
    created_at: "2026-07-20T10:00:00Z",
    updated_at: "2026-07-22T10:00:00Z",
  },
  {
    id: 3,
    name: "Cube keepers",
    description: "Cards that never leave the cube.",
    set_code: null,
    format: null,
    extra: {},
    entry_count: 40,
    created_at: "2026-06-01T10:00:00Z",
    updated_at: "2026-06-15T10:00:00Z",
  },
];

export const tierListDetail: TierListDetail = {
  ...tierListSummaries[0],
  entries: [
    { id: 11, card_name: "Lightning Bolt", tier: "S", position: 0, note: "Best common ever printed.", card: bolt },
    { id: 12, card_name: "Tarmogoyf", tier: "S", position: 1, note: null, card: tarmogoyf },
    { id: 13, card_name: "Counterspell", tier: "A", position: 0, note: null, card: counterspell },
    { id: 14, card_name: "Goblin Guide", tier: "A", position: 1, note: "Only in dedicated aggro.", card: goblinGuide },
    { id: 15, card_name: "Eidolon of the Great Revel", tier: "B", position: 0, note: null, card: eidolon },
    { id: 16, card_name: "Cut Down", tier: "C", position: 0, note: null, card: cutDown },
  ],
};
