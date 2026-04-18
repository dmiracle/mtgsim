import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { InteractionBuilder } from "./InteractionBuilder";
import { cardSummaries, interactions } from "@/fixtures";
import type { InteractionCard } from "@/types/api";

const sourceCard: InteractionCard = {
  uuid: "bolt-uuid",
  name: "Lightning Bolt",
  type_line: "Instant",
  mana_cost: "{R}",
  image_url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",
};

const meta: Meta<typeof InteractionBuilder> = {
  title: "Interactions/InteractionBuilder",
  component: InteractionBuilder,
  tags: ["autodocs"],
  parameters: { layout: "fullscreen" },
  args: {
    open: true,
    sourceCard,
    searchResults: [],
    onSearch: fn(),
    onSave: fn(),
    onClose: fn(),
  },
};

export default meta;
type Story = StoryObj<typeof InteractionBuilder>;

export const Empty: Story = {};

export const WithResults: Story = {
  args: { searchResults: cardSummaries },
};

export const Editing: Story = {
  args: {
    editing: interactions[0],
    searchResults: [],
  },
};

export const Interactive: Story = {
  render: () => {
    const [open, setOpen] = useState(true);
    const [results, setResults] = useState(cardSummaries);
    const [searching, setSearching] = useState(false);

    function handleSearch(q: string) {
      setSearching(true);
      setTimeout(() => {
        setResults(cardSummaries.filter((c) =>
          c.name.toLowerCase().includes(q.toLowerCase()) ||
          c.text.toLowerCase().includes(q.toLowerCase()),
        ));
        setSearching(false);
      }, 300);
    }

    return (
      <div className="h-screen bg-bg-primary p-8">
        <button onClick={() => setOpen(true)} className="text-sm px-3 py-1.5 rounded bg-accent text-white">
          Open Builder
        </button>
        <InteractionBuilder
          open={open}
          sourceCard={sourceCard}
          searchResults={results}
          searching={searching}
          onSearch={handleSearch}
          onSave={(data) => { console.log("save", data); setOpen(false); }}
          onClose={() => setOpen(false)}
        />
      </div>
    );
  },
};
