import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { DeckBrowserPage } from "./DeckBrowserPage";
import { deckSummaries } from "@/fixtures";

const meta: Meta<typeof DeckBrowserPage> = {
  title: "Pages/DeckBrowserPage",
  component: DeckBrowserPage,
  tags: ["autodocs"],
  args: { onDeckClick: fn(), onPageChange: fn(), onCreateDeck: fn(), onImportDeck: fn() },
  parameters: { layout: "padded" },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-4xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof DeckBrowserPage>;

export const Default: Story = {
  args: {
    decks: deckSummaries,
    pagination: { page: 1, pages: 3, total: 42, limit: 50 },
    availableFormats: ["standard", "modern", "commander", "legacy", "pioneer"],
    availableSources: ["user", "import", "precon"],
  },
};

export const Empty: Story = {
  args: {
    decks: [],
    pagination: { page: 1, pages: 1, total: 0, limit: 50 },
    availableFormats: [],
    availableSources: [],
  },
};
