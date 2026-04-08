import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { DeckDetailPage } from "./DeckDetailPage";
import { deckDetail, cardSummaries } from "@/fixtures";

const meta: Meta<typeof DeckDetailPage> = {
  title: "Pages/DeckDetailPage",
  component: DeckDetailPage,
  tags: ["autodocs"],
  args: { onBack: fn(), onCardClick: fn(), onSetClick: fn() },
  parameters: { layout: "padded" },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-5xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof DeckDetailPage>;

export const Default: Story = {
  args: { deck: deckDetail },
};

export const Editable: Story = {
  args: {
    deck: deckDetail,
    editable: true,
    searchResults: cardSummaries,
    onAddCard: fn(),
    onRemoveCard: fn(),
    onSearchCards: fn(),
    onTogglePin: fn(),
    onDuplicate: fn(),
    onDelete: fn(),
  },
};
