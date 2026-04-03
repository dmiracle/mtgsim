import type { Meta, StoryObj } from "@storybook/react";
import { CardRecallFlashcard } from "./CardRecallFlashcard";
import type { CardDetail } from "@/types/api";

const mockCreature: CardDetail = {
  uuid: "abc-123",
  name: "Slashing Tiger",
  mana_cost: "{2}{G}{G}",
  mana_value: 4,
  type: "Creature — Cat",
  types: ["Creature"],
  subtypes: ["Cat"],
  supertypes: [],
  text: "Flanking (Whenever a creature without flanking blocks this creature, the blocking creature gets -1/-1 until end of turn.)",
  flavor_text: "The razor-sharp claws of these great cats can strip the bark off a tree in a single swipe.",
  rarity: "common",
  set_code: "PTK",
  set_name: "Portal Three Kingdoms",
  color_identity: ["G"],
  colors: ["G"],
  keywords: ["Flanking"],
  tags: [],
  power: "3",
  toughness: "3",
  loyalty: null,
  defense: null,
  artist: "Qi Baocheng",
  number: "150",
  layout: "normal",
  finishes: ["nonfoil"],
  border_color: "black",
  frame_version: "1997",
  is_reprint: false,
  is_reserved: false,
  is_promo: false,
  image_url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",
  legalities: { vintage: "legal", legacy: "legal", pauper: "legal" },
  all_prices: [],
  appears_in_decks: [],
  other_printings: [],
  owns: false,
  wants: false,
  total_owned: 0,
  total_wanted: 0,
  collection: null,
  quadrant_rating: null,
};

const mockNoncreature: CardDetail = {
  ...mockCreature,
  uuid: "def-456",
  name: "Lightning Bolt",
  mana_cost: "{R}",
  mana_value: 1,
  type: "Instant",
  types: ["Instant"],
  subtypes: [],
  text: "Lightning Bolt deals 3 damage to any target.",
  flavor_text: null,
  color_identity: ["R"],
  colors: ["R"],
  keywords: [],
  power: null,
  toughness: null,
  rarity: "common",
  set_code: "A25",
  set_name: "Masters 25",
  image_url: null,
};

const meta: Meta<typeof CardRecallFlashcard> = {
  title: "Flashcards/CardRecallFlashcard",
  component: CardRecallFlashcard,
};
export default meta;

type Story = StoryObj<typeof CardRecallFlashcard>;

export const Creature: Story = {
  args: {
    card: mockCreature,
    onRate: (ratings, ms) => console.log("Rated:", ratings, `${ms}ms`),
  },
};

export const Noncreature: Story = {
  args: {
    card: mockNoncreature,
    onRate: (ratings, ms) => console.log("Rated:", ratings, `${ms}ms`),
  },
};

export const TrafficLightMode: Story = {
  args: {
    card: mockCreature,
    onRate: (ratings, ms) => console.log("Rated:", ratings, `${ms}ms`),
  },
};
