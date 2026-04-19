import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { InteractionList } from "./InteractionList";
import { interactions } from "@/fixtures";

const meta: Meta<typeof InteractionList> = {
  title: "Interactions/InteractionList",
  component: InteractionList,
  tags: ["autodocs"],
  args: { cardUuid: "bolt-uuid", onAdd: fn(), onEdit: fn(), onDelete: fn(), onCardClick: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof InteractionList>;

export const WithInteractions: Story = {
  args: { interactions },
};

export const Empty: Story = {
  args: { interactions: [] },
};

export const CombosOnly: Story = {
  args: { interactions: interactions.filter((i) => i.interaction_type === "combo") },
};

export const ReadOnly: Story = {
  args: { interactions, onAdd: undefined, onEdit: undefined, onDelete: undefined },
};
