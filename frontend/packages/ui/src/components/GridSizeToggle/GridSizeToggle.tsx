export type GridSize = "small" | "medium" | "large";

type GridSizeToggleProps = {
  value: GridSize;
  onChange: (size: GridSize) => void;
};

const sizes: { size: GridSize; label: string; title: string }[] = [
  { size: "small", label: "S", title: "Small grid items" },
  { size: "medium", label: "M", title: "Medium grid items" },
  { size: "large", label: "L", title: "Large grid items" },
];

export function GridSizeToggle({ value, onChange }: GridSizeToggleProps) {
  return (
    <div className="inline-flex items-center rounded border border-border overflow-hidden">
      {sizes.map(({ size, label, title }) => (
        <button
          key={size}
          onClick={() => onChange(size)}
          className={`px-2 py-1 text-xs font-medium transition-colors ${
            value === size
              ? "bg-accent text-white"
              : "bg-bg-secondary text-text-muted hover:text-text-secondary"
          }`}
          title={title}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
