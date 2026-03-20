import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { DeckDetailPage } from "./DeckDetailPage";
import { deckDetail } from "@/fixtures";

const meta: Meta<typeof DeckDetailPage> = {
  title: "Pages/DeckDetailPage",
  component: DeckDetailPage,
  tags: ["autodocs"],
  args: { onBack: fn(), onCardClick: fn(), onSetClick: fn() },
  parameters: { layout: "padded" },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-5xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof DeckDetailPage>;

export const Default: Story = {
  args: { deck: deckDetail },
};
