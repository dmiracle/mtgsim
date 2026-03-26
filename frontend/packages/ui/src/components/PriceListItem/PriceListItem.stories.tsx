import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { PriceListItem } from "./PriceListItem";
import { priceSummaries } from "@/fixtures";

const meta: Meta<typeof PriceListItem> = {
  title: "Prices/PriceListItem",
  component: PriceListItem,
  tags: ["autodocs"],
  args: { onClick: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-md"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof PriceListItem>;

export const Expensive: Story = {
  args: { price: priceSummaries[0] },
};

export const List: Story = {
  render: () => (
    <div className="space-y-2">
      {priceSummaries.map((p) => (
        <PriceListItem key={p.uuid} price={p} onClick={() => {}} />
      ))}
    </div>
  ),
};
