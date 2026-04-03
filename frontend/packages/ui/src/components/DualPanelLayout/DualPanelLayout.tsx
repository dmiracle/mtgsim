import { useState, type ReactNode } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const navItems = [
  { id: "home", path: "/", iconClass: "ms-planeswalker", iconFont: "ms", label: "Home" },
  { id: "decks", path: "/decks", iconClass: "ms-saga", iconFont: "ms", label: "Decks" },
  { id: "cards", path: "/cards", iconClass: "ms-creature", iconFont: "ms", label: "Cards" },
  { id: "sets", path: "/sets", iconClass: "ss-pmtg1", iconFont: "ss", label: "Sets" },
  { id: "prices", path: "/prices", iconClass: "ms-loyalty-up", iconFont: "ms", label: "Prices" },
  { id: "draft", path: "/draft", iconClass: "ms-chaos", iconFont: "ms", label: "Draft" },
  { id: "reference", path: "/reference", iconClass: "ms-ability-activated", iconFont: "ms", label: "Reference" },
];

type DualPanelLayoutProps = {
  sidebar?: ReactNode;
  children: ReactNode;
};

export function DualPanelLayout({ sidebar, children }: DualPanelLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  function isActive(path: string) {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  }

  return (
    <div className="flex flex-col h-screen bg-bg-primary text-text-primary">
      {/* Top bar */}
      <header className="shrink-0 h-12 border-b border-border bg-bg-secondary flex items-center px-3 sm:px-4 gap-3 sm:gap-6">
        <div className="flex items-center gap-2">
          <i className="ms ms-planeswalker text-accent" style={{ fontSize: "1.2em" }} />
          <span className="text-sm font-semibold text-text-primary hidden sm:inline">MTG Viewer</span>
        </div>
        <nav className="flex items-center gap-0.5 overflow-x-auto">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => navigate(item.path)}
              className={`px-2 sm:px-2.5 py-1.5 text-xs flex items-center gap-1.5 rounded transition-colors whitespace-nowrap shrink-0 ${
                isActive(item.path)
                  ? "text-accent bg-accent-muted"
                  : "text-text-muted hover:text-text-primary"
              }`}
            >
              <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: "0.9em" }} />
              <span className="hidden md:inline">{item.label}</span>
            </button>
          ))}
        </nav>
        {sidebar && (
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden ml-auto text-xs px-2 py-1 rounded border border-border text-text-muted"
          >
            {sidebarOpen ? "Hide" : "Filters"}
          </button>
        )}
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar — overlay on mobile, panel on desktop */}
        {sidebar && (
          <>
            <aside className="hidden md:block w-72 lg:w-80 shrink-0 border-r border-border bg-bg-secondary overflow-y-auto p-4">
              {sidebar}
            </aside>
            {sidebarOpen && (
              <div className="fixed inset-0 z-50 md:hidden">
                <div className="absolute inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
                <div className="absolute left-0 top-12 bottom-0 w-72 bg-bg-secondary border-r border-border overflow-y-auto p-4">
                  {sidebar}
                </div>
              </div>
            )}
          </>
        )}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}
