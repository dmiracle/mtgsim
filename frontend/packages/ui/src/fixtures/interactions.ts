import type { Interaction, InteractionCard } from "@/types/api";

const bolt: InteractionCard = {
  uuid: "bolt-uuid",
  name: "Lightning Bolt",
  type_line: "Instant",
  mana_cost: "{R}",
  image_url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",
};

const guide: InteractionCard = {
  uuid: "guide-uuid",
  name: "Goblin Guide",
  type_line: "Creature — Goblin Scout",
  mana_cost: "{R}",
  image_url: "https://cards.scryfall.io/normal/front/3/6/363339db-0caa-437c-98b0-ef6a7ed81e6e.jpg",
};

const eidolon: InteractionCard = {
  uuid: "eidolon-uuid",
  name: "Eidolon of the Great Revel",
  type_line: "Enchantment Creature — Spirit",
  mana_cost: "{R}{R}",
  image_url: null,
};

const counterspell: InteractionCard = {
  uuid: "counter-uuid",
  name: "Counterspell",
  type_line: "Instant",
  mana_cost: "{U}{U}",
  image_url: "https://cards.scryfall.io/normal/front/1/9/1920dae4-fb92-4f19-ae4b-eb3276b8571e.jpg",
};

const tarmogoyf: InteractionCard = {
  uuid: "goyf-uuid",
  name: "Tarmogoyf",
  type_line: "Creature — Lhurgoyf",
  mana_cost: "{1}{G}",
  image_url: "https://cards.scryfall.io/normal/front/6/9/69daba76-96e8-4bcc-ab79-2f00189ad8fb.jpg",
};

export const interactions: Interaction[] = [
  {
    id: 1,
    source_card: bolt,
    target_card: guide,
    interaction_type: "synergy",
    is_bidirectional: true,
    description: "Both are premier aggressive 1-drops that maximize early damage output in burn strategies.",
    strength: 4,
    extra: {},
    created_at: "2026-04-01T12:00:00Z",
    updated_at: "2026-04-01T12:00:00Z",
  },
  {
    id: 2,
    source_card: bolt,
    target_card: eidolon,
    interaction_type: "combo",
    is_bidirectional: true,
    description: "Eidolon punishes opponents for casting cheap spells while Bolt closes the game.",
    strength: 5,
    extra: {},
    created_at: "2026-04-01T12:00:00Z",
    updated_at: "2026-04-01T12:00:00Z",
  },
  {
    id: 3,
    source_card: bolt,
    target_card: counterspell,
    interaction_type: "counter",
    is_bidirectional: false,
    description: "Counterspell cleanly answers Lightning Bolt for the same mana investment.",
    strength: 3,
    extra: {},
    created_at: "2026-04-02T10:00:00Z",
    updated_at: "2026-04-02T10:00:00Z",
  },
  {
    id: 4,
    source_card: bolt,
    target_card: tarmogoyf,
    interaction_type: "counter",
    is_bidirectional: false,
    description: "Bolt cannot kill a full-size Tarmogoyf, making Goyf a natural counter to burn strategies.",
    strength: 4,
    extra: {},
    created_at: "2026-04-02T10:00:00Z",
    updated_at: "2026-04-02T10:00:00Z",
  },
  {
    id: 5,
    source_card: guide,
    target_card: eidolon,
    interaction_type: "synergy",
    is_bidirectional: true,
    description: null,
    strength: null,
    extra: {},
    created_at: "2026-04-03T08:00:00Z",
    updated_at: "2026-04-03T08:00:00Z",
  },
];
