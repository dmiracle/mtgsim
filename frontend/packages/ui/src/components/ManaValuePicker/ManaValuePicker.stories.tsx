import type { Meta, StoryObj } from "@storybook/react";
import { ManaValuePicker } from "./ManaValuePicker";

const meta: Meta<typeof ManaValuePicker> = {
  title: "App-v2/Recall Inputs/ManaValuePicker",
  component: ManaValuePicker,
  decorators: [(Story) => <div className="max-w-sm mx-auto p-4 bg-bg-primary"><Story /></div>],
};
export default meta;

type Story = StoryObj<typeof ManaValuePicker>;

export const Default: Story = {
  args: { onChange: (v) => console.log("MV:", v) },
};

export const Preselected: Story = {
  args: { value: 3, onChange: (v) => console.log("MV:", v) },
};
