import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { PackHistory } from "./PackHistory";
import type { BoosterPack } from "@/types/api";

const samplePacks: BoosterPack[] = [
  {
    set_code: "MH2", set_name: "Modern Horizons 2", booster_type: "draft",
    cards: [
      { uuid: "r1", name: "Ragavan, Nimble Pilferer", set_code: "MH2", rarity: "mythic", slot: "rare", number: "138", is_foil: false, image_url: null, mana_cost: "{R}", mana_value: 1, type_line: "Creature", colors: ["R"] },
    ],
  },
  {
    set_code: "MH2", set_name: "Modern Horizons 2", booster_type: "draft",
    cards: [
      { uuid: "r2", name: "Solitude", set_code: "MH2", rarity: "mythic", slot: "rare", number: "32", is_foil: false, image_url: null, mana_cost: "{3}{W}{W}", mana_value: 5, type_line: "Creature", colors: ["W"] },
    ],
  },
  {
    set_code: "MH2", set_name: "Modern Horizons 2", booster_type: "draft",
    cards: [
      { uuid: "r3", name: "Esper Sentinel", set_code: "MH2", rarity: "rare", slot: "rare", number: "12", is_foil: false, image_url: null, mana_cost: "{W}", mana_value: 1, type_line: "Creature", colors: ["W"] },
    ],
  },
];

const meta: Meta<typeof PackHistory> = {
  title: "Draft/PackHistory",
  component: PackHistory,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6 w-64"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof PackHistory>;

export const Interactive: Story = {
  render: () => {
    const [active, setActive] = useState(0);
    return <PackHistory packs={samplePacks} activeIndex={active} onSelect={setActive} />;
  },
};

export const SinglePack: Story = {
  args: { packs: [samplePacks[0]], activeIndex: 0, onSelect: () => {} },
};

export const Empty: Story = {
  args: { packs: [], activeIndex: 0, onSelect: () => {} },
};
