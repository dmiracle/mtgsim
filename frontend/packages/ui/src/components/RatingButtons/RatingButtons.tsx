type RatingButtonsProps = {
  onRate: (rating: number) => void;
  disabled?: boolean;
  compact?: boolean;
};

const ratings = [
  { value: 0, label: "Blackout", color: "bg-danger text-white hover:bg-danger/80" },
  { value: 1, label: "Wrong", color: "bg-danger/70 text-white hover:bg-danger/60" },
  { value: 2, label: "Wrong+", color: "bg-danger/50 text-white hover:bg-danger/40" },
  { value: 3, label: "Hard", color: "bg-warning text-yellow-900 hover:bg-warning/80" },
  { value: 4, label: "Good", color: "bg-success/80 text-white hover:bg-success/60" },
  { value: 5, label: "Perfect", color: "bg-success text-white hover:bg-success/80" },
];

export function RatingButtons({ onRate, disabled = false, compact = false }: RatingButtonsProps) {
  return (
    <div className={`flex flex-wrap items-center justify-center ${compact ? "gap-1" : "gap-2"}`}>
      {ratings.map((r) => (
        <button
          key={r.value}
          onClick={() => onRate(r.value)}
          disabled={disabled}
          className={`flex flex-col items-center rounded-lg font-medium transition-all disabled:opacity-50 ${r.color} ${
            compact ? "px-1.5 py-1 gap-0" : "px-3 sm:px-4 py-2 sm:py-3 gap-0.5"
          }`}
        >
          <span className={compact ? "text-[10px]" : "text-sm sm:text-base"}>{r.value}</span>
          {!compact && <span className="text-[10px] sm:text-xs opacity-80">{r.label}</span>}
        </button>
      ))}
    </div>
  );
}
