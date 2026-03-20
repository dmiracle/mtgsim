import type { Meta, StoryObj } from "@storybook/react-vite";
import { HBarChart } from "./HBarChart";

const meta: Meta<typeof HBarChart> = {
  title: "Charts/HBarChart",
  component: HBarChart,
  tags: ["autodocs"],
  argTypes: {
    color: { control: "radio", options: ["accent", "success", "warning", "danger"] },
  },
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6 max-w-2xl">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof HBarChart>;

export const FormatDistribution: Story = {
  args: {
    title: "Format Distribution",
    data: [
      { label: "Commander", value: 15 },
      { label: "Modern", value: 12 },
      { label: "Standard", value: 5 },
      { label: "Legacy", value: 4 },
      { label: "Pioneer", value: 3 },
      { label: "Vintage", value: 2 },
      { label: "Pauper", value: 1 },
    ],
    color: "accent",
  },
};

export const TypeDistribution: Story = {
  args: {
    title: "Card Types (Top 6)",
    data: [
      { label: "Land", value: 20 },
      { label: "Creature", value: 16 },
      { label: "Instant", value: 16 },
      { label: "Sorcery", value: 8 },
      { label: "Enchant.", value: 4 },
      { label: "Artifact", value: 2 },
    ],
    color: "success",
    maxBars: 6,
  },
};

export const KeywordFrequencies: Story = {
  args: {
    title: "Keyword Abilities",
    data: [
      { label: "Flying", value: 32 },
      { label: "Trample", value: 18 },
      { label: "Deathtouch", value: 15 },
      { label: "Haste", value: 12 },
      { label: "First Strike", value: 10 },
      { label: "Lifelink", value: 8 },
    ],
    color: "warning",
  },
};

export const TopExpensiveCards: Story = {
  args: {
    title: "Most Expensive Cards",
    data: [
      { label: "The One Ring", value: 65 },
      { label: "Ragavan", value: 55 },
      { label: "Wrenn and Six", value: 48 },
      { label: "Force of Neg.", value: 42 },
      { label: "Solitude", value: 38 },
    ],
    color: "danger",
  },
};

export const NoAnimation: Story = {
  args: {
    title: "Static Bars",
    data: [
      { label: "A", value: 10 },
      { label: "B", value: 7 },
      { label: "C", value: 3 },
    ],
    animate: false,
  },
};
