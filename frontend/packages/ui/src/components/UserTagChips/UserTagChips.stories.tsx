import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { UserTagChips } from "./UserTagChips";

const meta: Meta<typeof UserTagChips> = {
  title: "UserData/UserTagChips",
  component: UserTagChips,
  tags: ["autodocs"],
  parameters: { layout: "padded" },
  args: {
    userTags: ["removal", "wincon"],
    oracleTags: ["burn", "instant-speed"],
  },
  decorators: [(Story) => <div className="bg-bg-primary p-4 max-w-md"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof UserTagChips>;

export const Default: Story = {};

export const Editable: Story = {
  args: { onRemove: fn(), onAdd: fn(), onTagClick: fn() },
};

export const UserTagsOnly: Story = {
  args: { oracleTags: [] },
};

export const OracleTagsOnly: Story = {
  args: { userTags: [] },
};

export const EmptyWithAdd: Story = {
  args: { userTags: [], oracleTags: [], onAdd: fn() },
};

export const ManyTags: Story = {
  args: {
    userTags: ["removal", "wincon", "card-advantage", "enabler", "sacrifice-outlet", "graveyard-hate"],
    oracleTags: ["burn", "instant-speed", "reach", "tempo"],
    onRemove: fn(),
    onAdd: fn(),
  },
};
