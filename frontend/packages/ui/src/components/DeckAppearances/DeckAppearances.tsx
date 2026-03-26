type DeckAppearance = {
  file: string;
  name: string;
  count: number;
};

type DeckAppearancesProps = {
  decks: DeckAppearance[];
  onSelect: (file: string) => void;
};

export function DeckAppearances({ decks, onSelect }: DeckAppearancesProps) {
  if (decks.length === 0) return null;

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
      <h3 className="text-sm font-medium text-text-secondary">
        Appears In <span className="text-text-muted font-normal">({decks.length} decks)</span>
      </h3>
      <div className="space-y-1">
        {decks.map((d) => (
          <button
            key={d.file}
            onClick={() => onSelect(d.file)}
            className="w-full flex items-center justify-between px-3 py-2 rounded hover:bg-bg-hover transition-colors text-left"
          >
            <span className="text-xs text-text-primary">{d.name}</span>
            <span className="text-xs text-text-muted">×{d.count}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
