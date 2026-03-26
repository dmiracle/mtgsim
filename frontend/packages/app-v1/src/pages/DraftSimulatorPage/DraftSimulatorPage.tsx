import { useState } from "react";
import type { SetSummary, BoosterPack } from "@/types/api";
import { PackConfigPanel } from "@/components/PackConfigPanel/PackConfigPanel";
import { PackDisplay } from "@/components/PackDisplay/PackDisplay";
import { PackHistory } from "@/components/PackHistory/PackHistory";

type DraftSimulatorPageProps = {
  sets: SetSummary[];
  packs: BoosterPack[];
  onOpenPacks: (setCode: string, boosterType: string, count: number) => void;
  onCardClick: (uuid: string) => void;
  loading?: boolean;
};

export function DraftSimulatorPage({ sets, packs, onOpenPacks, onCardClick, loading = false }: DraftSimulatorPageProps) {
  const [activePackIndex, setActivePackIndex] = useState(0);

  const activePack = packs[activePackIndex] ?? null;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-text-primary">Draft Simulator</h2>

      <div className="grid grid-cols-1 md:grid-cols-[280px_1fr] lg:grid-cols-[280px_1fr_220px] gap-4">
        {/* Left: config */}
        <PackConfigPanel sets={sets} onOpen={onOpenPacks} loading={loading} />

        {/* Center: pack display */}
        <div className="min-w-0">
          {activePack ? (
            <PackDisplay
              cards={activePack.cards}
              setName={activePack.set_name}
              boosterType={activePack.booster_type}
              onCardClick={onCardClick}
            />
          ) : (
            <div className="flex items-center justify-center py-16 md:py-24 text-text-muted border border-border rounded-lg bg-bg-secondary text-sm text-center px-4">
              Select a set and open packs to begin
            </div>
          )}
        </div>

        {/* Right: pack history — below on mobile/tablet, sidebar on desktop */}
        <div className="md:col-span-2 lg:col-span-1">
          <PackHistory
            packs={packs}
            activeIndex={activePackIndex}
            onSelect={setActivePackIndex}
          />
        </div>
      </div>
    </div>
  );
}
