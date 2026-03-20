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

type RadialOrbitalLayoutProps = { children: ReactNode };

export function RadialOrbitalLayout({ children }: RadialOrbitalLayoutProps) {
  const [open, setOpen] = useState(false);
  const [hovered, setHovered] = useState<string | null>(null);
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

  const activePage = navItems.find((n) => isActive(n.path));

  // Orbit around center of screen
  const radius = 180;
  const angleStep = (Math.PI * 2) / navItems.length;
  const startAngle = -Math.PI / 2;

  return (
    <div className="h-screen bg-bg-primary text-text-primary relative overflow-hidden">
      <main className={`h-full overflow-y-auto p-6 transition-all duration-500 ${open ? "blur-sm scale-95 opacity-40" : ""}`}>
        {children}
      </main>

      {/* Center trigger */}
      <button
        onClick={() => setOpen(!open)}
        className={`fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-40 rounded-full flex flex-col items-center justify-center shadow-2xl transition-all duration-500 ${
          open
            ? "w-24 h-24 bg-bg-secondary border-2 border-accent"
            : "w-14 h-14 bg-accent hover:scale-110"
        }`}
      >
        <i className={`ms ms-planeswalker ${open ? "text-accent" : "text-white"}`} style={{ fontSize: open ? "1.8em" : "1.5em" }} />
        {open && activePage && (
          <span className="text-[10px] text-accent mt-0.5">{activePage.label}</span>
        )}
      </button>

      {/* Orbital items */}
      {open && (
        <>
          {/* Orbit ring */}
          <div
            className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 rounded-full border border-border/30 pointer-events-none"
            style={{ width: radius * 2, height: radius * 2 }}
          />

          {navItems.map((item, i) => {
            const angle = startAngle + angleStep * i;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            const active = isActive(item.path);
            const isHovered = hovered === item.id;

            return (
              <button
                key={item.id}
                onClick={() => go(item.path)}
                onMouseEnter={() => setHovered(item.id)}
                onMouseLeave={() => setHovered(null)}
                className="fixed z-30 transition-all duration-500"
                style={{
                  top: `calc(50% + ${y}px)`,
                  left: `calc(50% + ${x}px)`,
                  transform: "translate(-50%, -50%)",
                }}
              >
                <div className={`flex flex-col items-center gap-1.5 transition-transform duration-200 ${isHovered ? "scale-125" : ""}`}>
                  <div className={`w-14 h-14 rounded-full flex items-center justify-center shadow-xl transition-colors ${
                    active
                      ? "bg-accent text-white shadow-[0_0_20px_var(--color-accent)]"
                      : "bg-bg-secondary border-2 border-border text-text-secondary hover:border-accent hover:text-accent"
                  }`}>
                    <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: "1.3em" }} />
                  </div>
                  <span className={`text-xs font-medium transition-colors ${active ? "text-accent" : "text-text-muted"}`}>
                    {item.label}
                  </span>
                </div>
              </button>
            );
          })}

          <div className="fixed inset-0 z-20" onClick={() => setOpen(false)} />
        </>
      )}
    </div>
  );
}
