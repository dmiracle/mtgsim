type StrengthRatingProps = {
  value: number | null;
  max?: number;
  onChange?: (value: number) => void;
};

export function StrengthRating({ value, max = 5, onChange }: StrengthRatingProps) {
  return (
    <div className="inline-flex items-center gap-0.5">
      {Array.from({ length: max }, (_, i) => {
        const filled = value !== null && i < value;
        return (
          <button
            key={i}
            onClick={onChange ? () => onChange(i + 1) : undefined}
            disabled={!onChange}
            className={`text-sm transition-colors ${
              filled ? "text-warning" : "text-text-muted/20"
            } ${onChange ? "cursor-pointer hover:text-warning/70" : "cursor-default"}`}
          >
            ★
          </button>
        );
      })}
    </div>
  );
}
