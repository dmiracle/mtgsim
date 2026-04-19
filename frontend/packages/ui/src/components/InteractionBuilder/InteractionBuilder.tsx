import { useState } from "react";
import type { CardSummary, Interaction, InteractionCard, TagCount } from "@/types/api";
import type { CardFilters } from "@/components/CardFilterBar/CardFilterBar";
import { CardFilterBar } from "@/components/CardFilterBar/CardFilterBar";
import { CardGrid } from "@/components/CardGrid/CardGrid";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { InteractionTypeBadge } from "@/components/InteractionTypeBadge/InteractionTypeBadge";
import { StrengthRating } from "@/components/StrengthRating/StrengthRating";

export type InteractionBuilderProps = {
  sourceCard: InteractionCard;
  cards: CardSummary[];
  pagination?: { page: number; pages: number; total: number; limit: number };
  filters: CardFilters;
  availableTags?: TagCount[];
  onFiltersChange: (filters: CardFilters) => void;
  onPageChange?: (page: number) => void;
  onSave: (data: {
    target_uuid: string;
    interaction_type: string;
    is_bidirectional: boolean;
    description: string;
    strength: number | null;
  }) => void;
  onBack: () => void;
  onCardClick?: (uuid: string) => void;
  editing?: Interaction;
};

const TYPES = ["combo", "synergy", "counter"];

export function InteractionBuilder({
  sourceCard,
  cards,
  pagination,
  filters,
  availableTags,
  onFiltersChange,
  onPageChange,
  onSave,
  onBack,
  onCardClick,
  editing,
}: InteractionBuilderProps) {
  const [type, setType] = useState(editing?.interaction_type ?? "synergy");
  const [bidirectional, setBidirectional] = useState(editing?.is_bidirectional ?? true);
  const [strength, setStrength] = useState<number | null>(editing?.strength ?? null);
  const [description, setDescription] = useState(editing?.description ?? "");
  const [selectedTargets, setSelectedTargets] = useState<CardSummary[]>(
    editing ? [{ uuid: editing.target_card.uuid, name: editing.target_card.name, type: editing.target_card.type_line, mana_cost: editing.target_card.mana_cost, mana_value: 0, rarity: "", set_code: "", color_identity: [], tags: [], text: "", price: 0, image_url: editing.target_card.image_url, owns: false, wants: false, total_owned: 0, total_wanted: 0 }] : [],
  );

  function addTarget(card: CardSummary) {
    if (selectedTargets.some((t) => t.uuid === card.uuid)) return;
    if (card.uuid === sourceCard.uuid) return;
    setSelectedTargets((prev) => [...prev, card]);
  }

  function removeTarget(uuid: string) {
    setSelectedTargets((prev) => prev.filter((t) => t.uuid !== uuid));
  }

  function handleSaveAll() {
    for (const target of selectedTargets) {
      onSave({ target_uuid: target.uuid, interaction_type: type, is_bidirectional: bidirectional, description, strength });
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="text-xs text-text-muted hover:text-accent transition-colors">&larr; Back</button>
        <h2 className="text-xl font-bold text-text-primary">
          {editing ? "Edit Interaction" : "Add Interaction"}
        </h2>
      </div>

      {/* Source card */}
      <div className="bg-bg-secondary border border-border rounded-lg p-4">
        <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Source</span>
        <div className="flex items-center gap-3 mt-2">
          <div className="shrink-0 w-12 h-16 rounded bg-bg-tertiary overflow-hidden">
            {sourceCard.image_url ? (
              <img src={sourceCard.image_url} alt={sourceCard.name} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-[8px] text-text-muted">?</div>
            )}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-text-primary truncate">{sourceCard.name}</p>
            <div className="flex items-center gap-2">
              <span className="text-xs text-text-muted">{sourceCard.type_line}</span>
              <ManaSymbols cost={sourceCard.mana_cost} size="sm" />
            </div>
          </div>
        </div>
      </div>

      {/* Interaction details */}
      <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
        <div className="flex flex-wrap items-center gap-4">
          {/* Type */}
          <div className="space-y-1">
            <label className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Type</label>
            <div className="flex items-center gap-1.5">
              {TYPES.map((t) => (
                <button
                  key={t}
                  onClick={() => setType(t)}
                  className={`transition-opacity ${type === t ? "" : "opacity-30 hover:opacity-60"}`}
                >
                  <InteractionTypeBadge type={t} size="md" />
                </button>
              ))}
            </div>
          </div>

          {/* Direction */}
          <label className="inline-flex items-center gap-1.5 text-xs text-text-secondary cursor-pointer">
            <input type="checkbox" checked={bidirectional} onChange={(e) => setBidirectional(e.target.checked)} className="accent-accent" />
            Bidirectional
          </label>

          {/* Strength */}
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Strength</span>
            <StrengthRating value={strength} onChange={setStrength} />
          </div>
        </div>

        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe the interaction..."
          rows={2}
          className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent resize-none"
        />
      </div>

      {/* Selected targets bar */}
      <div className="bg-bg-secondary border border-border rounded-lg p-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">
            Targets <span className="font-normal">({selectedTargets.length})</span>
          </span>
          {selectedTargets.length > 0 && (
            <button
              onClick={handleSaveAll}
              className="text-xs px-3 py-1 rounded bg-accent text-white hover:bg-accent-hover transition-colors"
            >
              {editing ? "Update" : `Save ${selectedTargets.length} interaction${selectedTargets.length > 1 ? "s" : ""}`}
            </button>
          )}
        </div>
        {selectedTargets.length === 0 ? (
          <p className="text-xs text-text-muted text-center py-2">Select cards below to add as targets</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {selectedTargets.map((card) => (
              <div key={card.uuid} className="flex items-center gap-2 px-2 py-1 rounded-lg bg-accent/10 border border-accent/30">
                <div className="shrink-0 w-6 h-8 rounded bg-bg-tertiary overflow-hidden">
                  {card.image_url ? (
                    <img src={card.image_url} alt="" className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-[6px] text-text-muted">?</div>
                  )}
                </div>
                <span className="text-xs text-accent font-medium truncate max-w-[120px]">{card.name}</span>
                <button onClick={() => removeTarget(card.uuid)} className="text-text-muted hover:text-danger text-xs">×</button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Card search */}
      <CardFilterBar
        filters={filters}
        onChange={onFiltersChange}
        availableTags={availableTags}
      />

      <CardGrid
        cards={cards.filter((c) => c.uuid !== sourceCard.uuid)}
        pagination={pagination}
        onCardClick={onCardClick}
        onAddToDeck={addTarget ? (uuid) => {
          const card = cards.find((c) => c.uuid === uuid);
          if (card) addTarget(card);
        } : undefined}
        onPageChange={onPageChange}
      />
    </div>
  );
}
