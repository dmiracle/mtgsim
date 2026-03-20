import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { CardTypeFilter } from "./CardTypeFilter";

const meta: Meta<typeof CardTypeFilter> = {
  title: "Filters/CardTypeFilter",
  component: CardTypeFilter,
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
type Story = StoryObj<typeof CardTypeFilter>;

export const NoneSelected: Story = {
  args: { selected: [], onChange: () => {} },
};

export const Interactive: Story = {
  render: () => {
    const [selected, setSelected] = useState<string[]>(["Creature", "Instant"]);
    return (
      <div className="space-y-3">
        <CardTypeFilter selected={selected} onChange={setSelected} />
        <p className="text-text-muted text-sm">Selected: {selected.join(", ") || "none"}</p>
      </div>
    );
  },
};

export const SingleSelected: Story = {
  args: { selected: ["Land"], onChange: () => {} },
};
