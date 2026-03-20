import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { DraftSimulatorPage } from "./DraftSimulatorPage";
import { setSummaries } from "@/fixtures";
import type { BoosterPack } from "@/types/api";

const samplePacks: BoosterPack[] = [
  {
    set_code: "MH2", set_name: "Modern Horizons 2", booster_type: "Draft Booster",
    cards: [
      { uuid: "c1", name: "Ragavan, Nimble Pilferer", set_code: "MH2", rarity: "mythic", slot: "rare", number: "138", is_foil: false, image_url: null, mana_cost: "{R}", mana_value: 1, type_line: "Legendary Creature — Monkey Pirate", colors: ["R"] },
      { uuid: "c2", name: "Counterspell", set_code: "MH2", rarity: "uncommon", slot: "uncommon", number: "267", is_foil: false, image_url: null, mana_cost: "{U}{U}", mana_value: 2, type_line: "Instant", colors: ["U"] },
      { uuid: "c3", name: "Abundant Harvest", set_code: "MH2", rarity: "common", slot: "common", number: "147", is_foil: false, image_url: null, mana_cost: "{G}", mana_value: 1, type_line: "Sorcery", colors: ["G"] },
      { uuid: "c4", name: "Bone Shards", set_code: "MH2", rarity: "common", slot: "common", number: "76", is_foil: false, image_url: null, mana_cost: "{B}", mana_value: 1, type_line: "Sorcery", colors: ["B"] },
      { uuid: "c5", name: "Sanctum Prelate", set_code: "MH2", rarity: "rare", slot: "bonus", number: "491", is_foil: true, image_url: null, mana_cost: "{1}{W}{W}", mana_value: 3, type_line: "Creature — Human Cleric", colors: ["W"] },
    ],
  },
  {
    set_code: "MH2", set_name: "Modern Horizons 2", booster_type: "Draft Booster",
    cards: [
      { uuid: "c6", name: "Esper Sentinel", set_code: "MH2", rarity: "rare", slot: "rare", number: "12", is_foil: false, image_url: null, mana_cost: "{W}", mana_value: 1, type_line: "Artifact Creature — Human Soldier", colors: ["W"] },
    ],
  },
];

const meta: Meta<typeof DraftSimulatorPage> = {
  title: "Pages/DraftSimulatorPage",
  component: DraftSimulatorPage,
  tags: ["autodocs"],
  args: { onOpenPacks: fn(), onCardClick: fn() },
  parameters: { layout: "padded" },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-6xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof DraftSimulatorPage>;

export const WithPacks: Story = {
  args: { sets: setSummaries, packs: samplePacks },
};

export const Empty: Story = {
  args: { sets: setSummaries, packs: [] },
};

export const Loading: Story = {
  args: { sets: setSummaries, packs: [], loading: true },
};
