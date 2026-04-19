import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { InteractionListItem } from "./InteractionListItem";
import { interactions } from "@/fixtures";

const meta: Meta<typeof InteractionListItem> = {
  title: "Interactions/InteractionListItem",
  component: InteractionListItem,
  tags: ["autodocs"],
  args: { cardUuid: "bolt-uuid", onEdit: fn(), onDelete: fn(), onCardClick: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-4 max-w-lg"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof InteractionListItem>;

export const Synergy: Story = { args: { interaction: interactions[0] } };
export const Combo: Story = { args: { interaction: interactions[1] } };
export const Counter: Story = { args: { interaction: interactions[2] } };
export const NoDescription: Story = { args: { interaction: interactions[4] } };
export const ReadOnly: Story = { args: { interaction: interactions[0], onEdit: undefined, onDelete: undefined } };
