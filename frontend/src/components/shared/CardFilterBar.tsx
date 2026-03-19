import { useDebounce } from "../../hooks/useDebounce"
import { useEffect, useState } from "react"

const RARITIES = ["common", "uncommon", "rare", "mythic"]
const COLORS = ["W", "U", "B", "R", "G"]
const TYPES = ["Creature", "Instant", "Sorcery", "Enchantment", "Artifact", "Planeswalker", "Land"]
const SORTS = [
  { value: "name", label: "Name" },
  { value: "mana_value", label: "Mana Value" },
  { value: "rarity", label: "Rarity" },
  { value: "price", label: "Price" },
]
const OWNERSHIP = [
  { value: "", label: "All" },
  { value: "true", label: "Owned" },
  { value: "false", label: "Not Owned" },
]

interface Props {
  filters: Record<string, unknown>
  onFilterChange: (key: string, value: unknown) => void
  tags?: { tag: string; count: number }[]
  showSearch?: boolean
  showText?: boolean
  showOwnership?: boolean
  showUnique?: boolean
}

export default function CardFilterBar({
  filters,
  onFilterChange,
  tags,
  showSearch = true,
  showText = true,
  showOwnership = true,
  showUnique = false,
}: Props) {
  const [textInput, setTextInput] = useState((filters.text as string) || "")
  const debouncedText = useDebounce(textInput)

  useEffect(() => {
    if (debouncedText !== (filters.text || "")) {
      onFilterChange("text", debouncedText || undefined)
    }
  }, [debouncedText])

  const currentColors = ((filters.colors as string) || "").split("").filter(Boolean)

  function toggleColor(c: string) {
    const next = currentColors.includes(c)
      ? currentColors.filter((x) => x !== c)
      : [...currentColors, c]
    onFilterChange("colors", next.join("") || undefined)
  }

  return (
    <div className="flex flex-wrap gap-2 items-center py-3">
      {showSearch && (
        <input
          type="text"
          placeholder="Search name..."
          value={(filters.q as string) || ""}
          onChange={(e) => onFilterChange("q", e.target.value || undefined)}
          className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] w-40"
        />
      )}
      {showText && (
        <input
          type="text"
          placeholder="Oracle text..."
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] w-36"
        />
      )}
      <select
        value={(filters.rarity as string) || ""}
        onChange={(e) => onFilterChange("rarity", e.target.value || undefined)}
        className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
      >
        <option value="">All Rarities</option>
        {RARITIES.map((r) => (
          <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
        ))}
      </select>
      <div className="flex gap-0.5">
        {COLORS.map((c) => (
          <button
            key={c}
            onClick={() => toggleColor(c)}
            className={`w-7 h-7 rounded text-xs font-bold ${
              currentColors.includes(c)
                ? "bg-[var(--color-accent)] text-white"
                : "bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)]"
            }`}
          >
            {c}
          </button>
        ))}
      </div>
      <select
        value={(filters.type as string) || ""}
        onChange={(e) => onFilterChange("type", e.target.value || undefined)}
        className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
      >
        <option value="">All Types</option>
        {TYPES.map((t) => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>
      {tags && tags.length > 0 && (
        <select
          value={(filters.tags as string) || ""}
          onChange={(e) => onFilterChange("tags", e.target.value || undefined)}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] max-w-48"
        >
          <option value="">All Tags</option>
          {tags.map((t) => (
            <option key={t.tag} value={t.tag}>{t.tag} ({t.count})</option>
          ))}
        </select>
      )}
      {showOwnership && (
        <select
          value={filters.owns === true ? "true" : filters.owns === false ? "false" : ""}
          onChange={(e) => onFilterChange("owns", e.target.value === "" ? undefined : e.target.value === "true")}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          {OWNERSHIP.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      )}
      <div className="flex items-center gap-1">
        <select
          value={(filters.sort as string) || "name"}
          onChange={(e) => onFilterChange("sort", e.target.value)}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          {SORTS.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
        <button
          onClick={() => onFilterChange("order", filters.order === "desc" ? "asc" : "desc")}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
        >
          {filters.order === "desc" ? "↓" : "↑"}
        </button>
      </div>
      {showUnique && (
        <label className="flex items-center gap-1 text-sm text-[var(--color-text-secondary)]">
          <input
            type="checkbox"
            checked={filters.unique === true}
            onChange={(e) => onFilterChange("unique", e.target.checked || undefined)}
            className="accent-[var(--color-accent)]"
          />
          Unique
        </label>
      )}
    </div>
  )
}
