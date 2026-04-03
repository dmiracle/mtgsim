import { useState, useRef } from "react";
import type { DeckImportResult } from "@/types/api";

type DeckImportModalProps = {
  open: boolean;
  onClose: () => void;
  onImport: (text: string, name: string) => void;
  result?: DeckImportResult | null;
  importing?: boolean;
  onViewDeck?: (deckId: string) => void;
};

export function DeckImportModal({ open, onClose, onImport, result, importing = false, onViewDeck }: DeckImportModalProps) {
  const [text, setText] = useState("");
  const [name, setName] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  if (!open) return null;

  function handleFile(file: File) {
    const baseName = file.name.replace(/\.(txt|dec|dek)$/i, "");
    if (!name) setName(baseName);
    file.text().then(setText);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim() || !name.trim()) return;
    onImport(text.trim(), name.trim());
  }

  const exact = result?.resolved.filter((r) => r.match_type === "exact") ?? [];
  const fuzzy = result?.resolved.filter((r) => r.match_type === "fuzzy") ?? [];
  const created = result?.resolved.filter((r) => r.match_type === "created") ?? [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div className="bg-bg-secondary border border-border rounded-lg w-full max-w-lg shadow-xl max-h-[85vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
          <h2 className="text-sm font-semibold text-text-primary">Import Deck</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary text-lg">&times;</button>
        </div>

        {!result ? (
          <form onSubmit={handleSubmit} className="p-4 space-y-3 overflow-y-auto">
            <div className="space-y-1">
              <label className="text-xs font-medium text-text-secondary">Deck Name *</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Deck name"
                className="w-full bg-bg-tertiary border border-border rounded px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-text-secondary">MTGA Export</label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                placeholder="Paste MTGA export text, or drag & drop a .txt/.dec/.dek file..."
                rows={8}
                className="w-full bg-bg-tertiary border border-border rounded px-3 py-2 text-xs text-text-primary placeholder-text-muted focus:outline-none focus:border-accent resize-none font-mono"
              />
            </div>
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="text-xs px-3 py-1.5 rounded border border-border text-text-secondary hover:border-border-hover transition-colors"
              >
                Browse File
              </button>
              <input
                ref={fileRef}
                type="file"
                accept=".txt,.dec,.dek"
                className="hidden"
                onChange={(e) => { if (e.target.files?.[0]) handleFile(e.target.files[0]); }}
              />
              <button
                type="submit"
                disabled={!text.trim() || !name.trim() || importing}
                className="ml-auto text-sm font-medium px-4 py-2 rounded bg-accent text-white hover:bg-accent-hover disabled:opacity-50 transition-colors"
              >
                {importing ? "Importing..." : "Import"}
              </button>
            </div>
          </form>
        ) : (
          <div className="p-4 space-y-4 overflow-y-auto">
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-text-primary">{result.deck_name}</h3>
              <p className="text-xs text-text-muted">{result.total_cards} cards imported</p>
            </div>

            {exact.length > 0 && (
              <div className="space-y-1">
                <h4 className="text-xs font-semibold text-success">Exact Matches ({exact.length})</h4>
                <div className="text-xs text-text-muted max-h-24 overflow-y-auto space-y-0.5">
                  {exact.map((r, i) => <p key={i}>{r.count}x {r.matched_name}</p>)}
                </div>
              </div>
            )}

            {fuzzy.length > 0 && (
              <div className="space-y-1">
                <h4 className="text-xs font-semibold text-warning">Fuzzy Matches ({fuzzy.length})</h4>
                <div className="text-xs text-text-muted max-h-24 overflow-y-auto space-y-0.5">
                  {fuzzy.map((r, i) => (
                    <p key={i}>{r.count}x {r.name} → {r.matched_name} <span className="text-warning">({(r.match_score * 100).toFixed(0)}%)</span></p>
                  ))}
                </div>
              </div>
            )}

            {created.length > 0 && (
              <div className="space-y-1">
                <h4 className="text-xs font-semibold text-danger">Unresolved ({created.length})</h4>
                <div className="text-xs text-text-muted max-h-24 overflow-y-auto space-y-0.5">
                  {created.map((r, i) => <p key={i}>{r.count}x {r.name} (placeholder)</p>)}
                </div>
              </div>
            )}

            {result.legality.length > 0 && (
              <div className="space-y-1">
                <h4 className="text-xs font-semibold text-text-secondary">Format Legality</h4>
                <div className="flex flex-wrap gap-1">
                  {result.legality.map((l) => (
                    <span
                      key={l.format}
                      className={`px-2 py-0.5 text-[10px] rounded border ${
                        l.legal
                          ? "bg-success/15 text-success border-success/30"
                          : "bg-bg-tertiary text-text-muted border-border"
                      }`}
                    >
                      {l.format}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={() => onViewDeck?.(result.deck_id)}
              className="w-full text-sm font-medium px-4 py-2 rounded bg-accent text-white hover:bg-accent-hover transition-colors"
            >
              View Deck
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
