import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { CardTypeIcon } from "@/components/CardTypeIcon/CardTypeIcon";

type CardIdentityProps = {
  name: string;
  mana_cost: string;
  mana_value: number;
  type: string;
  types: string[];
  power: string | null;
  toughness: string | null;
  loyalty: string | null;
  defense: string | null;
  onAddToDeck?: () => void;
};

export function CardIdentity({
  name,
  mana_cost,
  mana_value,
  type,
  types,
  power,
  toughness,
  loyalty,
  defense,
  onAddToDeck,
}: CardIdentityProps) {
  const statParts: string[] = [];
  if (power !== null && toughness !== null) statParts.push(`${power}/${toughness}`);
  if (loyalty !== null) statParts.push(`Loyalty: ${loyalty}`);
  if (defense !== null) statParts.push(`Defense: ${defense}`);

  return (
    <div className="space-y-2">
      {/* Name + mana cost */}
      <div className="flex items-start justify-between gap-4">
        <h1 className="text-xl font-bold text-text-primary">{name}</h1>
        <div className="flex items-center gap-3 shrink-0">
          <ManaSymbols cost={mana_cost} size="md" />
          <span className="text-xs text-text-muted bg-bg-tertiary rounded px-1.5 py-0.5">
            MV {mana_value}
          </span>
        </div>
      </div>

      {/* Type line */}
      <div className="flex items-center gap-2">
        {types[0] && <CardTypeIcon type={types[0]} size={16} className="text-text-secondary" />}
        <span className="text-sm text-text-secondary">{type}</span>
      </div>

      {/* Stats + add to deck */}
      <div className="flex items-center gap-3">
        {statParts.length > 0 && (
          <div className="flex items-center gap-2">
            {statParts.map((s) => (
              <span key={s} className="text-sm font-semibold text-text-primary bg-bg-tertiary rounded px-2 py-0.5">
                {s}
              </span>
            ))}
          </div>
        )}
        {onAddToDeck && (
          <button
            onClick={onAddToDeck}
            className="ml-auto text-xs font-medium px-3 py-1.5 rounded border border-accent text-accent hover:bg-accent hover:text-white transition-colors"
          >
            + Add to Deck
          </button>
        )}
      </div>
    </div>
  );
}
