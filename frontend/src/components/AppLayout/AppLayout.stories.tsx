import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { AppLayout } from "./AppLayout";
import { StatCard } from "@/components/StatCard/StatCard";
import { HBarChart } from "@/components/charts/HBarChart/HBarChart";

const meta: Meta<typeof AppLayout> = {
  title: "Layout/AppLayout",
  component: AppLayout,
  tags: ["autodocs"],
  args: { onNavigate: fn() },
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof AppLayout>;

export const WithDashboardContent: Story = {
  args: {
    activeNav: "home",
    children: (
      <div className="space-y-6">
        <h2 className="text-xl font-bold">Dashboard</h2>
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
    ),
  },
};

export const EmptyContent: Story = {
  args: {
    activeNav: "cards",
    children: (
      <div className="flex items-center justify-center h-full text-text-muted">
        Select a filter to search cards
      </div>
    ),
  },
};
