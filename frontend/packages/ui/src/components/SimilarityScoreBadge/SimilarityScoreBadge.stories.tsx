import type { Meta, StoryObj } from "@storybook/react-vite";
import { SimilarityScoreBadge } from "./SimilarityScoreBadge";

const meta: Meta<typeof SimilarityScoreBadge> = {
  title: "Shared/SimilarityScoreBadge",
  component: SimilarityScoreBadge,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6 flex items-center gap-3">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof SimilarityScoreBadge>;

export const High: Story = { args: { score: 0.92 } };
export const Medium: Story = { args: { score: 0.55 } };
export const Low: Story = { args: { score: 0.22 } };
export const MediumSize: Story = { args: { score: 0.85, size: "md" } };

export const Range: Story = {
  render: () => (
    <div className="flex items-center gap-2">
      {[0.95, 0.82, 0.7, 0.55, 0.4, 0.25, 0.1].map((s) => (
        <SimilarityScoreBadge key={s} score={s} />
      ))}
    </div>
  ),
};
