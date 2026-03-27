import type { Meta, StoryObj } from "@storybook/react";
import { OracleTextInput } from "./OracleTextInput";

const meta: Meta<typeof OracleTextInput> = {
  title: "Flashcards/Recall Inputs/OracleTextInput",
  component: OracleTextInput,
  decorators: [(Story) => <div className="max-w-sm mx-auto p-4 bg-bg-primary"><Story /></div>],
};
export default meta;

type Story = StoryObj<typeof OracleTextInput>;

export const Default: Story = {
  args: { onChange: (v) => console.log("Oracle:", v) },
};

export const WithText: Story = {
  args: {
    value: "Flying\nWhen this creature enters, draw a card.",
    onChange: (v) => console.log("Oracle:", v),
  },
};
