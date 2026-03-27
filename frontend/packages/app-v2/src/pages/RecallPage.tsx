import { useState, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useSets, useCards } from "@/api/hooks";
import { CardRecallFlashcard } from "@/components/CardRecallFlashcard/CardRecallFlashcard";
import { SetBadge } from "@/components/SetBadge/SetBadge";
import type { CardSummary } from "@/types/api";

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function RecallPage() {
  const navigate = useNavigate();
  const [selectedSets, setSelectedSets] = useState<string[]>([]);
  const [studying, setStudying] = useState(false);
  const [deck, setDeck] = useState<CardSummary[]>([]);
  const [index, setIndex] = useState(0);
  const [search, setSearch] = useState("");

  const { data: setsData } = useSets({ limit: 200 });
  const sets = setsData?.data ?? [];

  const filteredSets = useMemo(() => {
    if (!search) return sets.slice(0, 30);
    const q = search.toLowerCase();
    return sets.filter(
      (s) => s.name.toLowerCase().includes(q) || s.code.toLowerCase().includes(q)
    );
  }, [sets, search]);

  // Fetch cards for selected sets when studying
  const setsParam = studying ? selectedSets.join(",") : "";
  const { data: cardsData, isLoading } = useCards(
    setsParam ? { sets: setsParam, limit: 100 } : {}
  );

  // Build shuffled deck when cards arrive
  if (studying && cardsData?.data && deck.length === 0 && !isLoading) {
    const shuffled = shuffle(cardsData.data);
    setDeck(shuffled);
  }

  function toggleSet(code: string) {
    setSelectedSets((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  }

  function startStudy() {
    if (selectedSets.length === 0) return;
    setDeck([]);
    setIndex(0);
    setStudying(true);
  }

  function backToPicker() {
    setStudying(false);
    setDeck([]);
    setIndex(0);
  }

  const handleRate = useCallback(
    (_ratings: Record<string, number | string>, _responseTimeMs: number) => {
      setIndex((i) => i + 1);
    },
    []
  );

  // -- Picker --
  if (!studying) {
    return (
      <div className="max-w-lg mx-auto px-4 py-8 min-h-screen">
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={() => navigate("/")}
            className="text-xs text-text-muted hover:text-accent transition-colors"
          >
            <i className="ms ms-ability-transform mr-1" style={{ transform: "scaleX(-1)", display: "inline-block" }} />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Card Recall</h1>
            <p className="text-sm text-text-muted">Pick sets to study</p>
          </div>
        </div>

        {selectedSets.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-1.5 mb-3">
              {selectedSets.map((code) => (
                <button
                  key={code}
                  onClick={() => toggleSet(code)}
                  className="flex items-center gap-1 px-2 py-1 text-xs rounded-lg bg-accent/20 text-accent hover:bg-accent/30 transition-colors"
                >
                  {code} &times;
                </button>
              ))}
            </div>
            <button
              onClick={startStudy}
              className="w-full py-3 rounded-lg bg-accent text-white font-semibold text-sm hover:bg-accent/80 transition-colors"
            >
              Start Recall ({selectedSets.length} {selectedSets.length === 1 ? "set" : "sets"})
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
      </div>
    );
  }

  // -- Study --
  const card = deck[index];

  if (isLoading || (deck.length === 0 && cardsData === undefined)) {
    return (
      <div className="max-w-lg mx-auto px-4 min-h-screen flex items-center justify-center text-text-muted">
        Loading cards...
      </div>
    );
  }

  if (!card || index >= deck.length) {
    return (
      <div className="max-w-lg mx-auto px-4 min-h-screen flex flex-col items-center justify-center space-y-4">
        <i className="ms ms-ability-adventure text-5xl text-success" />
        <h2 className="text-xl font-bold text-text-primary">Complete!</h2>
        <p className="text-sm text-text-muted">{deck.length} cards reviewed</p>
        <div className="flex gap-3">
          <button
            onClick={() => { setDeck(shuffle(deck)); setIndex(0); }}
            className="text-sm font-medium px-4 py-2 rounded-lg border border-accent text-accent hover:bg-accent/10 transition-colors"
          >
            Reshuffle
          </button>
          <button
            onClick={backToPicker}
            className="text-sm font-medium px-4 py-2 rounded-lg bg-accent text-white hover:bg-accent/80 transition-colors"
          >
            Pick Sets
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-4 min-h-screen">
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={backToPicker}
          className="text-xs text-text-muted hover:text-accent transition-colors"
        >
          <i className="ms ms-ability-transform mr-1" style={{ transform: "scaleX(-1)", display: "inline-block" }} />
          Sets
        </button>
        <span className="text-xs text-text-muted tabular-nums">
          {index + 1} / {deck.length}
        </span>
      </div>
      <CardRecallFlashcard card={card} onRate={handleRate} />
    </div>
  );
}
