import type { CardSet } from "../types";

interface SetPickerProps {
  sets: CardSet[];
  selected: string[];
  query: string;
  onQueryChange: (q: string) => void;
  onToggle: (code: string) => void;
}

export function SetPicker({ sets, selected, query, onQueryChange, onToggle }: SetPickerProps) {
  return (
    <div className="space-y-2">
      {selected.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selected.map((code) => (
            <button
              key={code}
              onClick={() => onToggle(code)}
              className="min-h-9 rounded-full bg-accent px-3 text-sm font-semibold text-bg"
            >
              {code} ✕
            </button>
          ))}
        </div>
      )}
      <input
        value={query}
        onChange={(e) => onQueryChange(e.target.value)}
        placeholder="Search sets…"
        className="w-full rounded-lg border border-line bg-surface px-3 py-2.5 text-base"
      />
      <ul className="max-h-56 overflow-y-auto rounded-lg border border-line divide-y divide-line">
        {sets.map((s) => (
          <li key={s.code}>
            <button
              onClick={() => onToggle(s.code)}
              className={`flex w-full items-center gap-3 px-3 py-2.5 text-left ${
                selected.includes(s.code) ? "bg-raised" : ""
              }`}
            >
              <span className="w-12 font-mono text-sm text-accent">{s.code}</span>
              <span className="flex-1 truncate">{s.name}</span>
              <span className="text-xs text-muted">{s.release_date?.slice(0, 4)}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
