type ResultItem = {
  set: string;
  created: number;
};

type GenerateResultProps = {
  results: ResultItem[];
  onStudy: () => void;
  onGenerateMore: () => void;
};

export function GenerateResult({ results, onStudy, onGenerateMore }: GenerateResultProps) {
  const total = results.reduce((sum, r) => sum + r.created, 0);

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <i className="ms ms-ability-adventure text-4xl text-success" />
        <h2 className="text-xl font-bold text-text-primary">
          {total} {total === 1 ? "card" : "cards"} created
        </h2>
        <p className="text-sm text-text-muted">
          from {results.length} {results.length === 1 ? "set" : "sets"}
        </p>
      </div>

      <div className="bg-bg-secondary rounded-xl border border-border overflow-hidden">
        {results.map((r, i) => (
          <div
            key={r.set}
            className={`flex items-center justify-between px-4 py-3 ${
              i > 0 ? "border-t border-border" : ""
            }`}
          >
            <span className="text-sm font-medium text-text-primary">{r.set.toUpperCase()}</span>
            <span className="text-xs text-text-muted">{r.created} cards</span>
          </div>
        ))}
      </div>

      <div className="space-y-2">
        <button
          onClick={onStudy}
          className="w-full py-3.5 rounded-xl bg-accent text-white font-semibold text-sm hover:bg-accent/80 active:scale-[0.98] transition-all"
        >
          Study Now
        </button>
        <button
          onClick={onGenerateMore}
          className="w-full py-3.5 rounded-xl bg-bg-secondary border border-border text-text-secondary font-semibold text-sm hover:border-border-hover active:scale-[0.98] transition-all"
        >
          Generate More
        </button>
      </div>
    </div>
  );
}
