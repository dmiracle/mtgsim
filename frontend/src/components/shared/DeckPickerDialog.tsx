import { useState } from "react"
import { useAddCardToDeck, useCreateDeck, useUserDecks } from "../../hooks/useDecks"

interface Props {
  cardUuid: string
  onClose: () => void
}

export default function DeckPickerDialog({ cardUuid, onClose }: Props) {
  const { data: decks } = useUserDecks()
  const addCard = useAddCardToDeck()
  const createDeckMut = useCreateDeck()
  const [selectedDeck, setSelectedDeck] = useState<number | null>(null)
  const [board, setBoard] = useState("main")
  const [count, setCount] = useState(1)
  const [newDeckName, setNewDeckName] = useState("")
  const [status, setStatus] = useState<string | null>(null)

  async function handleAdd() {
    if (!selectedDeck) return
    try {
      await addCard.mutateAsync({ deckId: selectedDeck, card_uuid: cardUuid, count, board })
      setStatus("Added!")
      setTimeout(onClose, 800)
    } catch {
      setStatus("Error adding card")
    }
  }

  async function handleCreateDeck() {
    if (!newDeckName.trim()) return
    try {
      const deck = await createDeckMut.mutateAsync({ name: newDeckName.trim() })
      setSelectedDeck(deck.id)
      setNewDeckName("")
    } catch {
      setStatus("Error creating deck")
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-[var(--color-bg-secondary)] rounded-lg border border-[var(--color-border)] p-5 w-80 space-y-3" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-sm font-bold">Add to Deck</h3>

        <select
          value={selectedDeck ?? ""}
          onChange={(e) => setSelectedDeck(e.target.value ? Number(e.target.value) : null)}
          className="w-full px-2 py-1.5 text-sm rounded bg-[var(--color-bg-primary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          <option value="">Select deck...</option>
          {decks?.map((d) => (
            <option key={d.id} value={d.id}>{d.name} ({d.card_count})</option>
          ))}
        </select>

        <div className="flex gap-2 items-center">
          <input
            type="text"
            placeholder="New deck name..."
            value={newDeckName}
            onChange={(e) => setNewDeckName(e.target.value)}
            className="flex-1 px-2 py-1.5 text-sm rounded bg-[var(--color-bg-primary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
          />
          <button onClick={handleCreateDeck} className="px-2 py-1.5 text-xs rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:text-white">
            Create
          </button>
        </div>

        <div className="flex gap-2">
          <select
            value={board}
            onChange={(e) => setBoard(e.target.value)}
            className="flex-1 px-2 py-1.5 text-sm rounded bg-[var(--color-bg-primary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
          >
            <option value="main">Main Board</option>
            <option value="side">Sideboard</option>
            <option value="commander">Commander</option>
          </select>
          <input
            type="number"
            min={1}
            max={99}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
            className="w-16 px-2 py-1.5 text-sm rounded bg-[var(--color-bg-primary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
          />
        </div>

        <div className="flex gap-2 justify-end items-center">
          {status && <span className="text-xs text-[var(--color-text-secondary)]">{status}</span>}
          <button onClick={onClose} className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)]">
            Cancel
          </button>
          <button
            onClick={handleAdd}
            disabled={!selectedDeck || addCard.isPending}
            className="px-3 py-1.5 text-sm rounded bg-[var(--color-accent)] text-white disabled:opacity-40"
          >
            Add
          </button>
        </div>
      </div>
    </div>
  )
}
