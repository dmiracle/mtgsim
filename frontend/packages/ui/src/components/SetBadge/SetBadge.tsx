import { SetIcon } from "@/components/SetIcon/SetIcon";
import type { SetIconProps } from "@/components/SetIcon/SetIcon";

type SetBadgeProps = SetIconProps;

const codeSizes = {
  sm: "text-xs",
  md: "text-xs",
  lg: "text-sm",
};

export function SetBadge({
  code,
  name,
  rarity,
  size = "md",
  navigable = false,
  onClick,
}: SetBadgeProps) {
  const interactiveClasses = navigable
    ? "cursor-pointer hover:opacity-80 transition-opacity"
    : "";

  return (
    <span
      className={`inline-flex items-center gap-1.5 ${interactiveClasses}`}
      title={name}
      onClick={navigable ? onClick : undefined}
      role={navigable ? "button" : undefined}
    >
      <SetIcon code={code} rarity={rarity} size={size} />
      <span className={`${codeSizes[size]} font-mono uppercase tracking-wide text-text-secondary`}>
        {code}
      </span>
    </span>
  );
}
