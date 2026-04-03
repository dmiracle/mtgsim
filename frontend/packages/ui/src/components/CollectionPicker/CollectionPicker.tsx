type Collection = {
  id: number;
  name: string;
  card_count: number;
};

type CollectionPickerProps = {
  collections: Collection[];
  dueCount: number;
  onStudyAll: () => void;
  onStudyCollection: (name: string) => void;
  onBack?: () => void;
};

function formatName(name: string) {
  return name.replace(/_/g, " ");
}

export function CollectionPicker({
  collections,
  dueCount,
  onStudyAll,
  onStudyCollection,
  onBack,
}: CollectionPickerProps) {
  return (
    <div className="max-w-lg mx-auto px-4 py-8 min-h-screen">
      <div className="flex items-center gap-3 mb-6">
        {onBack && (
          <button
            onClick={onBack}
            className="text-xs text-text-muted hover:text-accent transition-colors"
          >
            <i
              className="ms ms-ability-transform"
              style={{ transform: "scaleX(-1)", display: "inline-block", fontSize: "1.2em" }}
            />
          </button>
        )}
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Study</h1>
          <p className="text-sm text-text-muted">{dueCount} cards due</p>
        </div>
      </div>

      <button
        onClick={onStudyAll}
        disabled={dueCount === 0}
        className="w-full py-3 mb-6 rounded-lg bg-accent text-white font-semibold text-sm hover:bg-accent/80 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Study All Due ({dueCount})
      </button>

      {collections.length === 0 && (
        <p className="text-center text-text-muted text-sm py-8">No collections yet.</p>
      )}

      <div className="space-y-1">
        {collections.map((c) => (
          <button
            key={c.id}
            onClick={() => onStudyCollection(c.name)}
            className="w-full flex items-center justify-between px-4 py-4 rounded-lg bg-bg-secondary hover:bg-bg-tertiary border border-border transition-colors text-left"
          >
            <span className="text-sm font-medium text-text-primary">{formatName(c.name)}</span>
            <span className="text-xs text-text-muted">{c.card_count} cards</span>
          </button>
        ))}
      </div>
    </div>
  );
}
