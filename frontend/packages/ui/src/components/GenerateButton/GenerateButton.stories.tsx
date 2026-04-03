import type { Meta, StoryObj } from "@storybook/react";
import { GenerateButton } from "./GenerateButton";

const meta: Meta<typeof GenerateButton> = {
  title: "Flashcards/GenerateButton",
  component: GenerateButton,
  decorators: [
    (Story) => (
      <div className="max-w-lg mx-auto p-4 bg-bg-primary">
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof GenerateButton>;

export const Ready: Story = {
  args: {
    count: 3,
    generating: false,
    onClick: () => console.log("Generate"),
  },
};

export const SingleSet: Story = {
  args: {
    count: 1,
    generating: false,
    onClick: () => console.log("Generate"),
  },
};

export const Generating: Story = {
  args: {
    count: 3,
    generating: true,
    progress: { done: 1, total: 3 },
    onClick: () => {},
  },
};

export const Disabled: Story = {
  args: {
    count: 0,
    generating: false,
    onClick: () => {},
  },
};
