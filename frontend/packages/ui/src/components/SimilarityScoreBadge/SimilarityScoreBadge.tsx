type SimilarityScoreBadgeProps = {
  score: number;
  size?: "sm" | "md";
};

export function SimilarityScoreBadge({ score, size = "sm" }: SimilarityScoreBadgeProps) {
  const pct = Math.round(score * 100);
  const color =
    score >= 0.7 ? "bg-success/15 text-success" :
    score >= 0.4 ? "bg-warning/15 text-warning" :
    "bg-danger/15 text-danger";
  const sizeClasses = size === "sm" ? "text-[10px] px-1.5 py-0.5" : "text-xs px-2 py-1";

  return (
    <span className={`${sizeClasses} ${color} rounded font-semibold tabular-nums`}>
      {pct}%
    </span>
  );
}
