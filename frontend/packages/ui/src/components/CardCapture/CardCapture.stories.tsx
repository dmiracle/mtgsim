import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import type { DetectionStatus } from "@/components/CameraViewfinder/CameraViewfinder";
import { CardCaptureResult } from "@/components/CardCaptureResult/CardCaptureResult";
import { cardSummaries } from "@/fixtures";
import type { CardSummary } from "@/types/api";

// Full composed mock for Storybook — no real camera
function CardCaptureMock({
  status,
  matchedCard,
  confidence,
  onAddToDeck,
  onAddToCollection,
  onDismiss,
  onSetClick,
}: {
  status: DetectionStatus;
  matchedCard?: CardSummary | null;
  confidence?: number;
  onAddToDeck?: (uuid: string) => void;
  onAddToCollection?: (uuid: string) => void;
  onDismiss?: () => void;
  onSetClick?: (code: string) => void;
}) {
  const statusLabels: Record<DetectionStatus, string> = {
    idle: "Point camera at a card",
    scanning: "Scanning…",
    detected: "Card detected",
    error: "Camera unavailable",
  };

  const statusColors: Record<DetectionStatus, string> = {
    idle: "border-text-muted",
    scanning: "border-accent animate-pulse",
    detected: "border-success",
    error: "border-error",
  };

  const dotColors: Record<DetectionStatus, string> = {
    idle: "bg-text-muted",
    scanning: "bg-accent animate-pulse",
    detected: "bg-success",
    error: "bg-error",
  };

  return (
    <div className="flex flex-col gap-4 w-full max-w-md mx-auto">
      <div className="relative bg-black rounded-xl overflow-hidden aspect-[3/4]">
        <div className="w-full h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
          <span className="text-gray-600 text-sm">Camera feed</span>
        </div>

        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div
            className={`w-[70%] aspect-[5/7] border-2 rounded-lg relative ${statusColors[status]} transition-colors duration-300`}
          >
            <div className="absolute top-0 left-0 w-5 h-5 border-t-2 border-l-2 border-inherit rounded-tl-lg" />
            <div className="absolute top-0 right-0 w-5 h-5 border-t-2 border-r-2 border-inherit rounded-tr-lg" />
            <div className="absolute bottom-0 left-0 w-5 h-5 border-b-2 border-l-2 border-inherit rounded-bl-lg" />
            <div className="absolute bottom-0 right-0 w-5 h-5 border-b-2 border-r-2 border-inherit rounded-br-lg" />
          </div>
        </div>

        <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
          <div className="flex items-center gap-2 bg-black/70 backdrop-blur-sm text-white text-sm px-4 py-2 rounded-full">
            <span className={`w-2 h-2 rounded-full ${dotColors[status]}`} />
            {statusLabels[status]}
          </div>
        </div>
      </div>

      {matchedCard && confidence != null && (
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

const meta: Meta<typeof CardCaptureMock> = {
  title: "Capture/CardCapture",
  component: CardCaptureMock,
  tags: ["autodocs"],
  parameters: { layout: "padded" },
  args: {
    onAddToDeck: fn(),
    onAddToCollection: fn(),
    onDismiss: fn(),
    onSetClick: fn(),
  },
  decorators: [
    (Story) => (
      <div className="w-96">
        <Story />
      </div>
    ),
  ],
  argTypes: {
    status: {
      control: "select",
      options: ["idle", "scanning", "detected", "error"],
    },
    confidence: { control: { type: "range", min: 0, max: 1, step: 0.01 } },
  },
};

export default meta;
type Story = StoryObj<typeof CardCaptureMock>;

export const Idle: Story = {
  args: { status: "idle" },
};

export const Scanning: Story = {
  args: { status: "scanning" },
};

export const Detected: Story = {
  args: {
    status: "detected",
    matchedCard: cardSummaries[0],
    confidence: 0.97,
  },
};

export const LowConfidenceMatch: Story = {
  args: {
    status: "detected",
    matchedCard: cardSummaries[2],
    confidence: 0.52,
  },
};

export const CameraError: Story = {
  args: { status: "error" },
};
