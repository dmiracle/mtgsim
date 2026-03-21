import type { Meta, StoryObj } from "@storybook/react-vite";
import { MemoryRouter } from "react-router-dom";
import { SidebarNav } from "./SidebarNav";

function Wrapper({ path, children }: { path: string; children: React.ReactNode }) {
  return (
    <MemoryRouter initialEntries={[path]}>
      <div className="h-[600px] bg-bg-primary">{children}</div>
    </MemoryRouter>
  );
}

const meta: Meta<typeof SidebarNav> = {
  title: "Layouts/SidebarNav",
  component: SidebarNav,
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof SidebarNav>;

export const Home: Story = {
  render: () => <Wrapper path="/"><SidebarNav /></Wrapper>,
};

export const Decks: Story = {
  render: () => <Wrapper path="/decks"><SidebarNav /></Wrapper>,
};

export const Cards: Story = {
  render: () => <Wrapper path="/cards"><SidebarNav /></Wrapper>,
};

export const Draft: Story = {
  render: () => <Wrapper path="/draft"><SidebarNav /></Wrapper>,
};
