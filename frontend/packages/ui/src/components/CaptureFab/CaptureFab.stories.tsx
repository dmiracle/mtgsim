import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CaptureFab } from "./CaptureFab";

const meta: Meta<typeof CaptureFab> = {
  title: "Capture/CaptureFab",
  component: CaptureFab,
  tags: ["autodocs"],
  parameters: { layout: "fullscreen" },
  args: { onClick: fn() },
  decorators: [
    (Story) => (
      <div className="relative h-[500px] w-full bg-bg-primary p-6">
        <div className="space-y-3 opacity-40">
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={i}
              className="h-10 rounded-lg bg-bg-secondary"
              style={{ width: `${60 + Math.random() * 30}%` }}
            />
          ))}
        </div>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof CaptureFab>;

export const Default: Story = {};

export const WithBadge: Story = {
  args: { badge: 3 },
};

export const HighBadge: Story = {
  args: { badge: 15 },
};
