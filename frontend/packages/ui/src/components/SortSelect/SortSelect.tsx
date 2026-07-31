type SortOption = {
  value: string;
  label: string;
};

type SortSelectProps = {
  options: SortOption[];
  sort: string;
  /** Secondary sort field, shown as "then <label>" */
  secondary?: string;
  order: "asc" | "desc";
  onSortChange: (sort: string) => void;
  onOrderChange: (order: "asc" | "desc") => void;
};

export function SortSelect({ options, sort, secondary, order, onSortChange, onOrderChange }: SortSelectProps) {
  const secondaryLabel = secondary !== sort && options.find((o) => o.value === secondary)?.label;
  return (
    <div className="inline-flex items-center gap-1">
      <select
        value={sort}
        onChange={(e) => onSortChange(e.target.value)}
        className="bg-bg-secondary border border-border rounded px-2 py-1.5 text-xs text-text-secondary focus:outline-none focus:border-accent"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {secondaryLabel && (
        <span className="text-[10px] text-text-muted whitespace-nowrap" title="Secondary sort">
          then {secondaryLabel}
        </span>
      )}
      <button
        onClick={() => onOrderChange(order === "asc" ? "desc" : "asc")}
        className="px-2 py-1.5 text-xs rounded border border-border bg-bg-secondary text-text-muted hover:text-text-secondary hover:border-border-hover transition-colors"
        title={order === "asc" ? "Ascending" : "Descending"}
      >
        {order === "asc" ? "↑" : "↓"}
      </button>
    </div>
  );
}
