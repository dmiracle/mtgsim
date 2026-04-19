import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { DeckCardList } from "./DeckCardList";
import { deckDetail } from "@/fixtures";

const meta: Meta<typeof DeckCardList> = {
  title: "Decks/DeckCardList",
  component: DeckCardList,
  tags: ["autodocs"],
  args: {
    onRemove: fn(),
    onCardClick: fn(),
    onAddCard: fn(),
  },
  decorators: [
    (Story) => (
      <div className="w-full max-w-lg bg-bg-primary p-4">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof DeckCardList>;

export const MainBoard: Story = {
  args: {
    title: "Main Board",
    cards: deckDetail.main_board,
  },
};

export const Sideboard: Story = {
  args: {
    title: "Sideboard",
    cards: deckDetail.side_board,
  },
};

export const Empty: Story = {
  args: {
    title: "Commander",
    cards: [],
  },
};

export const ReadOnly: Story = {
  args: {
    title: "Main Board",
    cards: deckDetail.main_board,
    onRemove: undefined,
    onAddCard: undefined,
  },
};

export const FullDeck: Story = {
  render: (args) => (
    <div className="space-y-4">
      {deckDetail.commander.length > 0 && (
        <DeckCardList
          title="Commander"
          cards={deckDetail.commander}
          onRemove={args.onRemove}
          onCardClick={args.onCardClick}
          onAddCard={args.onAddCard}
        />
      )}
      <DeckCardList
        title="Main Board"
        cards={deckDetail.main_board}
        onRemove={args.onRemove}
        onCardClick={args.onCardClick}
        onAddCard={args.onAddCard}
      />
      <DeckCardList
        title="Sideboard"
        cards={deckDetail.side_board}
        onRemove={args.onRemove}
        onCardClick={args.onCardClick}
        onAddCard={args.onAddCard}
      />
    </div>
  ),
};
