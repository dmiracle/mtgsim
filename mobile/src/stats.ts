export interface Bucket {
  label: string;
  count: number;
}

// Integer keys become one bar per value from the lowest to `cap` (empty values
// included, so gaps in the curve show), with everything at or above `cap`
// merged into "cap+". Non-integer keys such as "*" or "1+*" go last.
export function histogram(dist: Record<string, number>, cap: number): Bucket[] {
  const counts = new Map<number, number>();
  const other: Bucket[] = [];
  for (const [key, count] of Object.entries(dist)) {
    const n = Number(key);
    if (key === "" || !Number.isInteger(n)) other.push({ label: key, count });
    else counts.set(Math.min(n, cap), (counts.get(Math.min(n, cap)) ?? 0) + count);
  }
  if (counts.size === 0) return other;
  const values = [...counts.keys()];
  const buckets: Bucket[] = [];
  for (let n = Math.min(0, ...values); n <= Math.max(...values); n++) {
    buckets.push({ label: n === cap ? `${cap}+` : String(n), count: counts.get(n) ?? 0 });
  }
  return [...buckets, ...other];
}

export function largestFirst(dist: Record<string, number>): Bucket[] {
  return Object.entries(dist)
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count);
}
