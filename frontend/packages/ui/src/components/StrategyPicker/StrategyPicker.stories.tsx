import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { StrategyPicker } from "./StrategyPicker";
import { strategies as mockStrategies } from "@/fixtures";

const meta: Meta<typeof StrategyPicker> = {
  title: "Filters/StrategyPicker",
  component: StrategyPicker,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof StrategyPicker>;

export const Interactive: Story = {
  render: () => {
    const [selected, setSelected] = useState(["keywords", "tags"]);
    return (
      <div className="space-y-3">
        <StrategyPicker strategies={mockStrategies} selected={selected} onChange={setSelected} />
        <p className="text-xs text-text-muted">Selected: {selected.join(", ")}</p>
      </div>
    );
  },
};

export const AllSelected: Story = {
  args: {
    strategies: mockStrategies,
    selected: mockStrategies.map((s) => s.name),
    onChange: () => {},
  },
};

export const OneSelected: Story = {
  args: {
    strategies: mockStrategies,
    selected: ["oracle_vector"],
    onChange: () => {},
  },
};
