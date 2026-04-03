import { useState } from "react";
import type { SetSummary } from "@/types/api";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { SetBadge } from "@/components/SetBadge/SetBadge";

type PackConfigPanelProps = {
  sets: SetSummary[];
  onOpen: (setCode: string, boosterType: string, count: number) => void;
  loading?: boolean;
};

const BOOSTER_TYPES = [
  { id: "auto", label: "Auto-detect" },
  { id: "play", label: "Play Booster" },
  { id: "draft", label: "Draft Booster" },
];

const PACK_COUNTS = [
  { value: 1, label: "1 Pack" },
  { value: 3, label: "3 Packs" },
  { value: 6, label: "6 (Sealed)" },
  { value: 12, label: "12 Packs" },
  { value: 24, label: "24 (Box)" },
  { value: 36, label: "36 (Box)" },
];

export function PackConfigPanel({ sets, onOpen, loading = false }: PackConfigPanelProps) {
  const [search, setSearch] = useState("");
  const [selectedSet, setSelectedSet] = useState<string | null>(null);
  const [boosterType, setBoosterType] = useState("auto");
  const [packCount, setPackCount] = useState(1);

  const filtered = search
    ? sets.filter((s) => s.name.toLowerCase().includes(search.toLowerCase()) || s.code.toLowerCase().includes(search.toLowerCase()))
    : sets.slice(0, 20);

  const selectedSetData = sets.find((s) => s.code === selectedSet);

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-4">
      <h3 className="text-sm font-medium text-text-secondary">Pack Configuration</h3>

      {/* Set selector */}
      <div className="space-y-2">
        <label className="text-xs font-medium text-text-secondary">Set</label>
        {selectedSetData ? (
          <div className="flex items-center justify-between bg-bg-tertiary rounded px-3 py-2">
            <SetBadge code={selectedSetData.code} name={selectedSetData.name} size="sm" />
            <button
              onClick={() => setSelectedSet(null)}
              className="text-xs text-text-muted hover:text-text-primary"
            >
              Change
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <SearchInput
              value={search}
              placeholder="Search sets..."
              onChange={setSearch}
              debounceMs={150}
            />
            <div className="max-h-40 overflow-y-auto space-y-0.5 rounded border border-border bg-bg-primary">
              {filtered.map((s) => (
                <button
                  key={s.code}
                  onClick={() => { setSelectedSet(s.code); setSearch(""); }}
                  className="w-full flex items-center gap-2 px-3 py-1.5 text-left hover:bg-bg-hover transition-colors"
                >
                  <SetBadge code={s.code} name={s.name} size="sm" />
                  <span className="text-xs text-text-muted ml-auto">{s.release_date}</span>
                </button>
              ))}
              {filtered.length === 0 && (
                <p className="px-3 py-4 text-xs text-text-muted text-center">No sets found</p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Booster type */}
      <div className="space-y-2">
        <label className="text-xs font-medium text-text-secondary">Booster Type</label>
        <div className="flex gap-1">
          {BOOSTER_TYPES.map((bt) => (
            <button
              key={bt.id}
              onClick={() => setBoosterType(bt.id)}
              className={`flex-1 px-2 py-1.5 text-xs font-medium rounded border transition-all ${
                boosterType === bt.id
                  ? "bg-accent text-white border-accent"
                  : "bg-bg-tertiary border-border text-text-muted hover:border-border-hover"
              }`}
            >
              {bt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Pack count */}
      <div className="space-y-2">
        <label className="text-xs font-medium text-text-secondary">Packs</label>
        <div className="grid grid-cols-3 gap-1">
          {PACK_COUNTS.map((pc) => (
            <button
              key={pc.value}
              onClick={() => setPackCount(pc.value)}
              className={`px-2 py-1.5 text-xs font-medium rounded border transition-all ${
                packCount === pc.value
                  ? "bg-accent text-white border-accent"
                  : "bg-bg-tertiary border-border text-text-muted hover:border-border-hover"
              }`}
            >
              {pc.label}
            </button>
          ))}
        </div>
      </div>

      {/* Open button */}
      <button
        onClick={() => selectedSet && onOpen(selectedSet, boosterType, packCount)}
        disabled={!selectedSet || loading}
        className="w-full text-sm font-semibold px-4 py-2.5 rounded bg-accent text-white hover:bg-accent-hover disabled:opacity-50 transition-colors"
      >
        {loading ? "Opening..." : `Open ${packCount} Pack${packCount > 1 ? "s" : ""}`}
      </button>
    </div>
  );
}
