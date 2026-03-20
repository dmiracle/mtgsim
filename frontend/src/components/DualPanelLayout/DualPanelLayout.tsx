import type { ReactNode } from "react";
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
  const location = useLocation();
  const navigate = useNavigate();

  function isActive(path: string) {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  }

  return (
    <div className="flex flex-col h-screen bg-bg-primary text-text-primary">
      {/* Top bar */}
      <header className="shrink-0 h-12 border-b border-border bg-bg-secondary flex items-center px-4 gap-6">
        <div className="flex items-center gap-2">
          <i className="ms ms-planeswalker text-accent" style={{ fontSize: "1.2em" }} />
          <span className="text-sm font-semibold text-text-primary">MTG Viewer</span>
        </div>
        <nav className="flex items-center gap-0.5">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => navigate(item.path)}
              className={`px-2.5 py-1.5 text-xs flex items-center gap-1.5 rounded transition-colors ${
                isActive(item.path)
                  ? "text-accent bg-accent-muted"
                  : "text-text-muted hover:text-text-primary"
              }`}
            >
              <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: "0.9em" }} />
              {item.label}
            </button>
          ))}
        </nav>
      </header>

      {/* Dual panel body */}
      <div className="flex flex-1 overflow-hidden">
        {sidebar && (
          <aside className="w-80 shrink-0 border-r border-border bg-bg-secondary overflow-y-auto p-4">
            {sidebar}
          </aside>
        )}
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
