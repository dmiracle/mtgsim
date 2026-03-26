type KeywordGroup = {
  category: string;
  keywords: { term: string; definition: string }[];
};

type CardKeywordsProps = {
  groups: KeywordGroup[];
};

export function CardKeywords({ groups }: CardKeywordsProps) {
  const nonEmpty = groups.filter((g) => g.keywords.length > 0);
  if (nonEmpty.length === 0) return null;

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
      <h3 className="text-sm font-medium text-text-secondary">Keywords</h3>
      {nonEmpty.map((group) => (
        <div key={group.category} className="space-y-1.5">
          <h4 className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">
            {group.category}
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {group.keywords.map((kw) => (
              <span
                key={kw.term}
                title={kw.definition}
                className="px-2 py-1 text-xs rounded bg-bg-tertiary text-text-secondary border border-border hover:border-accent hover:text-accent transition-colors cursor-help"
              >
                {kw.term}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
