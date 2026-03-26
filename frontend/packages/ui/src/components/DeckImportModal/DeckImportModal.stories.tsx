import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { DeckImportModal } from "./DeckImportModal";

const meta: Meta<typeof DeckImportModal> = {
  title: "Decks/DeckImportModal",
  component: DeckImportModal,
  tags: ["autodocs"],
  args: { onClose: fn(), onImport: fn(), onViewDeck: fn() },
  parameters: { layout: "fullscreen" },
};

export default meta;
type Story = StoryObj<typeof DeckImportModal>;

export const Empty: Story = {
  args: { open: true },
};

export const Importing: Story = {
  args: { open: true, importing: true },
};

export const WithResult: Story = {
  args: {
    open: true,
    result: {
      deck_id: "new-deck-123",
      deck_name: "Imported Burn",
      total_cards: 60,
      resolved: [
        { name: "Lightning Bolt", matched_name: "Lightning Bolt", match_type: "exact", match_score: 1, count: 4 },
        { name: "Goblin Guide", matched_name: "Goblin Guide", match_type: "exact", match_score: 1, count: 4 },
        { name: "Lava Spike", matched_name: "Lava Spike", match_type: "exact", match_score: 1, count: 4 },
        { name: "Eidlon of Great Revel", matched_name: "Eidolon of the Great Revel", match_type: "fuzzy", match_score: 0.87, count: 4 },
        { name: "Skaab Wranger", matched_name: "Skaab Wranger", match_type: "created", match_score: 0, count: 2 },
      ],
      legality: [
        { format: "modern", legal: true, reason: "" },
        { format: "legacy", legal: true, reason: "" },
        { format: "standard", legal: false, reason: "Contains non-standard cards" },
      ],
    },
  },
};
