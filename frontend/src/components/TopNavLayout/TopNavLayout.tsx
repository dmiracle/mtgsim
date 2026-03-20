import type { ReactNode } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const navItems = [
  { id: "home", label: "Home", path: "/", iconClass: "ms-planeswalker", iconFont: "ms" },
  { id: "decks", label: "Decks", path: "/decks", iconClass: "ms-saga", iconFont: "ms" },
  { id: "cards", label: "Cards", path: "/cards", iconClass: "ms-creature", iconFont: "ms" },
  { id: "sets", label: "Sets", path: "/sets", iconClass: "ss-pmtg1", iconFont: "ss" },
  { id: "prices", label: "Prices", path: "/prices", iconClass: "ms-loyalty-up", iconFont: "ms" },
  { id: "draft", label: "Draft", path: "/draft", iconClass: "ms-chaos", iconFont: "ms" },
  { id: "reference", label: "Reference", path: "/reference", iconClass: "ms-ability-activated", iconFont: "ms" },
];

type TopNavLayoutProps = { children: ReactNode };

export function TopNavLayout({ children }: TopNavLayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();

  function isActive(path: string) {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  }

  return (
    <div className="flex flex-col h-screen bg-bg-primary text-text-primary">
      <header className="shrink-0 border-b border-border bg-bg-secondary">
        <div className="flex items-center h-14 px-6 gap-8">
          <div className="flex items-center gap-2 shrink-0">
            <i className="ms ms-planeswalker text-accent" style={{ fontSize: "1.3em" }} />
            <h1 className="text-base text-text-primary">MTG Viewer</h1>
          </div>
          <nav className="flex items-center gap-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => navigate(item.path)}
                className={`px-3 py-2 text-sm flex items-center gap-2 rounded-lg transition-colors ${
                  isActive(item.path)
                    ? "bg-accent-muted text-accent"
                    : "text-text-muted hover:text-text-primary hover:bg-bg-hover"
                }`}
              >
                <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: "1em" }} />
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </header>
      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  );
}
