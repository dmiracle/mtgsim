import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { SetBrowserPage } from "./SetBrowserPage";
import { setSummaries } from "@/fixtures";

const meta: Meta<typeof SetBrowserPage> = {
  title: "Pages/SetBrowserPage",
  component: SetBrowserPage,
  tags: ["autodocs"],
  args: { onSetClick: fn(), onPageChange: fn() },
  parameters: { layout: "padded" },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-4xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof SetBrowserPage>;

export const Default: Story = {
  args: {
    sets: setSummaries,
    pagination: { page: 1, pages: 4, total: 156, limit: 50 },
    availableTypes: ["core", "expansion", "masters", "draft_innovation", "commander", "starter", "promo"],
  },
};
