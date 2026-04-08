import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { DeckCardItem } from "./DeckCardItem";
import { deckDetail } from "@/fixtures";

const meta: Meta<typeof DeckCardItem> = {
  title: "Decks/DeckCardItem",
  component: DeckCardItem,
  tags: ["autodocs"],
  args: { onRemove: fn(), onClick: fn() },
  decorators: [
    (Story) => (
      <div className="w-full max-w-lg bg-bg-primary p-2">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof DeckCardItem>;

const mainCards = deckDetail.main_board;
const sideCards = deckDetail.side_board;

export const Default: Story = {
  args: { card: mainCards[0] },
};

export const Creature: Story = {
  args: { card: mainCards[1] },
};

export const Sideboard: Story = {
  args: { card: sideCards[0] },
};

export const MissingCards: Story = {
  args: {
    card: { ...mainCards[0], owns_enough: false, missing_count: 2 },
  },
};

export const ReadOnly: Story = {
  args: { card: mainCards[0], onRemove: undefined },
};

export const List: Story = {
  render: (args) => (
    <div className="divide-y divide-border/50">
      {[...mainCards, ...sideCards].map((c) => (
        <DeckCardItem key={c.uuid} card={c} onRemove={args.onRemove} onClick={args.onClick} />
      ))}
    </div>
  ),
};
