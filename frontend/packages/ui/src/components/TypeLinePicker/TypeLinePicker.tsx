import { useState } from "react";

type TypeLinePickerProps = {
  value?: string;
  onChange: (typeLine: string) => void;
};

const SUPERTYPES = ["Legendary", "Basic", "Snow"];

const TYPES = [
  "Creature",
  "Instant",
  "Sorcery",
  "Enchantment",
  "Artifact",
  "Planeswalker",
  "Land",
  "Battle",
];

export function TypeLinePicker({ value = "", onChange }: TypeLinePickerProps) {
  const [selectedSupertypes, setSelectedSupertypes] = useState<string[]>(() => {
    if (!value) return [];
    return SUPERTYPES.filter((s) => value.includes(s));
  });
  const [selectedType, setSelectedType] = useState<string>(() => {
    if (!value) return "";
    return TYPES.find((t) => value.includes(t)) ?? "";
  });
  const [subtype, setSubtype] = useState(() => {
    if (!value || !value.includes("—")) return "";
    return value.split("—")[1]?.trim() ?? "";
  });

  function buildTypeLine(supers: string[], type: string, sub: string) {
    const parts = [...supers, type].filter(Boolean).join(" ");
    return sub ? `${parts} — ${sub}` : parts;
  }

  function emit(supers: string[], type: string, sub: string) {
    onChange(buildTypeLine(supers, type, sub));
  }

  function toggleSupertype(s: string) {
    const next = selectedSupertypes.includes(s)
      ? selectedSupertypes.filter((x) => x !== s)
      : [...selectedSupertypes, s];
    setSelectedSupertypes(next);
    emit(next, selectedType, subtype);
  }

  function selectType(t: string) {
    const next = selectedType === t ? "" : t;
    setSelectedType(next);
    emit(selectedSupertypes, next, subtype);
  }

  function updateSubtype(s: string) {
    setSubtype(s);
    emit(selectedSupertypes, selectedType, s);
  }

  return (
    <div className="space-y-2.5">
      {/* Supertypes */}
      <div className="flex gap-1 justify-center">
        {SUPERTYPES.map((s) => {
          const active = selectedSupertypes.includes(s);
          return (
            <button
              key={s}
              onClick={() => toggleSupertype(s)}
              className={`px-2.5 py-1.5 text-[11px] font-medium rounded-lg border transition-all active:scale-95 ${
                active
                  ? "bg-accent/15 border-accent text-accent"
                  : "bg-bg-tertiary border-border text-text-muted hover:border-border-hover"
              }`}
            >
              {s}
            </button>
          );
        })}
      </div>

      {/* Card types */}
      <div className="flex flex-wrap gap-1 justify-center">
        {TYPES.map((t) => {
          const active = selectedType === t;
          return (
            <button
              key={t}
              onClick={() => selectType(t)}
              className={`px-2.5 py-1.5 text-[11px] font-medium rounded-lg border transition-all active:scale-95 ${
                active
                  ? "bg-accent text-white border-accent"
                  : "bg-bg-tertiary border-border text-text-muted hover:border-border-hover"
              }`}
            >
              {t}
            </button>
          );
        })}
      </div>

      {/* Subtype text input */}
      <input
        type="text"
        value={subtype}
        onChange={(e) => updateSubtype(e.target.value)}
        placeholder="Subtypes (e.g. Human Wizard)"
        className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-xs text-text-primary placeholder-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-all"
      />

      {/* Preview */}
      {(selectedType || selectedSupertypes.length > 0) && (
        <p className="text-[10px] text-text-muted text-center">
          {buildTypeLine(selectedSupertypes, selectedType, subtype) || "—"}
        </p>
      )}
    </div>
  );
}
