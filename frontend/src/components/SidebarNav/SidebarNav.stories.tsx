import type { Meta, StoryObj } from "@storybook/react-vite";
import { MemoryRouter } from "react-router-dom";
import { SidebarNav } from "./SidebarNav";

const meta: Meta<typeof SidebarNav> = {
  title: "Layouts/SidebarNav",
  component: SidebarNav,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={["/"]}>
        <div className="h-[600px] bg-bg-primary">
          <Story />
        </div>
      </MemoryRouter>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof SidebarNav>;

export const Home: Story = {
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={["/"]}>
        <div className="h-[600px] bg-bg-primary"><Story /></div>
      </MemoryRouter>
    ),
  ],
};

export const Decks: Story = {
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={["/decks"]}>
        <div className="h-[600px] bg-bg-primary"><Story /></div>
      </MemoryRouter>
    ),
  ],
};

export const Cards: Story = {
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={["/cards"]}>
        <div className="h-[600px] bg-bg-primary"><Story /></div>
      </MemoryRouter>
    ),
  ],
};

export const Draft: Story = {
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={["/draft"]}>
        <div className="h-[600px] bg-bg-primary"><Story /></div>
      </MemoryRouter>
    ),
  ],
};
