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

type MinimalLayoutProps = { children: ReactNode };

export function MinimalLayout({ children }: MinimalLayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();

  function isActive(path: string) {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  }

  return (
    <div className="flex h-screen bg-bg-primary text-text-primary">
      {/* Icon-only rail */}
      <nav className="w-14 shrink-0 bg-bg-secondary border-r border-border flex flex-col items-center py-4 gap-1">
        <div className="mb-4">
          <i className="ms ms-planeswalker text-accent" style={{ fontSize: "1.5em" }} />
        </div>
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => navigate(item.path)}
            title={item.label}
            className={`group relative w-10 h-10 rounded-lg flex items-center justify-center transition-colors ${
              isActive(item.path)
                ? "bg-accent text-white"
                : "text-text-muted hover:bg-bg-hover hover:text-text-primary"
            }`}
          >
            <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: "1.1em" }} />
            <span className="absolute left-full ml-2 px-2 py-1 text-xs font-medium bg-bg-secondary border border-border rounded shadow-lg text-text-secondary whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-20">
              {item.label}
            </span>
          </button>
        ))}
      </nav>
      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  );
}
