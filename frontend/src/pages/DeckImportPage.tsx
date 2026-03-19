import { useCallback, useState } from "react"
import { Link } from "react-router-dom"
import { useImportDeck } from "../hooks/useDecks"
import type { DeckImportResult } from "../types/deck"

export default function DeckImportPage() {
  const importDeck = useImportDeck()
  const [text, setText] = useState("")
  const [name, setName] = useState("")
  const [result, setResult] = useState<DeckImportResult | null>(null)

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (!file) return
    if (!name) setName(file.name.replace(/\.(txt|dec|dek)$/i, ""))
    const reader = new FileReader()
    reader.onload = () => setText(reader.result as string)
    reader.readAsText(file)
  }, [name])

  async function handleImport(e: React.FormEvent) {
    e.preventDefault()
    if (!text.trim() || !name.trim()) return
    const res = await importDeck.mutateAsync({ text, name: name.trim() })
    setResult(res)
  }

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!name) setName(file.name.replace(/\.(txt|dec|dek)$/i, ""))
    const reader = new FileReader()
    reader.onload = () => setText(reader.result as string)
    reader.readAsText(file)
  }, [name])

  if (result) {
    const exact = result.resolved.filter((r) => r.match_type === "exact")
    const fuzzy = result.resolved.filter((r) => r.match_type === "fuzzy")
    const created = result.resolved.filter((r) => r.match_type === "created")

    return (
      <div className="max-w-lg space-y-4">
        <h1 className="text-xl font-bold">Import Results</h1>
        <div className="text-sm">
          <span className="text-[var(--color-text-secondary)]">{result.deck_name}</span> — {result.total_cards} cards
        </div>

        {exact.length > 0 && (
          <div>
            <h2 className="text-sm font-bold text-green-400 mb-1">Exact Matches ({exact.length})</h2>
            {exact.map((r, i) => (
              <div key={i} className="text-sm text-[var(--color-text-secondary)]">{r.count}x {r.name}</div>
            ))}
          </div>
        )}
        {fuzzy.length > 0 && (
          <div>
            <h2 className="text-sm font-bold text-yellow-400 mb-1">Fuzzy Matches ({fuzzy.length})</h2>
            {fuzzy.map((r, i) => (
              <div key={i} className="text-sm text-[var(--color-text-secondary)]">
                {r.count}x {r.name} → {r.matched_name} ({Math.round(r.match_score * 100)}%)
              </div>
            ))}
          </div>
        )}
        {created.length > 0 && (
          <div>
            <h2 className="text-sm font-bold text-red-400 mb-1">Unresolved ({created.length})</h2>
            {created.map((r, i) => (
              <div key={i} className="text-sm text-[var(--color-text-secondary)]">{r.count}x {r.name} (placeholder)</div>
            ))}
          </div>
        )}

        <div>
          <h2 className="text-sm font-bold mb-1">Legality</h2>
          <div className="flex flex-wrap gap-1">
            {result.legality.map((l) => (
              <span
                key={l.format}
                className={`px-2 py-0.5 text-xs rounded ${
                  l.legal ? "bg-green-900/40 text-green-400" : "bg-red-900/40 text-red-400"
                }`}
                title={l.reason || undefined}
              >
                {l.format}
              </span>
            ))}
          </div>
        </div>

        <Link
          to={`/decks/${result.deck_id}`}
          className="inline-block px-4 py-2 rounded bg-[var(--color-accent)] text-white"
        >
          View Deck
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-lg space-y-4">
      <h1 className="text-xl font-bold">Import Deck</h1>
      <form onSubmit={handleImport} className="space-y-3">
        <div>
          <label className="block text-sm text-[var(--color-text-secondary)] mb-1">Deck Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full px-3 py-2 rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
          />
        </div>
        <div>
          <label className="block text-sm text-[var(--color-text-secondary)] mb-1">MTGA Export Text</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            rows={12}
            required
            placeholder="Paste MTGA export text or drag a .txt/.dec/.dek file here..."
            className="w-full px-3 py-2 rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] resize-none font-mono text-sm"
          />
        </div>
        <div className="flex gap-2 items-center">
          <button
            type="submit"
            disabled={importDeck.isPending || !text.trim() || !name.trim()}
            className="px-4 py-2 rounded bg-[var(--color-accent)] text-white disabled:opacity-40"
          >
            {importDeck.isPending ? "Importing..." : "Import"}
          </button>
          <label className="px-3 py-2 rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] cursor-pointer text-sm">
            Browse File
            <input type="file" accept=".txt,.dec,.dek" onChange={handleFileInput} className="hidden" />
          </label>
        </div>
      </form>
    </div>
  )
}
