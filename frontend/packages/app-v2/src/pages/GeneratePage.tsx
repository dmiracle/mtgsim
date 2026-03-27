import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useSets } from "@/api/hooks";
import { useGenerateFlashcards } from "@/api/flashcard-hooks";
import { SetBadge } from "@/components/SetBadge/SetBadge";

const USER_ID = localStorage.getItem("flashcard_user_id") || "default_user";

export function GeneratePage() {
  const navigate = useNavigate();
  const [selectedSets, setSelectedSets] = useState<string[]>([]);
  const [search, setSearch] = useState("");
  const [generating, setGenerating] = useState(false);
  const [results, setResults] = useState<{ set: string; created: number }[]>([]);

  const { data: setsData } = useSets({ limit: 200 });
  const sets = setsData?.data ?? [];
  const generateMutation = useGenerateFlashcards();

  const filteredSets = useMemo(() => {
    if (!search) return sets.slice(0, 30);
    const q = search.toLowerCase();
    return sets.filter(
      (s) => s.name.toLowerCase().includes(q) || s.code.toLowerCase().includes(q)
    );
  }, [sets, search]);

  function toggleSet(code: string) {
    setSelectedSets((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  }

  async function handleGenerate() {
    if (selectedSets.length === 0) return;
    setGenerating(true);
    setResults([]);

    for (const setCode of selectedSets) {
      try {
        const res = await generateMutation.mutateAsync({
          user_id: USER_ID,
          card_type: "card_recall",
          set_code: setCode,
        });
        setResults((prev) => [...prev, { set: setCode, created: res.created }]);
      } catch {
        setResults((prev) => [...prev, { set: setCode, created: 0 }]);
      }
    }

    setGenerating(false);
  }

  const done = !generating && results.length > 0;
  const totalCreated = results.reduce((sum, r) => sum + r.created, 0);

  return (
    <div className="max-w-lg mx-auto px-4 py-8 min-h-screen">
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={() => navigate("/")}
          className="text-xs text-text-muted hover:text-accent transition-colors"
        >
          <i
            className="ms ms-ability-transform"
            style={{ transform: "scaleX(-1)", display: "inline-block", fontSize: "1.2em" }}
          />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Generate Card Recall</h1>
          <p className="text-sm text-text-muted">Pick sets to create recall flashcards</p>
        </div>
      </div>

      {done && (
        <div className="mb-6 p-4 rounded-lg bg-success/10 border border-success/30 space-y-3">
          <p className="text-sm font-semibold text-success">
            Created {totalCreated} flashcards from {results.length} {results.length === 1 ? "set" : "sets"}
          </p>
          <div className="space-y-1">
            {results.map((r) => (
              <div key={r.set} className="flex justify-between text-xs text-text-secondary">
                <span>{r.set.toUpperCase()}</span>
                <span>{r.created} cards</span>
              </div>
            ))}
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => navigate("/study")}
              className="flex-1 py-2 rounded-lg bg-accent text-white font-semibold text-sm hover:bg-accent/80 transition-colors"
            >
              Study Now
            </button>
            <button
              onClick={() => { setResults([]); setSelectedSets([]); }}
              className="flex-1 py-2 rounded-lg border border-border text-text-secondary font-semibold text-sm hover:border-border-hover transition-colors"
            >
              Generate More
            </button>
          </div>
        </div>
      )}

      {!done && (
        <>
          {selectedSets.length > 0 && (
            <div className="mb-4">
              <div className="flex flex-wrap gap-1.5 mb-3">
                {selectedSets.map((code) => (
                  <button
                    key={code}
                    onClick={() => toggleSet(code)}
                    className="flex items-center gap-1 px-2 py-1 text-xs rounded-lg bg-accent/20 text-accent hover:bg-accent/30 transition-colors"
                  >
                    {code.toUpperCase()} &times;
                  </button>
                ))}
              </div>
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="w-full py-3 rounded-lg bg-accent text-white font-semibold text-sm hover:bg-accent/80 transition-colors disabled:opacity-50"
              >
                {generating
                  ? `Generating... (${results.length}/${selectedSets.length})`
                  : `Generate from ${selectedSets.length} ${selectedSets.length === 1 ? "set" : "sets"}`}
              </button>
            </div>
          )}

          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search sets..."
            className="w-full mb-3 bg-bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
          />

          <div className="space-y-1">
            {filteredSets.map((s) => {
              const selected = selectedSets.includes(s.code);
              return (
                <button
                  key={s.code}
                  onClick={() => toggleSet(s.code)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-lg border transition-colors text-left ${
                    selected
                      ? "bg-accent/10 border-accent"
                      : "bg-bg-secondary border-border hover:border-border-hover"
                  }`}
                >
                  <SetBadge code={s.code} name={s.name} size="sm" />
                  <span className="text-xs text-text-muted">{s.base_set_size} cards</span>
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
