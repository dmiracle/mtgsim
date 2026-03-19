const MANA_RE = /\{([^}]+)\}/g

function symbolClass(sym: string): string {
  const s = sym.toLowerCase().replace("/", "")
  return `ms ms-${s} ms-cost`
}

export default function ManaSymbols({ cost }: { cost: string | null }) {
  if (!cost) return null
  const parts: React.ReactNode[] = []
  let last = 0
  let match: RegExpExecArray | null
  const re = new RegExp(MANA_RE)
  while ((match = re.exec(cost)) !== null) {
    if (match.index > last) {
      parts.push(cost.slice(last, match.index))
    }
    parts.push(<i key={match.index} className={symbolClass(match[1])} title={match[1]} />)
    last = re.lastIndex
  }
  if (last < cost.length) parts.push(cost.slice(last))
  return <span className="inline-flex items-center gap-0.5">{parts}</span>
}
