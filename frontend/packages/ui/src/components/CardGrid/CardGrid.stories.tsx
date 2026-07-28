import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardGrid } from "./CardGrid";
import { cardSummaries } from "@/fixtures";

const meta: Meta<typeof CardGrid> = {
  title: "Cards/CardGrid",
  component: CardGrid,
  tags: ["autodocs"],
  args: {
    onPageChange: fn(),
    onPin: fn(),
    onAddToDeck: fn(),
    onCardClick: fn(),
    onSetClick: fn(),
  },
  parameters: {
    layout: "padded",
  },
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof CardGrid>;

export const Default: Story = {
  args: {
    cards: cardSummaries,
    pagination: { page: 1, pages: 5, total: 250, limit: 50 },
  },
};

export const MediumSize: Story = {
  args: {
    cards: cardSummaries,
    size: "medium",
  },
};

export const LargeSize: Story = {
  args: {
    cards: cardSummaries,
    size: "large",
  },
};

export const WithPinnedCards: Story = {
  args: {
    cards: cardSummaries,
    pinnedIds: new Set([cardSummaries[0].uuid, cardSummaries[2].uuid]),
    pagination: { page: 1, pages: 3, total: 150, limit: 50 },
  },
};

export const WithQuantities: Story = {
  args: {
    cards: cardSummaries,
    quantities: {
      [cardSummaries[0].uuid]: 4,
      [cardSummaries[1].uuid]: 2,
    },
  },
};

export const Empty: Story = {
  args: {
    cards: [],
  },
};

export const SingleCard: Story = {
  args: {
    cards: [cardSummaries[0]],
  },
};
