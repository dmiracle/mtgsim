import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { InteractionBuilder } from "./InteractionBuilder";
import { cardSummaries, interactions } from "@/fixtures";
import type { InteractionCard } from "@/types/api";
import type { CardFilters } from "@/components/CardFilterBar/CardFilterBar";

const sourceCard: InteractionCard = {
  uuid: "bolt-uuid",
  name: "Lightning Bolt",
  type_line: "Instant",
  mana_cost: "{R}",
  image_url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",
};

const emptyFilters: CardFilters = {
  text: "", colors: [], rarities: [], types: [], tags: [], manaValue: [],
  ownership: "all", platform: "any", sort: "name", order: "asc", unique: false, subtype: "", sets: [], formats: [],
};

const meta: Meta<typeof InteractionBuilder> = {
  title: "Interactions/InteractionBuilder",
  component: InteractionBuilder,
  tags: ["autodocs"],
  parameters: { layout: "padded" },
  args: {
    sourceCard,
    cards: cardSummaries,
    filters: emptyFilters,
    onFiltersChange: fn(),
    onSave: fn(),
    onBack: fn(),
    onCardClick: fn(),
  },
  decorators: [(Story) => <div className="bg-bg-primary max-w-5xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof InteractionBuilder>;

export const Default: Story = {};

export const WithPagination: Story = {
  args: {
    pagination: { page: 1, pages: 3, total: 15, limit: 5 },
    onPageChange: fn(),
  },
};

export const Editing: Story = {
  args: {
    editing: interactions[0],
    cards: cardSummaries,
  },
};

export const Interactive: Story = {
  render: () => {
    const [filters, setFilters] = useState(emptyFilters);
    return (
      <InteractionBuilder
        sourceCard={sourceCard}
        cards={cardSummaries}
        filters={filters}
        onFiltersChange={setFilters}
        onSave={(data) => console.log("save", data)}
        onBack={() => console.log("back")}
      />
    );
  },
};
