import { useState } from "react";
import type { SetSummary } from "@/types/api";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { SetBadge } from "@/components/SetBadge/SetBadge";

type GenerateDialogProps = {
  sets: SetSummary[];
  onGenerate: (cardType: string, setCode?: string, rarity?: string) => void;
  onClose: () => void;
  generating?: boolean;
  result?: { created: number; collection: string } | null;
};

const CARD_TYPES = [
  { id: "keyword_definition", label: "Keyword Definitions", needsSet: false, description: "Learn what each keyword ability does" },
  { id: "card_oracle", label: "Card Oracle Text", needsSet: true, description: "See card name + image, recall oracle text" },
  { id: "card_mana_cost", label: "Card Mana Cost", needsSet: true, description: "See card text, recall the mana cost" },
  { id: "card_stats", label: "Card Stats (P/T)", needsSet: true, description: "See card text, recall power/toughness" },
];

const RARITIES = [
  { id: "", label: "All Rarities" },
  { id: "common", label: "Common" },
  { id: "uncommon", label: "Uncommon" },
  { id: "rare", label: "Rare" },
  { id: "mythic", label: "Mythic" },
];

export function GenerateDialog({ sets, onGenerate, onClose, generating = false, result }: GenerateDialogProps) {
  const [cardType, setCardType] = useState("keyword_definition");
  const [setCode, setSetCode] = useState("");
  const [rarity, setRarity] = useState("");
  const [setSearch, setSetSearch] = useState("");

  const selectedType = CARD_TYPES.find((t) => t.id === cardType);
  const needsSet = selectedType?.needsSet ?? false;

  const filteredSets = setSearch
    ? sets.filter((s) => s.name.toLowerCase().includes(setSearch.toLowerCase()) || s.code.toLowerCase().includes(setSearch.toLowerCase()))
    : sets.slice(0, 15);

  const selectedSet = sets.find((s) => s.code === setCode);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div className="bg-bg-secondary border border-border rounded-lg w-full max-w-md shadow-xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <h2 className="text-sm font-semibold text-text-primary">Generate Flashcards</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary text-lg">&times;</button>
        </div>

        {result ? (
          <div className="p-4 space-y-4 text-center">
            <div className="text-4xl">🎉</div>
            <h3 className="text-lg text-text-primary">Created {result.created} flashcards</h3>
            <p className="text-sm text-text-muted">Collection: {result.collection.replace(/_/g, " ")}</p>
            <button
              onClick={onClose}
              className="text-sm font-medium px-4 py-2 rounded bg-accent text-white hover:bg-accent-hover transition-colors"
            >
              Done
            </button>
          </div>
        ) : (
          <div className="p-4 space-y-4">
            {/* Card type */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-text-secondary">Flashcard Type</label>
              <div className="space-y-1.5">
                {CARD_TYPES.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setCardType(t.id)}
                    className={`w-full text-left px-3 py-2.5 rounded-lg border transition-colors ${
                      cardType === t.id
                        ? "border-accent bg-accent-muted text-accent"
                        : "border-border bg-bg-tertiary text-text-secondary hover:border-border-hover"
                    }`}
                  >
                    <p className="text-sm font-medium">{t.label}</p>
                    <p className="text-xs text-text-muted mt-0.5">{t.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Set selector (for card-based types) */}
            {needsSet && (
              <div className="space-y-2">
                <label className="text-xs font-medium text-text-secondary">Set</label>
                {selectedSet ? (
                  <div className="flex items-center justify-between bg-bg-tertiary rounded px-3 py-2">
                    <SetBadge code={selectedSet.code} name={selectedSet.name} size="sm" />
                    <button onClick={() => setSetCode("")} className="text-xs text-text-muted hover:text-text-primary">Change</button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <SearchInput value={setSearch} placeholder="Search sets..." onChange={setSetSearch} debounceMs={150} />
                    <div className="max-h-32 overflow-y-auto space-y-0.5 rounded border border-border bg-bg-primary">
                      {filteredSets.map((s) => (
                        <button
                          key={s.code}
                          onClick={() => { setSetCode(s.code); setSetSearch(""); }}
                          className="w-full flex items-center gap-2 px-3 py-1.5 text-left hover:bg-bg-hover transition-colors"
                        >
                          <SetBadge code={s.code} name={s.name} size="sm" />
                          <span className="text-xs text-text-muted ml-auto">{s.base_set_size} cards</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Rarity filter */}
            {needsSet && setCode && (
              <div className="space-y-2">
                <label className="text-xs font-medium text-text-secondary">Rarity</label>
                <select
                  value={rarity}
                  onChange={(e) => setRarity(e.target.value)}
                  className="w-full bg-bg-tertiary border border-border rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent"
                >
                  {RARITIES.map((r) => (
                    <option key={r.id} value={r.id}>{r.label}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Generate */}
            <button
              onClick={() => onGenerate(cardType, setCode || undefined, rarity || undefined)}
              disabled={generating || (needsSet && !setCode)}
              className="w-full text-sm font-medium px-4 py-2.5 rounded bg-accent text-white hover:bg-accent-hover disabled:opacity-50 transition-colors"
            >
              {generating ? "Generating..." : "Generate Flashcards"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
