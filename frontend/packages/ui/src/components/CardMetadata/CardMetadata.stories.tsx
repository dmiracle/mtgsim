import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardMetadata } from "./CardMetadata";

const meta: Meta<typeof CardMetadata> = {
  title: "CardDetail/CardMetadata",
  component: CardMetadata,
  tags: ["autodocs"],
  args: { onSetClick: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-sm"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CardMetadata>;

export const Default: Story = {
  args: {
    set_code: "M10",
    set_name: "Magic 2010",
    rarity: "common",
    number: "146",
    artist: "Christopher Moeller",
    layout: "normal",
    finishes: ["nonfoil", "foil"],
    border_color: "black",
    frame_version: "2003",
    is_reprint: true,
    is_reserved: false,
    is_promo: false,
  },
};

export const WithFlags: Story = {
  args: {
    set_code: "LEA",
    set_name: "Limited Edition Alpha",
    rarity: "rare",
    number: "232",
    artist: "Mark Poole",
    layout: "normal",
    finishes: ["nonfoil"],
    border_color: "black",
    frame_version: "1993",
    is_reprint: false,
    is_reserved: true,
    is_promo: false,
  },
};
