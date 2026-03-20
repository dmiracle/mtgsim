import type { CardPrinting } from "@/types/api";
import { SetBadge } from "@/components/SetBadge/SetBadge";

type OtherPrintingsProps = {
  printings: CardPrinting[];
  onSelect: (uuid: string) => void;
};

export function OtherPrintings({ printings, onSelect }: OtherPrintingsProps) {
  if (printings.length === 0) return null;

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
      <h3 className="text-sm font-medium text-text-secondary">
        Other Printings <span className="text-text-muted font-normal">({printings.length})</span>
      </h3>
      <div className="space-y-1.5">
        {printings.map((p) => (
          <button
            key={p.uuid}
            onClick={() => onSelect(p.uuid)}
            className="w-full flex items-center gap-3 px-3 py-2 rounded hover:bg-bg-hover transition-colors text-left"
          >
            <SetBadge
              code={p.set_code}
              name={p.set_name}
              rarity={p.rarity as "common" | "uncommon" | "rare" | "mythic"}
              size="sm"
            />
            <span className="text-xs text-text-muted">#{p.number}</span>
            {p.owns && (
              <span className="text-[10px] font-semibold text-success bg-success/15 px-1.5 py-0.5 rounded">
                Owned ({p.total_owned})
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
