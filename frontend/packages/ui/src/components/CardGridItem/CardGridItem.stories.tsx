import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardGridItem } from "./CardGridItem";
import { cardPrintings, cardSummaries } from "@/fixtures";

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

export const PrintingCarousel: Story = {
  render: (args) => {
    const [index, setIndex] = useState(0);
    const printing = cardPrintings[index];
    const card = {
      ...cardSummaries[0],
      uuid: printing.uuid,
      set_code: printing.set_code,
      image_url: printing.image_url,
    };
    return (
      <CardGridItem
        {...args}
        card={card}
        printingNav={{
          index,
          count: cardPrintings.length,
          onPrev: () => setIndex((i) => (i - 1 + cardPrintings.length) % cardPrintings.length),
          onNext: () => setIndex((i) => (i + 1) % cardPrintings.length),
        }}
      />
    );
  },
};
