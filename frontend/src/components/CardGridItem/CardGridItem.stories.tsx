import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardGridItem } from "./CardGridItem";
import { cardSummaries } from "@/fixtures";

const meta: Meta<typeof CardGridItem> = {
  title: "Cards/CardGridItem",
  component: CardGridItem,
  tags: ["autodocs"],
  args: {
    onPin: fn(),
    onAddToDeck: fn(),
    onClick: fn(),
    onSetClick: fn(),
  },
  decorators: [
    (Story) => (
      <div className="w-64 bg-gray-950 p-4">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof CardGridItem>;

export const Default: Story = {
  args: { card: cardSummaries[0] },
};

export const Pinned: Story = {
  args: { card: cardSummaries[0], pinned: true },
};

export const WithQuantity: Story = {
  args: { card: cardSummaries[0], quantity: 4 },
};

export const Uncommon: Story = {
  args: { card: cardSummaries[1] },
};

export const MythicRare: Story = {
  args: { card: cardSummaries[2] },
};

export const Rare: Story = {
  args: { card: cardSummaries[3] },
};

export const CheapCommon: Story = {
  args: { card: cardSummaries[4] },
};
