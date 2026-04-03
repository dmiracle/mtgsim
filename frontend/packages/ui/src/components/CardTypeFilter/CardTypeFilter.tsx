import { CardTypeIcon } from "@/components/CardTypeIcon/CardTypeIcon";

const CARD_TYPES = [
  "Creature",
  "Instant",
  "Sorcery",
  "Enchantment",
  "Artifact",
  "Planeswalker",
  "Land",
];

type CardTypeFilterProps = {
  selected: string[];
  onChange: (selected: string[]) => void;
};

export function CardTypeFilter({ selected, onChange }: CardTypeFilterProps) {
  function toggle(type: string) {
    if (selected.includes(type)) {
      onChange(selected.filter((t) => t !== type));
    } else {
      onChange([...selected, type]);
    }
  }

  return (
    <div className="flex flex-wrap gap-1">
      {CARD_TYPES.map((type) => {
        const active = selected.includes(type);
        return (
          <button
            key={type}
            onClick={() => toggle(type)}
            title={type}
            className={`group relative inline-flex items-center justify-center w-9 h-9 rounded-lg border-2 transition-all ${
              active
                ? "bg-accent text-white border-accent shadow-[0_0_8px_var(--color-accent)] hover:bg-accent-hover hover:shadow-[0_0_14px_var(--color-accent)] hover:scale-110"
                : "bg-bg-tertiary border-border text-text-muted hover:bg-bg-hover hover:border-accent hover:text-accent"
            }`}
          >
            <CardTypeIcon type={type} size={18} />
            <span className="absolute -bottom-7 left-1/2 -translate-x-1/2 px-1.5 py-0.5 text-[10px] font-medium bg-bg-secondary border border-border rounded shadow-lg text-text-secondary whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
              {type}
            </span>
          </button>
        );
      })}
    </div>
  );
}
