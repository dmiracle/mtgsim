import type { ReactNode } from "react";

type StudyFeedProps = {
  collection?: string;
  onBack: () => void;
  children: ReactNode;
};

function formatName(name: string) {
  return name.replace(/_/g, " ");
}

export function StudyFeed({ collection, onBack, children }: StudyFeedProps) {
  return (
    <div className="max-w-lg mx-auto px-4 py-4 min-h-screen">
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={onBack}
          className="text-xs text-text-muted hover:text-accent transition-colors"
        >
          <i
            className="ms ms-ability-transform mr-1"
            style={{ transform: "scaleX(-1)", display: "inline-block" }}
          />
          Collections
        </button>
        {collection && (
          <span className="text-[10px] uppercase tracking-widest text-text-muted">
            {formatName(collection)}
          </span>
        )}
      </div>
      {children}
    </div>
  );
}

export function StudyFeedEmpty({ onBack }: { onBack: () => void }) {
  return (
    <div className="max-w-lg mx-auto px-4 min-h-screen flex flex-col items-center justify-center space-y-4">
      <i className="ms ms-ability-adventure text-5xl text-success" />
      <h2 className="text-xl font-bold text-text-primary">All caught up!</h2>
      <p className="text-sm text-text-muted">No more cards due for review.</p>
      <button
        onClick={onBack}
        className="text-sm font-medium px-4 py-2 rounded-lg bg-accent text-white hover:bg-accent/80 transition-colors"
      >
        Back to Collections
      </button>
    </div>
  );
}

export function StudyFeedLoading() {
  return (
    <div className="max-w-lg mx-auto px-4 min-h-screen flex items-center justify-center text-text-muted">
      Loading...
    </div>
  );
}
