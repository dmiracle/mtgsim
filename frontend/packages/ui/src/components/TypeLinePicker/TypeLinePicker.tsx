import { useState, useCallback } from "react";

type TypeLinePickerProps = {
  value?: string;
  onChange: (typeLine: string) => void;
};

const SUPERTYPES = [
  { name: "Legendary", iconClass: "ms ms-planeswalker" },
];

const TYPES = [
  { name: "Creature", iconClass: "ms ms-creature" },
  { name: "Instant", iconClass: "ms ms-instant" },
  { name: "Sorcery", iconClass: "ms ms-sorcery" },
  { name: "Enchantment", iconClass: "ms ms-enchantment" },
  { name: "Artifact", iconClass: "ms ms-artifact" },
  { name: "Planeswalker", iconClass: "ms ms-planeswalker" },
  { name: "Land", iconClass: "ms ms-land" },
  { name: "Battle", iconClass: "ms ms-saga" },
];

function parseValue(value: string) {
  const supers = SUPERTYPES.map((s) => s.name).filter((n) => value.includes(n));
  const types = TYPES.map((t) => t.name).filter((n) => value.includes(n));
  const dashIdx = value.indexOf("—");
  const subtype = dashIdx >= 0 ? value.slice(dashIdx + 1).trim() : "";
  return { supers, types, subtype };
}

export function TypeLinePicker({ value = "", onChange }: TypeLinePickerProps) {
  const parsed = parseValue(value);
  const [selectedSupers, setSelectedSupers] = useState<string[]>(parsed.supers);
  const [selectedTypes, setSelectedTypes] = useState<string[]>(parsed.types);
  const [subtype, setSubtype] = useState(parsed.subtype);

  const emit = useCallback((supers: string[], types: string[], sub: string) => {
    const main = [...supers, ...types].join(" ");
    const line = sub ? `${main} — ${sub}` : main;
    onChange(line);
  }, [onChange]);

  function toggleSuper(name: string) {
    const next = selectedSupers.includes(name)
      ? selectedSupers.filter((s) => s !== name)
      : [...selectedSupers, name];
    setSelectedSupers(next);
    emit(next, selectedTypes, subtype);
  }

  function toggleType(name: string) {
    const next = selectedTypes.includes(name)
      ? selectedTypes.filter((t) => t !== name)
      : [...selectedTypes, name];
    setSelectedTypes(next);
    emit(selectedSupers, next, subtype);
  }

  function updateSubtype(s: string) {
    setSubtype(s);
    emit(selectedSupers, selectedTypes, s);
  }

  const prefix = [...selectedSupers, ...selectedTypes].join(" ");

  return (
    <div className="space-y-2.5">
      {/* Supertype + Type icons */}
      <div className="flex flex-wrap items-center justify-center gap-1.5">
        {SUPERTYPES.map((s) => {
          const active = selectedSupers.includes(s.name);
          return (
            <div key={s.name} className="relative group">
              <button
                onClick={() => toggleSuper(s.name)}
                className={`w-10 h-10 rounded-lg border-2 flex items-center justify-center transition-all active:scale-90 ${
                  active
                    ? "bg-accent/15 border-accent text-accent"
                    : "bg-bg-tertiary border-border text-text-muted hover:border-border-hover"
                }`}
              >
                <i className={s.iconClass} style={{ fontSize: "1.2em" }} />
              </button>
              <div className="pointer-events-none absolute -top-7 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                <div className="bg-bg-primary border border-border rounded px-2 py-0.5 text-[10px] font-semibold text-text-secondary whitespace-nowrap shadow-lg">
                  {s.name}
                </div>
              </div>
            </div>
          );
        })}

        <div className="w-px h-6 bg-border mx-0.5" />

        {TYPES.map((t) => {
          const active = selectedTypes.includes(t.name);
          return (
            <div key={t.name} className="relative group">
              <button
                onClick={() => toggleType(t.name)}
                className={`w-10 h-10 rounded-lg border-2 flex items-center justify-center transition-all active:scale-90 ${
                  active
                    ? "bg-accent text-white border-accent"
                    : "bg-bg-tertiary border-border text-text-muted hover:border-border-hover"
                }`}
              >
                <i className={t.iconClass} style={{ fontSize: "1.2em" }} />
              </button>
              <div className="pointer-events-none absolute -top-7 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                <div className="bg-bg-primary border border-border rounded px-2 py-0.5 text-[10px] font-semibold text-text-secondary whitespace-nowrap shadow-lg">
                  {t.name}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Subtype input with type prefix */}
      <div className="flex items-center gap-0 bg-bg-tertiary border border-border rounded-lg overflow-hidden focus-within:border-accent focus-within:ring-1 focus-within:ring-accent/30 transition-all">
        {prefix && (
          <span className="pl-3 pr-1 text-sm text-text-secondary whitespace-nowrap">{prefix} —</span>
        )}
        <input
          type="text"
          value={subtype}
          onChange={(e) => updateSubtype(e.target.value)}
          placeholder={prefix ? "Subtypes..." : "Type line..."}
          className="flex-1 bg-transparent px-2 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none"
        />
      </div>
    </div>
  );
}
