import { useRef, useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { RadarChart } from "./RadarChart";

const meta: Meta<typeof RadarChart> = {
  title: "Charts/RadarChart",
  component: RadarChart,
  tags: ["autodocs"],
  argTypes: {
    color: { control: "radio", options: ["accent", "success", "warning", "danger"] },
  },
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6 max-w-md">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof RadarChart>;

export const QuadrantRating: Story = {
  args: {
    title: "Quadrant Rating",
    data: [
      { axis: "Developing", value: 2 },
      { axis: "Ahead", value: 3.5 },
      { axis: "Behind", value: 4 },
      { axis: "Parity", value: 3 },
    ],
    maxValue: 5,
    color: "accent",
  },
};

export const HighRating: Story = {
  args: {
    title: "Bomb Card",
    data: [
      { axis: "Developing", value: 4.5 },
      { axis: "Ahead", value: 5 },
      { axis: "Behind", value: 4 },
      { axis: "Parity", value: 4.5 },
    ],
    maxValue: 5,
    color: "success",
  },
};

export const LowRating: Story = {
  args: {
    title: "Situational Card",
    data: [
      { axis: "Developing", value: 1 },
      { axis: "Ahead", value: 4 },
      { axis: "Behind", value: 0.5 },
      { axis: "Parity", value: 1.5 },
    ],
    maxValue: 5,
    color: "warning",
  },
};

export const Unrated: Story = {
  args: {
    title: "No Rating Yet",
    data: [
      { axis: "Developing", value: 0 },
      { axis: "Ahead", value: 0 },
      { axis: "Behind", value: 0 },
      { axis: "Parity", value: 0 },
    ],
    maxValue: 5,
    color: "accent",
  },
};

export const Large: Story = {
  args: {
    title: "Large Radar",
    data: [
      { axis: "Developing", value: 3 },
      { axis: "Ahead", value: 4 },
      { axis: "Behind", value: 2 },
      { axis: "Parity", value: 3.5 },
    ],
    maxValue: 5,
    size: 360,
    color: "danger",
  },
};

export const Interactive: Story = {
  render: () => {
    const [data, setData] = useState([
      { axis: "Developing", value: 2 },
      { axis: "Ahead", value: 3.5 },
      { axis: "Behind", value: 4 },
      { axis: "Parity", value: 3 },
    ]);
    const spanRefs = useRef<(HTMLSpanElement | null)[]>([]);
    return (
      <div className="space-y-3">
        <RadarChart
          title="Drag points to rate"
          data={data}
          maxValue={5}
          color="accent"
          interactive
          animate={false}
          onDrag={(i, v) => {
            const el = spanRefs.current[i];
            if (el) el.textContent = v.toFixed(1);
          }}
          onValueChange={(i, v) =>
            setData((prev) => prev.map((d, idx) => (idx === i ? { ...d, value: v } : d)))
          }
        />
        <div className="flex gap-4 text-xs text-text-muted justify-center">
          {data.map((d, i) => (
            <span key={d.axis}>{d.axis}: <span ref={(el) => { spanRefs.current[i] = el; }} className="text-text-primary font-medium">{d.value.toFixed(1)}</span></span>
          ))}
        </div>
      </div>
    );
  },
};

export const SixAxis: Story = {
  args: {
    title: "Extended Rating",
    data: [
      { axis: "Developing", value: 3 },
      { axis: "Ahead", value: 4.5 },
      { axis: "Behind", value: 2 },
      { axis: "Parity", value: 3 },
      { axis: "Tempo", value: 4 },
      { axis: "Synergy", value: 3.5 },
    ],
    maxValue: 5,
    color: "accent",
  },
};
