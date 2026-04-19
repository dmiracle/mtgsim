import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { StrengthRating } from "./StrengthRating";

const meta: Meta<typeof StrengthRating> = {
  title: "Interactions/StrengthRating",
  component: StrengthRating,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof StrengthRating>;

export const ReadOnly: Story = { args: { value: 3 } };
export const Full: Story = { args: { value: 5 } };
export const Empty: Story = { args: { value: null } };
export const Low: Story = { args: { value: 1 } };

export const Interactive: Story = {
  render: () => {
    const [val, setVal] = useState<number | null>(3);
    return (
      <div className="space-y-2">
        <StrengthRating value={val} onChange={setVal} />
        <p className="text-xs text-text-muted">Strength: {val ?? "unset"}</p>
      </div>
    );
  },
};
