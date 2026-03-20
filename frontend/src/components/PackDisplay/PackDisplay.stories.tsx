import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { PackDisplay } from "./PackDisplay";
import type { BoosterCard } from "@/types/api";

const sampleCards: BoosterCard[] = [
  { uuid: "c1", name: "Ragavan, Nimble Pilferer", set_code: "MH2", rarity: "mythic", slot: "rare", number: "138", is_foil: false, image_url: null, mana_cost: "{R}", mana_value: 1, type_line: "Legendary Creature — Monkey Pirate", colors: ["R"] },
  { uuid: "c2", name: "Counterspell", set_code: "MH2", rarity: "uncommon", slot: "uncommon", number: "267", is_foil: false, image_url: null, mana_cost: "{U}{U}", mana_value: 2, type_line: "Instant", colors: ["U"] },
  { uuid: "c3", name: "Sanctum Prelate", set_code: "MH2", rarity: "rare", slot: "rare_bonus", number: "491", is_foil: true, image_url: null, mana_cost: "{1}{W}{W}", mana_value: 3, type_line: "Creature — Human Cleric", colors: ["W"] },
  { uuid: "c4", name: "Abundant Harvest", set_code: "MH2", rarity: "common", slot: "common", number: "147", is_foil: false, image_url: null, mana_cost: "{G}", mana_value: 1, type_line: "Sorcery", colors: ["G"] },
  { uuid: "c5", name: "Bone Shards", set_code: "MH2", rarity: "common", slot: "common", number: "76", is_foil: false, image_url: null, mana_cost: "{B}", mana_value: 1, type_line: "Sorcery", colors: ["B"] },
];

const meta: Meta<typeof PackDisplay> = {
  title: "Draft/PackDisplay",
  component: PackDisplay,
  tags: ["autodocs"],
  args: { onCardClick: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-4xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof PackDisplay>;

export const Default: Story = {
  args: {
    cards: sampleCards,
    setName: "Modern Horizons 2",
    boosterType: "Draft Booster",
  },
};

export const Empty: Story = {
  args: { cards: [] },
};
