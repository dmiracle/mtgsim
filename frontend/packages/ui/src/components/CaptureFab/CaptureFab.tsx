type CaptureFabProps = {
  onClick: () => void;
  badge?: number;
};

export function CaptureFab({ onClick, badge }: CaptureFabProps) {
  return (
    <button
      onClick={onClick}
      aria-label="Scan a card"
      className="group fixed bottom-6 right-6 z-40 flex items-center gap-2 rounded-full bg-accent text-white shadow-lg shadow-accent/25 transition-all duration-200 hover:bg-accent/90 hover:shadow-xl hover:shadow-accent/30 active:scale-95 sm:bottom-8 sm:right-8"
    >
      {/* Icon — always visible */}
      <span className="flex h-14 w-14 items-center justify-center sm:h-12 sm:w-12 sm:group-hover:w-auto sm:group-hover:pr-0">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
          className="h-6 w-6"
        >
          {/* Viewfinder / scan icon */}
          <path d="M2 7V2h5" />
          <path d="M17 2h5v5" />
          <path d="M22 17v5h-5" />
          <path d="M7 22H2v-5" />
          <circle cx="12" cy="12" r="3" />
          <line x1="12" y1="8" x2="12" y2="5" />
          <line x1="12" y1="19" x2="12" y2="16" />
          <line x1="8" y1="12" x2="5" y2="12" />
          <line x1="19" y1="12" x2="16" y2="12" />
        </svg>
      </span>

      {/* Label — visible on desktop hover */}
      <span className="hidden max-w-0 overflow-hidden whitespace-nowrap text-sm font-medium transition-all duration-200 sm:group-hover:inline sm:group-hover:max-w-24 sm:group-hover:pr-4">
        Scan
      </span>

      {/* Badge — recent scan count */}
      {badge != null && badge > 0 && (
        <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-white text-[10px] font-bold text-accent shadow">
          {badge > 9 ? "9+" : badge}
        </span>
      )}
    </button>
  );
}
