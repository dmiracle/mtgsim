import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { RarityFilter } from "./RarityFilter";

const meta: Meta<typeof RarityFilter> = {
  title: "Filters/RarityFilter",
  component: RarityFilter,
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
type Story = StoryObj<typeof RarityFilter>;

export const NoneSelected: Story = {
  args: { selected: [], onChange: () => {} },
};

export const Interactive: Story = {
  render: () => {
    const [selected, setSelected] = useState<string[]>(["rare"]);
    return (
      <div className="space-y-3">
        <RarityFilter selected={selected} onChange={setSelected} />
        <p className="text-text-muted text-sm">Selected: {selected.join(", ") || "none"}</p>
      </div>
    );
  },
};

export const AllSelected: Story = {
  args: { selected: ["common", "uncommon", "rare", "mythic"], onChange: () => {} },
};
