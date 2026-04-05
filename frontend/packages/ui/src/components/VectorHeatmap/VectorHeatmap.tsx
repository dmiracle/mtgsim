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

function intensityColor(value: number): string {
  if (value <= 0) return "bg-bg-tertiary";
  if (value < 0.2) return "bg-accent/15";
  if (value < 0.4) return "bg-accent/30";
  if (value < 0.6) return "bg-accent/50";
  if (value < 0.8) return "bg-accent/70";
  return "bg-accent";
}

export function VectorHeatmap({ vector, featureNames, label, size = "md" }: VectorHeatmapProps) {
  const s = sizes[size];
  const cells = vector.length > 0 ? vector : Array(64).fill(0);
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
            className={`${s.cell} ${intensityColor(val)} transition-colors`}
            title={featureNames?.[i] ? `${featureNames[i]}: ${val.toFixed(2)}` : `[${i}]: ${val.toFixed(2)}`}
          />
        ))}
      </div>
    </div>
  );
}
