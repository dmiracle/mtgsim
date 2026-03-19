import { useCallback, useSyncExternalStore } from "react"

const STORAGE_KEY = "mtg-pinned-cards"

let pinnedSet: Set<string> | null = null

function getPinned(): Set<string> {
  if (!pinnedSet) {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      pinnedSet = raw ? new Set(JSON.parse(raw)) : new Set()
    } catch {
      pinnedSet = new Set()
    }
  }
  return pinnedSet
}

function savePinned() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...getPinned()]))
}

const listeners = new Set<() => void>()
let snapshot = getPinned()

function subscribe(cb: () => void) {
  listeners.add(cb)
  return () => listeners.delete(cb)
}

function getSnapshot() {
  return snapshot
}

function notify() {
  snapshot = new Set(getPinned())
  listeners.forEach((cb) => cb())
}

export function usePinnedCards() {
  const pinned = useSyncExternalStore(subscribe, getSnapshot)

  const isPinned = useCallback((uuid: string) => pinned.has(uuid), [pinned])

  const togglePin = useCallback((uuid: string) => {
    const set = getPinned()
    if (set.has(uuid)) set.delete(uuid)
    else set.add(uuid)
    savePinned()
    notify()
  }, [])

  return { isPinned, togglePin, pinnedSet: pinned }
}
