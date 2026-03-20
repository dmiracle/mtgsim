import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { OtherPrintings } from "./OtherPrintings";
import { cardDetail } from "@/fixtures";

const meta: Meta<typeof OtherPrintings> = {
  title: "CardDetail/OtherPrintings",
  component: OtherPrintings,
  tags: ["autodocs"],
  args: { onSelect: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-sm"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof OtherPrintings>;

export const Default: Story = {
  args: { printings: cardDetail.other_printings },
};

export const Empty: Story = {
  args: { printings: [] },
};
