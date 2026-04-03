import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { SearchInput } from "./SearchInput";

const meta: Meta<typeof SearchInput> = {
  title: "Shared/SearchInput",
  component: SearchInput,
  tags: ["autodocs"],
  args: { onChange: fn() },
};

export default meta;
type Story = StoryObj<typeof SearchInput>;

export const Default: Story = {
  args: { placeholder: "Search cards..." },
};

export const WithValue: Story = {
  args: { value: "Lightning Bolt", placeholder: "Search cards..." },
};

export const CustomPlaceholder: Story = {
  args: { placeholder: "Search decks by name..." },
};
