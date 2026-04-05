import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { PinnedBadge } from "./PinnedBadge";

const meta: Meta<typeof PinnedBadge> = {
  title: "Shared/PinnedBadge",
  component: PinnedBadge,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div className="flex items-center gap-4 p-6 bg-bg-primary">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof PinnedBadge>;

export const Interactive: Story = {
  render: () => {
    const [pinned, setPinned] = useState(false);
    return <PinnedBadge pinned={pinned} onToggle={() => setPinned(!pinned)} />;
  },
};

export const PinnedReadOnly: Story = {
  args: { pinned: true },
};

export const PinnedToggle: Story = {
  args: { pinned: true, onToggle: () => {} },
};

export const UnpinnedToggle: Story = {
  args: { pinned: false, onToggle: () => {} },
};

export const Medium: Story = {
  args: { pinned: true, onToggle: () => {}, size: "md" },
};

export const OnCard: Story = {
  render: () => {
    const [pinned, setPinned] = useState(true);
    return (
      <div className="relative w-48 h-64 bg-bg-tertiary rounded-lg overflow-hidden">
        <div className="w-full h-full bg-gradient-to-br from-gray-700 to-gray-900" />
        <div className="absolute top-2 left-2">
          <PinnedBadge pinned={pinned} onToggle={() => setPinned(!pinned)} />
        </div>
      </div>
    );
  },
};

export const OnListItem: Story = {
  render: () => {
    const [pinned, setPinned] = useState(true);
    return (
      <div className="flex items-center gap-3 px-4 py-3 bg-bg-secondary border border-border rounded-lg w-80">
        <PinnedBadge pinned={pinned} onToggle={() => setPinned(!pinned)} />
        <span className="text-sm text-text-primary">Mono Red Burn</span>
      </div>
    );
  },
};
