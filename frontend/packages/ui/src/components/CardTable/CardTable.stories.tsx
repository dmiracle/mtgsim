import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardTable } from "./CardTable";
import { cardSummaries } from "@/fixtures";

const meta: Meta<typeof CardTable> = {
  title: "Cards/CardTable",
  component: CardTable,
  tags: ["autodocs"],
  args: {
    onPageChange: fn(),
    onPin: fn(),
    onCardClick: fn(),
    onSetClick: fn(),
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
type Story = StoryObj<typeof CardTable>;

export const Default: Story = {
  args: {
    cards: cardSummaries,
    pagination: { page: 1, pages: 5, total: 250, limit: 50 },
  },
};

export const WithPinnedCards: Story = {
  args: {
    cards: cardSummaries,
    pinnedIds: new Set([cardSummaries[0].uuid, cardSummaries[2].uuid]),
    pagination: { page: 1, pages: 3, total: 150, limit: 50 },
  },
};

export const Empty: Story = {
  args: { cards: [] },
};
