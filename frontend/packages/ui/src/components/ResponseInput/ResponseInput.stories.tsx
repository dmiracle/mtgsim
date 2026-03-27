import type { Meta, StoryObj } from "@storybook/react";
import { ResponseInput } from "./ResponseInput";

const meta: Meta<typeof ResponseInput> = {
  title: "Flashcards/ResponseInput",
  component: ResponseInput,
};
export default meta;

type Story = StoryObj<typeof ResponseInput>;

export const SingleButtons: Story = {
  args: {
    aspects: { key: "overall", label: "Overall" },
    mode: "buttons",
    onComplete: (r) => console.log("Complete:", r),
  },
};

export const SingleSlider: Story = {
  args: {
    aspects: { key: "overall", label: "Overall" },
    mode: "slider",
    onComplete: (r) => console.log("Complete:", r),
  },
};

export const SingleSliderHorizontal: Story = {
  args: {
    aspects: { key: "overall", label: "Overall" },
    mode: "slider-horizontal",
    onComplete: (r) => console.log("Complete:", r),
  },
};

export const MultiButtons: Story = {
  args: {
    aspects: [
      { key: "mana", label: "Mana Cost" },
      { key: "stats", label: "Power / Toughness" },
      { key: "oracle", label: "Oracle Text" },
    ],
    mode: "buttons",
    compact: true,
    onComplete: (r) => console.log("Complete:", r),
  },
};

export const MultiSlider: Story = {
  args: {
    aspects: [
      { key: "mana", label: "Mana Cost" },
      { key: "stats", label: "Power / Toughness" },
      { key: "oracle", label: "Oracle Text" },
    ],
    mode: "slider",
    onComplete: (r) => console.log("Complete:", r),
  },
};

export const MultiSliderHorizontal: Story = {
  args: {
    aspects: [
      { key: "mana", label: "Mana Cost" },
      { key: "stats", label: "Power / Toughness" },
      { key: "oracle", label: "Oracle Text" },
    ],
    mode: "slider-horizontal",
    onComplete: (r) => console.log("Complete:", r),
  },
};

export const TrafficLight: Story = {
  args: {
    aspects: [
      { key: "mana", label: "MV", iconClass: "ms ms-x" },
      { key: "type", label: "Type", iconClass: "ms ms-saga" },
      { key: "stats", label: "Stats", iconClass: "ms ms-creature" },
      { key: "oracle", label: "Oracle", iconClass: "ms ms-ability-activated" },
    ],
    mode: "traffic-light",
    onComplete: (r) => console.log("Complete:", r),
  },
};

export const SingleCompact: Story = {
  args: {
    aspects: { key: "recall", label: "Recall" },
    mode: "buttons",
    compact: true,
    onComplete: (r) => console.log("Complete:", r),
  },
};
