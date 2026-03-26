import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { FlipCard } from "./FlipCard";

const meta: Meta<typeof FlipCard> = {
  title: "Flashcards/FlipCard",
  component: FlipCard,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-8 flex justify-center"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof FlipCard>;

export const Interactive: Story = {
  render: () => {
    const [flipped, setFlipped] = useState(false);
    return (
      <div className="w-[360px]">
        <FlipCard
          flipped={flipped}
          onFlip={() => setFlipped(!flipped)}
          front={
            <div className="bg-bg-secondary border-2 border-accent rounded-xl p-8 text-center min-h-[200px] flex items-center justify-center">
              <div>
                <p className="text-text-muted text-xs uppercase tracking-widest mb-2">Question</p>
                <h2 className="text-xl text-text-primary">What does Flying do?</h2>
                <p className="text-text-muted text-sm mt-4">Click to reveal</p>
              </div>
            </div>
          }
          back={
            <div className="bg-bg-secondary border-2 border-success rounded-xl p-8 text-center min-h-[200px] flex items-center justify-center">
              <div>
                <p className="text-text-muted text-xs uppercase tracking-widest mb-2">Answer</p>
                <p className="text-sm text-text-primary leading-relaxed">This creature can't be blocked except by creatures with flying and/or reach.</p>
              </div>
            </div>
          }
        />
        <p className="text-text-muted text-xs text-center mt-3">Click the card to flip</p>
      </div>
    );
  },
};
