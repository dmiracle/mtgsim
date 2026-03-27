import type { Meta, StoryObj } from "@storybook/react";
import { RecallGuessForm } from "./RecallGuessForm";

const meta: Meta<typeof RecallGuessForm> = {
  title: "Flashcards/RecallGuessForm",
  component: RecallGuessForm,
  decorators: [
    (Story) => (
      <div className="max-w-[400px] mx-auto p-4 bg-bg-primary min-h-screen">
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof RecallGuessForm>;

export const Default: Story = {
  args: {
    cardName: "Tarmogoyf",
    onReveal: (guess) => console.log("Guess:", guess),
  },
};

export const LongName: Story = {
  args: {
    cardName: "Emrakul, the Aeons Torn",
    onReveal: (guess) => console.log("Guess:", guess),
  },
};
