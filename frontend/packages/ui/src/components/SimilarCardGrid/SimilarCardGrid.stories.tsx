import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { SimilarCardGrid } from "./SimilarCardGrid";
import { similarResults } from "@/fixtures";

const meta: Meta<typeof SimilarCardGrid> = {
  title: "Cards/SimilarCardGrid",
  component: SimilarCardGrid,
  tags: ["autodocs"],
  args: { onCardClick: fn() },
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6 max-w-4xl">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof SimilarCardGrid>;

export const Default: Story = {
  args: { results: similarResults },
};

export const Empty: Story = {
  args: { results: [] },
};

export const FewResults: Story = {
  args: { results: similarResults.slice(0, 2) },
};
