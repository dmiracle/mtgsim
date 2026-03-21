import type { Meta, StoryObj } from "@storybook/react-vite";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { MinimalLayout } from "./MinimalLayout";
import { StatCard } from "@/components/StatCard/StatCard";

function DemoContent() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl">Dashboard</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Decks" value={42} />
        <StatCard label="Total Sets" value={156} />
        <StatCard label="Total Cards" value="28,500" />
        <StatCard label="With Prices" value="25,000" />
      </div>
    </div>
  );
}

const meta: Meta<typeof MinimalLayout> = {
  title: "Layouts/MinimalRail",
  component: MinimalLayout,
  parameters: { layout: "fullscreen" },
};

export default meta;
type Story = StoryObj<typeof MinimalLayout>;

export const Default: Story = {
  render: () => {
    const router = createMemoryRouter([
      { path: "/", element: <MinimalLayout><DemoContent /></MinimalLayout> },
    ], { initialEntries: ["/"] });
    return <RouterProvider router={router} />;
  },
};
