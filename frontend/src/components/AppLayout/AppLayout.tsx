import { useState } from "react";
import { Outlet } from "react-router-dom";
import { SidebarNav } from "@/components/SidebarNav/SidebarNav";

export function AppLayout() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="flex h-screen bg-bg-primary text-text-primary">
      {/* Desktop sidebar */}
      <div className="hidden md:block">
        <SidebarNav />
      </div>

      {/* Mobile nav overlay */}
      {mobileNavOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setMobileNavOpen(false)} />
          <div className="relative w-56 h-full">
            <SidebarNav onNavigate={() => setMobileNavOpen(false)} />
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile header */}
        <header className="md:hidden shrink-0 h-12 border-b border-border bg-bg-secondary flex items-center px-4 gap-3">
          <button onClick={() => setMobileNavOpen(true)} className="text-text-muted hover:text-text-primary">
            <i className="ms ms-planeswalker text-accent" style={{ fontSize: "1.3em" }} />
          </button>
          <h1 className="text-sm text-text-primary">MTG Viewer</h1>
        </header>

        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
