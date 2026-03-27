import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { RatingSlider } from "./RatingSlider";

const meta: Meta<typeof RatingSlider> = {
  title: "Flashcards/RatingSlider",
  component: RatingSlider,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-8"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof RatingSlider>;

export const Interactive: Story = {
  render: () => {
    const [value, setValue] = useState<number | null>(2.5);
    return (
      <div className="space-y-4">
        <RatingSlider value={value} onChange={setValue} />
        <p className="text-text-muted text-sm">Value: {value?.toFixed(1)}</p>
      </div>
    );
  },
};

export const Compact: Story = {
  render: () => {
    const [value, setValue] = useState<number | null>(3.0);
    return <RatingSlider value={value} onChange={setValue} compact />;
  },
};

export const Low: Story = {
  render: () => {
    const [value, setValue] = useState<number | null>(0.5);
    return <RatingSlider value={value} onChange={setValue} />;
  },
};

export const High: Story = {
  render: () => {
    const [value, setValue] = useState<number | null>(4.8);
    return <RatingSlider value={value} onChange={setValue} />;
  },
};

export const Horizontal: Story = {
  render: () => {
    const [value, setValue] = useState<number | null>(2.5);
    return (
      <div className="space-y-4">
        <RatingSlider value={value} onChange={setValue} orientation="horizontal" />
        <p className="text-text-muted text-sm">Value: {value?.toFixed(1)}</p>
      </div>
    );
  },
};

export const HorizontalCompact: Story = {
  render: () => {
    const [value, setValue] = useState<number | null>(3.0);
    return <RatingSlider value={value} onChange={setValue} orientation="horizontal" compact />;
  },
};
