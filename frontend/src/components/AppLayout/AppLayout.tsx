import { Outlet } from "react-router-dom";
import { SidebarNav } from "@/components/SidebarNav/SidebarNav";

export function AppLayout() {
  return (
    <div className="flex h-screen bg-bg-primary text-text-primary">
      <SidebarNav />
      <main className="flex-1 overflow-y-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
