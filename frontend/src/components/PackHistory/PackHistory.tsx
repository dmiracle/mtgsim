import type { BoosterPack } from "@/types/api";
import { SetIcon } from "@/components/SetIcon/SetIcon";

type PackHistoryProps = {
  packs: BoosterPack[];
  activeIndex: number;
  onSelect: (index: number) => void;
};

function getRarePull(pack: BoosterPack): string {
  const mythic = pack.cards.find((c) => c.rarity === "mythic");
  if (mythic) return mythic.name;
  const rare = pack.cards.find((c) => c.rarity === "rare");
  if (rare) return rare.name;
  return "No rare";
}

function getRarePullRarity(pack: BoosterPack): string {
  const mythic = pack.cards.find((c) => c.rarity === "mythic");
  if (mythic) return "mythic";
  const rare = pack.cards.find((c) => c.rarity === "rare");
  if (rare) return "rare";
  return "common";
}

const rarityText: Record<string, string> = {
  mythic: "text-orange-400",
  rare: "text-amber-400",
  uncommon: "text-text-secondary",
  common: "text-text-muted",
};

export function PackHistory({ packs, activeIndex, onSelect }: PackHistoryProps) {
  if (packs.length === 0) return null;

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-3 space-y-2">
      <h3 className="text-xs font-semibold text-text-muted uppercase tracking-widest">
        Pack History ({packs.length})
      </h3>
      <div className="space-y-1 max-h-80 overflow-y-auto">
        {packs.map((pack, i) => {
          const active = i === activeIndex;
          const pull = getRarePull(pack);
          const pullRarity = getRarePullRarity(pack);

          return (
            <button
              key={i}
              onClick={() => onSelect(i)}
              className={`w-full flex items-center gap-2 px-2.5 py-2 rounded text-left text-xs transition-colors ${
                active
                  ? "bg-accent-muted border border-accent text-accent"
                  : "hover:bg-bg-hover border border-transparent text-text-secondary"
              }`}
            >
              <SetIcon
                code={pack.set_code}
                size="sm"
                rarity={pullRarity as "common" | "uncommon" | "rare" | "mythic"}
              />
              <div className="flex-1 min-w-0">
                <span className="text-text-muted">Pack {i + 1}</span>
                <p className={`truncate font-medium ${rarityText[pullRarity]}`}>{pull}</p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
