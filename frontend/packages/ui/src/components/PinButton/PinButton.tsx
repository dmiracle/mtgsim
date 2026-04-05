type PinButtonProps = {
  pinned: boolean;
  onToggle: () => void;
  size?: "sm" | "md";
};

export function PinButton({ pinned, onToggle, size = "sm" }: PinButtonProps) {
  const sizeClasses = size === "sm" ? "text-xs w-7 h-7" : "text-sm w-8 h-8";

  return (
    <button
      onClick={onToggle}
      title={pinned ? "Unpin" : "Pin"}
      className={`${sizeClasses} rounded flex items-center justify-center border transition-all ${
        pinned
          ? "bg-warning/20 text-warning border-warning/40 hover:bg-warning/30"
          : "bg-bg-tertiary text-text-muted border-border hover:text-warning hover:border-warning/40"
      }`}
    >
      {pinned ? "★" : "☆"}
    </button>
  );
}
