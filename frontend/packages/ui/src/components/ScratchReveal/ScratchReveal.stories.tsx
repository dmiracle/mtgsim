import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { ScratchReveal } from "./ScratchReveal";

const meta: Meta<typeof ScratchReveal> = {
  title: "Flashcards/ScratchReveal",
  component: ScratchReveal,
  tags: ["autodocs"],
  args: { onRevealChange: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-8 w-[360px] mx-auto"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof ScratchReveal>;

export const Default: Story = {
  args: {
    imageUrl: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",
  },
};

export const HeavyBlur: Story = {
  args: {
    imageUrl: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",
    blurAmount: 40,
  },
};

export const LargeBrush: Story = {
  args: {
    imageUrl: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",
    brushSize: 80,
  },
};
