import type { Meta, StoryObj } from "@storybook/react-vite";
import { DonutChart } from "./DonutChart";

const meta: Meta<typeof DonutChart> = {
  title: "Charts/DonutChart",
  component: DonutChart,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6 max-w-lg">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof DonutChart>;

export const ColorDistribution: Story = {
  args: {
    title: "Color Distribution",
    data: [
      { label: "White", value: 12, color: "#f9faf4" },
      { label: "Blue", value: 8, color: "#0e68ab" },
      { label: "Black", value: 10, color: "#150b00" },
      { label: "Red", value: 15, color: "#d3202a" },
      { label: "Green", value: 6, color: "#00733e" },
    ],
  },
};

export const RarityDistribution: Story = {
  args: {
    title: "Rarity Breakdown",
    data: [
      { label: "Common", value: 101 },
      { label: "Uncommon", value: 100 },
      { label: "Rare", value: 78 },
      { label: "Mythic", value: 24 },
    ],
  },
};

export const Small: Story = {
  args: {
    title: "Small Donut",
    data: [
      { label: "A", value: 30 },
      { label: "B", value: 70 },
    ],
    size: 120,
  },
};

export const Large: Story = {
  args: {
    title: "Large Donut",
    data: [
      { label: "Creature", value: 16 },
      { label: "Instant", value: 16 },
      { label: "Sorcery", value: 8 },
      { label: "Land", value: 20 },
      { label: "Enchantment", value: 4 },
      { label: "Artifact", value: 2 },
    ],
    size: 300,
  },
};

export const Pie: Story = {
  args: {
    title: "Full Pie (no hole)",
    data: [
      { label: "Modern", value: 12 },
      { label: "Commander", value: 15 },
      { label: "Standard", value: 5 },
    ],
    innerRadiusRatio: 0,
  },
};

export const NoLegend: Story = {
  args: {
    title: "Donut Only",
    data: [
      { label: "Owned", value: 180 },
      { label: "Missing", value: 50 },
    ],
    showLegend: false,
  },
};
