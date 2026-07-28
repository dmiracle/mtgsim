import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { GridSizeToggle, type GridSize } from "./GridSizeToggle";

const meta: Meta<typeof GridSizeToggle> = {
  title: "Cards/GridSizeToggle",
  component: GridSizeToggle,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof GridSizeToggle>;

export const Small: Story = {
  args: { value: "small", onChange: fn() },
};

export const Medium: Story = {
  args: { value: "medium", onChange: fn() },
};

export const Large: Story = {
  args: { value: "large", onChange: fn() },
};

export const Interactive: Story = {
  render: () => {
    const [size, setSize] = useState<GridSize>("small");
    return <GridSizeToggle value={size} onChange={setSize} />;
  },
};
