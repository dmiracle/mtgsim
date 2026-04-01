import type { Meta, StoryObj } from "@storybook/react";
import { GenerateResult } from "./GenerateResult";

const meta: Meta<typeof GenerateResult> = {
  title: "Flashcards/GenerateResult",
  component: GenerateResult,
  decorators: [
    (Story) => (
      <div className="max-w-lg mx-auto p-4 bg-bg-primary min-h-screen">
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof GenerateResult>;

export const SingleSet: Story = {
  args: {
    results: [{ set: "FIN", created: 309 }],
    onStudy: () => console.log("Study"),
    onGenerateMore: () => console.log("Generate more"),
  },
};

export const MultipleSets: Story = {
  args: {
    results: [
      { set: "FIN", created: 309 },
      { set: "TDM", created: 291 },
      { set: "BLB", created: 281 },
    ],
    onStudy: () => console.log("Study"),
    onGenerateMore: () => console.log("Generate more"),
  },
};

export const WithFailure: Story = {
  args: {
    results: [
      { set: "FIN", created: 309 },
      { set: "XYZ", created: 0 },
    ],
    onStudy: () => console.log("Study"),
    onGenerateMore: () => console.log("Generate more"),
  },
};
