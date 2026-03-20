type OwnershipToggleProps = {
  value: "all" | "owned" | "not_owned";
  onChange: (value: "all" | "owned" | "not_owned") => void;
};

const options: { id: "all" | "owned" | "not_owned"; label: string }[] = [
  { id: "all", label: "All" },
  { id: "owned", label: "Owned" },
  { id: "not_owned", label: "Not Owned" },
];

export function OwnershipToggle({ value, onChange }: OwnershipToggleProps) {
  return (
    <div className="inline-flex items-center rounded border border-border overflow-hidden">
      {options.map((opt) => (
        <button
          key={opt.id}
          onClick={() => onChange(opt.id)}
          className={`px-2.5 py-1.5 text-xs font-medium transition-colors ${
            value === opt.id
              ? "bg-accent text-white"
              : "bg-bg-secondary text-text-muted hover:text-text-secondary hover:bg-bg-tertiary"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
