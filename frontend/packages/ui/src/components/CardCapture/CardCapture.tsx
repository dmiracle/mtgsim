import type { CardSummary } from "@/types/api";
import type { DetectionStatus } from "@/components/CameraViewfinder/CameraViewfinder";
import { CameraViewfinder } from "@/components/CameraViewfinder/CameraViewfinder";
import { CardCaptureResult } from "@/components/CardCaptureResult/CardCaptureResult";

type CardCaptureProps = {
  status: DetectionStatus;
  matchedCard?: CardSummary | null;
  confidence?: number;
  onFrame?: (video: HTMLVideoElement) => void;
  frameInterval?: number;
  onAddToDeck?: (uuid: string) => void;
  onAddToCollection?: (uuid: string) => void;
  onDismiss?: () => void;
  onSetClick?: (code: string) => void;
};

export function CardCapture({
  status,
  matchedCard = null,
  confidence = 0,
  onFrame,
  frameInterval,
  onAddToDeck,
  onAddToCollection,
  onDismiss,
  onSetClick,
}: CardCaptureProps) {
  return (
    <div className="flex flex-col gap-4 w-full max-w-md mx-auto">
      <CameraViewfinder
        status={status}
        onFrame={onFrame}
        frameInterval={frameInterval}
        className="aspect-[3/4]"
      />

      {matchedCard && (
        <CardCaptureResult
          card={matchedCard}
          confidence={confidence}
          onAddToDeck={onAddToDeck}
          onAddToCollection={onAddToCollection}
          onDismiss={onDismiss}
          onSetClick={onSetClick}
        />
      )}
    </div>
  );
}
