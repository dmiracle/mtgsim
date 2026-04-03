import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { PackConfigPanel } from "./PackConfigPanel";
import { setSummaries } from "@/fixtures";

const meta: Meta<typeof PackConfigPanel> = {
  title: "Draft/PackConfigPanel",
  component: PackConfigPanel,
  tags: ["autodocs"],
  args: { onOpen: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-sm"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof PackConfigPanel>;

export const Default: Story = {
  args: { sets: setSummaries },
};

export const Loading: Story = {
  args: { sets: setSummaries, loading: true },
};
