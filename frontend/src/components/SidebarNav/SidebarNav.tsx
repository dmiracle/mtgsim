type NavItem = {
  id: string;
  label: string;
  icon: string;
};

const navItems: NavItem[] = [
  { id: "home", label: "Home", icon: "🏠" },
  { id: "decks", label: "Decks", icon: "📋" },
  { id: "cards", label: "Cards", icon: "🃏" },
  { id: "sets", label: "Sets", icon: "📦" },
  { id: "prices", label: "Prices", icon: "💲" },
  { id: "draft", label: "Draft", icon: "🎲" },
  { id: "reference", label: "Reference", icon: "📖" },
];

type SidebarNavProps = {
  activeId: string;
  onNavigate: (id: string) => void;
};

export function SidebarNav({ activeId, onNavigate }: SidebarNavProps) {
  return (
    <nav className="w-56 bg-bg-primary border-r border-border flex flex-col h-full">
      <div className="px-4 py-5 border-b border-border">
        <h1 className="text-lg font-bold text-text-primary tracking-tight">MTG Viewer</h1>
      </div>
      <ul className="flex-1 py-2">
        {navItems.map((item) => (
          <li key={item.id}>
            <button
              onClick={() => onNavigate(item.id)}
              className={`w-full text-left px-4 py-2.5 flex items-center gap-3 text-sm transition-colors ${
                activeId === item.id
                  ? "bg-accent-muted text-accent border-r-2 border-accent"
                  : "text-text-muted hover:text-text-primary hover:bg-bg-hover"
              }`}
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
