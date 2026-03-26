import { useState, useEffect } from "react";
import { ScratchReveal } from "@/components/ScratchReveal/ScratchReveal";
import { RatingButtons } from "@/components/RatingButtons/RatingButtons";

type RecallPromptType = "full" | "stats" | "abilities" | "cost";

type CardRecallChallengeProps = {
  cardName: string;
  imageUrl: string;
  promptType?: RecallPromptType;
  onRate: (rating: number, responseTimeMs: number, revealPercentage: number) => void;
};

const promptLabels: Record<RecallPromptType, string[]> = {
  full: ["Mana Value", "Power / Toughness", "Keywords & Abilities", "Mana Cost"],
  stats: ["Mana Value", "Power / Toughness"],
  abilities: ["Keywords & Abilities"],
  cost: ["Mana Cost"],
};

export function CardRecallChallenge({
  cardName,
  imageUrl,
  promptType = "full",
  onRate,
}: CardRecallChallengeProps) {
  const [revealPct, setRevealPct] = useState(0);
  const [startTime] = useState(Date.now());
  const [showRating, setShowRating] = useState(false);

  useEffect(() => {
    setShowRating(false);
    setRevealPct(0);
  }, [cardName]);

  function handleRevealChange(pct: number, _mask?: unknown) {
    setRevealPct(pct);
    // Show rating buttons once user starts revealing
    if (pct > 5 && !showRating) {
      setShowRating(true);
    }
  }

  function handleRate(rating: number) {
    const responseMs = Date.now() - startTime;
    onRate(rating, responseMs, revealPct);
  }

  const prompts = promptLabels[promptType];

  return (
    <div className="w-full max-w-[400px] mx-auto space-y-4">
      {/* Card name — always visible */}
      <div className="text-center">
        <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold mb-1">
          Card Recall
        </p>
        <h2 className="text-xl sm:text-2xl text-text-primary">{cardName}</h2>
      </div>

      {/* Recall prompts */}
      <div className="bg-bg-secondary border border-border rounded-lg p-3">
        <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold mb-2">
          Try to recall:
        </p>
        <div className="flex flex-wrap gap-1.5">
          {prompts.map((p) => (
            <span
              key={p}
              className="px-2.5 py-1 text-xs rounded bg-bg-tertiary text-text-secondary border border-border"
            >
              {p}
            </span>
          ))}
        </div>
      </div>

      {/* Scratch to reveal */}
      <ScratchReveal
        imageUrl={imageUrl}
        blurAmount={25}
        brushSize={40}
        onRevealChange={handleRevealChange}
      />

      {/* Self-rating */}
      {showRating && (
        <div className="space-y-3">
          <p className="text-text-muted text-xs text-center">How well did you recall?</p>
          <RatingButtons onRate={handleRate} />
        </div>
      )}

      {!showRating && (
        <p className="text-text-muted text-xs text-center">
          Scratch the image to check your recall, then rate yourself
        </p>
      )}
    </div>
  );
}
