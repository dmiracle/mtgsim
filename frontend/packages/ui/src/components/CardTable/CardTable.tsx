import type { CardSummary, Pagination as PaginationType } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { SetBadge } from "@/components/SetBadge/SetBadge";
import { Pagination } from "@/components/Pagination/Pagination";
import { PinnedBadge } from "@/components/PinnedBadge/PinnedBadge";

type CardTableProps = {
  cards: CardSummary[];
  pagination?: PaginationType;
  pinnedIds?: Set<string>;
  onPageChange?: (page: number) => void;
  onPin?: (uuid: string) => void;
  onCardClick?: (uuid: string) => void;
  onSetClick?: (code: string) => void;
};

const rarityDot: Record<string, string> = {
  common: "bg-text-muted",
  uncommon: "bg-gray-300",
  rare: "bg-amber-400",
  mythic: "bg-orange-500",
};

export function CardTable({
  cards,
  pagination,
  pinnedIds = new Set(),
  onPageChange,
  onPin,
  onCardClick,
  onSetClick,
}: CardTableProps) {
  if (cards.length === 0) {
    return (
      <div className="flex items-center justify-center py-16 text-text-muted">
        No cards found
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto border border-border rounded-lg">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-bg-secondary border-b border-border text-text-muted">
              <th className="text-left px-3 py-2 font-medium w-8"></th>
              <th className="text-left px-3 py-2 font-medium">Name</th>
              <th className="text-left px-3 py-2 font-medium">Mana</th>
              <th className="text-center px-3 py-2 font-medium">MV</th>
              <th className="text-left px-3 py-2 font-medium">Type</th>
              <th className="text-center px-3 py-2 font-medium">P/T</th>
              <th className="text-left px-3 py-2 font-medium">Set</th>
              <th className="text-center px-3 py-2 font-medium">Rarity</th>
              <th className="text-left px-3 py-2 font-medium hidden lg:table-cell">Colors</th>
              <th className="text-right px-3 py-2 font-medium">Price</th>
              <th className="text-center px-3 py-2 font-medium hidden sm:table-cell">Own</th>
            </tr>
          </thead>
          <tbody>
            {cards.map((card) => {
              const pinned = pinnedIds.has(card.uuid);
              return (
                <tr
                  key={card.uuid}
                  className={`border-b border-border/50 last:border-none hover:bg-bg-hover transition-colors ${
                    pinned ? "bg-warning/5" : ""
                  }`}
                >
                  {/* Pin */}
                  <td className="px-3 py-2">
                    <PinnedBadge pinned={pinned} onToggle={onPin ? () => onPin(card.uuid) : undefined} size="sm" />
                  </td>

                  {/* Name */}
                  <td className="px-3 py-2">
                    <button
                      onClick={() => onCardClick?.(card.uuid)}
                      className="text-text-primary hover:text-accent transition-colors font-medium text-left truncate max-w-[200px] block"
                      title={card.name}
                    >
                      {card.name}
                    </button>
                  </td>

                  {/* Mana cost */}
                  <td className="px-3 py-2">
                    <ManaSymbols cost={card.mana_cost} size="sm" shadow={false} />
                  </td>

                  {/* Mana value */}
                  <td className="px-3 py-2 text-center text-text-muted tabular-nums">
                    {card.mana_value}
                  </td>

                  {/* Type */}
                  <td className="px-3 py-2 text-text-secondary truncate max-w-[180px]" title={card.type}>
                    {card.type}
                  </td>

                  {/* P/T */}
                  <td className="px-3 py-2 text-center text-text-muted tabular-nums">
                    {card.type.includes("Creature") ? "—" : ""}
                  </td>

                  {/* Set */}
                  <td className="px-3 py-2">
                    <SetBadge
                      code={card.set_code}
                      rarity={card.rarity as "common" | "uncommon" | "rare" | "mythic"}
                      size="sm"
                      navigable
                      onClick={() => onSetClick?.(card.set_code)}
                    />
                  </td>

                  {/* Rarity */}
                  <td className="px-3 py-2 text-center">
                    <span
                      className={`inline-block w-2.5 h-2.5 rounded-full ${rarityDot[card.rarity] ?? "bg-text-muted"}`}
                      title={card.rarity}
                    />
                  </td>

                  {/* Colors — hidden on small */}
                  <td className="px-3 py-2 hidden lg:table-cell">
                    <div className="flex items-center gap-0.5">
                      {card.color_identity.length > 0 ? (
                        <ManaSymbols
                          cost={card.color_identity.map((c) => `{${c}}`).join("")}
                          size="sm"
                          shadow={false}
                        />
                      ) : (
                        <span className="text-text-muted">C</span>
                      )}
                    </div>
                  </td>

                  {/* Price */}
                  <td className="px-3 py-2 text-right tabular-nums">
                    {card.price != null && card.price > 0 ? (
                      <span className="text-success font-medium">${card.price.toFixed(2)}</span>
                    ) : (
                      <span className="text-text-muted">—</span>
                    )}
                  </td>

                  {/* Owned — hidden on small */}
                  <td className="px-3 py-2 text-center hidden sm:table-cell">
                    {card.owns ? (
                      <span className="text-success text-[10px] font-semibold">{card.total_owned}</span>
                    ) : (
                      <span className="text-text-muted">—</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
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
