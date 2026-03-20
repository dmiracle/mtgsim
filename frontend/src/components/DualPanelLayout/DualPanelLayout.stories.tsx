import type { Meta, StoryObj } from "@storybook/react-vite";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { DualPanelLayout } from "./DualPanelLayout";
import { StatCard } from "@/components/StatCard/StatCard";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { CardGrid } from "@/components/CardGrid/CardGrid";
import { cardSummaries } from "@/fixtures";

function SidebarContent() {
  return (
    <div className="space-y-4">
      <SearchInput placeholder="Search cards..." onChange={() => {}} />
      <div className="space-y-2">
        <h3 className="text-xs font-semibold text-text-muted uppercase tracking-widest">Filters</h3>
        <div className="space-y-1.5 text-xs text-text-secondary">
          <p>Format: Modern</p>
          <p>Colors: R, G</p>
          <p>Rarity: Rare, Mythic</p>
        </div>
      </div>
      <div className="space-y-2">
        <h3 className="text-xs font-semibold text-text-muted uppercase tracking-widest">Recent</h3>
        <div className="space-y-1 text-xs text-text-muted">
          <p>Lightning Bolt</p>
          <p>Tarmogoyf</p>
          <p>Counterspell</p>
        </div>
      </div>
    </div>
  );
}

function MainContent() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        <StatCard label="Results" value="250" />
        <StatCard label="Owned" value="142" />
        <StatCard label="Value" value="$1,245" />
      </div>
      <CardGrid cards={cardSummaries} />
    </div>
  );
}

const meta: Meta<typeof DualPanelLayout> = {
  title: "Layouts/DualPanel",
  component: DualPanelLayout,
  parameters: { layout: "fullscreen" },
};

export default meta;
type Story = StoryObj<typeof DualPanelLayout>;

export const WithSidebar: Story = {
  render: () => {
    const router = createMemoryRouter([
      { path: "/cards", element: <DualPanelLayout sidebar={<SidebarContent />}><MainContent /></DualPanelLayout> },
    ], { initialEntries: ["/cards"] });
    return <RouterProvider router={router} />;
  },
};

export const NoSidebar: Story = {
  render: () => {
    const router = createMemoryRouter([
      { path: "/", element: <DualPanelLayout><MainContent /></DualPanelLayout> },
    ], { initialEntries: ["/"] });
    return <RouterProvider router={router} />;
  },
};
