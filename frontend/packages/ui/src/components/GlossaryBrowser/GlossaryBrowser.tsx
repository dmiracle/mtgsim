import { useState } from "react";
import { SearchInput } from "@/components/SearchInput/SearchInput";

type GlossaryEntry = {
  term: string;
  definition: string;
  category: string;
};

type GlossaryBrowserProps = {
  entries: GlossaryEntry[];
};

const CATEGORY_COLORS: Record<string, string> = {
  zone: "bg-accent/15 text-accent",
  "card type": "bg-success/15 text-success",
  format: "bg-warning/15 text-warning",
  keyword: "bg-danger/15 text-danger",
  mechanic: "bg-text-secondary/15 text-text-secondary",
};

export function GlossaryBrowser({ entries }: GlossaryBrowserProps) {
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const categories = [...new Set(entries.map((e) => e.category))].sort();

  const filtered = entries.filter((e) => {
    const matchesCategory = !activeCategory || e.category === activeCategory;
    if (!matchesCategory) return false;
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      e.term.toLowerCase().includes(q) ||
      e.definition.toLowerCase().includes(q) ||
      e.category.toLowerCase().includes(q)
    );
  });

  // Group by first letter
  const grouped = new Map<string, GlossaryEntry[]>();
  for (const entry of filtered) {
    const letter = entry.term[0]?.toUpperCase() ?? "#";
    if (!grouped.has(letter)) grouped.set(letter, []);
    grouped.get(letter)!.push(entry);
  }

  const letters = [...grouped.keys()].sort();

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <SearchInput
            value={search}
            placeholder="Search terms, definitions, or categories..."
            onChange={setSearch}
          />
        </div>
        <span className="text-xs text-text-muted tabular-nums">{filtered.length}</span>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-1">
        <button
          onClick={() => setActiveCategory(null)}
          className={`px-3 py-1.5 text-xs font-medium rounded border transition-all ${
            !activeCategory
              ? "bg-accent text-white border-accent"
              : "bg-bg-secondary border-border text-text-muted hover:border-border-hover"
          }`}
        >
          All
        </button>
        {categories.map((cat) => {
          const colorClass = CATEGORY_COLORS[cat.toLowerCase()] ?? "bg-bg-tertiary text-text-muted";
          const isActive = activeCategory === cat;
          return (
            <button
              key={cat}
              onClick={() => setActiveCategory(isActive ? null : cat)}
              className={`px-3 py-1.5 text-xs font-medium rounded border transition-all ${
                isActive
                  ? "bg-accent text-white border-accent"
                  : `border-border ${colorClass} hover:border-border-hover`
              }`}
            >
              {cat} ({entries.filter((e) => e.category === cat).length})
            </button>
          );
        })}
      </div>

      {/* Letter jump nav */}
      {!search && (
        <div className="flex flex-wrap gap-1">
          {letters.map((letter) => (
            <a
              key={letter}
              href={`#glossary-${letter}`}
              className="w-7 h-7 flex items-center justify-center text-xs font-medium rounded bg-bg-secondary border border-border text-text-muted hover:text-accent hover:border-accent transition-colors"
            >
              {letter}
            </a>
          ))}
        </div>
      )}

      {filtered.length === 0 && (
        <p className="text-sm text-text-muted py-8 text-center">No terms found</p>
      )}

      {letters.map((letter) => (
        <div key={letter} id={`glossary-${letter}`}>
          <h3 className="text-lg font-bold text-text-primary border-b border-border pb-1 mb-2">
            {letter}
          </h3>
          <div className="space-y-1">
            {grouped.get(letter)!.map((entry) => (
              <div
                key={entry.term}
                className="flex items-start gap-3 px-4 py-2.5 rounded-lg hover:bg-bg-hover transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-text-primary">{entry.term}</h4>
                    <span className={`text-[10px] font-medium uppercase tracking-wide px-1.5 py-0.5 rounded ${CATEGORY_COLORS[entry.category.toLowerCase()] ?? "bg-bg-tertiary text-text-muted"}`}>
                      {entry.category}
                    </span>
                  </div>
                  <p className="text-xs text-text-secondary mt-0.5 leading-relaxed">{entry.definition}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
