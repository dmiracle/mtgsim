import { NavLink } from "react-router-dom"
import { useGlossary } from "../../GlossaryContext"

const NAV_ITEMS = [
  { to: "/", label: "Home" },
  { to: "/decks", label: "Decks" },
  { to: "/cards", label: "Cards" },
  { to: "/sets", label: "Sets" },
  { to: "/prices", label: "Prices" },
  { to: "/draft", label: "Draft" },
  { to: "/reference", label: "Reference" },
]

export default function Sidebar() {
  const { toggle } = useGlossary()

  return (
    <aside className="w-56 shrink-0 h-screen flex flex-col bg-[var(--color-bg-secondary)] border-r border-[var(--color-border)]">
      <NavLink to="/" className="px-5 py-4 text-lg font-bold bg-[var(--color-bg-tertiary)] text-[var(--color-accent)] block">
        MTG Viewer
      </NavLink>
      <nav className="flex-1 overflow-y-auto py-2">
        {NAV_ITEMS.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `block px-5 py-2.5 text-sm transition-colors ${
                isActive
                  ? "text-[var(--color-accent)] bg-[var(--color-bg-tertiary)] border-r-2 border-[var(--color-accent)]"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-primary)]"
              }`
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>
      <button
        onClick={toggle}
        className="px-5 py-3 text-sm text-left text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-primary)] border-t border-[var(--color-border)]"
      >
        Glossary
      </button>
    </aside>
  )
}
