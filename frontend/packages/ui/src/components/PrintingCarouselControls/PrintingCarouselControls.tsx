type PrintingCarouselControlsProps = {
  index: number;
  count: number;
  onPrev: () => void;
  onNext: () => void;
};

const arrowClass =
  "absolute top-1/2 -translate-y-1/2 w-6 h-10 flex items-center justify-center rounded bg-black/50 text-white " +
  "opacity-0 group-hover:opacity-100 focus-visible:opacity-100 pointer-coarse:opacity-100 " +
  "hover:bg-black/70 transition-opacity";

export function PrintingCarouselControls({ index, count, onPrev, onNext }: PrintingCarouselControlsProps) {
  return (
    <>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onPrev();
        }}
        className={`${arrowClass} left-1`}
        title="Previous printing"
      >
        ‹
      </button>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onNext();
        }}
        className={`${arrowClass} right-1`}
        title="Next printing"
      >
        ›
      </button>
      <span
        className="absolute bottom-1 left-1/2 -translate-x-1/2 px-1.5 py-0.5 rounded bg-black/50 text-white text-[10px] font-medium tabular-nums opacity-0 group-hover:opacity-100 pointer-coarse:opacity-100 transition-opacity"
        onClick={(e) => e.stopPropagation()}
      >
        {index + 1} / {count}
      </span>
    </>
  );
}
