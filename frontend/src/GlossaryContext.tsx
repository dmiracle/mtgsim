import { createContext, useCallback, useContext, useState, type ReactNode } from "react"

interface GlossaryState {
  isOpen: boolean
  open: () => void
  close: () => void
  toggle: () => void
}

const GlossaryContext = createContext<GlossaryState>({
  isOpen: false,
  open: () => {},
  close: () => {},
  toggle: () => {},
})

export function GlossaryProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)
  const open = useCallback(() => setIsOpen(true), [])
  const close = useCallback(() => setIsOpen(false), [])
  const toggle = useCallback(() => setIsOpen((v) => !v), [])
  return (
    <GlossaryContext.Provider value={{ isOpen, open, close, toggle }}>
      {children}
    </GlossaryContext.Provider>
  )
}

export function useGlossary() {
  return useContext(GlossaryContext)
}
