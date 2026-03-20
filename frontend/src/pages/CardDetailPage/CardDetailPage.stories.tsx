import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardDetailPage } from "./CardDetailPage";
import { cardDetail, keywordsResponse } from "@/fixtures";

const meta: Meta<typeof CardDetailPage> = {
  title: "Pages/CardDetailPage",
  component: CardDetailPage,
  tags: ["autodocs"],
  args: {
    onBack: fn(), onSetClick: fn(), onPrintingClick: fn(),
    onDeckClick: fn(), onAddToDeck: fn(), onAddToCollection: fn(), onSaveRating: fn(),
  },
  parameters: { layout: "padded" },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-5xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CardDetailPage>;

export const Default: Story = {
  args: { card: cardDetail, keywordTypes: keywordsResponse },
};

export const NoKeywords: Story = {
  args: { card: { ...cardDetail, keywords: [] } },
};
