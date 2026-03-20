import type { KeywordFrequencies } from "@/types/api";

type KeywordCloudProps = {
  frequencies: KeywordFrequencies;
  selectedKeywords: string[];
  onToggleKeyword: (keyword: string) => void;
  keywordDefinitions?: Record<string, string>;
};

type CloudItem = {
  keyword: string;
  count: number;
  category: string;
};

const categoryColors: Record<string, string> = {
  keyword_abilities: "text-accent",
  keyword_actions: "text-success",
  ability_words: "text-warning",
};

const categoryLabels: Record<string, string> = {
  keyword_abilities: "Keyword Abilities",
  keyword_actions: "Keyword Actions",
  ability_words: "Ability Words",
};

function buildItems(frequencies: KeywordFrequencies): CloudItem[] {
  const items: CloudItem[] = [];
  for (const [category, map] of Object.entries(frequencies)) {
    for (const [keyword, count] of Object.entries(map)) {
      items.push({ keyword, count, category });
    }
  }
  return items.sort((a, b) => b.count - a.count);
}

function getFontSize(count: number, max: number, min: number): number {
  if (max === min) return 14;
  const ratio = (count - min) / (max - min);
  return 11 + ratio * 13; // 11px to 24px
}

export function KeywordCloud({
  frequencies,
  selectedKeywords,
  onToggleKeyword,
  keywordDefinitions = {},
}: KeywordCloudProps) {
  const items = buildItems(frequencies);
  if (items.length === 0) return null;

  const maxCount = Math.max(...items.map((i) => i.count));
  const minCount = Math.min(...items.map((i) => i.count));

  // Group by category for the legend
  const categories = [...new Set(items.map((i) => i.category))];

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-text-secondary">Keywords</h3>
        <div className="flex items-center gap-3">
          {categories.map((cat) => (
            <span key={cat} className="flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${categoryColors[cat]?.replace("text-", "bg-")}`} />
              <span className="text-[10px] text-text-muted">{categoryLabels[cat]}</span>
            </span>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-1.5 py-2">
        {items.map((item) => {
          const active = selectedKeywords.includes(item.keyword);
          const fontSize = getFontSize(item.count, maxCount, minCount);
          const colorClass = categoryColors[item.category] ?? "text-text-secondary";

          return (
            <button
              key={item.keyword}
              onClick={() => onToggleKeyword(item.keyword)}
              title={keywordDefinitions[item.keyword] ? `${keywordDefinitions[item.keyword]} (${item.count})` : `${item.count}`}
              className={`px-1.5 py-0.5 rounded transition-all leading-none ${
                active
                  ? "bg-accent text-white ring-1 ring-accent"
                  : `${colorClass} opacity-70 hover:opacity-100 hover:bg-bg-tertiary`
              }`}
              style={{ fontSize }}
            >
              {item.keyword}
            </button>
          );
        })}
      </div>

      {selectedKeywords.length > 0 && (
        <div className="flex items-center gap-2 pt-1 border-t border-border">
          <span className="text-[10px] text-text-muted">Active:</span>
          <div className="flex flex-wrap gap-1">
            {selectedKeywords.map((kw) => (
              <span
                key={kw}
                className="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded bg-accent/20 text-accent"
              >
                {kw}
                <button
                  onClick={() => onToggleKeyword(kw)}
                  className="hover:text-white transition-colors"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
