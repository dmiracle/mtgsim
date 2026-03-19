import type { Pagination } from "../../types/common"

interface Props {
  pagination: Pagination
  onPageChange: (page: number) => void
}

export default function PaginationBar({ pagination, onPageChange }: Props) {
  const { page, pages, total } = pagination
  if (pages <= 1) return null

  return (
    <div className="flex items-center justify-between py-3">
      <span className="text-sm text-[var(--color-text-secondary)]">
        {total} results — page {page} of {pages}
      </span>
      <div className="flex gap-2">
        <button
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          className="px-3 py-1 text-sm rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-primary)] disabled:opacity-40 hover:bg-[var(--color-accent)] transition-colors"
        >
          Prev
        </button>
        <button
          disabled={page >= pages}
          onClick={() => onPageChange(page + 1)}
          className="px-3 py-1 text-sm rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-primary)] disabled:opacity-40 hover:bg-[var(--color-accent)] transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  )
}
