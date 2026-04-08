type OwnershipToggleProps = {
  value: "all" | "owned" | "not_owned";
  platform?: "any" | "paper" | "mtga";
  onChange: (value: "all" | "owned" | "not_owned") => void;
  onPlatformChange?: (platform: "any" | "paper" | "mtga") => void;
};

const options: { id: "all" | "owned" | "not_owned"; label: string }[] = [
  { id: "all", label: "All" },
  { id: "owned", label: "Owned" },
  { id: "not_owned", label: "Not Owned" },
];

const platforms: { id: "any" | "paper" | "mtga"; label: string }[] = [
  { id: "any", label: "Any" },
  { id: "paper", label: "Paper" },
  { id: "mtga", label: "MTGA" },
];

export function OwnershipToggle({ value, platform = "any", onChange, onPlatformChange }: OwnershipToggleProps) {
  return (
    <div className="flex items-center gap-2">
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
      {value === "owned" && onPlatformChange && (
        <div className="inline-flex items-center rounded border border-border overflow-hidden">
          {platforms.map((p) => (
            <button
              key={p.id}
              onClick={() => onPlatformChange(p.id)}
              className={`px-2 py-1.5 text-[10px] font-medium transition-colors ${
                platform === p.id
                  ? "bg-accent text-white"
                  : "bg-bg-secondary text-text-muted hover:text-text-secondary hover:bg-bg-tertiary"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
