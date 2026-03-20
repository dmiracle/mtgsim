import { useState } from "react";

type DeckCreateModalProps = {
  open: boolean;
  onClose: () => void;
  onCreate: (data: { name: string; format: string | null; description: string | null }) => void;
  creating?: boolean;
};

const FORMATS = ["standard", "pioneer", "modern", "legacy", "vintage", "commander", "brawl", "historic", "pauper"];

export function DeckCreateModal({ open, onClose, onCreate, creating = false }: DeckCreateModalProps) {
  const [name, setName] = useState("");
  const [format, setFormat] = useState("");
  const [description, setDescription] = useState("");

  if (!open) return null;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    onCreate({
      name: name.trim(),
      format: format || null,
      description: description.trim() || null,
    });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div className="bg-bg-secondary border border-border rounded-lg w-full max-w-md shadow-xl" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <h2 className="text-sm font-semibold text-text-primary">New Deck</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary text-lg">&times;</button>
        </div>
        <form onSubmit={handleSubmit} className="p-4 space-y-3">
          <div className="space-y-1">
            <label className="text-xs font-medium text-text-secondary">Name *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Deck name"
              autoFocus
              className="w-full bg-bg-tertiary border border-border rounded px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-text-secondary">Format</label>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="w-full bg-bg-tertiary border border-border rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent"
            >
              <option value="">None</option>
              {FORMATS.map((f) => (
                <option key={f} value={f} className="capitalize">{f}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-text-secondary">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description"
              rows={2}
              className="w-full bg-bg-tertiary border border-border rounded px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent resize-none"
            />
          </div>
          <button
            type="submit"
            disabled={!name.trim() || creating}
            className="w-full text-sm font-medium px-4 py-2 rounded bg-accent text-white hover:bg-accent-hover disabled:opacity-50 transition-colors"
          >
            {creating ? "Creating..." : "Create Deck"}
          </button>
        </form>
      </div>
    </div>
  );
}
