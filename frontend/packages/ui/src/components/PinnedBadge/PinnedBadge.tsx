type PinnedBadgeProps = {
  pinned: boolean;
  onToggle?: () => void;
  size?: "sm" | "md";
};

export function PinnedBadge({ pinned, onToggle, size = "sm" }: PinnedBadgeProps) {
  if (!pinned && !onToggle) return null;

  const sizeClasses = size === "sm"
    ? "w-6 h-6 text-xs"
    : "w-7 h-7 text-sm";

  if (!onToggle) {
    return (
      <span
        className={`${sizeClasses} rounded-full flex items-center justify-center bg-warning/90 text-yellow-900 font-bold shadow-sm`}
        title="Pinned"
      >
        ★
      </span>
    );
  }

  return (
    <button
      onClick={onToggle}
      title={pinned ? "Unpin" : "Pin"}
      className={`${sizeClasses} rounded-full flex items-center justify-center font-bold transition-all shadow-sm ${
        pinned
          ? "bg-warning/90 text-yellow-900 hover:bg-warning"
          : "bg-black/40 text-white/60 hover:text-warning hover:bg-black/60"
      }`}
    >
      {pinned ? "★" : "☆"}
    </button>
  );
}
