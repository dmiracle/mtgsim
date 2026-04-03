import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { DeckCreateModal } from "./DeckCreateModal";

const meta: Meta<typeof DeckCreateModal> = {
  title: "Decks/DeckCreateModal",
  component: DeckCreateModal,
  tags: ["autodocs"],
  args: { onClose: fn(), onCreate: fn() },
  parameters: { layout: "fullscreen" },
};

export default meta;
type Story = StoryObj<typeof DeckCreateModal>;

export const Open: Story = {
  args: { open: true },
};

export const Creating: Story = {
  args: { open: true, creating: true },
};
