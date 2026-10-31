export type UserTagChipsProps = {
  userTags: string[];
  oracleTags?: string[];
  onTagClick?: (tag: string, source: "user" | "oracle") => void;
  onRemove?: (tag: string) => void;
  onAdd?: () => void;
};

export function UserTagChips({ userTags, oracleTags = [], onTagClick, onRemove, onAdd }: UserTagChipsProps) {
  if (userTags.length === 0 && oracleTags.length === 0 && !onAdd) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {userTags.map((tag) => (
        <span
          key={tag}
          className="inline-flex items-center gap-1 px-2 py-1 text-xs rounded bg-accent/10 text-accent border border-accent/30"
        >
          {onTagClick ? (
            <button onClick={() => onTagClick(tag, "user")} className="hover:underline">
              {tag}
            </button>
          ) : (
            tag
          )}
          {onRemove && (
            <button
              onClick={() => onRemove(tag)}
              aria-label={`Remove ${tag}`}
              className="text-accent/60 hover:text-danger transition-colors"
            >
              ×
            </button>
          )}
        </span>
      ))}
      {oracleTags.map((tag) => (
        <span
          key={tag}
          title="Oracle tag"
          className="px-2 py-1 text-xs rounded bg-bg-tertiary text-text-secondary border border-border"
        >
          {onTagClick ? (
            <button onClick={() => onTagClick(tag, "oracle")} className="hover:text-accent transition-colors">
              {tag}
            </button>
          ) : (
            tag
          )}
        </span>
      ))}
      {onAdd && (
        <button
          onClick={onAdd}
          className="px-2 py-1 text-xs rounded border border-dashed border-border text-text-muted hover:text-accent hover:border-accent transition-colors"
        >
          + tag
        </button>
      )}
    </div>
  );
}
