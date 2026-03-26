import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardQuiz } from "./CardQuiz";

const meta: Meta<typeof CardQuiz> = {
  title: "Flashcards/CardQuiz",
  component: CardQuiz,
  tags: ["autodocs"],
  args: { onRate: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-4 sm:p-8"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CardQuiz>;

export const LightningBolt: Story = {
  args: {
    cardName: "Lightning Bolt",
    imageUrl: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",
    manaValue: 1,
    manaCost: "{R}",
    typeLine: "Instant",
    rarity: "common",
    powerToughness: null,
    oracleText: "Lightning Bolt deals 3 damage to any target.",
  },
};

export const Tarmogoyf: Story = {
  args: {
    cardName: "Tarmogoyf",
    imageUrl: "https://cards.scryfall.io/normal/front/6/9/69daba76-96e8-4bcc-ab79-2f00189ad8fb.jpg",
    manaValue: 2,
    manaCost: "{1}{G}",
    typeLine: "Creature — Lhurgoyf",
    rarity: "mythic",
    powerToughness: "*/1+*",
    oracleText: "Tarmogoyf's power is equal to the number of card types among cards in all graveyards and its toughness is equal to that number plus 1.",
  },
};

export const QuestingBeast: Story = {
  args: {
    cardName: "Questing Beast",
    imageUrl: "https://cards.scryfall.io/normal/front/e/4/e41cf82d-3213-47ce-a015-6e51a8b07e4f.jpg",
    manaValue: 4,
    manaCost: "{2}{G}{G}",
    typeLine: "Legendary Creature — Beast",
    rarity: "mythic",
    powerToughness: "4/4",
    oracleText: "Vigilance, deathtouch, haste\nQuesting Beast can't be blocked by creatures with power 2 or less.\nCombat damage that would be dealt by creatures you control can't be prevented.\nWhenever Questing Beast deals combat damage to an opponent, it deals that much damage to target planeswalker that player controls.",
  },
};

export const WrathOfGod: Story = {
  args: {
    cardName: "Wrath of God",
    imageUrl: "https://cards.scryfall.io/normal/front/6/6/664e6656-36a3-4f9e-a4c4-5ec4cae2a29c.jpg",
    manaValue: 4,
    manaCost: "{2}{W}{W}",
    typeLine: "Sorcery",
    rarity: "rare",
    powerToughness: null,
    oracleText: "Destroy all creatures. They can't be regenerated.",
  },
};
