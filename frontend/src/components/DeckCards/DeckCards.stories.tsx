import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { DeckCards } from "./DeckCards";
import type { CardFilters } from "@/components/CardFilterBar/CardFilterBar";
import { deckDetail } from "@/fixtures";

const emptyFilters: CardFilters = {
  text: "", colors: [], rarities: [], types: [], tags: [],
  ownership: "all", sort: "name", order: "asc", unique: false,
};

const meta: Meta<typeof DeckCards> = {
  title: "Decks/DeckCards",
  component: DeckCards,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-5xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof DeckCards>;

export const Interactive: Story = {
  render: () => {
    const [filters, setFilters] = useState(emptyFilters);
    return (
      <DeckCards
        commander={deckDetail.commander}
        main_board={deckDetail.main_board}
        side_board={deckDetail.side_board}
        filters={filters}
        onFiltersChange={setFilters}
      />
    );
  },
};
