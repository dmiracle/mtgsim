import type { CardSummary, Pagination as PaginationType } from "@/types/api";
import { CardGridItem } from "@/components/CardGridItem/CardGridItem";
import { Pagination } from "@/components/Pagination/Pagination";

type CardGridProps = {
  cards: CardSummary[];
  pagination?: PaginationType;
  pinnedIds?: Set<string>;
  quantities?: Record<string, number>;
  onPageChange?: (page: number) => void;
  onPin?: (uuid: string) => void;
  onAddToDeck?: (uuid: string) => void;
  onFindSimilar?: (uuid: string) => void;
  onAddToCollection?: (uuid: string) => void;
  onCardClick?: (uuid: string) => void;
  onSetClick?: (code: string) => void;
};

export function CardGrid({
  cards,
  pagination,
  pinnedIds = new Set(),
  quantities,
  onPageChange,
  onPin,
  onAddToDeck,
  onFindSimilar,
  onAddToCollection,
  onCardClick,
  onSetClick,
}: CardGridProps) {
  if (cards.length === 0) {
    return (
      <div className="flex items-center justify-center py-16 text-text-muted">
        No cards found
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {cards.map((card) => (
          <CardGridItem
            key={card.uuid}
            card={card}
            pinned={pinnedIds.has(card.uuid)}
            quantity={quantities?.[card.uuid]}
            onPin={onPin}
            onAddToDeck={onAddToDeck}
            onFindSimilar={onFindSimilar}
            onAddToCollection={onAddToCollection}
            onClick={onCardClick}
            onSetClick={onSetClick}
          />
        ))}
      </div>
      {pagination && onPageChange && (
        <Pagination
          page={pagination.page}
          pages={pagination.pages}
          total={pagination.total}
          limit={pagination.limit}
          onPageChange={onPageChange}
        />
      )}
    </div>
  );
}
