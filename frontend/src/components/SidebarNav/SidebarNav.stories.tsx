import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { SidebarNav } from "./SidebarNav";

const meta: Meta<typeof SidebarNav> = {
  title: "Layout/SidebarNav",
  component: SidebarNav,
  tags: ["autodocs"],
  args: { onNavigate: fn() },
  decorators: [
    (Story) => (
      <div className="h-[600px] bg-bg-primary">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof SidebarNav>;

export const Home: Story = {
  args: { activeId: "home" },
};

export const Decks: Story = {
  args: { activeId: "decks" },
};

export const Cards: Story = {
  args: { activeId: "cards" },
};

export const Draft: Story = {
  args: { activeId: "draft" },
};
