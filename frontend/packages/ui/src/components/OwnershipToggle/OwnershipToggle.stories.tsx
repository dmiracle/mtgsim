import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { OwnershipToggle } from "./OwnershipToggle";

const meta: Meta<typeof OwnershipToggle> = {
  title: "Filters/OwnershipToggle",
  component: OwnershipToggle,
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
type Story = StoryObj<typeof OwnershipToggle>;

export const All: Story = {
  args: { value: "all", onChange: () => {} },
};

export const Owned: Story = {
  args: { value: "owned", onChange: () => {} },
};

export const Interactive: Story = {
  render: () => {
    const [value, setValue] = useState<"all" | "owned" | "not_owned">("all");
    return (
      <div className="space-y-3">
        <OwnershipToggle value={value} onChange={setValue} />
        <p className="text-text-muted text-sm">Filter: {value}</p>
      </div>
    );
  },
};
