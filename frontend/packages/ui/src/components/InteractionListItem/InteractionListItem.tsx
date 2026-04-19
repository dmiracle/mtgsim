import type { Interaction } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { InteractionTypeBadge } from "@/components/InteractionTypeBadge/InteractionTypeBadge";
import { StrengthRating } from "@/components/StrengthRating/StrengthRating";

type InteractionListItemProps = {
  interaction: Interaction;
  cardUuid: string;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
  onCardClick?: (uuid: string) => void;
};

export function InteractionListItem({ interaction, cardUuid, onEdit, onDelete, onCardClick }: InteractionListItemProps) {
  const other = interaction.source_card.uuid === cardUuid
    ? interaction.target_card
    : interaction.source_card;

  return (
    <div className="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-bg-hover transition-colors">
      {/* Thumbnail */}
      <button
        onClick={() => onCardClick?.(other.uuid)}
        className="shrink-0 w-10 h-14 rounded bg-bg-tertiary overflow-hidden"
      >
        {other.image_url ? (
          <img src={other.image_url} alt={other.name} className="w-full h-full object-cover" loading="lazy" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-[8px] text-text-muted">?</div>
        )}
      </button>

      {/* Info */}
      <div className="flex-1 min-w-0 space-y-1">
        <div className="flex items-center gap-2">
          <button
            onClick={() => onCardClick?.(other.uuid)}
            className="text-sm font-medium text-text-primary truncate hover:text-accent transition-colors"
          >
            {other.name}
          </button>
          <ManaSymbols cost={other.mana_cost} size="sm" />
        </div>
        <div className="flex items-center gap-2">
          <InteractionTypeBadge type={interaction.interaction_type} />
          {interaction.is_bidirectional && (
            <span className="text-[10px] text-text-muted">↔</span>
          )}
          {interaction.strength !== null && (
            <StrengthRating value={interaction.strength} />
          )}
        </div>
        {interaction.description && (
          <p className="text-xs text-text-muted line-clamp-2">{interaction.description}</p>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1 shrink-0">
        {onEdit && (
          <button
            onClick={() => onEdit(interaction.id)}
            className="w-5 h-5 flex items-center justify-center rounded text-transparent group-hover:text-text-muted/40 hover:!text-accent hover:!bg-accent/10 transition-all"
            title="Edit"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3 h-3">
              <path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.848 2.047a.75.75 0 0 0 .98.98l2.047-.848a2.75 2.75 0 0 0 .892-.596l4.261-4.262a1.75 1.75 0 0 0 0-2.474Z" />
              <path d="M4.75 3.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V9A.75.75 0 0 1 14 9v2.25A2.75 2.75 0 0 1 11.25 14h-6.5A2.75 2.75 0 0 1 2 11.25v-6.5A2.75 2.75 0 0 1 4.75 2H7a.75.75 0 0 1 0 1.5H4.75Z" />
            </svg>
          </button>
        )}
        {onDelete && (
          <button
            onClick={() => onDelete(interaction.id)}
            className="w-5 h-5 flex items-center justify-center rounded text-transparent group-hover:text-text-muted/40 hover:!text-danger hover:!bg-danger/10 transition-all"
            title="Delete"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3 h-3">
              <path d="M5.28 4.22a.75.75 0 0 0-1.06 1.06L6.94 8l-2.72 2.72a.75.75 0 1 0 1.06 1.06L8 9.06l2.72 2.72a.75.75 0 1 0 1.06-1.06L9.06 8l2.72-2.72a.75.75 0 0 0-1.06-1.06L8 6.94 5.28 4.22Z" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
