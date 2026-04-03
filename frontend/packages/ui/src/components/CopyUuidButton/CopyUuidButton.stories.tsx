import type { Meta, StoryObj } from "@storybook/react-vite";
import { CopyUuidButton } from "./CopyUuidButton";

const meta: Meta<typeof CopyUuidButton> = {
  title: "Shared/CopyUuidButton",
  component: CopyUuidButton,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CopyUuidButton>;

export const Default: Story = {
  args: { uuid: "a1b2c3d4-e5f6-7890-abcd-ef1234567890" },
};

export const Medium: Story = {
  args: { uuid: "a1b2c3d4-e5f6-7890-abcd-ef1234567890", size: "md" },
};
