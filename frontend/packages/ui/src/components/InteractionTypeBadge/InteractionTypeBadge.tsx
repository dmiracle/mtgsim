type InteractionTypeBadgeProps = {
  type: string;
  size?: "sm" | "md";
};

const styles: Record<string, string> = {
  combo: "bg-accent/15 text-accent border-accent/30",
  synergy: "bg-success/15 text-success border-success/30",
  counter: "bg-danger/15 text-danger border-danger/30",
};

export function InteractionTypeBadge({ type, size = "sm" }: InteractionTypeBadgeProps) {
  const sizeClasses = size === "sm" ? "text-[10px] px-1.5 py-0.5" : "text-xs px-2 py-1";
  const color = styles[type] ?? "bg-bg-tertiary text-text-muted border-border";

  return (
    <span className={`${sizeClasses} ${color} rounded-full font-semibold border capitalize`}>
      {type}
    </span>
  );
}
