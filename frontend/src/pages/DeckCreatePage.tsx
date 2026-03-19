import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useCreateDeck } from "../hooks/useDecks"

export default function DeckCreatePage() {
  const navigate = useNavigate()
  const createDeck = useCreateDeck()
  const [name, setName] = useState("")
  const [format, setFormat] = useState("")
  const [description, setDescription] = useState("")

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    await createDeck.mutateAsync({
      name: name.trim(),
      format: format || null,
      description: description || null,
    })
    navigate("/decks")
  }

  return (
    <div className="max-w-md space-y-4">
      <h1 className="text-xl font-bold">Create Deck</h1>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-sm text-[var(--color-text-secondary)] mb-1">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full px-3 py-2 rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
          />
        </div>
        <div>
          <label className="block text-sm text-[var(--color-text-secondary)] mb-1">Format</label>
          <input
            type="text"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            placeholder="e.g. standard, commander..."
            className="w-full px-3 py-2 rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)]"
          />
        </div>
        <div>
          <label className="block text-sm text-[var(--color-text-secondary)] mb-1">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] resize-none"
          />
        </div>
        <div className="flex gap-2">
          <button
            type="submit"
            disabled={createDeck.isPending || !name.trim()}
            className="px-4 py-2 rounded bg-[var(--color-accent)] text-white disabled:opacity-40"
          >
            {createDeck.isPending ? "Creating..." : "Create Deck"}
          </button>
          <button type="button" onClick={() => navigate("/decks")} className="px-4 py-2 rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)]">
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
