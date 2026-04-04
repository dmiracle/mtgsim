import type { Meta, StoryObj } from "@storybook/react-vite";
import type { DetectionStatus } from "./CameraViewfinder";

// Storybook-only mock — renders a static placeholder instead of a live camera
function CameraViewfinderMock({
  status,
  className = "",
}: {
  status: DetectionStatus;
  className?: string;
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
    <div
      className={`relative bg-black rounded-xl overflow-hidden ${className}`}
    >
      {/* Simulated camera feed */}
      <div className="w-full h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <span className="text-gray-600 text-sm">Camera feed</span>
      </div>

      {/* Card guide overlay */}
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

      {/* Status pill */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
        <div className="flex items-center gap-2 bg-black/70 backdrop-blur-sm text-white text-sm px-4 py-2 rounded-full">
          <span className={`w-2 h-2 rounded-full ${dotColors[status]}`} />
          {statusLabels[status]}
        </div>
      </div>
    </div>
  );
}

const meta: Meta<typeof CameraViewfinderMock> = {
  title: "Capture/CameraViewfinder",
  component: CameraViewfinderMock,
  tags: ["autodocs"],
  parameters: { layout: "padded" },
  decorators: [
    (Story) => (
      <div className="w-80">
        <Story />
      </div>
    ),
  ],
  argTypes: {
    status: {
      control: "select",
      options: ["idle", "scanning", "detected", "error"],
    },
  },
};

export default meta;
type Story = StoryObj<typeof CameraViewfinderMock>;

export const Idle: Story = {
  args: { status: "idle", className: "aspect-[3/4]" },
};

export const Scanning: Story = {
  args: { status: "scanning", className: "aspect-[3/4]" },
};

export const Detected: Story = {
  args: { status: "detected", className: "aspect-[3/4]" },
};

export const Error: Story = {
  args: { status: "error", className: "aspect-[3/4]" },
};
