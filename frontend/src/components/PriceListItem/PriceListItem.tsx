import type { PriceSummary } from "@/types/api";
import { SetBadge } from "@/components/SetBadge/SetBadge";

type PriceListItemProps = {
  price: PriceSummary;
  onClick: (uuid: string) => void;
};

export function PriceListItem({ price, onClick }: PriceListItemProps) {
  return (
    <button
      onClick={() => onClick(price.uuid)}
      className="w-full flex items-center gap-3 px-4 py-3 rounded-lg border border-border bg-bg-secondary hover:bg-bg-hover hover:border-border-hover transition-colors text-left group"
    >
      <div className="flex-1 min-w-0">
        <h3 className="text-sm font-medium text-text-primary group-hover:text-accent transition-colors truncate">
          {price.name}
        </h3>
        <div className="flex items-center gap-2 mt-0.5">
          <SetBadge
            code={price.set_code}
            rarity={price.rarity as "common" | "uncommon" | "rare" | "mythic"}
            size="sm"
          />
          <span className="text-[10px] uppercase tracking-wide text-text-muted capitalize">{price.rarity}</span>
        </div>
      </div>
      <span className="text-lg font-bold text-success shrink-0 tabular-nums">
        ${price.average_usd.toFixed(2)}
      </span>
    </button>
  );
}
