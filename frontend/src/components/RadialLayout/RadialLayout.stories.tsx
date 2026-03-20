import type { Meta, StoryObj } from "@storybook/react-vite";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { RadialLayout } from "./RadialLayout";
import { StatCard } from "@/components/StatCard/StatCard";

function DemoContent() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <h2 className="text-xl">Dashboard</h2>
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total Decks" value={42} />
        <StatCard label="Total Sets" value={156} />
        <StatCard label="Total Cards" value="28,500" />
        <StatCard label="With Prices" value="25,000" />
      </div>
      <p className="text-sm text-text-muted">Click the planeswalker button in the bottom-right to open the radial menu.</p>
    </div>
  );
}

const meta: Meta<typeof RadialLayout> = {
  title: "Layouts/RadialMenu",
  component: RadialLayout,
  parameters: { layout: "fullscreen" },
};

export default meta;
type Story = StoryObj<typeof RadialLayout>;

export const Default: Story = {
  render: () => {
    const router = createMemoryRouter([
      { path: "/", element: <RadialLayout><DemoContent /></RadialLayout> },
    ], { initialEntries: ["/"] });
    return <RouterProvider router={router} />;
  },
};
