import { useState } from "react";
import type { Tier, TierEntry } from "@/types/api";

export type TierListBoardProps = {
  entries: TierEntry[];
  onMove: (cardName: string, tier: Tier, position?: number) => void;
  onRemove?: (cardName: string) => void;
  onNoteChange?: (cardName: string, note: string) => void;
  onCardClick?: (uuid: string) => void;
};

// 17Lands-style grades, A+ (best) through F
const TIERS: { tier: Tier; label: string; bar: string }[] = [
  { tier: "A+", label: "A+", bar: "bg-red-500" },
  { tier: "A", label: "A", bar: "bg-orange-500" },
  { tier: "A-", label: "A-", bar: "bg-amber-400" },
  { tier: "B+", label: "B+", bar: "bg-yellow-400" },
  { tier: "B", label: "B", bar: "bg-lime-400" },
  { tier: "B-", label: "B-", bar: "bg-green-500" },
  { tier: "C+", label: "C+", bar: "bg-emerald-500" },
  { tier: "C", label: "C", bar: "bg-teal-400" },
  { tier: "C-", label: "C-", bar: "bg-cyan-400" },
  { tier: "D+", label: "D+", bar: "bg-sky-500" },
  { tier: "D", label: "D", bar: "bg-blue-500" },
  { tier: "D-", label: "D-", bar: "bg-indigo-400" },
  { tier: "F", label: "F", bar: "bg-zinc-500" },
];

export function TierListBoard({ entries, onMove, onRemove, onNoteChange, onCardClick }: TierListBoardProps) {
  const [dragging, setDragging] = useState<string | null>(null);
  const [dropTier, setDropTier] = useState<Tier | null>(null);
  const [noteFor, setNoteFor] = useState<string | null>(null);
  const [noteDraft, setNoteDraft] = useState("");

  const byTier = new Map<string, TierEntry[]>(TIERS.map((t) => [t.tier, []]));
  for (const entry of entries) byTier.get(entry.tier)?.push(entry);
  for (const list of byTier.values()) list.sort((a, b) => a.position - b.position);

  function draggedName(e: React.DragEvent): string {
    return e.dataTransfer.getData("text/plain") || dragging || "";
  }

  function dropOnTier(e: React.DragEvent, tier: Tier) {
    e.preventDefault();
    const name = draggedName(e);
    if (name) onMove(name, tier);
    setDragging(null);
    setDropTier(null);
  }

  function dropOnEntry(e: React.DragEvent, tier: Tier, target: TierEntry) {
    e.preventDefault();
    e.stopPropagation();
    const name = draggedName(e);
    if (name && name !== target.card_name) onMove(name, tier, target.position);
    setDragging(null);
    setDropTier(null);
  }

  function toggleNote(entry: TierEntry) {
    if (noteFor === entry.card_name) {
      setNoteFor(null);
    } else {
      setNoteFor(entry.card_name);
      setNoteDraft(entry.note ?? "");
    }
  }

  return (
    <div className="space-y-1.5">
      {TIERS.map(({ tier, label, bar }) => {
        const tierEntries = byTier.get(tier) ?? [];
        const noteEntry = tierEntries.find((en) => en.card_name === noteFor);
        return (
          <div key={tier}>
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDropTier(tier);
              }}
              onDragLeave={() => setDropTier((t) => (t === tier ? null : t))}
              onDrop={(e) => dropOnTier(e, tier)}
              className={`flex items-stretch rounded-lg border overflow-hidden transition-colors ${
                dropTier === tier ? "border-accent bg-accent/5" : "border-border bg-bg-secondary"
              }`}
            >
              <div className={`w-10 shrink-0 flex items-center justify-center ${bar}`}>
                <span className="text-lg font-bold text-black/70">{label}</span>
              </div>
              <div className="flex flex-wrap gap-2 p-2 min-h-[72px] flex-1">
                {tierEntries.length === 0 && (
                  <span className="self-center text-[10px] text-text-muted px-2">Drop cards here</span>
                )}
                {tierEntries.map((entry) => (
                  <div
                    key={entry.id}
                    draggable
                    onDragStart={(e) => {
                      e.dataTransfer.setData("text/plain", entry.card_name);
                      setDragging(entry.card_name);
                    }}
                    onDragEnd={() => {
                      setDragging(null);
                      setDropTier(null);
                    }}
                    onDrop={(e) => dropOnEntry(e, tier, entry)}
                    onDragOver={(e) => e.preventDefault()}
                    className={`group relative w-16 cursor-grab active:cursor-grabbing ${
                      dragging === entry.card_name ? "opacity-40" : ""
                    }`}
                    title={entry.note ? `${entry.card_name} — ${entry.note}` : entry.card_name}
                  >
                    <div
                      onClick={() => entry.card?.uuid && onCardClick?.(entry.card.uuid)}
                      className="aspect-[5/7] rounded bg-bg-tertiary overflow-hidden border border-border group-hover:border-accent transition-colors"
                    >
                      {entry.card?.image_url ? (
                        <img
                          src={entry.card.image_url}
                          alt={entry.card_name}
                          className="w-full h-full object-cover"
                          draggable={false}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center p-1">
                          <span className="text-[8px] text-text-secondary text-center leading-tight">
                            {entry.card_name}
                          </span>
                        </div>
                      )}
                    </div>
                    <p className="mt-0.5 text-[9px] text-text-muted truncate text-center">{entry.card_name}</p>
                    <div className="absolute top-0.5 right-0.5 flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      {onNoteChange && (
                        <button
                          onClick={() => toggleNote(entry)}
                          aria-label={`Note for ${entry.card_name}`}
                          className={`w-4 h-4 flex items-center justify-center rounded text-[9px] leading-none ${
                            entry.note ? "bg-accent text-white" : "bg-black/60 text-white hover:bg-accent"
                          }`}
                        >
                          ✎
                        </button>
                      )}
                      {onRemove && (
                        <button
                          onClick={() => onRemove(entry.card_name)}
                          aria-label={`Remove ${entry.card_name}`}
                          className="w-4 h-4 flex items-center justify-center rounded bg-black/60 text-white hover:bg-danger text-[10px] leading-none"
                        >
                          ×
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {noteEntry && onNoteChange && (
              <div className="mt-1 ml-10 bg-bg-tertiary border border-border rounded-lg p-2 space-y-1.5">
                <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">
                  {noteEntry.card_name}
                </span>
                <textarea
                  value={noteDraft}
                  onChange={(e) => setNoteDraft(e.target.value)}
                  placeholder="Why is it in this tier?"
                  rows={2}
                  className="w-full bg-bg-secondary border border-border rounded-lg px-3 py-1.5 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent resize-none"
                />
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      onNoteChange(noteEntry.card_name, noteDraft.trim());
                      setNoteFor(null);
                    }}
                    className="text-xs px-3 py-1 rounded bg-accent text-white hover:bg-accent-hover transition-colors"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => setNoteFor(null)}
                    className="text-xs text-text-muted hover:text-text-primary transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
