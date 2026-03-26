import { useState, useEffect, type ReactNode } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ManaIcon } from "@/components/ManaSymbols/ManaSymbols";

const navItems = [
  { id: "home", path: "/", iconClass: "ms-planeswalker", iconFont: "ms", label: "Home" },
  { id: "decks", path: "/decks", iconClass: "ms-saga", iconFont: "ms", label: "Decks" },
  { id: "cards", path: "/cards", iconClass: "ms-creature", iconFont: "ms", label: "Cards" },
  { id: "sets", path: "/sets", iconClass: "ss-pmtg1", iconFont: "ss", label: "Sets" },
  { id: "prices", path: "/prices", iconClass: "ms-loyalty-up", iconFont: "ms", label: "Prices" },
  { id: "draft", path: "/draft", iconClass: "ms-chaos", iconFont: "ms", label: "Draft" },
  { id: "reference", path: "/reference", iconClass: "ms-ability-activated", iconFont: "ms", label: "Reference" },
];

const manaColors = ["W", "U", "B", "R", "G"];

type RadialManaLayoutProps = { children: ReactNode };

export function RadialManaLayout({ children }: RadialManaLayoutProps) {
  const [open, setOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 640);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const handler = () => setIsMobile(window.innerWidth < 640);
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, []);

  function isActive(path: string) {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  }

  function go(path: string) {
    navigate(path);
    setOpen(false);
  }

  const navRadius = isMobile ? 90 : 130;
  const manaRadius = isMobile ? 140 : 210;
  const angleStep = (Math.PI * 2) / navItems.length;
  const manaAngleStep = (Math.PI * 2) / manaColors.length;
  const startAngle = -Math.PI / 2;

  return (
    <div className="h-screen bg-bg-primary text-text-primary relative overflow-hidden">
      <main className={`h-full overflow-y-auto p-4 sm:p-6 transition-all duration-500 ${open ? "blur-sm scale-95 opacity-30" : ""}`}>
        {children}
      </main>

      <button
        onClick={() => setOpen(!open)}
        className={`fixed bottom-4 left-1/2 -translate-x-1/2 sm:bottom-6 z-40 w-12 h-12 sm:w-14 sm:h-14 rounded-full flex items-center justify-center shadow-2xl transition-all duration-300 ${
          open ? "bg-bg-secondary border-2 border-accent scale-110" : "bg-accent text-white hover:scale-110"
        }`}
      >
        <i className={`ms ms-planeswalker ${open ? "text-accent" : "text-white"}`} style={{ fontSize: isMobile ? "1.2em" : "1.5em" }} />
      </button>

      {open && (
        <div className="fixed inset-0 z-30 flex items-center justify-center">
          {/* Outer mana ring — hidden on very small screens */}
          {!isMobile && manaColors.map((color, i) => {
            const angle = startAngle + manaAngleStep * i;
            const x = Math.cos(angle) * manaRadius;
            const y = Math.sin(angle) * manaRadius;
            return (
              <div
                key={color}
                className="absolute opacity-30"
                style={{
                  top: `calc(50% + ${y}px)`,
                  left: `calc(50% + ${x}px)`,
                  transform: "translate(-50%, -50%)",
                }}
              >
                <ManaIcon symbol={color} size="lg" shadow={false} />
              </div>
            );
          })}

          {/* Center emblem */}
          <div className={`absolute ${isMobile ? "w-14 h-14" : "w-20 h-20"} rounded-full bg-bg-secondary border-2 border-accent flex items-center justify-center shadow-[0_0_30px_var(--color-accent-muted)]`}>
            <i className="ms ms-planeswalker text-accent" style={{ fontSize: isMobile ? "1.3em" : "2em" }} />
          </div>

          {/* Nav items */}
          {navItems.map((item, i) => {
            const angle = startAngle + angleStep * i;
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
                }}
              >
                <div className="flex flex-col items-center gap-1 group">
                  <div className={`${isMobile ? "w-10 h-10" : "w-12 h-12"} rounded-full flex items-center justify-center shadow-xl transition-all group-hover:scale-110 ${
                    active
                      ? "bg-accent text-white shadow-[0_0_16px_var(--color-accent)]"
                      : "bg-bg-secondary border-2 border-border text-text-secondary group-hover:border-accent group-hover:text-accent"
                  }`}>
                    <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: isMobile ? "0.9em" : "1.2em" }} />
                  </div>
                  <span className={`text-[9px] sm:text-[11px] font-medium ${active ? "text-accent" : "text-text-muted group-hover:text-text-primary"}`}>
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
