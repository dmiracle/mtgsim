import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { DeckAppearances } from "./DeckAppearances";
import { cardDetail } from "@/fixtures";

const meta: Meta<typeof DeckAppearances> = {
  title: "CardDetail/DeckAppearances",
  component: DeckAppearances,
  tags: ["autodocs"],
  args: { onSelect: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-sm"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof DeckAppearances>;

export const Default: Story = {
  args: { decks: cardDetail.appears_in_decks },
};

export const Empty: Story = {
  args: { decks: [] },
};
