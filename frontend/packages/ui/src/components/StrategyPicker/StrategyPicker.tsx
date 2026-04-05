import type { Strategy } from "@/types/api";

type StrategyPickerProps = {
  strategies: Strategy[];
  selected: string[];
  onChange: (selected: string[]) => void;
};

export function StrategyPicker({ strategies, selected, onChange }: StrategyPickerProps) {
  function toggle(name: string) {
    if (selected.includes(name)) {
      if (selected.length === 1) return;
      onChange(selected.filter((s) => s !== name));
    } else {
      onChange([...selected, name]);
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {strategies.map((s) => {
        const active = selected.includes(s.name);
        return (
          <button
            key={s.name}
            onClick={() => toggle(s.name)}
            title={s.description}
            className={`text-xs px-3 py-1.5 rounded-full font-medium border transition-colors ${
              active
                ? "bg-accent text-white border-accent"
                : "bg-bg-tertiary text-text-muted border-border hover:text-text-secondary hover:border-border-hover"
            }`}
          >
            {s.name.replace(/_/g, " ")}
          </button>
        );
      })}
    </div>
  );
}
