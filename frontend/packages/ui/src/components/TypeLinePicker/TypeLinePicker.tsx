import { useState, useEffect } from "react";

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

function buildTypeLine(supers: string[], types: string[], subtext: string): string {
  const main = [...supers, ...types].join(" ");
  return subtext ? `${main} — ${subtext}` : main;
}

export function TypeLinePicker({ value = "", onChange }: TypeLinePickerProps) {
  const [selectedSupers, setSelectedSupers] = useState<string[]>(() => {
    if (!value) return [];
    return SUPERTYPES.map((s) => s.name).filter((s) => value.includes(s));
  });
  const [selectedTypes, setSelectedTypes] = useState<string[]>(() => {
    if (!value) return [];
    return TYPES.map((t) => t.name).filter((t) => value.includes(t));
  });
  const [subtext, setSubtext] = useState(() => {
    if (!value || !value.includes("—")) return "";
    return value.split("—")[1]?.trim() ?? "";
  });

  const typeLine = buildTypeLine(selectedSupers, selectedTypes, subtext);

  useEffect(() => {
    onChange(typeLine);
  }, [typeLine, onChange]);

  function toggleSuper(name: string) {
    setSelectedSupers((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name]
    );
  }

  function toggleType(name: string) {
    setSelectedTypes((prev) =>
      prev.includes(name) ? prev.filter((t) => t !== name) : [...prev, name]
    );
  }

  return (
    <div className="space-y-2.5">
      {/* Supertype + Type icons in one row */}
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

      {/* Editable type line */}
      <input
        type="text"
        value={typeLine}
        onChange={(e) => {
          // Allow free editing — parse back into state
          const raw = e.target.value;
          const allNames = [...SUPERTYPES.map((s) => s.name), ...TYPES.map((t) => t.name)];
          setSelectedSupers(SUPERTYPES.map((s) => s.name).filter((n) => raw.includes(n)));
          setSelectedTypes(TYPES.map((t) => t.name).filter((n) => raw.includes(n)));
          const dashIdx = raw.indexOf("—");
          setSubtext(dashIdx >= 0 ? raw.slice(dashIdx + 1).trim() :
            raw.split(" ").filter((w) => !allNames.includes(w)).join(" "));
        }}
        placeholder="Type line..."
        className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-all"
      />
    </div>
  );
}
