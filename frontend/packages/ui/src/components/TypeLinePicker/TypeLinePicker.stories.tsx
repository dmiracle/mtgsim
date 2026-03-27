import type { Meta, StoryObj } from "@storybook/react";
import { TypeLinePicker } from "./TypeLinePicker";

const meta: Meta<typeof TypeLinePicker> = {
  title: "App-v2/Recall Inputs/TypeLinePicker",
  component: TypeLinePicker,
  decorators: [(Story) => <div className="max-w-sm mx-auto p-4 bg-bg-primary"><Story /></div>],
};
export default meta;

type Story = StoryObj<typeof TypeLinePicker>;

export const Default: Story = {
  args: { onChange: (v) => console.log("Type:", v) },
};

export const Preselected: Story = {
  args: {
    value: "Legendary Creature — Human Wizard",
    onChange: (v) => console.log("Type:", v),
  },
};
