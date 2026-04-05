import type { SimilarCardResult } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { SimilarityScoreBadge } from "@/components/SimilarityScoreBadge/SimilarityScoreBadge";

type SimilarCardGridProps = {
  results: SimilarCardResult[];
  onCardClick?: (uuid: string) => void;
};

export function SimilarCardGrid({ results, onCardClick }: SimilarCardGridProps) {
  if (results.length === 0) {
    return (
      <p className="text-xs text-text-muted text-center py-8">No similar cards found</p>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
      {results.map(({ card, score }) => (
        <button
          key={card.uuid}
          onClick={() => onCardClick?.(card.uuid)}
          className="relative bg-bg-secondary border border-border rounded-lg hover:border-accent transition-colors text-left group"
        >
          <div className="absolute -top-2 -right-2 z-10">
            <SimilarityScoreBadge score={score} />
          </div>
          <div className="aspect-[5/7] bg-bg-tertiary rounded-t-lg overflow-hidden">
            {card.image_url ? (
              <img src={card.image_url} alt={card.name} className="w-full h-full object-cover" loading="lazy" />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <span className="text-text-muted text-xs text-center px-2">{card.name}</span>
              </div>
            )}
          </div>
          <div className="p-2 space-y-1">
            <div className="flex items-start justify-between gap-1">
              <span className="text-xs font-medium text-text-primary truncate group-hover:text-accent transition-colors">
                {card.name}
              </span>
              <ManaSymbols cost={card.mana_cost} size="sm" />
            </div>
            <p className="text-[10px] text-text-muted truncate">{card.type}</p>
          </div>
        </button>
      ))}
    </div>
  );
}
