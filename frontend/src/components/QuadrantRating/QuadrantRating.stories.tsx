import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { QuadrantRating } from "./QuadrantRating";

const meta: Meta<typeof QuadrantRating> = {
  title: "CardDetail/QuadrantRating",
  component: QuadrantRating,
  tags: ["autodocs"],
  args: { onSave: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-sm"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof QuadrantRating>;

export const WithRating: Story = {
  args: {
    rating: { developing: 2, ahead: 3.5, behind: 4, parity: 3, notes: "Efficient removal." },
  },
};

export const Empty: Story = {
  args: { rating: null },
};

export const Saving: Story = {
  args: {
    rating: { developing: 4, ahead: 5, behind: 3, parity: 4, notes: null },
    saving: true,
  },
};
