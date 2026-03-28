import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSets } from "@/api/hooks";
import { useGenerateFlashcards } from "@/api/flashcard-hooks";
import { SetPicker } from "@/components/SetPicker/SetPicker";
import { GenerateButton } from "@/components/GenerateButton/GenerateButton";
import { GenerateResult } from "@/components/GenerateResult/GenerateResult";

const USER_ID = localStorage.getItem("flashcard_user_id") || "default_user";

export function GeneratePage() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState<string[]>([]);
  const [search, setSearch] = useState("");
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState({ done: 0, total: 0 });
  const [results, setResults] = useState<{ set: string; created: number }[]>([]);

  const { data: setsData } = useSets(search ? { q: search, limit: 30 } : { limit: 30 });
  const sets = setsData?.data ?? [];
  const generateMutation = useGenerateFlashcards();

  const done = !generating && results.length > 0;

  function toggle(code: string) {
    setSelected((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  }

  async function handleGenerate() {
    if (selected.length === 0) return;
    setGenerating(true);
    setResults([]);
    setProgress({ done: 0, total: selected.length });

    for (const setCode of selected) {
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
      setProgress((prev) => ({ ...prev, done: prev.done + 1 }));
    }

    setGenerating(false);
  }

  function reset() {
    setResults([]);
    setSelected([]);
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-8 min-h-screen">
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={() => navigate("/")}
          className="w-9 h-9 rounded-lg bg-bg-secondary border border-border flex items-center justify-center text-text-muted hover:text-accent hover:border-accent transition-colors shrink-0"
        >
          <i
            className="ms ms-ability-transform"
            style={{ transform: "scaleX(-1)", display: "inline-block", fontSize: "1em" }}
          />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Generate Card Recall</h1>
          <p className="text-sm text-text-muted">Pick sets to create recall flashcards</p>
        </div>
      </div>

      {done ? (
        <GenerateResult
          results={results}
          onStudy={() => navigate("/study")}
          onGenerateMore={reset}
        />
      ) : (
        <div className="space-y-4">
          {selected.length > 0 && (
            <GenerateButton
              count={selected.length}
              generating={generating}
              progress={generating ? progress : undefined}
              onClick={handleGenerate}
            />
          )}
          <SetPicker
            sets={sets}
            selected={selected}
            search={search}
            onSearchChange={setSearch}
            onToggle={toggle}
            onClear={() => setSelected([])}
          />
        </div>
      )}
    </div>
  );
}
