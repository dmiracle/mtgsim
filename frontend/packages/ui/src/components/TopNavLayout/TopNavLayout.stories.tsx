import type { Meta, StoryObj } from "@storybook/react-vite";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { TopNavLayout } from "./TopNavLayout";
import { StatCard } from "@/components/StatCard/StatCard";
import { HBarChart } from "@/components/charts/HBarChart/HBarChart";

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
      <HBarChart title="Format Distribution" data={[{ label: "Commander", value: 15 }, { label: "Modern", value: 12 }, { label: "Standard", value: 5 }]} color="accent" />
    </div>
  );
}

const meta: Meta<typeof TopNavLayout> = {
  title: "Layouts/TopNav",
  component: TopNavLayout,
  parameters: { layout: "fullscreen" },
};

export default meta;
type Story = StoryObj<typeof TopNavLayout>;

export const Default: Story = {
  render: () => {
    const router = createMemoryRouter([
      { path: "/", element: <TopNavLayout><DemoContent /></TopNavLayout> },
    ], { initialEntries: ["/"] });
    return <RouterProvider router={router} />;
  },
};
