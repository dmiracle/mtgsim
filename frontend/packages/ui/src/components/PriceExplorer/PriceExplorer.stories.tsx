import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { PriceExplorer } from "./PriceExplorer";
import { homeStats } from "@/fixtures";

const meta: Meta<typeof PriceExplorer> = {
  title: "Prices/PriceExplorer",
  component: PriceExplorer,
  tags: ["autodocs"],
  args: { onCardClick: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-2xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof PriceExplorer>;

export const Default: Story = {
  args: { stats: homeStats },
};
