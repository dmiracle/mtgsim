import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CollectionStatus } from "./CollectionStatus";
import { cardDetail } from "@/fixtures";

const meta: Meta<typeof CollectionStatus> = {
  title: "CardDetail/CollectionStatus",
  component: CollectionStatus,
  tags: ["autodocs"],
  args: { onAddToCollection: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-xs"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CollectionStatus>;

export const Owned: Story = {
  args: { owns: true, collection: cardDetail.collection },
};

export const NotOwned: Story = {
  args: { owns: false, collection: null },
};
