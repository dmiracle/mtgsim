type PaginationProps = {
  page: number;
  pages: number;
  total: number;
  limit: number;
  onPageChange: (page: number) => void;
};

export function Pagination({ page, pages, total, limit, onPageChange }: PaginationProps) {
  if (pages <= 1) return null;

  const start = (page - 1) * limit + 1;
  const end = Math.min(page * limit, total);

  function getPageNumbers(): (number | "...")[] {
    const result: (number | "...")[] = [];
    if (pages <= 7) {
      for (let i = 1; i <= pages; i++) result.push(i);
      return result;
    }
    result.push(1);
    if (page > 3) result.push("...");
    for (let i = Math.max(2, page - 1); i <= Math.min(pages - 1, page + 1); i++) {
      result.push(i);
    }
    if (page < pages - 2) result.push("...");
    result.push(pages);
    return result;
  }

  const btnBase = "px-3 py-1.5 text-sm rounded border";
  const btnActive = "bg-accent border-accent text-white";
  const btnInactive = "bg-bg-secondary border-border text-text-secondary hover:bg-bg-tertiary hover:border-border-hover";
  const btnDisabled = "bg-bg-secondary border-border text-text-muted cursor-not-allowed";

  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-sm text-text-muted">
        {start}–{end} of {total.toLocaleString()}
      </span>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className={`${btnBase} ${page <= 1 ? btnDisabled : btnInactive}`}
        >
          Prev
        </button>
        {getPageNumbers().map((p, i) =>
          p === "..." ? (
            <span key={`ellipsis-${i}`} className="px-2 text-text-muted">...</span>
          ) : (
            <button
              key={p}
              onClick={() => onPageChange(p)}
              className={`${btnBase} ${p === page ? btnActive : btnInactive}`}
            >
              {p}
            </button>
          )
        )}
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= pages}
          className={`${btnBase} ${page >= pages ? btnDisabled : btnInactive}`}
        >
          Next
        </button>
      </div>
    </div>
  );
}
