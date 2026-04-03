type PinButtonProps = {
  pinned: boolean;
  onToggle: () => void;
  size?: "sm" | "md";
};

export function PinButton({ pinned, onToggle, size = "sm" }: PinButtonProps) {
  const sizeClasses = size === "sm" ? "text-xs px-2 py-1" : "text-sm px-3 py-1.5";

  return (
    <button
      onClick={onToggle}
      title={pinned ? "Unpin" : "Pin"}
      className={`${sizeClasses} rounded font-medium transition-all ${
        pinned
          ? "bg-warning/20 text-warning border border-warning/40 hover:bg-warning/30"
          : "bg-bg-tertiary text-text-muted border border-border hover:text-warning hover:border-warning/40"
      }`}
    >
      {pinned ? "★ Pinned" : "☆ Pin"}
    </button>
  );
}
