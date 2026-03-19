export default function SetIcon({ code, name, rarity }: { code: string; name?: string; rarity?: string }) {
  const rarityClass = rarity ? ` ss-${rarity.toLowerCase()}` : ""
  return (
    <i
      className={`ss ss-${code.toLowerCase()}${rarityClass}`}
      title={name || code.toUpperCase()}
    />
  )
}
