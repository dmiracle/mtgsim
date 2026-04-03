type GenerateButtonProps = {
  count: number;
  generating: boolean;
  progress?: { done: number; total: number };
  disabled?: boolean;
  onClick: () => void;
};

export function GenerateButton({
  count,
  generating,
  progress,
  disabled = false,
  onClick,
}: GenerateButtonProps) {
  const label = generating
    ? `Generating${progress ? ` ${progress.done}/${progress.total}` : "..."}`
    : `Generate from ${count} ${count === 1 ? "set" : "sets"}`;

  return (
    <button
      onClick={onClick}
      disabled={disabled || generating || count === 0}
      className="w-full py-3.5 rounded-xl bg-accent text-white font-semibold text-sm hover:bg-accent/80 active:scale-[0.98] transition-all disabled:opacity-40 disabled:cursor-not-allowed relative overflow-hidden"
    >
      {generating && progress && (
        <div
          className="absolute inset-y-0 left-0 bg-white/10 transition-all duration-300"
          style={{ width: `${(progress.done / progress.total) * 100}%` }}
        />
      )}
      <span className="relative">{label}</span>
    </button>
  );
}
