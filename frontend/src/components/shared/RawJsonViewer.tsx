import { useState } from "react"

interface Props {
  data: unknown
  label?: string
}

export default function RawJsonViewer({ data, label = "Raw JSON" }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <div className="border border-[var(--color-border)] rounded overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full px-3 py-2 text-sm text-left bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
      >
        {open ? "▼" : "▶"} {label}
      </button>
      {open && (
        <pre className="p-3 text-xs overflow-auto max-h-96 bg-[var(--color-bg-primary)] text-green-400">
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  )
}
