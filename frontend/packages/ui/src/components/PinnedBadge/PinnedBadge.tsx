type PinnedBadgeProps = {
  pinned: boolean;
  onToggle?: () => void;
  size?: "sm" | "md";
  icon?: "pin" | "loyalty" | "planeswalker" | "saga" | "rarity" | "acorn";

};

const iconClass: Record<string, string> = {
  pin: "ms ms-counter-pin",
  loyalty: "ms ms-loyalty-start",
  planeswalker: "ms ms-planeswalker",
  saga: "ms ms-saga",
  rarity: "ms ms-rarity",
  acorn: "ms ms-acorn",
};

export function PinnedBadge({ pinned, onToggle, size = "sm", icon = "acorn" }: PinnedBadgeProps) {
  if (!pinned && !onToggle) return null;

  const sizeClasses = size === "sm" ? "text-sm" : "text-base";

  const colorClasses = pinned
    ? "text-warning drop-shadow-[0_1px_2px_rgba(0,0,0,0.3)]"
    : "text-text-muted/30";

  const hoverClasses = onToggle
    ? pinned
      ? "hover:text-warning/80 cursor-pointer"
      : "hover:text-warning/70 cursor-pointer"
    : "";

  const Tag = onToggle ? "button" : "span";

  return (
    <Tag
      onClick={onToggle}
      title={onToggle ? (pinned ? "Unpin" : "Pin") : "Pinned"}
      className={`${sizeClasses} ${colorClasses} ${hoverClasses} leading-none transition-colors`}
    >
      <i className={`${iconClass[icon]} leading-none`} />
    </Tag>
  );
}
