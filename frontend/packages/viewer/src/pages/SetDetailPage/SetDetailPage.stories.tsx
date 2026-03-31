import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { SetDetailPage } from "./SetDetailPage";
import { setDetail, cardSummaries } from "@/fixtures";

const meta: Meta<typeof SetDetailPage> = {
  title: "Pages/SetDetailPage",
  component: SetDetailPage,
  tags: ["autodocs"],
  args: { onBack: fn(), onCardClick: fn(), onSetClick: fn(), onCardPageChange: fn() },
  parameters: { layout: "padded" },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-5xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof SetDetailPage>;

export const Default: Story = {
  args: {
    set: setDetail,
    cards: cardSummaries,
    cardPagination: { page: 1, pages: 7, total: 303, limit: 50 },
  },
};
