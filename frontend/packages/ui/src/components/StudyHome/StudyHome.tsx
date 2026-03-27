type StudyMode = {
  key: string;
  label: string;
  description: string;
  iconClass: string;
  badge?: number;
};

type StudyHomeProps = {
  modes: StudyMode[];
  onSelect: (key: string) => void;
};

export function StudyHome({ modes, onSelect }: StudyHomeProps) {
  return (
    <div className="max-w-lg mx-auto px-4 py-12 min-h-screen">
      <div className="text-center mb-10">
        <i className="ms ms-planeswalker text-5xl text-accent" />
        <h1 className="text-3xl font-bold text-text-primary mt-3">MTG Study</h1>
      </div>

      <div className="space-y-3">
        {modes.map((m) => (
          <button
            key={m.key}
            onClick={() => onSelect(m.key)}
            className="w-full flex items-center gap-4 px-5 py-5 rounded-xl bg-bg-secondary border border-border hover:border-accent transition-colors text-left"
          >
            <i className={`${m.iconClass} text-2xl text-accent`} />
            <div className="flex-1">
              <p className="text-sm font-semibold text-text-primary">{m.label}</p>
              <p className="text-xs text-text-muted">{m.description}</p>
            </div>
            {m.badge !== undefined && m.badge > 0 && (
              <span className="bg-accent text-white text-xs font-bold px-2 py-0.5 rounded-full">
                {m.badge}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
