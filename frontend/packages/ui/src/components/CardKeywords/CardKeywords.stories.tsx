import type { Meta, StoryObj } from "@storybook/react-vite";
import { CardKeywords } from "./CardKeywords";

const meta: Meta<typeof CardKeywords> = {
  title: "CardDetail/CardKeywords",
  component: CardKeywords,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-md"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CardKeywords>;

export const MultipleGroups: Story = {
  args: {
    groups: [
      {
        category: "Keyword Abilities",
        keywords: [
          { term: "Flying", definition: "This creature can't be blocked except by creatures with flying and/or reach." },
          { term: "Trample", definition: "This creature can deal excess combat damage to the player or planeswalker it's attacking." },
        ],
      },
      {
        category: "Keyword Actions",
        keywords: [
          { term: "Destroy", definition: "Move a permanent from the battlefield to its owner's graveyard." },
        ],
      },
      {
        category: "Ability Words",
        keywords: [
          { term: "Delirium", definition: "An ability that checks if you have four or more card types in your graveyard." },
        ],
      },
    ],
  },
};

export const SingleKeyword: Story = {
  args: {
    groups: [
      {
        category: "Keyword Abilities",
        keywords: [{ term: "Haste", definition: "This creature can attack and tap as soon as it comes under your control." }],
      },
    ],
  },
};

export const Empty: Story = {
  args: { groups: [] },
};
