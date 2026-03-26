import { useState } from "react";
import type { KeywordsResponse } from "@/types/api";
import { SearchInput } from "@/components/SearchInput/SearchInput";

type KeywordBrowserProps = {
  keywords: KeywordsResponse;
};

const CATEGORIES = [
  { key: "keyword_abilities" as const, label: "Keyword Abilities" },
  { key: "keyword_actions" as const, label: "Keyword Actions" },
  { key: "ability_words" as const, label: "Ability Words" },
];

export function KeywordBrowser({ keywords }: KeywordBrowserProps) {
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const allEntries = CATEGORIES.flatMap((cat) =>
    keywords[cat.key].map((kw) => ({ ...kw, category: cat.key, categoryLabel: cat.label }))
  );

  const filtered = allEntries.filter((entry) => {
    const matchesSearch = !search ||
      entry.term.toLowerCase().includes(search.toLowerCase()) ||
      entry.definition.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = !activeCategory || entry.category === activeCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-4">
      {/* Search + category filter */}
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <SearchInput
            value={search}
            placeholder="Search keywords or definitions..."
            onChange={setSearch}
          />
        </div>
        <span className="text-xs text-text-muted tabular-nums">{filtered.length}</span>
      </div>

      <div className="flex gap-1">
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
        {CATEGORIES.map((cat) => (
          <button
            key={cat.key}
            onClick={() => setActiveCategory(activeCategory === cat.key ? null : cat.key)}
            className={`px-3 py-1.5 text-xs font-medium rounded border transition-all ${
              activeCategory === cat.key
                ? "bg-accent text-white border-accent"
                : "bg-bg-secondary border-border text-text-muted hover:border-border-hover"
            }`}
          >
            {cat.label} ({keywords[cat.key].length})
          </button>
        ))}
      </div>

      {/* Keyword list */}
      <div className="space-y-1">
        {filtered.length === 0 && (
          <p className="text-sm text-text-muted py-8 text-center">No keywords found</p>
        )}
        {filtered.map((entry) => (
          <div
            key={`${entry.category}-${entry.term}`}
            className="flex items-start gap-4 px-4 py-3 rounded-lg border border-border bg-bg-secondary hover:bg-bg-hover transition-colors"
          >
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-semibold text-text-primary">{entry.term}</h4>
                <span className="text-[10px] uppercase tracking-wide text-text-muted bg-bg-tertiary px-1.5 py-0.5 rounded">
                  {entry.categoryLabel}
                </span>
              </div>
              <p className="text-xs text-text-secondary mt-1 leading-relaxed">{entry.definition}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
