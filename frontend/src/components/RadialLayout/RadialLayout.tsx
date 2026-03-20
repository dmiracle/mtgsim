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

type RadialLayoutProps = { children: ReactNode };

export function RadialLayout({ children }: RadialLayoutProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  function isActive(path: string) {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  }

  function go(path: string) {
    navigate(path);
    setMenuOpen(false);
  }

  const radius = 130;
  const angleStep = (Math.PI * 2) / navItems.length;
  const startAngle = -Math.PI / 2;

  return (
    <div className="h-screen bg-bg-primary text-text-primary relative overflow-hidden">
      <main className="h-full overflow-y-auto p-6">{children}</main>

      {/* Radial menu trigger — bottom right */}
      <button
        onClick={() => setMenuOpen(!menuOpen)}
        className={`fixed bottom-8 right-8 z-40 w-14 h-14 rounded-full flex items-center justify-center shadow-2xl transition-all duration-300 ${
          menuOpen
            ? "bg-danger text-white rotate-45 scale-110"
            : "bg-accent text-white hover:scale-110"
        }`}
      >
        <i className="ms ms-planeswalker" style={{ fontSize: "1.5em" }} />
      </button>

      {/* Radial menu items */}
      {menuOpen && (
        <div className="fixed bottom-8 right-8 z-30">
          {navItems.map((item, i) => {
            const angle = startAngle + angleStep * i;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            const active = isActive(item.path);

            return (
              <button
                key={item.id}
                onClick={() => go(item.path)}
                className={`absolute w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 ${
                  active
                    ? "bg-accent text-white shadow-[0_0_12px_var(--color-accent)]"
                    : "bg-bg-secondary border border-border text-text-secondary hover:bg-accent hover:text-white hover:border-accent"
                }`}
                style={{
                  transform: `translate(${x}px, ${y}px) translate(-50%, -50%)`,
                  top: "50%",
                  left: "50%",
                }}
                title={item.label}
              >
                <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: "1.1em" }} />
              </button>
            );
          })}
        </div>
      )}

      {/* Backdrop */}
      {menuOpen && (
        <div className="fixed inset-0 z-20 bg-black/30" onClick={() => setMenuOpen(false)} />
      )}
    </div>
  );
}
