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

type FloatingNavLayoutProps = { children: ReactNode };

export function FloatingNavLayout({ children }: FloatingNavLayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [hovered, setHovered] = useState<string | null>(null);

  function isActive(path: string) {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  }

  return (
    <div className="h-screen bg-bg-primary text-text-primary relative overflow-hidden">
      <main className="h-full overflow-y-auto p-4 sm:p-6 pb-20 sm:pb-24">{children}</main>

      {/* Floating dock — smaller on mobile */}
      <div className="absolute bottom-3 sm:bottom-6 left-1/2 -translate-x-1/2 z-30">
        <nav className="flex items-end gap-0.5 sm:gap-1 px-2 sm:px-3 py-1.5 sm:py-2 rounded-2xl bg-bg-secondary/90 backdrop-blur-lg border border-border shadow-2xl">
          {navItems.map((item) => {
            const active = isActive(item.path);
            const isHovered = hovered === item.id;
            const scale = isHovered ? "scale-125" : active ? "scale-110" : "scale-100";

            return (
              <button
                key={item.id}
                onClick={() => navigate(item.path)}
                onMouseEnter={() => setHovered(item.id)}
                onMouseLeave={() => setHovered(null)}
                className={`relative flex flex-col items-center transition-all duration-200 ${scale}`}
              >
                <div className={`w-9 h-9 sm:w-11 sm:h-11 rounded-xl flex items-center justify-center transition-colors ${
                  active
                    ? "bg-accent text-white shadow-[0_0_12px_var(--color-accent)]"
                    : "text-text-muted hover:bg-bg-tertiary hover:text-text-primary"
                }`}>
                  <i className={`${item.iconFont} ${item.iconClass}`} style={{ fontSize: "1em" }} />
                </div>
                {(isHovered || active) && (
                  <span className="absolute -top-6 sm:-top-7 text-[9px] sm:text-[10px] font-medium text-text-secondary bg-bg-secondary border border-border rounded px-1 sm:px-1.5 py-0.5 whitespace-nowrap shadow-lg">
                    {item.label}
                  </span>
                )}
                {active && <div className="w-1 h-1 rounded-full bg-accent mt-0.5 sm:mt-1" />}
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
