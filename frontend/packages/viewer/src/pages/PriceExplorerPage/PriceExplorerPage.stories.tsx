import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { PriceExplorerPage } from "./PriceExplorerPage";
import { homeStats, priceSummaries } from "@/fixtures";

const meta: Meta<typeof PriceExplorerPage> = {
  title: "Pages/PriceExplorerPage",
  component: PriceExplorerPage,
  tags: ["autodocs"],
  args: { onCardClick: fn(), onPageChange: fn() },
  parameters: { layout: "padded" },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-4xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof PriceExplorerPage>;

export const Landing: Story = {
  args: {
    stats: homeStats,
    prices: [],
    pagination: { page: 1, pages: 1, total: 0, limit: 50 },
  },
};

export const WithResults: Story = {
  args: {
    stats: homeStats,
    prices: priceSummaries,
    pagination: { page: 1, pages: 10, total: 500, limit: 50 },
  },
};
