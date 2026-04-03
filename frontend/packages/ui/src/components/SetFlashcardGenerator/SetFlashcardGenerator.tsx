import { useState } from "react";
import type { SetSummary } from "@/types/api";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { SetBadge } from "@/components/SetBadge/SetBadge";

type GenerationJob = {
  id: string;
  label: string;
  cardType: string;
  setCode?: string;
  status: "pending" | "running" | "done" | "error";
  created: number;
  error?: string;
};

type SetFlashcardGeneratorProps = {
  sets: SetSummary[];
  onGenerate: (cardType: string, setCode?: string, rarity?: string) => Promise<{ created: number; collection: string }>;
  onComplete: () => void;
};

export function SetFlashcardGenerator({ sets, onGenerate, onComplete }: SetFlashcardGeneratorProps) {
  const [setCode, setSetCode] = useState("");
  const [setSearch, setSetSearch] = useState("");
  const [jobs, setJobs] = useState<GenerationJob[]>([]);
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);

  const selectedSet = sets.find((s) => s.code === setCode);
  const filteredSets = setSearch
    ? sets.filter((s) => s.name.toLowerCase().includes(setSearch.toLowerCase()) || s.code.toLowerCase().includes(setSearch.toLowerCase()))
    : sets.slice(0, 15);

  function buildJobs(): GenerationJob[] {
    return [
      { id: "keywords", label: "Keyword Definitions", cardType: "keyword_definition", status: "pending", created: 0 },
      { id: "oracle", label: "Card Oracle Text", cardType: "card_oracle", setCode, status: "pending", created: 0 },
      { id: "mana_cost", label: "Card Mana Costs", cardType: "card_mana_cost", setCode, status: "pending", created: 0 },
      { id: "stats", label: "Card Stats (P/T)", cardType: "card_stats", setCode, status: "pending", created: 0 },
    ];
  }

  async function runGeneration() {
    if (!setCode) return;
    const newJobs = buildJobs();
    setJobs(newJobs);
    setRunning(true);
    setDone(false);

    for (let i = 0; i < newJobs.length; i++) {
      setJobs((prev) => prev.map((j, idx) => idx === i ? { ...j, status: "running" } : j));
      try {
        const result = await onGenerate(newJobs[i].cardType, newJobs[i].setCode);
        setJobs((prev) => prev.map((j, idx) => idx === i ? { ...j, status: "done", created: result.created } : j));
      } catch (err) {
        setJobs((prev) => prev.map((j, idx) => idx === i ? { ...j, status: "error", error: String(err) } : j));
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
        <h2 className="text-xl text-text-primary">Generate Set Flashcards</h2>
        <p className="text-xs text-text-muted mt-1">
          Creates card quizzes and keyword flashcards for an entire set
        </p>
      </div>

      {/* Set selector */}
      {!running && !done && (
        <div className="space-y-3">
          <div className="space-y-2">
            <label className="text-xs font-medium text-text-secondary">Select a Set</label>
            {selectedSet ? (
              <div className="flex items-center justify-between bg-bg-secondary border border-border rounded-lg px-4 py-3">
                <div>
                  <SetBadge code={selectedSet.code} name={selectedSet.name} size="md" />
                  <p className="text-xs text-text-muted mt-1">
                    {selectedSet.base_set_size} cards
                    {selectedSet.total_set_size > selectedSet.base_set_size && ` (${selectedSet.total_set_size} total)`}
                  </p>
                </div>
                <button onClick={() => setSetCode("")} className="text-xs text-text-muted hover:text-text-primary">
                  Change
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <SearchInput value={setSearch} placeholder="Search sets..." onChange={setSetSearch} debounceMs={150} />
                <div className="max-h-48 overflow-y-auto space-y-0.5 rounded-lg border border-border bg-bg-primary">
                  {filteredSets.map((s) => (
                    <button
                      key={s.code}
                      onClick={() => { setSetCode(s.code); setSetSearch(""); }}
                      className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-bg-hover transition-colors"
                    >
                      <SetBadge code={s.code} name={s.name} size="sm" />
                      <div className="text-right">
                        <span className="text-xs text-text-muted">{s.base_set_size} cards</span>
                        <p className="text-[10px] text-text-muted">{s.release_date}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* What will be generated */}
          {selectedSet && (
            <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-2">
              <h3 className="text-xs font-semibold text-text-secondary">This will generate:</h3>
              <ul className="space-y-1 text-xs text-text-muted">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent shrink-0" />
                  Keyword definitions for all MTG keywords
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent shrink-0" />
                  Oracle text quizzes for {selectedSet.base_set_size} cards in {selectedSet.name}
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent shrink-0" />
                  Mana cost quizzes for cards with mana costs
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent shrink-0" />
                  Power/toughness quizzes for creatures
                </li>
              </ul>
            </div>
          )}

          <button
            onClick={runGeneration}
            disabled={!setCode}
            className="w-full text-sm font-semibold px-4 py-3 rounded-lg bg-accent text-white hover:bg-accent-hover disabled:opacity-50 transition-colors"
          >
            Generate All Flashcards
          </button>
        </div>
      )}

      {/* Progress */}
      {(running || done) && (
        <div className="space-y-3">
          {/* Progress bar */}
          <div className="w-full h-2 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className="h-full bg-accent transition-all duration-500 rounded-full"
              style={{ width: `${(completedJobs / jobs.length) * 100}%` }}
            />
          </div>

          {/* Job list */}
          <div className="space-y-1.5">
            {jobs.map((job) => (
              <div
                key={job.id}
                className={`flex items-center justify-between px-3 py-2 rounded-lg border ${
                  job.status === "done" ? "border-success/30 bg-success/5"
                    : job.status === "error" ? "border-danger/30 bg-danger/5"
                    : job.status === "running" ? "border-accent/30 bg-accent/5"
                    : "border-border bg-bg-secondary"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${
                    job.status === "done" ? "bg-success"
                      : job.status === "error" ? "bg-danger"
                      : job.status === "running" ? "bg-accent animate-pulse"
                      : "bg-border"
                  }`} />
                  <span className="text-sm text-text-primary">{job.label}</span>
                </div>
                <span className="text-xs text-text-muted tabular-nums">
                  {job.status === "done" && `${job.created} created`}
                  {job.status === "running" && "Generating..."}
                  {job.status === "error" && "Error"}
                  {job.status === "pending" && "Waiting"}
                </span>
              </div>
            ))}
          </div>

          {/* Summary */}
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
