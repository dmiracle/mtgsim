import { useState } from "react";
import { ManaIcon, ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";

type ManaValuePickerProps = {
  value?: string;
  onChange: (manaCost: string) => void;
};

const COLORS = ["W", "U", "B", "R", "G"];

function buildCost(generic: number, colors: string[]): string {
  const parts: string[] = [];
  if (generic > 0) parts.push(`{${generic}}`);
  for (const c of colors) parts.push(`{${c}}`);
  return parts.join("");
}

function parseCost(cost: string): { generic: number; colors: string[] } {
  if (!cost) return { generic: 0, colors: [] };
  const matches = cost.match(/\{([^}]+)\}/g) ?? [];
  let generic = 0;
  const colors: string[] = [];
  for (const m of matches) {
    const sym = m.replace(/[{}]/g, "");
    if (COLORS.includes(sym)) colors.push(sym);
    else generic += parseInt(sym) || 0;
  }
  return { generic, colors };
}

export function ManaValuePicker({ value = "", onChange }: ManaValuePickerProps) {
  const [generic, setGeneric] = useState(() => parseCost(value).generic);
  const [colors, setColors] = useState(() => parseCost(value).colors);

  function emit(g: number, c: string[]) {
    onChange(buildCost(g, c));
  }

  function addGeneric() {
    const next = generic + 1;
    setGeneric(next);
    emit(next, colors);
  }

  function addColor(sym: string) {
    const next = [...colors, sym];
    setColors(next);
    emit(generic, next);
  }

  function undo() {
    if (colors.length > 0) {
      const next = colors.slice(0, -1);
      setColors(next);
      emit(generic, next);
    } else if (generic > 0) {
      const next = generic - 1;
      setGeneric(next);
      emit(next, colors);
    }
  }

  function clear() {
    setGeneric(0);
    setColors([]);
    onChange("");
  }

  const hasCost = generic > 0 || colors.length > 0;
  const cost = buildCost(generic, colors);

  return (
    <div className="space-y-3">
      {/* Display */}
      <div className="flex items-center justify-center min-h-[2.5rem]">
        {hasCost ? (
          <ManaSymbols cost={cost} size="lg" />
        ) : (
          <span className="text-sm text-text-muted">Tap to build mana cost</span>
        )}
      </div>

      {/* Buttons */}
      <div className="flex items-center justify-center gap-2">
        <button
          onClick={addGeneric}
          className="w-10 h-10 rounded-full bg-bg-tertiary border-2 border-border hover:border-border-hover flex items-center justify-center transition-all active:scale-90"
          title="Add generic mana"
        >
          <ManaIcon symbol="1" size="md" shadow={false} dimmed />
        </button>

        {COLORS.map((sym) => (
          <button
            key={sym}
            onClick={() => addColor(sym)}
            className="w-10 h-10 rounded-full flex items-center justify-center transition-all active:scale-90 hover:scale-105"
            title={`Add {${sym}}`}
          >
            <ManaIcon symbol={sym} size="md" />
          </button>
        ))}
      </div>

      {/* Actions */}
      {hasCost && (
        <div className="flex items-center justify-center gap-3">
          <button onClick={undo} className="text-[10px] text-text-muted hover:text-warning transition-colors">
            Undo
          </button>
          <button onClick={clear} className="text-[10px] text-text-muted hover:text-danger transition-colors">
            Clear
          </button>
        </div>
      )}
    </div>
  );
}
