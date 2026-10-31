interface ChipRowProps {
  options: { value: string; label: string }[];
  selected: string[];
  onToggle: (value: string) => void;
}

export function ChipRow({ options, selected, onToggle }: ChipRowProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => (
        <button
          key={o.value}
          onClick={() => onToggle(o.value)}
          className={`min-h-10 rounded-full border px-4 text-sm capitalize ${
            selected.includes(o.value) ? "border-accent bg-accent text-bg font-semibold" : "border-line bg-surface text-fg"
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
