import { type ReactNode } from "react";

type FlipCardProps = {
  flipped: boolean;
  front: ReactNode;
  back: ReactNode;
  onFlip?: () => void;
};

export function FlipCard({ flipped, front, back, onFlip }: FlipCardProps) {
  return (
    <div className="cursor-pointer" onClick={onFlip}>
      {flipped ? back : front}
    </div>
  );
}
