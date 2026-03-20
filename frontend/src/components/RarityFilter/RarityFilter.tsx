const RARITIES = [
  { id: "common", label: "Common", letter: "C" },
  { id: "uncommon", label: "Uncommon", letter: "U" },
  { id: "rare", label: "Rare", letter: "R" },
  { id: "mythic", label: "Mythic", letter: "M" },
];

const inactiveStyle = "bg-bg-tertiary border-border text-text-muted opacity-40 hover:opacity-90 hover:border-border-hover";

const activeStyles: Record<string, string> = {
  common: "bg-text-muted/25 border-text-secondary text-text-primary shadow-[0_0_6px_var(--color-text-muted)]",
  uncommon: "bg-gray-400/25 border-gray-400 text-gray-100 shadow-[0_0_6px_theme(colors.gray.400)]",
  rare: "bg-amber-500/25 border-amber-500 text-amber-300 shadow-[0_0_6px_theme(colors.amber.500)]",
  mythic: "bg-orange-500/25 border-orange-500 text-orange-300 shadow-[0_0_6px_theme(colors.orange.500)]",
};

type RarityFilterProps = {
  selected: string[];
  onChange: (selected: string[]) => void;
};

export function RarityFilter({ selected, onChange }: RarityFilterProps) {
  function toggle(id: string) {
    if (selected.includes(id)) {
      onChange(selected.filter((r) => r !== id));
    } else {
      onChange([...selected, id]);
    }
  }

  return (
    <div className="inline-flex items-center gap-1">
      {RARITIES.map((r) => {
        const active = selected.includes(r.id);
        return (
          <button
            key={r.id}
            onClick={() => toggle(r.id)}
            title={r.label}
            className={`group relative w-8 h-8 rounded-lg border-2 inline-flex items-center justify-center text-sm font-black tracking-tight transition-all ${
              active ? activeStyles[r.id] : inactiveStyle
            }`}
          >
            {r.letter}
            <span className="absolute -bottom-7 left-1/2 -translate-x-1/2 px-1.5 py-0.5 text-[10px] font-medium bg-bg-secondary border border-border rounded shadow-lg text-text-secondary whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
              {r.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}
