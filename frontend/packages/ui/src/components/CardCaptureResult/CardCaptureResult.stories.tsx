import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardCaptureResult } from "./CardCaptureResult";
import { cardSummaries } from "@/fixtures";

const meta: Meta<typeof CardCaptureResult> = {
  title: "Capture/CardCaptureResult",
  component: CardCaptureResult,
  tags: ["autodocs"],
  args: {
    onAddToDeck: fn(),
    onAddToCollection: fn(),
    onDismiss: fn(),
    onSetClick: fn(),
  },
  decorators: [
    (Story) => (
      <div className="w-96 bg-bg-primary p-4">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof CardCaptureResult>;

export const HighConfidence: Story = {
  args: { card: cardSummaries[0], confidence: 0.97 },
};

export const MediumConfidence: Story = {
  args: { card: cardSummaries[1], confidence: 0.78 },
};

export const LowConfidence: Story = {
  args: { card: cardSummaries[2], confidence: 0.45 },
};

export const OwnedCard: Story = {
  args: { card: cardSummaries[0], confidence: 0.95 },
};

export const WantedCard: Story = {
  args: { card: cardSummaries[2], confidence: 0.92 },
};

export const NoImage: Story = {
  args: {
    card: { ...cardSummaries[0], image_url: null },
    confidence: 0.88,
  },
};
