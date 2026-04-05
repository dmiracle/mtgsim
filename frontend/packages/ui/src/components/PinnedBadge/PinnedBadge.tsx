type PinnedBadgeProps = {
  pinned: boolean;
  onToggle?: () => void;
  size?: "sm" | "md";
};

export function PinnedBadge({ pinned, onToggle, size = "sm" }: PinnedBadgeProps) {
  if (!pinned && !onToggle) return null;

  const sizeClasses = size === "sm"
    ? "w-5 h-5 text-[10px]"
    : "w-6 h-6 text-xs";

  const icon = <i className={`ms ms-counter-pin leading-none`} />;

  if (!onToggle) {
    return (
      <span
        className={`${sizeClasses} rounded-full flex items-center justify-center bg-warning/90 text-yellow-900 shadow-sm`}
        title="Pinned"
      >
        {icon}
      </span>
    );
  }

  return (
    <button
      onClick={onToggle}
      title={pinned ? "Unpin" : "Pin"}
      className={`${sizeClasses} rounded-full flex items-center justify-center transition-all shadow-sm ${
        pinned
          ? "bg-warning/90 text-yellow-900 hover:bg-warning"
          : "bg-black/40 text-white/50 hover:text-warning hover:bg-black/60"
      }`}
    >
      {icon}
    </button>
  );
}
