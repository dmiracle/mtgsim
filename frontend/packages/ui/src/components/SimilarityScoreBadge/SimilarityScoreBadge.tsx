type SimilarityScoreBadgeProps = {
  score: number;
  size?: "sm" | "md";
};

export function SimilarityScoreBadge({ score, size = "sm" }: SimilarityScoreBadgeProps) {
  const pct = Math.round(score * 100);
  const bg =
    score >= 0.7 ? "bg-success border-success/60" :
    score >= 0.4 ? "bg-warning border-warning/60" :
    "bg-danger border-danger/60";
  const sizeClasses = size === "sm" ? "text-[10px] px-1.5 py-0.5 border" : "text-xs px-2 py-1 border-2";

  return (
    <span className={`${sizeClasses} ${bg} text-white rounded-full font-bold tabular-nums shadow-md`}>
      {pct}%
    </span>
  );
}
