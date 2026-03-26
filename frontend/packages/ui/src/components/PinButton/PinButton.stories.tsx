import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { PinButton } from "./PinButton";

const meta: Meta<typeof PinButton> = {
  title: "Shared/PinButton",
  component: PinButton,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof PinButton>;

export const Interactive: Story = {
  render: () => {
    const [pinned, setPinned] = useState(false);
    return <PinButton pinned={pinned} onToggle={() => setPinned(!pinned)} />;
  },
};

export const Pinned: Story = {
  args: { pinned: true, onToggle: () => {} },
};

export const Unpinned: Story = {
  args: { pinned: false, onToggle: () => {} },
};

export const MediumSize: Story = {
  args: { pinned: true, onToggle: () => {}, size: "md" },
};
