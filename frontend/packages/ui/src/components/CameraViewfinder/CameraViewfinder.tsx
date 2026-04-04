import { useEffect, useRef, useState } from "react";

export type DetectionStatus = "idle" | "scanning" | "detected" | "error";

type CameraViewfinderProps = {
  status: DetectionStatus;
  onFrame?: (video: HTMLVideoElement) => void;
  frameInterval?: number;
  className?: string;
};

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

export function CameraViewfinder({
  status,
  onFrame,
  frameInterval = 500,
  className = "",
}: CameraViewfinderProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [streamActive, setStreamActive] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const video = videoRef.current;
    if (!video) return;

    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: "environment" } })
      .then((stream) => {
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        video.srcObject = stream;
        video.play();
        setStreamActive(true);
      })
      .catch(() => setStreamActive(false));

    return () => {
      cancelled = true;
      const stream = video.srcObject as MediaStream | null;
      stream?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  useEffect(() => {
    if (!streamActive || !onFrame || !videoRef.current) return;
    const id = setInterval(() => {
      if (videoRef.current) onFrame(videoRef.current);
    }, frameInterval);
    return () => clearInterval(id);
  }, [streamActive, onFrame, frameInterval]);

  return (
    <div className={`relative bg-black rounded-xl overflow-hidden ${className}`}>
      <video
        ref={videoRef}
        className="w-full h-full object-cover"
        autoPlay
        playsInline
        muted
      />

      {/* Card guide overlay */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div
          className={`w-[70%] aspect-[5/7] border-2 rounded-lg ${statusColors[status]} transition-colors duration-300`}
        >
          {/* Corner brackets */}
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
