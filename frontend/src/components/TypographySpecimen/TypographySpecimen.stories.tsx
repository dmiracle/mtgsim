import type { Meta, StoryObj } from "@storybook/react-vite";
import { TypographySpecimen } from "./TypographySpecimen";

const meta: Meta<typeof TypographySpecimen> = {
  title: "Design/TypographySpecimen",
  component: TypographySpecimen,
  tags: ["autodocs"],
  parameters: { layout: "padded" },
  decorators: [(Story) => <div className="bg-bg-primary p-8 max-w-3xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof TypographySpecimen>;

export const Default: Story = {};
