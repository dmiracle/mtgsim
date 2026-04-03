import type { Meta, StoryObj } from "@storybook/react-vite";
import { DeckStats } from "./DeckStats";
import { deckDetail } from "@/fixtures";

const meta: Meta<typeof DeckStats> = {
  title: "Decks/DeckStats",
  component: DeckStats,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-4xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof DeckStats>;

export const Default: Story = {
  args: {
    stats: deckDetail.stats,
    legality: deckDetail.legality,
    price: deckDetail.price,
  },
};
