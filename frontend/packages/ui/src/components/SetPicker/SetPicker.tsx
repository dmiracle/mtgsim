import { SetBadge } from "@/components/SetBadge/SetBadge";

type SetItem = {
  code: string;
  name: string;
  base_set_size: number;
};

type SetPickerProps = {
  sets: SetItem[];
  selected: string[];
  search: string;
  onSearchChange: (query: string) => void;
  onToggle: (code: string) => void;
  onClear?: () => void;
};

export function SetPicker({ sets, selected, search, onSearchChange, onToggle, onClear }: SetPickerProps) {
  return (
    <div className="space-y-3">
      {/* Selected chips */}
      {selected.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5">
          {selected.map((code) => (
            <button
              key={code}
              onClick={() => onToggle(code)}
              className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full bg-accent/15 text-accent border border-accent/30 hover:bg-accent/25 transition-colors"
            >
              {code.toUpperCase()}
              <span className="text-accent/60 ml-0.5">&times;</span>
            </button>
          ))}
          {onClear && selected.length > 1 && (
            <button
              onClick={onClear}
              className="text-[10px] text-text-muted hover:text-danger transition-colors ml-1"
            >
              Clear all
            </button>
          )}
        </div>
      )}

      {/* Search */}
      <div className="relative">
        <i className="ms ms-ability-scry absolute left-3 top-1/2 -translate-y-1/2 text-text-muted text-sm" />
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search sets..."
          className="w-full bg-bg-secondary border border-border rounded-xl pl-9 pr-3 py-2.5 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-all"
        />
      </div>

      {/* Set list */}
      <div className="space-y-1.5">
        {sets.map((s) => {
          const isSelected = selected.includes(s.code);
          return (
            <button
              key={s.code}
              onClick={() => onToggle(s.code)}
              className={`w-full flex items-center justify-between px-4 py-3.5 rounded-xl border-2 transition-all text-left active:scale-[0.98] ${
                isSelected
                  ? "bg-accent/10 border-accent shadow-sm shadow-accent/10"
                  : "bg-bg-secondary border-transparent hover:border-border"
              }`}
            >
              <div className="flex items-center gap-3 min-w-0">
                {isSelected && (
                  <div className="w-5 h-5 rounded-full bg-accent flex items-center justify-center shrink-0">
                    <span className="text-white text-xs font-bold">✓</span>
                  </div>
                )}
                <SetBadge code={s.code} name={s.name} size="sm" />
              </div>
              <span className="text-xs text-text-muted ml-2 shrink-0">{s.base_set_size}</span>
            </button>
          );
        })}
        {sets.length === 0 && (
          <p className="text-center text-text-muted text-sm py-6">No sets found</p>
        )}
      </div>
    </div>
  );
}
