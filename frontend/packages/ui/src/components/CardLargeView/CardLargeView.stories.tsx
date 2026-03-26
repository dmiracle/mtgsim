import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardLargeView } from "./CardLargeView";
import { cardDetail } from "@/fixtures";

const meta: Meta<typeof CardLargeView> = {
  title: "Cards/CardLargeView",
  component: CardLargeView,
  tags: ["autodocs"],
  args: {
    onPin: fn(),
    onAddToDeck: fn(),
    onClick: fn(),
    onSetClick: fn(),
  },
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-8">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof CardLargeView>;

export const Default: Story = {
  args: { card: cardDetail },
};

export const Pinned: Story = {
  args: { card: cardDetail, pinned: true, quantity: 4 },
};

export const CreatureWithStats: Story = {
  args: {
    card: {
      ...cardDetail,
      name: "Tarmogoyf",
      mana_cost: "{1}{G}",
      mana_value: 2,
      type: "Creature — Lhurgoyf",
      types: ["Creature"],
      text: "Tarmogoyf's power is equal to the number of card types among cards in all graveyards and its toughness is equal to that number plus 1.",
      flavor_text: null,
      power: "*",
      toughness: "1+*",
      keywords: [],
      image_url: "https://cards.scryfall.io/normal/front/6/9/69daba76-96e8-4bcc-ab79-2f00189ad8fb.jpg",
    },
  },
};

export const PlaneswalkerWithLoyalty: Story = {
  args: {
    card: {
      ...cardDetail,
      name: "Wrenn and Six",
      mana_cost: "{R}{G}",
      mana_value: 2,
      type: "Legendary Planeswalker — Wrenn",
      types: ["Planeswalker"],
      text: "+1: Return up to one target land card from your graveyard to your hand.\n-1: Wrenn and Six deals 1 damage to any target.\n-7: You get an emblem with \"Instant and sorcery cards in your graveyard have retrace.\"",
      flavor_text: null,
      power: null,
      toughness: null,
      loyalty: "3",
      keywords: ["Retrace"],
      image_url: null,
    },
  },
};

export const WithManyKeywords: Story = {
  args: {
    card: {
      ...cardDetail,
      name: "Questing Beast",
      mana_cost: "{2}{G}{G}",
      mana_value: 4,
      type: "Legendary Creature — Beast",
      types: ["Creature"],
      text: "Vigilance, deathtouch, haste\nQuesting Beast can't be blocked by creatures with power 2 or less.\nCombat damage that would be dealt by creatures you control can't be prevented.\nWhenever Questing Beast deals combat damage to an opponent, it deals that much damage to target planeswalker that player controls.",
      flavor_text: null,
      power: "4",
      toughness: "4",
      keywords: ["Vigilance", "Deathtouch", "Haste"],
      image_url: null,
    },
  },
};
