import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardQuizGenerator } from "./CardQuizGenerator";
import { setSummaries } from "@/fixtures";

const meta: Meta<typeof CardQuizGenerator> = {
  title: "Flashcards/CardQuizGenerator",
  component: CardQuizGenerator,
  tags: ["autodocs"],
  args: {
    onGenerate: async (cardType: string) => {
      await new Promise((r) => setTimeout(r, 500));
      return { created: Math.floor(Math.random() * 200) + 50, collection: `${cardType}_test` };
    },
    onComplete: fn(),
  },
  decorators: [(Story) => <div className="bg-bg-primary p-6"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CardQuizGenerator>;

export const Default: Story = {
  args: { sets: setSummaries },
};
