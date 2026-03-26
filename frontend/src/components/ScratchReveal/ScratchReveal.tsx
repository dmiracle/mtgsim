import { useRef, useEffect, useState } from "react";

export type ScratchMask = {
  width: number;
  height: number;
  data: Uint8Array; // 1 bit per pixel packed into bytes
};

type ScratchRevealProps = {
  imageUrl: string;
  blurAmount?: number;
  brushSize?: number;
  onRevealChange?: (percentage: number, mask: ScratchMask) => void;
};

export function ScratchReveal({
  imageUrl,
  blurAmount = 20,
  brushSize = 40,
  onRevealChange,
}: ScratchRevealProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const drawingRef = useRef(false);
  const [revealed, setRevealed] = useState(false);
  const [percentage, setPercentage] = useState(0);

  // Fill canvas with semi-transparent frost overlay
  useEffect(() => {
    function init() {
      const canvas = canvasRef.current;
      const container = containerRef.current;
      if (!canvas || !container) return;
      const rect = container.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      // Frost overlay — matches theme bg
      ctx.fillStyle = "rgba(15, 23, 42, 0.92)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      // Set composite mode for erasing
      ctx.globalCompositeOperation = "destination-out";
    }
    init();
    setRevealed(false);
    setPercentage(0);
    window.addEventListener("resize", init);
    return () => window.removeEventListener("resize", init);
  }, [imageUrl]);

  function getPos(e: React.MouseEvent | React.TouchEvent): { x: number; y: number } | null {
    const canvas = canvasRef.current;
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    if ("touches" in e) {
      const touch = e.touches[0];
      if (!touch) return null;
      return { x: touch.clientX - rect.left, y: touch.clientY - rect.top };
    }
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  }

  function scratch(pos: { x: number; y: number }) {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    // Erase the frost overlay to reveal the image underneath
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, brushSize / 2, 0, Math.PI * 2);
    ctx.fill();
  }

  function calculatePercentage() {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const prevOp = ctx.globalCompositeOperation;
    ctx.globalCompositeOperation = "source-over";
    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    ctx.globalCompositeOperation = prevOp;

    const pixels = imgData.data;
    // Sample every 4th pixel for percentage (performance)
    let cleared = 0;
    const sampleStep = 16;
    for (let i = 3; i < pixels.length; i += sampleStep) {
      if (pixels[i] === 0) cleared++;
    }
    const total = pixels.length / sampleStep;
    const pct = Math.round((cleared / total) * 100);

    // Build packed 1-bit mask: 1 = scratched (alpha === 0), 0 = covered
    const totalPixels = canvas.width * canvas.height;
    const maskBytes = new Uint8Array(Math.ceil(totalPixels / 8));
    for (let p = 0; p < totalPixels; p++) {
      const alpha = pixels[p * 4 + 3];
      if (alpha === 0) {
        maskBytes[p >> 3] |= 1 << (7 - (p & 7));
      }
    }

    const mask: ScratchMask = {
      width: canvas.width,
      height: canvas.height,
      data: maskBytes,
    };

    setPercentage(pct);
    onRevealChange?.(pct, mask);
  }

  function handleStart(e: React.MouseEvent | React.TouchEvent) {
    e.preventDefault();
    drawingRef.current = true;
    const pos = getPos(e);
    if (pos) scratch(pos);
  }

  function handleMove(e: React.MouseEvent | React.TouchEvent) {
    if (!drawingRef.current) return;
    e.preventDefault();
    const pos = getPos(e);
    if (pos) scratch(pos);
  }

  function handleEnd() {
    drawingRef.current = false;
    calculatePercentage();
  }

  function revealAll() {
    const canvas = canvasRef.current;
    setRevealed(true);
    setPercentage(100);
    const w = canvas?.width ?? 1;
    const h = canvas?.height ?? 1;
    const totalPixels = w * h;
    const fullMask = new Uint8Array(Math.ceil(totalPixels / 8));
    fullMask.fill(0xFF);
    onRevealChange?.(100, { width: w, height: h, data: fullMask });
  }

  return (
    <div className="space-y-2">
      <div
        ref={containerRef}
        className="relative aspect-[5/7] rounded-lg overflow-hidden select-none touch-none bg-bg-tertiary"
      >
        {/* Sharp image underneath everything */}
        <img
          src={imageUrl}
          alt=""
          className="absolute inset-0 w-full h-full object-cover"
        />

        {/* Canvas frost overlay — scratching erases it to reveal image */}
        {!revealed && (
          <canvas
            ref={canvasRef}
            className="absolute inset-0 w-full h-full cursor-crosshair"
            onMouseDown={handleStart}
            onMouseMove={handleMove}
            onMouseUp={handleEnd}
            onMouseLeave={handleEnd}
            onTouchStart={handleStart}
            onTouchMove={handleMove}
            onTouchEnd={handleEnd}
          />
        )}
      </div>

      <div className="flex items-center justify-between">
        <span className="text-xs text-text-muted tabular-nums">{percentage}% revealed</span>
        {!revealed && (
          <button
            onClick={revealAll}
            className="text-xs px-3 py-1 rounded border border-border text-text-muted hover:text-text-secondary hover:border-border-hover transition-colors"
          >
            Reveal All
          </button>
        )}
      </div>
    </div>
  );
}
