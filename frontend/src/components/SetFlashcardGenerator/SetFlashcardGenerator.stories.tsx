import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { SetFlashcardGenerator } from "./SetFlashcardGenerator";
import { setSummaries } from "@/fixtures";

const meta: Meta<typeof SetFlashcardGenerator> = {
  title: "Flashcards/SetFlashcardGenerator",
  component: SetFlashcardGenerator,
  tags: ["autodocs"],
  args: {
    onGenerate: async (cardType: string) => {
      await new Promise((r) => setTimeout(r, 800));
      const counts: Record<string, number> = {
        keyword_definition: 52,
        card_oracle: 309,
        card_mana_cost: 280,
        card_stats: 145,
      };
      return { created: counts[cardType] ?? 0, collection: `${cardType}_FIN` };
    },
    onComplete: fn(),
  },
  decorators: [(Story) => <div className="bg-bg-primary p-6"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof SetFlashcardGenerator>;

export const Default: Story = {
  args: { sets: setSummaries },
};
