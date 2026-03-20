import type { Meta, StoryObj } from "@storybook/react-vite";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { AppLayout } from "./AppLayout";
import { StatCard } from "@/components/StatCard/StatCard";
import { HBarChart } from "@/components/charts/HBarChart/HBarChart";

function DashboardContent() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl">Dashboard</h2>
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Total Decks" value={42} />
        <StatCard label="Total Sets" value={156} />
        <StatCard label="Cards with Prices" value="25,000" />
      </div>
      <HBarChart
        title="Format Distribution"
        data={[
          { label: "Commander", value: 15 },
          { label: "Modern", value: 12 },
          { label: "Standard", value: 5 },
        ]}
        color="accent"
      />
    </div>
  );
}

function EmptyContent() {
  return (
    <div className="flex items-center justify-center h-full text-text-muted">
      Select a filter to search cards
    </div>
  );
}

const meta: Meta<typeof AppLayout> = {
  title: "Layout/AppLayout",
  component: AppLayout,
  tags: ["autodocs"],
  parameters: { layout: "fullscreen" },
};

export default meta;
type Story = StoryObj<typeof AppLayout>;

export const WithDashboardContent: Story = {
  render: () => {
    const router = createMemoryRouter([
      { element: <AppLayout />, children: [{ path: "/", element: <DashboardContent /> }] },
    ], { initialEntries: ["/"] });
    return <RouterProvider router={router} />;
  },
};

export const EmptyPage: Story = {
  render: () => {
    const router = createMemoryRouter([
      { element: <AppLayout />, children: [{ path: "/cards", element: <EmptyContent /> }] },
    ], { initialEntries: ["/cards"] });
    return <RouterProvider router={router} />;
  },
};
