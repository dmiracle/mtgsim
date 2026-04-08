import { PinnedBadge } from "@/components/PinnedBadge/PinnedBadge";

type PinButtonProps = {
  pinned: boolean;
  onToggle: () => void;
  size?: "sm" | "md";
};

export function PinButton({ pinned, onToggle, size = "sm" }: PinButtonProps) {
  return <PinnedBadge pinned={pinned} onToggle={onToggle} size={size} />;
}
