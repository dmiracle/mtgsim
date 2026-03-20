import type { Meta, StoryObj } from "@storybook/react-vite";
import { StatCard } from "./StatCard";

const meta: Meta<typeof StatCard> = {
  title: "Shared/StatCard",
  component: StatCard,
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof StatCard>;

export const TotalDecks: Story = {
  args: { label: "Total Decks", value: 42 },
};

export const TotalCards: Story = {
  args: { label: "Cards with Prices", value: "25,000", subtitle: "of 28,500 total" },
};

export const Price: Story = {
  args: { label: "Collection Value", value: "$1,245.50" },
};
