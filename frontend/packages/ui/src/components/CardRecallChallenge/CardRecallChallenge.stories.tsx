import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardRecallChallenge } from "./CardRecallChallenge";

const meta: Meta<typeof CardRecallChallenge> = {
  title: "Flashcards/CardRecallChallenge",
  component: CardRecallChallenge,
  tags: ["autodocs"],
  args: { onRate: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-8 min-h-[700px] flex items-center justify-center"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CardRecallChallenge>;

export const FullRecall: Story = {
  args: {
    cardName: "Lightning Bolt",
    imageUrl: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",
    promptType: "full",
  },
};

export const StatCheck: Story = {
  args: {
    cardName: "Tarmogoyf",
    imageUrl: "https://cards.scryfall.io/normal/front/6/9/69daba76-96e8-4bcc-ab79-2f00189ad8fb.jpg",
    promptType: "stats",
  },
};

export const AbilityRecall: Story = {
  args: {
    cardName: "Wrath of God",
    imageUrl: "https://cards.scryfall.io/normal/front/6/6/664e6656-36a3-4f9e-a4c4-5ec4cae2a29c.jpg",
    promptType: "abilities",
  },
};

export const CostRecall: Story = {
  args: {
    cardName: "Dark Ritual",
    imageUrl: "https://cards.scryfall.io/normal/front/9/5/95f27eeb-6f14-4db3-adb9-9be5ed76b34b.jpg",
    promptType: "cost",
  },
};
