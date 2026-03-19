import { useReducer, useState } from "react"
import { Link } from "react-router-dom"
import ManaSymbols from "../components/shared/ManaSymbols"
import SetIcon from "../components/shared/SetIcon"
import { useOpenPacks } from "../hooks/useBoosters"
import { useAllSets } from "../hooks/useSets"
import type { BoosterPack } from "../types/booster"

interface DraftState {
  packs: BoosterPack[]
  currentIndex: number
}

type DraftAction =
  | { type: "add_packs"; packs: BoosterPack[] }
  | { type: "select_pack"; index: number }

function draftReducer(state: DraftState, action: DraftAction): DraftState {
  switch (action.type) {
    case "add_packs":
      return {
        packs: [...state.packs, ...action.packs],
        currentIndex: state.packs.length,
      }
    case "select_pack":
      return { ...state, currentIndex: action.index }
  }
}

const PACK_COUNTS = [1, 3, 6, 12, 24, 36]
const BOOSTER_TYPES = [
  { value: "", label: "Auto-detect" },
  { value: "play", label: "Play Booster" },
  { value: "draft", label: "Draft Booster" },
]

export default function DraftPage() {
  const { data: allSets } = useAllSets()
  const openPacks = useOpenPacks()
  const [setCode, setSetCode] = useState("")
  const [packCount, setPackCount] = useState(6)
  const [boosterType, setBoosterType] = useState("")
  const [setSearch, setSetSearch] = useState("")
  const [state, dispatch] = useReducer(draftReducer, { packs: [], currentIndex: -1 })

  const filteredSets = allSets?.filter(
    (s) =>
      s.name.toLowerCase().includes(setSearch.toLowerCase()) ||
      s.code.toLowerCase().includes(setSearch.toLowerCase()),
  )

  async function handleOpen() {
    if (!setCode) return
    const packs = await openPacks.mutateAsync({
      setCode,
      count: packCount,
      type: boosterType || undefined,
    })
    dispatch({ type: "add_packs", packs })
  }

  const currentPack = state.currentIndex >= 0 ? state.packs[state.currentIndex] : null

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Draft Simulator</h1>

      <div className="flex flex-wrap gap-3 items-end">
        <div>
          <label className="block text-xs text-[var(--color-text-secondary)] mb-1">Set</label>
          <div className="relative">
            <input
              type="text"
              placeholder="Search sets..."
              value={setSearch}
              onChange={(e) => setSetSearch(e.target.value)}
              className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] w-56"
            />
            {setSearch && filteredSets && filteredSets.length > 0 && (
              <div className="absolute z-10 mt-1 w-full max-h-48 overflow-y-auto bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded shadow-lg">
                {filteredSets.slice(0, 20).map((s) => (
                  <button
                    key={s.code}
                    onClick={() => {
                      setSetCode(s.code)
                      setSetSearch(s.name)
                    }}
                    className="w-full text-left px-3 py-1.5 text-sm hover:bg-[var(--color-bg-tertiary)] flex items-center gap-2"
                  >
                    <SetIcon code={s.keyrune_code || s.code} name={s.name} />
                    <span className="truncate">{s.name}</span>
                    <span className="text-[var(--color-text-muted)] ml-auto">{s.code.toUpperCase()}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
          {setCode && <div className="text-xs text-[var(--color-accent)] mt-0.5">{setCode.toUpperCase()}</div>}
        </div>

        <div>
          <label className="block text-xs text-[var(--color-text-secondary)] mb-1">Booster Type</label>
          <select
            value={boosterType}
            onChange={(e) => setBoosterType(e.target.value)}
            className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
          >
            {BOOSTER_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs text-[var(--color-text-secondary)] mb-1">Packs</label>
          <select
            value={packCount}
            onChange={(e) => setPackCount(Number(e.target.value))}
            className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
          >
            {PACK_COUNTS.map((c) => (
              <option key={c} value={c}>
                {c} {c === 6 ? "(sealed)" : c === 24 ? "(box)" : c === 36 ? "(box)" : ""}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleOpen}
          disabled={!setCode || openPacks.isPending}
          className="px-4 py-1.5 text-sm rounded bg-[var(--color-accent)] text-white disabled:opacity-40"
        >
          {openPacks.isPending ? "Opening..." : "Open Packs"}
        </button>
      </div>

      <div className="flex gap-4">
        {/* Pack History */}
        {state.packs.length > 0 && (
          <div className="w-48 shrink-0 space-y-1">
            <h2 className="text-sm font-bold">Pack History</h2>
            {state.packs.map((pack, i) => {
              const rare = pack.cards.find((c) => c.rarity === "mythic" || c.rarity === "rare")
              return (
                <button
                  key={i}
                  onClick={() => dispatch({ type: "select_pack", index: i })}
                  className={`w-full text-left px-2 py-1.5 text-xs rounded ${
                    i === state.currentIndex
                      ? "bg-[var(--color-accent)] text-white"
                      : "bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)]"
                  }`}
                >
                  <div className="truncate">Pack {i + 1}</div>
                  {rare && <div className="truncate text-[10px] opacity-80">{rare.name}</div>}
                </button>
              )
            })}
          </div>
        )}

        {/* Current Pack */}
        {currentPack && (
          <div className="flex-1">
            <h2 className="text-sm font-bold mb-2">
              {currentPack.set_name} — {currentPack.booster_type}
            </h2>
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
              {currentPack.cards.map((card) => (
                <Link
                  key={card.uuid + card.slot}
                  to={`/cards/${card.uuid}`}
                  className="bg-[var(--color-bg-secondary)] rounded border border-[var(--color-border)] overflow-hidden hover:border-[var(--color-accent)] transition-colors"
                >
                  {card.image_url ? (
                    <img src={card.image_url} alt={card.name} loading="lazy" className="w-full aspect-[488/680] object-cover" />
                  ) : (
                    <div className="w-full aspect-[488/680] bg-[var(--color-bg-tertiary)] flex items-center justify-center text-[var(--color-text-muted)] text-xs p-1 text-center">
                      {card.name}
                    </div>
                  )}
                  <div className="p-1.5">
                    <div className="text-xs font-medium truncate">
                      {card.is_foil && <span className="text-yellow-400 mr-1">F</span>}
                      {card.name}
                    </div>
                    <div className="flex items-center justify-between text-[10px] text-[var(--color-text-muted)]">
                      <span className="capitalize">{card.rarity}</span>
                      <ManaSymbols cost={card.mana_cost} />
                    </div>
                    <div className="text-[10px] text-[var(--color-text-muted)]">{card.slot}</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {state.packs.length === 0 && (
          <div className="flex-1 text-center py-12 text-[var(--color-text-muted)]">
            Select a set and open packs to start drafting
          </div>
        )}
      </div>
    </div>
  )
}
