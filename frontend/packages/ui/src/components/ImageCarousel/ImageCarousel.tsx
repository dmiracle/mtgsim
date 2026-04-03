import { useState, useEffect } from "react";

type ImageItem = {
  url: string;
  label?: string;
};

type ImageCarouselProps = {
  images: ImageItem[];
  maxHeight?: string;
};

export function ImageCarousel({ images, maxHeight = "480px" }: ImageCarouselProps) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    setIndex(0);
  }, [images]);

  if (images.length === 0) return null;

  const current = images[index];
  const hasMultiple = images.length > 1;

  function prev() {
    setIndex((i) => (i === 0 ? images.length - 1 : i - 1));
  }

  function next() {
    setIndex((i) => (i === images.length - 1 ? 0 : i + 1));
  }

  return (
    <div className="relative">
      <div className="flex justify-center bg-bg-tertiary p-4">
        <img
          src={current.url}
          alt={current.label ?? ""}
          className="rounded-lg object-contain"
          style={{ maxHeight }}
        />
      </div>

      {hasMultiple && (
        <>
          <button
            onClick={prev}
            className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-bg-primary/80 border border-border text-text-secondary hover:text-accent hover:border-accent flex items-center justify-center transition-colors"
          >
            <span className="text-sm">&#x25C0;</span>
          </button>
          <button
            onClick={next}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-bg-primary/80 border border-border text-text-secondary hover:text-accent hover:border-accent flex items-center justify-center transition-colors"
          >
            <span className="text-sm">&#x25B6;</span>
          </button>

          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-bg-primary/80 rounded-full px-3 py-1">
            {current.label && (
              <span className="text-[10px] uppercase tracking-wider text-text-muted font-semibold">
                {current.label}
              </span>
            )}
            <span className="text-[10px] text-text-muted tabular-nums">
              {index + 1}/{images.length}
            </span>
          </div>
        </>
      )}
    </div>
  );
}
