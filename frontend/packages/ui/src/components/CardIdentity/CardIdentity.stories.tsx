import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardIdentity } from "./CardIdentity";

const meta: Meta<typeof CardIdentity> = {
  title: "CardDetail/CardIdentity",
  component: CardIdentity,
  tags: ["autodocs"],
  args: { onAddToDeck: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CardIdentity>;

export const Creature: Story = {
  args: {
    name: "Tarmogoyf",
    mana_cost: "{1}{G}",
    mana_value: 2,
    type: "Creature — Lhurgoyf",
    types: ["Creature"],
    power: "*",
    toughness: "1+*",
    loyalty: null,
    defense: null,
  },
};

export const Instant: Story = {
  args: {
    name: "Lightning Bolt",
    mana_cost: "{R}",
    mana_value: 1,
    type: "Instant",
    types: ["Instant"],
    power: null,
    toughness: null,
    loyalty: null,
    defense: null,
  },
};

export const Planeswalker: Story = {
  args: {
    name: "Wrenn and Six",
    mana_cost: "{R}{G}",
    mana_value: 2,
    type: "Legendary Planeswalker — Wrenn",
    types: ["Planeswalker"],
    power: null,
    toughness: null,
    loyalty: "3",
    defense: null,
  },
};

export const Battle: Story = {
  args: {
    name: "Invasion of Gobakhan",
    mana_cost: "{1}{W}",
    mana_value: 2,
    type: "Battle — Siege",
    types: ["Battle"],
    power: null,
    toughness: null,
    loyalty: null,
    defense: "3",
  },
};
