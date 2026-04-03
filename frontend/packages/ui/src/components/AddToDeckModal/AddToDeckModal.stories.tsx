import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { AddToDeckModal } from "./AddToDeckModal";
import { userDecks } from "@/fixtures";

const meta: Meta<typeof AddToDeckModal> = {
  title: "Decks/AddToDeckModal",
  component: AddToDeckModal,
  tags: ["autodocs"],
  args: { onClose: fn(), onAdd: fn(), onCreateDeck: fn() },
  parameters: { layout: "fullscreen" },
};

export default meta;
type Story = StoryObj<typeof AddToDeckModal>;

export const Open: Story = {
  args: {
    open: true,
    cardName: "Lightning Bolt",
    cardUuid: "abc-123",
    decks: userDecks,
  },
};

export const NoDecks: Story = {
  args: {
    open: true,
    cardName: "Counterspell",
    cardUuid: "def-456",
    decks: [],
  },
};

export const Adding: Story = {
  args: {
    open: true,
    cardName: "Lightning Bolt",
    cardUuid: "abc-123",
    decks: userDecks,
    adding: true,
  },
};
