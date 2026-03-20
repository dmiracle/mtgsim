import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardBrowserPage } from "./CardBrowserPage";
import { cardSummaries, keywordFrequencies } from "@/fixtures";

const sampleTags = [
  { tag: "removal", count: 245 },
  { tag: "burn", count: 128 },
  { tag: "counter", count: 89 },
  { tag: "draw", count: 312 },
];

const meta: Meta<typeof CardBrowserPage> = {
  title: "Pages/CardBrowserPage",
  component: CardBrowserPage,
  tags: ["autodocs"],
  args: { onCardClick: fn(), onSetClick: fn(), onPin: fn(), onAddToDeck: fn(), onPageChange: fn() },
  parameters: { layout: "padded" },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-6xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CardBrowserPage>;

export const WithResults: Story = {
  args: {
    cards: cardSummaries,
    pagination: { page: 1, pages: 5, total: 250, limit: 50 },
    availableTags: sampleTags,
    keywordFrequencies,
    pinnedIds: new Set([cardSummaries[0].uuid]),
  },
};

export const Empty: Story = {
  args: {
    cards: [],
    pagination: { page: 1, pages: 1, total: 0, limit: 50 },
    availableTags: [],
    keywordFrequencies: { keyword_abilities: {}, keyword_actions: {}, ability_words: {} },
    pinnedIds: new Set(),
  },
};
