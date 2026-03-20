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

type RadialFanLayoutProps = { children: ReactNode };

export function RadialFanLayout({ children }: RadialFanLayoutProps) {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  function isActive(path: string) {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  }

  function go(path: string) {
    navigate(path);
    setOpen(false);
  }

  // Fan spreads upward in a 120 degree arc from bottom-left
  const fanAngle = Math.PI * 0.65;
  const startAngle = -Math.PI / 2 - fanAngle / 2;
  const step = fanAngle / (navItems.length - 1);
  const radius = 140;

  return (
    <div className="h-screen bg-bg-primary text-text-primary relative overflow-hidden">
      <main className="h-full overflow-y-auto p-6">{children}</main>

      {/* Trigger — bottom left */}
      <button
        onClick={() => setOpen(!open)}
        className={`fixed bottom-6 left-6 z-40 w-14 h-14 rounded-full flex items-center justify-center shadow-2xl transition-all duration-300 ${
          open ? "bg-danger text-white rotate-45" : "bg-accent text-white hover:scale-110"
        }`}
      >
        <i className="ms ms-planeswalker" style={{ fontSize: "1.5em" }} />
      </button>

      {/* Fan items */}
      {navItems.map((item, i) => {
        const angle = startAngle + step * i;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;
        const active = isActive(item.path);

        return (
          <button
            key={item.id}
            onClick={() => go(item.path)}
            className={`fixed z-30 flex items-center gap-2 transition-all duration-300 ${
              open ? "opacity-100 scale-100" : "opacity-0 scale-0"
            }`}
            style={{
              bottom: `${24 + 28 - y}px`,
              left: `${24 + 28 + x}px`,
              transitionDelay: open ? `${i * 40}ms` : "0ms",
            }}
          >
            <div className={`w-11 h-11 rounded-full flex items-center justify-center shadow-lg ${
              active
                ? "bg-accent text-white shadow-[0_0_12px_var(--color-accent)]"
                : "bg-bg-secondary border border-border text-text-secondary hover:bg-accent hover:text-white"
            }`}>
              <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: "1.1em" }} />
            </div>
            <span className={`text-xs font-medium px-2 py-1 rounded bg-bg-secondary border border-border text-text-secondary shadow-lg transition-opacity duration-200 ${
              open ? "opacity-100 delay-300" : "opacity-0"
            }`}>
              {item.label}
            </span>
          </button>
        );
      })}

      {open && <div className="fixed inset-0 z-20 bg-black/30" onClick={() => setOpen(false)} />}
    </div>
  );
}
