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

type HexLayoutProps = { children: ReactNode };

export function HexLayout({ children }: HexLayoutProps) {
  const [expanded, setExpanded] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  function isActive(path: string) {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  }

  return (
    <div className="flex h-screen bg-bg-primary text-text-primary">
      {/* Morphing sidebar — collapsed = hex tiles, expanded = full labels */}
      <nav
        className={`shrink-0 bg-bg-secondary border-r border-border flex flex-col items-center py-4 transition-all duration-300 ${
          expanded ? "w-48" : "w-16"
        }`}
        onMouseEnter={() => setExpanded(true)}
        onMouseLeave={() => setExpanded(false)}
      >
        <div className="mb-6 flex items-center gap-2 px-3">
          <i className="ms ms-planeswalker text-accent" style={{ fontSize: "1.5em" }} />
          {expanded && <span className="text-sm font-semibold text-text-primary whitespace-nowrap overflow-hidden">MTG Viewer</span>}
        </div>

        <div className="flex flex-col gap-2 items-center w-full px-2">
          {navItems.map((item) => {
            const active = isActive(item.path);
            return (
              <button
                key={item.id}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center gap-3 transition-all duration-200 ${
                  expanded ? "px-3 py-2 rounded-lg" : "justify-center py-2"
                } ${
                  active
                    ? "bg-accent text-white"
                    : "text-text-muted hover:text-text-primary hover:bg-bg-hover"
                }`}
                style={!expanded ? {
                  clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
                  width: "44px",
                  height: "48px",
                  background: active ? "var(--color-accent)" : "var(--color-bg-tertiary)",
                } : undefined}
              >
                <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: expanded ? "1em" : "1.2em" }} />
                {expanded && <span className="text-sm whitespace-nowrap">{item.label}</span>}
              </button>
            );
          })}
        </div>
      </nav>

      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  );
}
