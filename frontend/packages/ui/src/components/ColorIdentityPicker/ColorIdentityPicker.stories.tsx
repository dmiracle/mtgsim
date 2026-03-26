import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { ColorIdentityPicker } from "./ColorIdentityPicker";

const meta: Meta<typeof ColorIdentityPicker> = {
  title: "Filters/ColorIdentityPicker",
  component: ColorIdentityPicker,
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
type Story = StoryObj<typeof ColorIdentityPicker>;

export const NoneSelected: Story = {
  args: { selected: [], onChange: () => {} },
};

export const Interactive: Story = {
  render: () => {
    const [selected, setSelected] = useState<string[]>(["R"]);
    return (
      <div className="space-y-3">
        <ColorIdentityPicker selected={selected} onChange={setSelected} />
        <p className="text-text-muted text-sm">Selected: {selected.join(", ") || "none"}</p>
      </div>
    );
  },
};

export const MultiSelected: Story = {
  args: { selected: ["W", "U", "B"], onChange: () => {} },
};

export const AllSelected: Story = {
  args: { selected: ["W", "U", "B", "R", "G", "C"], onChange: () => {} },
};

export const Small: Story = {
  args: { selected: ["R", "G"], onChange: () => {}, size: "sm" },
};

export const Large: Story = {
  args: { selected: ["U"], onChange: () => {}, size: "lg" },
};
