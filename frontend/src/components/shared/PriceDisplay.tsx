export default function PriceDisplay({ price }: { price: number | null | undefined }) {
  if (price == null) return <span className="text-[var(--color-text-muted)]">--</span>
  const formatted = price >= 1000 ? `$${(price / 1000).toFixed(1)}k` : `$${price.toFixed(2)}`
  return <span className="text-green-400">{formatted}</span>
}
