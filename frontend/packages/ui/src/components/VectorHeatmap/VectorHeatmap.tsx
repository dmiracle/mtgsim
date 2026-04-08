type VectorHeatmapProps = {
  vector: number[];
  featureNames?: string[];
  label?: string;
  size?: "xs" | "sm" | "md" | "lg";
};

const sizes = {
  xs: { cell: "w-2 h-2", gap: "gap-0", text: "text-[8px]" },
  sm: { cell: "w-3 h-3", gap: "gap-px", text: "text-[10px]" },
  md: { cell: "w-5 h-5", gap: "gap-0.5", text: "text-xs" },
  lg: { cell: "w-8 h-8", gap: "gap-0.5", text: "text-sm" },
};

function intensityColor(ratio: number): string {
  if (ratio <= 0) return "bg-bg-tertiary";
  if (ratio < 0.15) return "bg-accent/10";
  if (ratio < 0.3) return "bg-accent/25";
  if (ratio < 0.5) return "bg-accent/40";
  if (ratio < 0.7) return "bg-accent/60";
  if (ratio < 0.85) return "bg-accent/80";
  return "bg-accent";
}

export function VectorHeatmap({ vector, featureNames, label, size = "md" }: VectorHeatmapProps) {
  const s = sizes[size];
  const cells = vector.length > 0 ? vector : Array(64).fill(0);
  const max = Math.max(...cells, 0.001);
  const cols = 8;

  return (
    <div className="inline-flex flex-col items-start">
      {label && (
        <span className={`${s.text} text-text-muted font-medium mb-1`}>{label}</span>
      )}
      <div className={`grid grid-cols-8 ${s.gap} rounded overflow-hidden`}>
        {cells.slice(0, cols * cols).map((val, i) => (
          <div
            key={i}
            className={`${s.cell} ${intensityColor(val / max)} transition-colors`}
            title={featureNames?.[i] ? `${featureNames[i]}: ${val.toFixed(3)}` : `[${i}]: ${val.toFixed(3)}`}
          />
        ))}
      </div>
    </div>
  );
}
