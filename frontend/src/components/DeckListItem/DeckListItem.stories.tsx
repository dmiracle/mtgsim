import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { DeckListItem } from "./DeckListItem";
import { deckSummaries } from "@/fixtures";

const meta: Meta<typeof DeckListItem> = {
  title: "Decks/DeckListItem",
  component: DeckListItem,
  tags: ["autodocs"],
  args: { onClick: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-xl space-y-2"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof DeckListItem>;

export const MonoRed: Story = {
  args: { deck: deckSummaries[0] },
};

export const MultiColor: Story = {
  args: { deck: deckSummaries[1] },
};

export const Commander: Story = {
  args: { deck: deckSummaries[2] },
};

export const List: Story = {
  render: () => (
    <div className="space-y-2">
      {deckSummaries.map((d) => (
        <DeckListItem key={d.file} deck={d} onClick={() => {}} />
      ))}
    </div>
  ),
};
