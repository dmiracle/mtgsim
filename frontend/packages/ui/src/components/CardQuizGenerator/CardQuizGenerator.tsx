import { useState } from "react";
import type { SetSummary } from "@/types/api";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { SetBadge } from "@/components/SetBadge/SetBadge";

type GenerationJob = {
  setCode: string;
  setName: string;
  types: string[];
  status: "pending" | "running" | "done" | "error";
  created: number;
};

type CardQuizGeneratorProps = {
  sets: SetSummary[];
  onGenerate: (cardType: string, setCode: string, collectionName?: string) => Promise<{ created: number; collection: string }>;
  onComplete: () => void;
};

const FORMATS = ["standard", "pioneer", "modern", "legacy", "vintage", "commander", "pauper"];

const CARD_TYPES = [
  { id: "card_oracle", label: "Oracle Text" },
  { id: "card_mana_cost", label: "Mana Cost" },
  { id: "card_stats", label: "P/T Stats" },
  { id: "card_rarity", label: "Rarity" },
];

export function CardQuizGenerator({ sets, onGenerate, onComplete }: CardQuizGeneratorProps) {
  const [mode, setMode] = useState<"sets" | "format">("format");
  const [selectedFormat, setSelectedFormat] = useState("");
  const [selectedSetCodes, setSelectedSetCodes] = useState<Set<string>>(new Set());
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(new Set(["card_oracle", "card_mana_cost", "card_stats", "card_rarity"]));
  const [setSearch, setSetSearch] = useState("");
  const [jobs, setJobs] = useState<GenerationJob[]>([]);
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);
  const [includeKeywords, setIncludeKeywords] = useState(true);
  const [singleCollection, setSingleCollection] = useState(true);
  const [collectionName, setCollectionName] = useState("");

  // Get sets for a format by filtering set types (expansion, core)
  const formatSets = selectedFormat
    ? sets.filter((s) =>
        (s.type === "expansion" || s.type === "core") &&
        s.base_set_size > 0
      ).slice(0, 20) // Take recent sets as approximation — backend would ideally filter
    : [];

  const filteredSets = setSearch
    ? sets.filter((s) =>
        (s.name.toLowerCase().includes(setSearch.toLowerCase()) ||
         s.code.toLowerCase().includes(setSearch.toLowerCase())) &&
        s.base_set_size > 0
      )
    : sets.filter((s) => s.base_set_size > 0).slice(0, 20);

  function toggleSet(code: string) {
    setSelectedSetCodes((prev) => {
      const next = new Set(prev);
      if (next.has(code)) next.delete(code);
      else next.add(code);
      return next;
    });
  }

  function toggleType(id: string) {
    setSelectedTypes((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  const targetSets = mode === "format"
    ? formatSets
    : sets.filter((s) => selectedSetCodes.has(s.code));

  const totalEstimate = targetSets.reduce((sum, s) => sum + s.base_set_size, 0) * selectedTypes.size;

  async function runGeneration() {
    if (targetSets.length === 0 || selectedTypes.size === 0) return;

    const newJobs: GenerationJob[] = [];

    // Per-set jobs — include keywords per set if selected
    for (const s of targetSets) {
      const types = [...selectedTypes];
      if (includeKeywords) {
        types.unshift("keyword_definition");
      }
      newJobs.push({
        setCode: s.code,
        setName: s.name,
        types,
        status: "pending",
        created: 0,
      });
    }

    setJobs(newJobs);
    setRunning(true);
    setDone(false);

    for (let i = 0; i < newJobs.length; i++) {
      setJobs((prev) => prev.map((j, idx) => idx === i ? { ...j, status: "running" } : j));

      let totalCreated = 0;
      try {
        for (const type of newJobs[i].types) {
          const colName = singleCollection && collectionName ? collectionName : undefined;
          const result = await onGenerate(type, newJobs[i].setCode, colName);
          totalCreated += result.created;
        }
        setJobs((prev) => prev.map((j, idx) => idx === i ? { ...j, status: "done", created: totalCreated } : j));
      } catch {
        setJobs((prev) => prev.map((j, idx) => idx === i ? { ...j, status: "error", created: totalCreated } : j));
      }
    }

    setRunning(false);
    setDone(true);
  }

  const totalCreated = jobs.reduce((sum, j) => sum + j.created, 0);
  const completedJobs = jobs.filter((j) => j.status === "done" || j.status === "error").length;

  return (
    <div className="w-full max-w-lg mx-auto space-y-4">
      <div className="text-center">
        <h2 className="text-xl text-text-primary">Card Quiz Generator</h2>
        <p className="text-xs text-text-muted mt-1">
          Create card quizzes for sets by format or individual selection
        </p>
      </div>

      {!running && !done && (
        <div className="space-y-4">
          {/* Mode toggle */}
          <div className="flex rounded-lg border border-border overflow-hidden">
            <button
              onClick={() => setMode("format")}
              className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                mode === "format" ? "bg-accent text-white" : "bg-bg-secondary text-text-muted hover:text-text-secondary"
              }`}
            >
              By Format
            </button>
            <button
              onClick={() => setMode("sets")}
              className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                mode === "sets" ? "bg-accent text-white" : "bg-bg-secondary text-text-muted hover:text-text-secondary"
              }`}
            >
              By Sets
            </button>
          </div>

          {/* Format selector */}
          {mode === "format" && (
            <div className="space-y-2">
              <label className="text-xs font-medium text-text-secondary">Format</label>
              <div className="flex flex-wrap gap-1.5">
                {FORMATS.map((f) => (
                  <button
                    key={f}
                    onClick={() => setSelectedFormat(selectedFormat === f ? "" : f)}
                    className={`px-3 py-1.5 text-xs font-medium rounded-lg border capitalize transition-colors ${
                      selectedFormat === f
                        ? "bg-accent text-white border-accent"
                        : "bg-bg-secondary border-border text-text-muted hover:border-border-hover"
                    }`}
                  >
                    {f}
                  </button>
                ))}
              </div>
              {selectedFormat && (
                <p className="text-xs text-text-muted">
                  {formatSets.length} sets ({formatSets.reduce((s, x) => s + x.base_set_size, 0)} cards)
                </p>
              )}
            </div>
          )}

          {/* Set selector */}
          {mode === "sets" && (
            <div className="space-y-2">
              <label className="text-xs font-medium text-text-secondary">Select Sets</label>
              <SearchInput value={setSearch} placeholder="Search sets..." onChange={setSetSearch} debounceMs={150} />

              {/* Selected sets */}
              {selectedSetCodes.size > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {[...selectedSetCodes].map((code) => {
                    const s = sets.find((x) => x.code === code);
                    return (
                      <button
                        key={code}
                        onClick={() => toggleSet(code)}
                        className="flex items-center gap-1 px-2 py-1 rounded bg-accent/20 text-accent text-xs"
                      >
                        <SetBadge code={code} name={s?.name} size="sm" />
                        <span>×</span>
                      </button>
                    );
                  })}
                </div>
              )}

              <div className="max-h-48 overflow-y-auto space-y-0.5 rounded-lg border border-border bg-bg-primary">
                {filteredSets.map((s) => (
                  <button
                    key={s.code}
                    onClick={() => toggleSet(s.code)}
                    className={`w-full flex items-center justify-between px-3 py-2 text-left transition-colors ${
                      selectedSetCodes.has(s.code) ? "bg-accent/10" : "hover:bg-bg-hover"
                    }`}
                  >
                    <SetBadge code={s.code} name={s.name} size="sm" />
                    <span className="text-xs text-text-muted">{s.base_set_size} cards</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Quiz types */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-text-secondary">Quiz Types</label>
            <div className="flex flex-wrap gap-1.5">
              {CARD_TYPES.map((t) => (
                <button
                  key={t.id}
                  onClick={() => toggleType(t.id)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${
                    selectedTypes.has(t.id)
                      ? "bg-accent text-white border-accent"
                      : "bg-bg-secondary border-border text-text-muted hover:border-border-hover"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
            <label className="flex items-center gap-2 text-xs text-text-secondary cursor-pointer">
              <input
                type="checkbox"
                checked={includeKeywords}
                onChange={(e) => setIncludeKeywords(e.target.checked)}
                className="accent-accent"
              />
              Include keyword definitions
            </label>
          </div>

          {/* Single collection option */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-xs text-text-secondary cursor-pointer">
              <input
                type="checkbox"
                checked={singleCollection}
                onChange={(e) => setSingleCollection(e.target.checked)}
                className="accent-accent"
              />
              Combine into single collection
            </label>
            {singleCollection && (
              <input
                type="text"
                value={collectionName}
                onChange={(e) => setCollectionName(e.target.value)}
                placeholder={mode === "format" && selectedFormat
                  ? `${selectedFormat.charAt(0).toUpperCase() + selectedFormat.slice(1)} Study Deck`
                  : targetSets.length === 1
                    ? `${targetSets[0].name} Study Deck`
                    : "My Study Deck"
                }
                className="w-full bg-bg-tertiary border border-border rounded px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
              />
            )}
          </div>

          {/* Summary */}
          {targetSets.length > 0 && selectedTypes.size > 0 && (
            <div className="bg-bg-secondary border border-border rounded-lg p-3 text-xs text-text-muted">
              Will generate quizzes for <span className="text-text-primary font-medium">{targetSets.length}</span> sets
              ({selectedTypes.size} quiz types, ~{totalEstimate.toLocaleString()} flashcards)
            </div>
          )}

          <button
            onClick={runGeneration}
            disabled={targetSets.length === 0 || selectedTypes.size === 0}
            className="w-full text-sm font-semibold px-4 py-3 rounded-lg bg-accent text-white hover:bg-accent-hover disabled:opacity-50 transition-colors"
          >
            Generate Card Quizzes
          </button>
        </div>
      )}

      {/* Progress */}
      {(running || done) && (
        <div className="space-y-3">
          <div className="w-full h-2 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className="h-full bg-accent transition-all duration-500 rounded-full"
              style={{ width: `${(completedJobs / jobs.length) * 100}%` }}
            />
          </div>

          <div className="max-h-64 overflow-y-auto space-y-1">
            {jobs.map((job, i) => (
              <div
                key={i}
                className={`flex items-center justify-between px-3 py-1.5 rounded-lg border text-xs ${
                  job.status === "done" ? "border-success/30 bg-success/5"
                    : job.status === "error" ? "border-danger/30 bg-danger/5"
                    : job.status === "running" ? "border-accent/30 bg-accent/5"
                    : "border-border bg-bg-secondary"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full shrink-0 ${
                    job.status === "done" ? "bg-success"
                      : job.status === "error" ? "bg-danger"
                      : job.status === "running" ? "bg-accent animate-pulse"
                      : "bg-border"
                  }`} />
                  <span className="text-text-primary">{job.setName}</span>
                </div>
                <span className="text-text-muted tabular-nums">
                  {job.status === "done" && `${job.created}`}
                  {job.status === "running" && "..."}
                  {job.status === "error" && "Error"}
                </span>
              </div>
            ))}
          </div>

          {done && (
            <div className="text-center space-y-3 pt-2">
              <div>
                <p className="text-2xl font-bold text-text-primary">{totalCreated}</p>
                <p className="text-xs text-text-muted">flashcards created</p>
              </div>
              <button
                onClick={onComplete}
                className="text-sm font-medium px-6 py-2.5 rounded-lg bg-accent text-white hover:bg-accent-hover transition-colors"
              >
                Start Studying
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
