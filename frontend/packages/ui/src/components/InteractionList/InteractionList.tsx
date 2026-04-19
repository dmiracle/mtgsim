import type { Interaction } from "@/types/api";
import { InteractionListItem } from "@/components/InteractionListItem/InteractionListItem";

type InteractionListProps = {
  interactions: Interaction[];
  cardUuid: string;
  onAdd?: () => void;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
  onCardClick?: (uuid: string) => void;
};

const groupOrder = ["combo", "synergy", "counter"];
const groupLabels: Record<string, string> = {
  combo: "Combos",
  synergy: "Synergies",
  counter: "Counters",
};

export function InteractionList({ interactions, cardUuid, onAdd, onEdit, onDelete, onCardClick }: InteractionListProps) {
  const groups = new Map<string, Interaction[]>();
  for (const i of interactions) {
    const type = i.interaction_type;
    if (!groups.has(type)) groups.set(type, []);
    groups.get(type)!.push(i);
  }

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-text-secondary">
          Interactions <span className="text-text-muted font-normal">({interactions.length})</span>
        </h3>
        {onAdd && (
          <button
            onClick={onAdd}
            className="flex items-center gap-1 text-[11px] text-text-muted hover:text-accent transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
              <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
            </svg>
            Add
          </button>
        )}
      </div>

      {interactions.length === 0 ? (
        <p className="text-xs text-text-muted text-center py-4">No interactions yet</p>
      ) : (
        <div className="space-y-3">
          {groupOrder.filter((t) => groups.has(t)).map((type) => (
            <div key={type} className="space-y-1">
              <h4 className="text-[10px] uppercase tracking-widest text-text-muted font-semibold px-3">
                {groupLabels[type] ?? type}
              </h4>
              <div className="divide-y divide-border/50">
                {groups.get(type)!.map((interaction) => (
                  <InteractionListItem
                    key={interaction.id}
                    interaction={interaction}
                    cardUuid={cardUuid}
                    onEdit={onEdit}
                    onDelete={onDelete}
                    onCardClick={onCardClick}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
