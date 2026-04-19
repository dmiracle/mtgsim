import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { AddCardToDeckModal } from "./AddCardToDeckModal";
import { cardSummaries } from "@/fixtures";

const meta: Meta<typeof AddCardToDeckModal> = {
  title: "Decks/AddCardToDeckModal",
  component: AddCardToDeckModal,
  tags: ["autodocs"],
  parameters: { layout: "fullscreen" },
  args: {
    open: true,
    deckName: "Mono Red Burn",
    searchResults: [],
    searching: false,
    onSearch: fn(),
    onAdd: fn(),
    onClose: fn(),
  },
};

export default meta;
type Story = StoryObj<typeof AddCardToDeckModal>;

export const Empty: Story = {};

export const WithResults: Story = {
  args: {
    searchResults: cardSummaries,
  },
};

export const Searching: Story = {
  args: {
    searching: true,
  },
};

export const NoResults: Story = {
  args: {
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
        setResults(
          cardSummaries.filter(
            (c) =>
              c.name.toLowerCase().includes(q.toLowerCase()) ||
              c.text.toLowerCase().includes(q.toLowerCase()),
          ),
        );
        setSearching(false);
      }, 400);
    }

    return (
      <div className="h-screen bg-bg-primary p-8">
        <button
          onClick={() => setOpen(true)}
          className="text-sm px-3 py-1.5 rounded bg-accent text-white"
        >
          Open Modal
        </button>
        <AddCardToDeckModal
          open={open}
          deckName="Mono Red Burn"
          searchResults={results}
          searching={searching}
          onSearch={handleSearch}
          onAdd={fn()}
          onClose={() => setOpen(false)}
        />
      </div>
    );
  },
};
