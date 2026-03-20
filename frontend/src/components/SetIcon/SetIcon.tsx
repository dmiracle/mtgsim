export type SetIconProps = {
  code: string;
  name?: string;
  rarity?: "common" | "uncommon" | "rare" | "mythic";
  size?: "sm" | "md" | "lg";
  navigable?: boolean;
  onClick?: () => void;
};

const sizeClasses = {
  sm: "",
  md: "ss-2x",
  lg: "ss-3x",
};

const rarityClasses: Record<string, string> = {
  uncommon: "ss-uncommon",
  rare: "ss-rare",
  mythic: "ss-mythic",
};

export function SetIcon({
  code,
  name,
  rarity,
  size = "md",
  navigable = false,
  onClick,
}: SetIconProps) {
  const usesKeyruneColor = rarity && rarity !== "common" && rarityClasses[rarity];
  const iconClasses = [
    "ss",
    `ss-${code.toLowerCase()}`,
    sizeClasses[size],
    usesKeyruneColor ? rarityClasses[rarity] : "",
  ]
    .filter(Boolean)
    .join(" ");
  const themeColor = !usesKeyruneColor ? "text-text-secondary" : "";

  const interactiveClasses = navigable
    ? "cursor-pointer hover:opacity-80 transition-opacity"
    : "";

  return (
    <span
      className={`inline-flex items-center ${interactiveClasses}`}
      title={name ?? code.toUpperCase()}
      onClick={navigable ? onClick : undefined}
      role={navigable ? "button" : undefined}
    >
      <i className={`${iconClasses} ${themeColor}`} aria-hidden="true" />
    </span>
  );
}
