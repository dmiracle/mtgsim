import type { Meta, StoryObj } from "@storybook/react";
import { TrafficLight } from "./TrafficLight";

const meta: Meta<typeof TrafficLight> = {
  title: "Flashcards/TrafficLight",
  component: TrafficLight,
  decorators: [(Story) => <div className="bg-bg-primary p-8"><Story /></div>],
};
export default meta;

type Story = StoryObj<typeof TrafficLight>;

export const CardRecall: Story = {
  args: {
    aspects: [
      { key: "manaValue", label: "MV", iconClass: "ms ms-x" },
      { key: "type", label: "Type", iconClass: "ms ms-saga" },
      { key: "stats", label: "Stats", iconClass: "ms ms-creature" },
      { key: "oracle", label: "Oracle", iconClass: "ms ms-ability-activated" },
    ],
    onComplete: (r) => console.log("Submitted:", r),
  },
};

export const TwoAspects: Story = {
  args: {
    aspects: [
      { key: "name", label: "Name", iconClass: "ms ms-planeswalker" },
      { key: "art", label: "Art", iconClass: "ms ms-artist-nib" },
    ],
    onComplete: (r) => console.log("Submitted:", r),
  },
};
