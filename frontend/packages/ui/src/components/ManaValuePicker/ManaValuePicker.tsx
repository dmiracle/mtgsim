import { useState, useRef } from "react";
import { ManaIcon, ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";

type ManaValuePickerProps = {
  value?: string;
  onChange: (manaCost: string) => void;
};

const COLORS = ["W", "U", "B", "R", "G"];

function buildCost(generic: number, symbols: string[]): string {
  const parts: string[] = [];
  if (generic > 0) parts.push(`{${generic}}`);
  for (const s of symbols) parts.push(`{${s}}`);
  return parts.join("");
}

function parseCost(cost: string): { generic: number; symbols: string[] } {
  if (!cost) return { generic: 0, symbols: [] };
  const matches = cost.match(/\{([^}]+)\}/g) ?? [];
  let generic = 0;
  const symbols: string[] = [];
  for (const m of matches) {
    const sym = m.replace(/[{}]/g, "");
    if (COLORS.includes(sym) || sym.includes("/")) symbols.push(sym);
    else generic += parseInt(sym) || 0;
  }
  return { generic, symbols };
}

export function ManaValuePicker({ value = "", onChange }: ManaValuePickerProps) {
  const [generic, setGeneric] = useState(() => parseCost(value).generic);
  const [symbols, setSymbols] = useState(() => parseCost(value).symbols);
  const [dragFrom, setDragFrom] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState<string | null>(null);
  const touchStart = useRef<string | null>(null);

  function emit(g: number, s: string[]) {
    onChange(buildCost(g, s));
  }

  function addGeneric() {
    const next = generic + 1;
    setGeneric(next);
    emit(next, symbols);
  }

  function addSymbol(sym: string) {
    const next = [...symbols, sym];
    setSymbols(next);
    emit(generic, next);
  }

  function addHybrid(a: string, b: string) {
    if (a === b) { addSymbol(a); return; }
    const hybrid = `${a}/${b}`;
    const next = [...symbols, hybrid];
    setSymbols(next);
    emit(generic, next);
  }

  function undo() {
    if (symbols.length > 0) {
      const next = symbols.slice(0, -1);
      setSymbols(next);
      emit(generic, next);
    } else if (generic > 0) {
      const next = generic - 1;
      setGeneric(next);
      emit(next, symbols);
    }
  }

  function clear() {
    setGeneric(0);
    setSymbols([]);
    onChange("");
  }

  // Drag handlers
  function handleDragStart(sym: string) {
    setDragFrom(sym);
  }

  function handleDragEnter(sym: string) {
    if (dragFrom && dragFrom !== sym) setDragOver(sym);
  }

  function handleDragEnd() {
    if (dragFrom && dragOver) {
      addHybrid(dragFrom, dragOver);
    }
    setDragFrom(null);
    setDragOver(null);
  }

  // Touch handlers for mobile
  function handleTouchStart(sym: string) {
    touchStart.current = sym;
  }

  function handleTouchEnd(e: React.TouchEvent) {
    const touch = e.changedTouches[0];
    const el = document.elementFromPoint(touch.clientX, touch.clientY);
    const target = el?.closest("[data-mana]")?.getAttribute("data-mana");
    if (touchStart.current && target && touchStart.current !== target) {
      addHybrid(touchStart.current, target);
    } else if (touchStart.current) {
      addSymbol(touchStart.current);
    }
    touchStart.current = null;
    setDragOver(null);
  }

  const hasCost = generic > 0 || symbols.length > 0;
  const cost = buildCost(generic, symbols);
  const hybridPreview = dragFrom && dragOver ? `${dragFrom}/${dragOver}` : null;

  return (
    <div className="space-y-3">
      {/* Display */}
      <div className="flex items-center justify-center min-h-[2.5rem]">
        {hasCost ? (
          <ManaSymbols cost={cost} size="lg" />
        ) : (
          <span className="text-sm text-text-muted">Tap to add, drag to combine</span>
        )}
      </div>

      {/* Hybrid preview */}
      {hybridPreview && (
        <div className="flex items-center justify-center">
          <ManaIcon symbol={hybridPreview.replace("/", "")} size="lg" />
        </div>
      )}

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
            data-mana={sym}
            draggable
            onClick={() => addSymbol(sym)}
            onDragStart={() => handleDragStart(sym)}
            onDragEnter={() => handleDragEnter(sym)}
            onDragOver={(e) => e.preventDefault()}
            onDragEnd={handleDragEnd}
            onTouchStart={() => handleTouchStart(sym)}
            onTouchEnd={handleTouchEnd}
            className={`w-10 h-10 rounded-full flex items-center justify-center transition-all active:scale-90 hover:scale-105 ${
              dragOver === sym ? "ring-2 ring-accent scale-110" : ""
            }`}
            title={`{${sym}} — drag onto another color to combine`}
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
