import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { OracleTagsDropdown } from "./OracleTagsDropdown";

const sampleTags = [
  { tag: "removal", count: 245 },
  { tag: "burn", count: 128 },
  { tag: "board-wipe", count: 67 },
  { tag: "counter", count: 89 },
  { tag: "draw", count: 312 },
  { tag: "ramp", count: 156 },
  { tag: "token", count: 201 },
  { tag: "graveyard", count: 98 },
  { tag: "lifegain", count: 134 },
  { tag: "sacrifice", count: 76 },
  { tag: "equipment", count: 45 },
  { tag: "tribal", count: 112 },
];

const meta: Meta<typeof OracleTagsDropdown> = {
  title: "Filters/OracleTagsDropdown",
  component: OracleTagsDropdown,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6 min-h-[400px]">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof OracleTagsDropdown>;

export const Default: Story = {
  args: { tags: sampleTags, selected: [], onChange: () => {} },
};

export const Interactive: Story = {
  render: () => {
    const [selected, setSelected] = useState<string[]>(["removal", "burn"]);
    return (
      <div className="space-y-3">
        <OracleTagsDropdown tags={sampleTags} selected={selected} onChange={setSelected} />
        <p className="text-text-muted text-sm">Selected: {selected.join(", ") || "none"}</p>
      </div>
    );
  },
};

export const WithSelections: Story = {
  args: { tags: sampleTags, selected: ["removal", "burn", "counter"], onChange: () => {} },
};

export const Empty: Story = {
  args: { tags: [], selected: [], onChange: () => {} },
};
