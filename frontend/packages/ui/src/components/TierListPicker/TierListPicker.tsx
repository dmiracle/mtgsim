import { useState } from "react";
import type { TierListSummary } from "@/types/api";

export type TierListPickerProps = {
  lists: TierListSummary[];
  selectedId?: number | null;
  onSelect: (id: number | null) => void;
  onCreate?: (data: { name: string; set_code: string | null; format: string | null }) => void;
};

export function TierListPicker({ lists, selectedId = null, onSelect, onCreate }: TierListPickerProps) {
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");
  const [setCode, setSetCode] = useState("");
  const [format, setFormat] = useState("");

  const selected = lists.find((l) => l.id === selectedId);

  function handleCreate() {
    if (!onCreate || !name.trim()) return;
    onCreate({
      name: name.trim(),
      set_code: setCode.trim() ? setCode.trim().toUpperCase() : null,
      format: format.trim() ? format.trim().toLowerCase() : null,
    });
    setCreating(false);
    setName("");
    setSetCode("");
    setFormat("");
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <select
          value={selectedId ?? ""}
          onChange={(e) => onSelect(e.target.value === "" ? null : Number(e.target.value))}
          className="bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent"
        >
          <option value="">No tier list</option>
          {lists.map((l) => (
            <option key={l.id} value={l.id}>
              {l.name}
              {l.set_code ? ` · ${l.set_code}` : ""}
              {l.format ? ` · ${l.format}` : ""}
            </option>
          ))}
        </select>
        {onCreate && !creating && (
          <button
            onClick={() => setCreating(true)}
            className="text-xs text-accent hover:text-accent-hover transition-colors whitespace-nowrap"
          >
            + New list
          </button>
        )}
      </div>

      {selected && (
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <span>{selected.entry_count} cards</span>
          {selected.set_code && (
            <span className="px-1.5 py-0.5 rounded bg-bg-tertiary border border-border text-text-secondary">
              {selected.set_code}
            </span>
          )}
          {selected.format && (
            <span className="px-1.5 py-0.5 rounded bg-bg-tertiary border border-border text-text-secondary">
              {selected.format}
            </span>
          )}
          {selected.description && <span className="truncate">{selected.description}</span>}
        </div>
      )}

      {creating && (
        <div className="bg-bg-tertiary border border-border rounded-lg p-3 space-y-2">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="List name"
            className="w-full bg-bg-secondary border border-border rounded-lg px-3 py-1.5 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
          />
          <div className="flex gap-2">
            <input
              value={setCode}
              onChange={(e) => setSetCode(e.target.value)}
              placeholder="Set code (optional)"
              className="flex-1 bg-bg-secondary border border-border rounded-lg px-3 py-1.5 text-xs text-text-secondary placeholder-text-muted focus:outline-none focus:border-accent"
            />
            <input
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              placeholder="Format (optional)"
              className="flex-1 bg-bg-secondary border border-border rounded-lg px-3 py-1.5 text-xs text-text-secondary placeholder-text-muted focus:outline-none focus:border-accent"
            />
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCreate}
              disabled={!name.trim()}
              className="text-xs px-3 py-1 rounded bg-accent text-white hover:bg-accent-hover transition-colors disabled:opacity-40"
            >
              Create
            </button>
            <button
              onClick={() => setCreating(false)}
              className="text-xs text-text-muted hover:text-text-primary transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
