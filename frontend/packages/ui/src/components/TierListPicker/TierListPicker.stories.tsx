import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { TierListPicker } from "./TierListPicker";
import { tierListSummaries } from "@/fixtures";

const meta: Meta<typeof TierListPicker> = {
  title: "UserData/TierListPicker",
  component: TierListPicker,
  tags: ["autodocs"],
  parameters: { layout: "padded" },
  args: {
    lists: tierListSummaries,
    selectedId: 1,
    onSelect: fn(),
    onCreate: fn(),
  },
  decorators: [(Story) => <div className="bg-bg-primary p-4 max-w-md min-h-[220px]"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof TierListPicker>;

export const Default: Story = {};

export const NothingSelected: Story = {
  args: { selectedId: null },
};

export const NoLists: Story = {
  args: { lists: [], selectedId: null },
};

export const WithoutCreate: Story = {
  args: { onCreate: undefined },
};

export const Interactive: Story = {
  render: () => {
    const [selectedId, setSelectedId] = useState<number | null>(1);
    return (
      <TierListPicker
        lists={tierListSummaries}
        selectedId={selectedId}
        onSelect={setSelectedId}
        onCreate={(data) => console.log("create", data)}
      />
    );
  },
};
