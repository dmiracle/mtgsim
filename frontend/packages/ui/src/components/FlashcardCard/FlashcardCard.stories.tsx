import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { FlashcardCard } from "./FlashcardCard";
import { keywordFlashcard, cardOracleFlashcard, manaCostFlashcard, cardStatsFlashcard } from "@/fixtures/flashcards";

const meta: Meta<typeof FlashcardCard> = {
  title: "Flashcards/FlashcardCard",
  component: FlashcardCard,
  tags: ["autodocs"],
  args: { onRate: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-8 min-h-[600px] flex items-center justify-center"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof FlashcardCard>;

export const KeywordDefinition: Story = {
  args: { flashcard: keywordFlashcard },
};

export const CardOracle: Story = {
  args: { flashcard: cardOracleFlashcard },
};

export const ManaCost: Story = {
  args: { flashcard: manaCostFlashcard },
};

export const CardStats: Story = {
  args: { flashcard: cardStatsFlashcard },
};
