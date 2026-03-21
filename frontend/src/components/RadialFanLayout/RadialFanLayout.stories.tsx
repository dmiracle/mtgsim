import type { Meta, StoryObj } from "@storybook/react-vite";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { RadialFanLayout } from "./RadialFanLayout";
import { StatCard } from "@/components/StatCard/StatCard";

function DemoContent() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <h2 className="text-xl">Dashboard</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Decks" value={42} />
        <StatCard label="Total Sets" value={156} />
        <StatCard label="Total Cards" value="28,500" />
        <StatCard label="With Prices" value="25,000" />
      </div>
      <p className="text-sm text-text-muted">Click the bottom-left button to fan out the navigation with staggered animation.</p>
    </div>
  );
}

const meta: Meta<typeof RadialFanLayout> = {
  title: "Layouts/RadialFan",
  component: RadialFanLayout,
  parameters: { layout: "fullscreen" },
};

export default meta;
type Story = StoryObj<typeof RadialFanLayout>;

export const Default: Story = {
  render: () => {
    const router = createMemoryRouter([
      { path: "/", element: <RadialFanLayout><DemoContent /></RadialFanLayout> },
    ], { initialEntries: ["/"] });
    return <RouterProvider router={router} />;
  },
};
