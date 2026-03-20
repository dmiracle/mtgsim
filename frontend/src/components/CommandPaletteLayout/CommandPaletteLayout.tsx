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

type CommandPaletteLayoutProps = { children: ReactNode };

export function CommandPaletteLayout({ children }: CommandPaletteLayoutProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const location = useLocation();
  const navigate = useNavigate();

  const filtered = navItems.filter((item) =>
    item.label.toLowerCase().includes(search.toLowerCase())
  );

  function go(path: string) {
    navigate(path);
    setOpen(false);
    setSearch("");
  }

  function isActive(path: string) {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  }

  const activePage = navItems.find((n) => isActive(n.path));

  return (
    <div className="flex flex-col h-screen bg-bg-primary text-text-primary">
      {/* Minimal header with command trigger */}
      <header className="shrink-0 h-12 border-b border-border bg-bg-secondary/50 flex items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <i className="ms ms-planeswalker text-accent" style={{ fontSize: "1.2em" }} />
          {activePage && (
            <span className="text-sm text-text-secondary flex items-center gap-2">
              <i className={`${activePage.iconFont} ${activePage.iconClass}`} style={{ fontSize: "0.9em" }} />
              {activePage.label}
            </span>
          )}
        </div>
        <button
          onClick={() => setOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-bg-tertiary text-xs text-text-muted hover:border-border-hover hover:text-text-secondary transition-colors"
        >
          Navigate...
          <kbd className="px-1.5 py-0.5 rounded bg-bg-secondary border border-border text-[10px] font-mono">
            Ctrl+K
          </kbd>
        </button>
      </header>

      <main className="flex-1 overflow-y-auto p-6">{children}</main>

      {/* Command palette overlay */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] bg-black/60" onClick={() => setOpen(false)}>
          <div className="w-full max-w-md bg-bg-secondary border border-border rounded-xl shadow-2xl overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <div className="p-3 border-b border-border">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Where do you want to go?"
                autoFocus
                className="w-full bg-transparent text-sm text-text-primary placeholder-text-muted focus:outline-none"
              />
            </div>
            <div className="py-1">
              {filtered.map((item) => (
                <button
                  key={item.id}
                  onClick={() => go(item.path)}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                    isActive(item.path)
                      ? "bg-accent-muted text-accent"
                      : "text-text-secondary hover:bg-bg-hover"
                  }`}
                >
                  <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: "1.1em", width: "1.2em", textAlign: "center" }} />
                  {item.label}
                </button>
              ))}
              {filtered.length === 0 && (
                <p className="px-4 py-6 text-sm text-text-muted text-center">No results</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
