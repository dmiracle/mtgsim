import { useState, useEffect } from "react";
import { ScratchReveal } from "@/components/ScratchReveal/ScratchReveal";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { FlipCard } from "@/components/FlipCard/FlipCard";
import { RatingButtons } from "@/components/RatingButtons/RatingButtons";

type QuizField = {
  id: string;
  label: string;
  answer: string;
};

type CardQuizProps = {
  cardName: string;
  imageUrl: string;
  manaValue: number;
  manaCost: string;
  typeLine: string;
  rarity: string;
  powerToughness: string | null;
  oracleText: string;
  onRate: (rating: number, responseTimeMs: number, revealPercentage: number) => void;
};

export function CardQuiz({
  cardName,
  imageUrl,
  manaValue,
  manaCost,
  typeLine,
  rarity,
  powerToughness,
  oracleText,
  onRate,
}: CardQuizProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [fieldRatings, setFieldRatings] = useState<Record<string, number>>({});
  const [revealPct, setRevealPct] = useState(0);
  const [startTime] = useState(Date.now());
  const [touchStartX, setTouchStartX] = useState<number | null>(null);

  const fields: QuizField[] = [
    { id: "manaValue", label: "Mana Value", answer: String(manaValue) },
    { id: "manaCost", label: "Mana Cost", answer: manaCost },
    { id: "typeLine", label: "Card Type", answer: typeLine },
    { id: "rarity", label: "Rarity", answer: rarity },
  ];
  if (powerToughness) {
    fields.push({ id: "pt", label: "P / T", answer: powerToughness });
  }
  fields.push({ id: "oracle", label: "Oracle Text", answer: oracleText });

  const currentField = fields[currentIndex];
  const isRated = fieldRatings[currentField.id] !== undefined;
  const allRated = fields.every((f) => fieldRatings[f.id] !== undefined);
  const ratedCount = fields.filter((f) => fieldRatings[f.id] !== undefined).length;

  function rateField(rating: number) {
    setFieldRatings((prev) => ({ ...prev, [currentField.id]: rating }));
    // Auto-advance after a short delay
    setTimeout(() => {
      if (currentIndex < fields.length - 1) {
        setCurrentIndex(currentIndex + 1);
        setFlipped(false);
      }
    }, 400);
  }

  function goNext() {
    if (currentIndex < fields.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setFlipped(false);
    }
  }

  function goPrev() {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setFlipped(false);
    }
  }

  function handleOverallRate(rating: number) {
    const responseMs = Date.now() - startTime;
    onRate(rating, responseMs, revealPct);
  }

  // Swipe support
  function handleTouchStart(e: React.TouchEvent) {
    setTouchStartX(e.touches[0].clientX);
  }

  function handleTouchEnd(e: React.TouchEvent) {
    if (touchStartX === null) return;
    const diff = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(diff) > 50) {
      if (diff < 0) goNext();
      else goPrev();
    }
    setTouchStartX(null);
  }

  // Keyboard: arrows to navigate, space to flip
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.code === "ArrowRight") goNext();
      if (e.code === "ArrowLeft") goPrev();
      if (e.code === "Space") {
        e.preventDefault();
        setFlipped((f) => !f);
      }
      if (flipped && !isRated && e.key >= "0" && e.key <= "5") {
        rateField(parseInt(e.key));
      }
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  });

  // Reset on card change
  useEffect(() => {
    setCurrentIndex(0);
    setFlipped(false);
    setFieldRatings({});
    setRevealPct(0);
  }, [cardName]);

  return (
    <div className="w-full max-w-3xl mx-auto space-y-4">
      {/* Card name */}
      <div className="text-center">
        <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold mb-1">Card Quiz</p>
        <h2 className="text-xl sm:text-2xl text-text-primary">{cardName}</h2>
      </div>

      {/* Side by side: scratch image left, flashcard carousel right */}
      <div className="flex gap-4 sm:gap-6">
        {/* Scratch reveal image */}
        <div className="w-[200px] sm:w-[260px] shrink-0">
          <ScratchReveal
            imageUrl={imageUrl}
            brushSize={30}
            onRevealChange={(pct) => setRevealPct(pct)}
          />
        </div>

        {/* Question carousel + rating */}
        <div
          className="flex-1 min-w-0 flex flex-col gap-3 justify-center"
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
        >
          <FlipCard
            flipped={flipped}
            onFlip={() => setFlipped(!flipped)}
            front={
              <div className="bg-bg-secondary border-2 border-accent rounded-xl p-5 text-center min-h-[160px] flex flex-col items-center justify-center">
                <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold mb-2">
                  {currentField.label}
                </p>
                <p className="text-sm text-text-muted">What is the {currentField.label.toLowerCase()}?</p>
                <p className="text-text-muted text-xs mt-4">Tap to reveal</p>
              </div>
            }
            back={
              <div className="bg-bg-secondary border-2 border-success rounded-xl p-5 text-center min-h-[160px] flex flex-col items-center justify-center">
                <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold mb-2">
                  {currentField.label}
                </p>
                {currentField.id === "manaCost" ? (
                  <div className="flex justify-center">
                    <ManaSymbols cost={currentField.answer} size="lg" />
                  </div>
                ) : (
                  <p className="text-base text-text-primary leading-relaxed whitespace-pre-line">
                    {currentField.answer}
                  </p>
                )}
              </div>
            }
          />

          {/* Per-field rating */}
          {flipped && !isRated && (
            <RatingButtons onRate={rateField} compact />
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <button
              onClick={goPrev}
              disabled={currentIndex === 0}
              className="px-2 py-1 text-xs rounded border border-border text-text-muted hover:text-text-secondary disabled:opacity-30 transition-colors"
            >
              ←
            </button>
            <div className="flex items-center gap-1">
              {fields.map((f, i) => (
                <button
                  key={f.id}
                  onClick={() => { setCurrentIndex(i); setFlipped(false); }}
                  className={`w-2.5 h-2.5 rounded-full transition-colors ${
                    i === currentIndex
                      ? "bg-accent scale-125"
                      : fieldRatings[f.id] !== undefined
                        ? "bg-success"
                        : "bg-border"
                  }`}
                />
              ))}
            </div>
            <button
              onClick={goNext}
              disabled={currentIndex === fields.length - 1}
              className="px-2 py-1 text-xs rounded border border-border text-text-muted hover:text-text-secondary disabled:opacity-30 transition-colors"
            >
              →
            </button>
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
        <div
          className="h-full bg-accent transition-all duration-300 rounded-full"
          style={{ width: `${(ratedCount / fields.length) * 100}%` }}
        />
      </div>

      {/* Navigation arrows + progress */}
      <div className="flex items-center justify-between">
        <button
          onClick={goPrev}
          disabled={currentIndex === 0}
          className="px-3 py-1.5 text-xs rounded border border-border text-text-muted hover:text-text-secondary disabled:opacity-30 transition-colors"
        >
          ← Prev
        </button>

        <div className="flex items-center gap-1">
          {fields.map((f, i) => (
            <button
              key={f.id}
              onClick={() => { setCurrentIndex(i); setFlipped(false); }}
              className={`w-2.5 h-2.5 rounded-full transition-colors ${
                i === currentIndex
                  ? "bg-accent scale-125"
                  : fieldRatings[f.id] !== undefined
                    ? "bg-success"
                    : "bg-border"
              }`}
            />
          ))}
        </div>

        <button
          onClick={goNext}
          disabled={currentIndex === fields.length - 1}
          className="px-3 py-1.5 text-xs rounded border border-border text-text-muted hover:text-text-secondary disabled:opacity-30 transition-colors"
        >
          Next →
        </button>
      </div>

      {/* Progress bar */}
      <div className="w-full h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
        <div
          className="h-full bg-accent transition-all duration-300 rounded-full"
          style={{ width: `${(ratedCount / fields.length) * 100}%` }}
        />
      </div>

      {/* Overall rating — shown when all fields rated */}
      {allRated && (
        <div className="space-y-3 pt-2 border-t border-border">
          <p className="text-xs text-text-muted text-center">Overall recall</p>
          <RatingButtons onRate={handleOverallRate} />
        </div>
      )}
    </div>
  );
}
