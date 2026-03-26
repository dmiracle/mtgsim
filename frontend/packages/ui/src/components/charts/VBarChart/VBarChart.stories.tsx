import type { Meta, StoryObj } from "@storybook/react-vite";
import { VBarChart } from "./VBarChart";

const meta: Meta<typeof VBarChart> = {
  title: "Charts/VBarChart",
  component: VBarChart,
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
type Story = StoryObj<typeof VBarChart>;

export const ManaCurve: Story = {
  args: {
    title: "Mana Curve",
    data: [
      { label: "0", value: 2 },
      { label: "1", value: 20 },
      { label: "2", value: 16 },
      { label: "3", value: 8 },
      { label: "4", value: 4 },
      { label: "5", value: 2 },
      { label: "6", value: 1 },
      { label: "7+", value: 1 },
    ],
    color: "accent",
  },
};

export const PriceHistogram: Story = {
  args: {
    title: "Deck Price Distribution",
    data: [
      { label: "$0-50", value: 8 },
      { label: "$50-100", value: 12 },
      { label: "$100-200", value: 10 },
      { label: "$200-500", value: 7 },
      { label: "$500+", value: 5 },
    ],
    color: "success",
    height: 220,
  },
};

export const RarityBreakdown: Story = {
  args: {
    title: "Rarity Distribution",
    data: [
      { label: "Common", value: 101 },
      { label: "Uncommon", value: 100 },
      { label: "Rare", value: 78 },
      { label: "Mythic", value: 24 },
    ],
    color: "warning",
  },
};

export const Tall: Story = {
  args: {
    title: "Tall Chart",
    data: [
      { label: "A", value: 50 },
      { label: "B", value: 30 },
      { label: "C", value: 80 },
      { label: "D", value: 15 },
    ],
    height: 320,
    color: "danger",
  },
};
