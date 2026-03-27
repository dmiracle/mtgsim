import type { Meta, StoryObj } from "@storybook/react";
import { ManaValuePicker } from "./ManaValuePicker";

const meta: Meta<typeof ManaValuePicker> = {
  title: "Flashcards/Recall Inputs/ManaValuePicker",
  component: ManaValuePicker,
  decorators: [(Story) => <div className="max-w-sm mx-auto p-4 bg-bg-primary"><Story /></div>],
};
export default meta;

type Story = StoryObj<typeof ManaValuePicker>;

export const Default: Story = {
  args: { onChange: (v) => console.log("Cost:", v) },
};

export const Prebuilt: Story = {
  args: {
    value: "{5}{R}{U}",
    onChange: (v) => console.log("Cost:", v),
  },
};
