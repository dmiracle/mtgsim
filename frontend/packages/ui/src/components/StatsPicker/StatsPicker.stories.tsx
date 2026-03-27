import type { Meta, StoryObj } from "@storybook/react";
import { StatsPicker } from "./StatsPicker";

const meta: Meta<typeof StatsPicker> = {
  title: "App-v2/Recall Inputs/StatsPicker",
  component: StatsPicker,
  decorators: [(Story) => <div className="max-w-sm mx-auto p-4 bg-bg-primary"><Story /></div>],
};
export default meta;

type Story = StoryObj<typeof StatsPicker>;

export const Default: Story = {
  args: { onChange: (p, t) => console.log("Stats:", p, t) },
};

export const Preselected: Story = {
  args: {
    power: "3",
    toughness: "3",
    onChange: (p, t) => console.log("Stats:", p, t),
  },
};
