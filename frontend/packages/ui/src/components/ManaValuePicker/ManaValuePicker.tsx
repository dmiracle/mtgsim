import { useState } from "react";

type ManaValuePickerProps = {
  value?: number | null;
  onChange: (value: number) => void;
};

const VALUES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

export function ManaValuePicker({ value = null, onChange }: ManaValuePickerProps) {
  const [selected, setSelected] = useState<number | null>(value);

  function pick(v: number) {
    setSelected(v);
    onChange(v);
  }

  return (
    <div className="space-y-1.5">
      <div className="flex flex-wrap gap-1 justify-center">
        {VALUES.map((v) => (
          <button
            key={v}
            onClick={() => pick(v)}
            className={`w-9 h-9 rounded-full text-xs font-bold transition-all active:scale-90 ${
              selected === v
                ? "bg-accent text-white ring-2 ring-accent/40"
                : "bg-bg-tertiary border border-border text-text-muted hover:border-border-hover hover:text-text-secondary"
            }`}
          >
            {v}
          </button>
        ))}
        <button
          onClick={() => pick(11)}
          className={`w-9 h-9 rounded-full text-xs font-bold transition-all active:scale-90 ${
            selected !== null && selected > 10
              ? "bg-accent text-white ring-2 ring-accent/40"
              : "bg-bg-tertiary border border-border text-text-muted hover:border-border-hover hover:text-text-secondary"
          }`}
        >
          11+
        </button>
      </div>
    </div>
  );
}
