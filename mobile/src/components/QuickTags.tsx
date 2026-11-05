const QUICK_TAGS = ["payoff", "enabler", "removal", "card advantage"];

interface QuickTagsProps {
  tags: string[];
  onToggle: (tag: string) => void;
}

export function QuickTags({ tags, onToggle }: QuickTagsProps) {
  return (
    <div className="grid grid-cols-4 gap-1.5">
      {QUICK_TAGS.map((tag) => {
        const active = tags.includes(tag);
        return (
          <button
            key={tag}
            onClick={() => onToggle(tag)}
            aria-pressed={active}
            className={`min-h-10 rounded-lg px-1 text-xs font-semibold capitalize leading-tight ${
              active ? "bg-accent text-bg" : "bg-surface text-fg"
            }`}
          >
            {tag}
          </button>
        );
      })}
    </div>
  );
}
