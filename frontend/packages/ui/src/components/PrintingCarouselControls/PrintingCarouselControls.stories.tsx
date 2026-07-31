import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { PrintingCarouselControls } from "./PrintingCarouselControls";
import { cardPrintings } from "@/fixtures";

const meta: Meta<typeof PrintingCarouselControls> = {
  title: "Cards/PrintingCarouselControls",
  component: PrintingCarouselControls,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6">
        <div className="group relative aspect-[5/7] w-56 rounded-lg overflow-hidden bg-bg-tertiary">
          <img src={cardPrintings[0].image_url ?? undefined} alt="Card" className="w-full h-full object-cover" />
          <Story />
        </div>
        <p className="mt-2 text-xs text-text-muted">Hover the card to reveal the controls.</p>
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof PrintingCarouselControls>;

export const Default: Story = {
  args: { index: 2, count: 12, onPrev: fn(), onNext: fn() },
};

export const FirstOfTwo: Story = {
  args: { index: 0, count: 2, onPrev: fn(), onNext: fn() },
};
