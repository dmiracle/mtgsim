import { useLocation, useNavigate } from "react-router-dom";

type NavItem = {
  id: string;
  label: string;
  path: string;
  iconClass: string;
  iconFont: "ms" | "ss";
};

const navItems: NavItem[] = [
  { id: "home", label: "Home", path: "/", iconClass: "ms-planeswalker", iconFont: "ms" },
  { id: "decks", label: "Decks", path: "/decks", iconClass: "ms-saga", iconFont: "ms" },
  { id: "cards", label: "Cards", path: "/cards", iconClass: "ms-creature", iconFont: "ms" },
  { id: "sets", label: "Sets", path: "/sets", iconClass: "ss-pmtg1", iconFont: "ss" },
  { id: "prices", label: "Prices", path: "/prices", iconClass: "ms-loyalty-up", iconFont: "ms" },
  { id: "draft", label: "Draft", path: "/draft", iconClass: "ms-chaos", iconFont: "ms" },
  { id: "reference", label: "Reference", path: "/reference", iconClass: "ms-ability-activated", iconFont: "ms" },
];

type SidebarNavProps = {
  onNavigate?: () => void;
};

export function SidebarNav({ onNavigate }: SidebarNavProps = {}) {
  const location = useLocation();
  const navigate = useNavigate();

  function isActive(path: string) {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  }

  return (
    <nav className="w-56 bg-bg-primary border-r border-border flex flex-col h-full shrink-0">
      <div className="px-4 py-5 border-b border-border flex items-center gap-2">
        <i className="ms ms-planeswalker text-accent" style={{ fontSize: "1.4em" }} aria-hidden="true" />
        <h1 className="text-lg text-text-primary">MTG Viewer</h1>
      </div>
      <ul className="flex-1 py-2">
        {navItems.map((item) => {
          const active = isActive(item.path);
          return (
            <li key={item.id}>
              <button
                onClick={() => { navigate(item.path); onNavigate?.(); }}
                className={`w-full text-left px-4 py-2.5 flex items-center gap-3 text-sm transition-colors ${
                  active
                    ? "bg-accent-muted text-accent border-r-2 border-accent"
                    : "text-text-muted hover:text-text-primary hover:bg-bg-hover"
                }`}
              >
                <i
                  className={`${item.iconFont} ${item.iconClass}`}
                  style={{ fontSize: "1.1em", width: "1.2em", textAlign: "center" }}
                  aria-hidden="true"
                />
                {item.label}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
