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

type MinimalLayoutProps = { children: ReactNode };

export function MinimalLayout({ children }: MinimalLayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  function isActive(path: string) {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  }

  function go(path: string) {
    navigate(path);
    setMobileOpen(false);
  }

  return (
    <div className="flex h-screen bg-bg-primary text-text-primary">
      {/* Desktop icon rail */}
      <nav className="hidden sm:flex w-14 shrink-0 bg-bg-secondary border-r border-border flex-col items-center py-4 gap-1">
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

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile header */}
        <header className="sm:hidden shrink-0 h-12 border-b border-border bg-bg-secondary flex items-center px-4 gap-3">
          <button onClick={() => setMobileOpen(true)}>
            <i className="ms ms-planeswalker text-accent" style={{ fontSize: "1.3em" }} />
          </button>
          <span className="text-sm text-text-primary">MTG Viewer</span>
        </header>

        {/* Mobile slide-out */}
        {mobileOpen && (
          <div className="fixed inset-0 z-50 sm:hidden">
            <div className="absolute inset-0 bg-black/50" onClick={() => setMobileOpen(false)} />
            <div className="relative w-56 h-full bg-bg-secondary border-r border-border p-4 space-y-1">
              <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border">
                <i className="ms ms-planeswalker text-accent" style={{ fontSize: "1.4em" }} />
                <span className="text-sm font-semibold text-text-primary">MTG Viewer</span>
              </div>
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => go(item.path)}
                  className={`w-full text-left px-3 py-2 text-sm rounded-lg flex items-center gap-3 transition-colors ${
                    isActive(item.path) ? "bg-accent-muted text-accent" : "text-text-muted hover:bg-bg-hover"
                  }`}
                >
                  <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: "1em" }} />
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        )}

        <main className="flex-1 overflow-y-auto p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}
