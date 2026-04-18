import { useState } from "react";
import type { CardSummary, Interaction, InteractionCard } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { InteractionTypeBadge } from "@/components/InteractionTypeBadge/InteractionTypeBadge";
import { StrengthRating } from "@/components/StrengthRating/StrengthRating";

type InteractionBuilderProps = {
  open: boolean;
  sourceCard: InteractionCard;
  searchResults: CardSummary[];
  searching?: boolean;
  onSearch: (query: string) => void;
  onSave: (data: {
    target_uuid: string;
    interaction_type: string;
    is_bidirectional: boolean;
    description: string;
    strength: number | null;
  }) => void;
  onClose: () => void;
  editing?: Interaction;
};

const TYPES = ["combo", "synergy", "counter"];

export function InteractionBuilder({
  open,
  sourceCard,
  searchResults,
  searching = false,
  onSearch,
  onSave,
  onClose,
  editing,
}: InteractionBuilderProps) {
  const [type, setType] = useState(editing?.interaction_type ?? "synergy");
  const [bidirectional, setBidirectional] = useState(editing?.is_bidirectional ?? true);
  const [strength, setStrength] = useState<number | null>(editing?.strength ?? null);
  const [description, setDescription] = useState(editing?.description ?? "");
  const [targetUuid, setTargetUuid] = useState(editing?.target_card.uuid ?? "");
  const [targetCard, setTargetCard] = useState<InteractionCard | CardSummary | null>(editing?.target_card ?? null);
  const [query, setQuery] = useState("");

  if (!open) return null;

  function handleSearch(val: string) {
    setQuery(val);
    if (val.length >= 2) onSearch(val);
  }

  function selectTarget(card: CardSummary) {
    setTargetUuid(card.uuid);
    setTargetCard(card);
  }

  function handleSave() {
    if (!targetUuid) return;
    onSave({ target_uuid: targetUuid, interaction_type: type, is_bidirectional: bidirectional, description, strength });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/50" onClick={onClose}>
      <div
        className="bg-bg-secondary border border-border rounded-t-xl sm:rounded-xl w-full sm:max-w-lg shadow-xl max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
          <h2 className="text-sm font-semibold text-text-primary">
            {editing ? "Edit Interaction" : "Add Interaction"}
          </h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary text-lg leading-none">&times;</button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {/* Source card */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-border bg-bg-tertiary/50">
            <div className="shrink-0 w-10 h-14 rounded bg-bg-tertiary overflow-hidden">
              {sourceCard.image_url ? (
                <img src={sourceCard.image_url} alt={sourceCard.name} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-[8px] text-text-muted">?</div>
              )}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-text-primary truncate">{sourceCard.name}</p>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-text-muted">{sourceCard.type_line}</span>
                <ManaSymbols cost={sourceCard.mana_cost} size="sm" />
              </div>
            </div>
          </div>

          {/* Interaction details */}
          <div className="px-4 py-3 space-y-3 border-b border-border">
            {/* Type */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Type</label>
              <div className="flex items-center gap-1.5">
                {TYPES.map((t) => (
                  <button
                    key={t}
                    onClick={() => setType(t)}
                    className={`transition-colors ${type === t ? "" : "opacity-40 hover:opacity-70"}`}
                  >
                    <InteractionTypeBadge type={t} size="md" />
                  </button>
                ))}
              </div>
            </div>

            {/* Direction + Strength */}
            <div className="flex items-center gap-4">
              <label className="inline-flex items-center gap-1.5 text-xs text-text-secondary cursor-pointer">
                <input
                  type="checkbox"
                  checked={bidirectional}
                  onChange={(e) => setBidirectional(e.target.checked)}
                  className="accent-accent"
                />
                Bidirectional
              </label>
              <div className="flex items-center gap-1.5">
                <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Strength</span>
                <StrengthRating value={strength} onChange={setStrength} />
              </div>
            </div>

            {/* Description */}
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the interaction..."
              rows={2}
              className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent resize-none"
            />
          </div>

          {/* Target card */}
          <div className="px-4 py-3 space-y-2">
            <label className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">
              {targetCard ? "Target Card" : "Find Target Card"}
            </label>

            {targetCard && (
              <div className="flex items-center gap-3 p-2 rounded-lg bg-accent/10 border border-accent/30">
                <div className="shrink-0 w-8 h-11 rounded bg-bg-tertiary overflow-hidden">
                  {targetCard.image_url ? (
                    <img src={targetCard.image_url} alt={targetCard.name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-[8px] text-text-muted">?</div>
                  )}
                </div>
                <span className="text-sm text-accent font-medium truncate">{targetCard.name}</span>
                <button
                  onClick={() => { setTargetUuid(""); setTargetCard(null); }}
                  className="ml-auto text-xs text-text-muted hover:text-danger"
                >
                  ×
                </button>
              </div>
            )}

            <input
              type="text"
              value={query}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search by name or oracle text..."
              className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
            />

            {searching && <p className="text-xs text-text-muted text-center py-3">Searching...</p>}

            {!searching && query.length >= 2 && searchResults.length === 0 && (
              <p className="text-xs text-text-muted text-center py-3">No cards found</p>
            )}

            {searchResults.length > 0 && (
              <div className="max-h-48 overflow-y-auto space-y-0.5">
                {searchResults.filter((c) => c.uuid !== sourceCard.uuid).map((card) => (
                  <button
                    key={card.uuid}
                    onClick={() => selectTarget(card)}
                    className={`w-full flex items-center gap-3 px-2 py-1.5 rounded-lg text-left transition-colors ${
                      card.uuid === targetUuid ? "bg-accent/10" : "hover:bg-bg-hover"
                    }`}
                  >
                    <div className="shrink-0 w-7 h-10 rounded bg-bg-tertiary overflow-hidden">
                      {card.image_url ? (
                        <img src={card.image_url} alt="" className="w-full h-full object-cover" loading="lazy" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-[7px] text-text-muted">?</div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-xs text-text-primary truncate block">{card.name}</span>
                      <span className="text-[10px] text-text-muted">{card.type}</span>
                    </div>
                    <ManaSymbols cost={card.mana_cost} size="sm" />
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 px-4 py-3 border-t border-border shrink-0">
          <button
            onClick={onClose}
            className="text-xs px-3 py-1.5 rounded border border-border text-text-muted hover:text-text-secondary transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!targetUuid}
            className="text-xs px-4 py-1.5 rounded bg-accent text-white hover:bg-accent-hover disabled:opacity-40 transition-colors"
          >
            {editing ? "Update" : "Save Interaction"}
          </button>
        </div>
      </div>
    </div>
  );
}
