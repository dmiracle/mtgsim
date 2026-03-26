import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { RatingButtons } from "./RatingButtons";

const meta: Meta<typeof RatingButtons> = {
  title: "Flashcards/RatingButtons",
  component: RatingButtons,
  tags: ["autodocs"],
  args: { onRate: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-8"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof RatingButtons>;

export const Default: Story = {};

export const Disabled: Story = {
  args: { disabled: true },
};
