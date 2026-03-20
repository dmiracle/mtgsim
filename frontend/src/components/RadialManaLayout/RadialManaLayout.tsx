import { useState, type ReactNode } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ManaIcon } from "@/components/ManaSymbols/ManaSymbols";

const navItems = [
  { id: "home", path: "/", iconClass: "ms-planeswalker", iconFont: "ms", label: "Home", mana: null },
  { id: "decks", path: "/decks", iconClass: "ms-saga", iconFont: "ms", label: "Decks", mana: null },
  { id: "cards", path: "/cards", iconClass: "ms-creature", iconFont: "ms", label: "Cards", mana: null },
  { id: "sets", path: "/sets", iconClass: "ss-pmtg1", iconFont: "ss", label: "Sets", mana: null },
  { id: "prices", path: "/prices", iconClass: "ms-loyalty-up", iconFont: "ms", label: "Prices", mana: null },
  { id: "draft", path: "/draft", iconClass: "ms-chaos", iconFont: "ms", label: "Draft", mana: null },
  { id: "reference", path: "/reference", iconClass: "ms-ability-activated", iconFont: "ms", label: "Reference", mana: null },
];

// Mana wheel positions — 5 colors in a ring + colorless center
const manaColors = ["W", "U", "B", "R", "G"];

type RadialManaLayoutProps = { children: ReactNode };

export function RadialManaLayout({ children }: RadialManaLayoutProps) {
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

  // Inner ring: nav items
  const navRadius = 130;
  const navAngleStep = (Math.PI * 2) / navItems.length;
  const navStart = -Math.PI / 2;

  // Outer ring: mana colors (decorative)
  const manaRadius = 210;
  const manaAngleStep = (Math.PI * 2) / manaColors.length;
  const manaStart = -Math.PI / 2;

  return (
    <div className="h-screen bg-bg-primary text-text-primary relative overflow-hidden">
      <main className={`h-full overflow-y-auto p-6 transition-all duration-500 ${open ? "blur-sm scale-95 opacity-30" : ""}`}>
        {children}
      </main>

      {/* Trigger — bottom center */}
      <button
        onClick={() => setOpen(!open)}
        className={`fixed bottom-6 left-1/2 -translate-x-1/2 z-40 w-14 h-14 rounded-full flex items-center justify-center shadow-2xl transition-all duration-300 ${
          open ? "bg-bg-secondary border-2 border-accent scale-110" : "bg-accent text-white hover:scale-110"
        }`}
      >
        <i className={`ms ms-planeswalker ${open ? "text-accent" : "text-white"}`} style={{ fontSize: "1.5em" }} />
      </button>

      {open && (
        <div className="fixed inset-0 z-30 flex items-center justify-center">
          {/* Outer mana color ring */}
          {manaColors.map((color, i) => {
            const angle = manaStart + manaAngleStep * i;
            const x = Math.cos(angle) * manaRadius;
            const y = Math.sin(angle) * manaRadius;

            return (
              <div
                key={color}
                className="absolute opacity-30 transition-all duration-700"
                style={{
                  top: `calc(50% + ${y}px)`,
                  left: `calc(50% + ${x}px)`,
                  transform: "translate(-50%, -50%)",
                  transitionDelay: `${i * 60}ms`,
                }}
              >
                <ManaIcon symbol={color} size="lg" shadow={false} />
              </div>
            );
          })}

          {/* Connecting lines from center to nav items */}
          <svg className="absolute inset-0 pointer-events-none" style={{ width: "100%", height: "100%" }}>
            {navItems.map((_, i) => {
              const angle = navStart + navAngleStep * i;
              const x = Math.cos(angle) * navRadius;
              const y = Math.sin(angle) * navRadius;
              return (
                <line
                  key={i}
                  x1="50%" y1="50%"
                  x2={`calc(50% + ${x}px)`} y2={`calc(50% + ${y}px)`}
                  stroke="var(--color-border)"
                  strokeWidth="1"
                  strokeDasharray="4,4"
                  opacity="0.3"
                />
              );
            })}
          </svg>

          {/* Center planeswalker emblem */}
          <div className="absolute w-20 h-20 rounded-full bg-bg-secondary border-2 border-accent flex items-center justify-center shadow-[0_0_30px_var(--color-accent-muted)]">
            <i className="ms ms-planeswalker text-accent" style={{ fontSize: "2em" }} />
          </div>

          {/* Nav items ring */}
          {navItems.map((item, i) => {
            const angle = navStart + navAngleStep * i;
            const x = Math.cos(angle) * navRadius;
            const y = Math.sin(angle) * navRadius;
            const active = isActive(item.path);

            return (
              <button
                key={item.id}
                onClick={() => go(item.path)}
                className="absolute z-10 transition-all duration-500"
                style={{
                  top: `calc(50% + ${y}px)`,
                  left: `calc(50% + ${x}px)`,
                  transform: "translate(-50%, -50%)",
                  transitionDelay: `${i * 50}ms`,
                }}
              >
                <div className="flex flex-col items-center gap-1.5 group">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center shadow-xl transition-all group-hover:scale-115 ${
                    active
                      ? "bg-accent text-white shadow-[0_0_16px_var(--color-accent)]"
                      : "bg-bg-secondary border-2 border-border text-text-secondary group-hover:border-accent group-hover:text-accent"
                  }`}>
                    <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: "1.2em" }} />
                  </div>
                  <span className={`text-[11px] font-medium ${active ? "text-accent" : "text-text-muted group-hover:text-text-primary"}`}>
                    {item.label}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      )}

      {open && <div className="fixed inset-0 z-20 bg-black/50" onClick={() => setOpen(false)} />}
    </div>
  );
}
