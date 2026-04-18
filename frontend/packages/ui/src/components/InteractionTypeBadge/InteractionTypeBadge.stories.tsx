import type { Meta, StoryObj } from "@storybook/react-vite";
import { InteractionTypeBadge } from "./InteractionTypeBadge";

const meta: Meta<typeof InteractionTypeBadge> = {
  title: "Interactions/InteractionTypeBadge",
  component: InteractionTypeBadge,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6 flex gap-3"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof InteractionTypeBadge>;

export const Combo: Story = { args: { type: "combo" } };
export const Synergy: Story = { args: { type: "synergy" } };
export const Counter: Story = { args: { type: "counter" } };
export const Medium: Story = { args: { type: "combo", size: "md" } };

export const AllTypes: Story = {
  render: () => (
    <div className="flex gap-2">
      <InteractionTypeBadge type="combo" />
      <InteractionTypeBadge type="synergy" />
      <InteractionTypeBadge type="counter" />
    </div>
  ),
};
