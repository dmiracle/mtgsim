// Pairwise ranking: comparisons form a directed "beats" graph over card names.
// Re-ranking a pair overrides earlier results, so a cycle (A>B>C>A) can always be
// resolved by re-ranking the cards in it.

export interface Comparison {
  winner_name: string;
  loser_name: string;
}

export type Graph = Map<string, Set<string>>;

export interface Round {
  kind: "cycle" | "new" | "refine" | "done";
  names: string[];
}

export function buildGraph(names: string[], comparisons: Comparison[]): Graph {
  const pool = new Set(names);
  const latest = new Map<string, Comparison>();
  for (const c of comparisons) {
    if (pool.has(c.winner_name) && pool.has(c.loser_name)) {
      latest.set([c.winner_name, c.loser_name].sort().join("\u0000"), c);
    }
  }
  const graph: Graph = new Map(names.map((n) => [n, new Set<string>()]));
  for (const c of latest.values()) graph.get(c.winner_name)!.add(c.loser_name);
  return graph;
}

export function reaches(graph: Graph, from: string, to: string): boolean {
  const seen = new Set([from]);
  const stack = [from];
  while (stack.length) {
    for (const next of graph.get(stack.pop()!)!) {
      if (next === to) return true;
      if (!seen.has(next)) {
        seen.add(next);
        stack.push(next);
      }
    }
  }
  return false;
}

// Shortest cycle in the graph (BFS back to each start node), or null if it's acyclic.
export function shortestCycle(graph: Graph): string[] | null {
  let best: string[] | null = null;
  for (const start of graph.keys()) {
    const parent = new Map<string, string>([[start, start]]);
    const queue = [start];
    search: while (queue.length) {
      const node = queue.shift()!;
      for (const next of graph.get(node)!) {
        if (next === start) {
          const cycle = [node];
          while (cycle[0] !== start) cycle.unshift(parent.get(cycle[0])!);
          if (!best || cycle.length < best.length) best = cycle;
          break search;
        }
        if (!parent.has(next)) {
          parent.set(next, node);
          queue.push(next);
        }
      }
    }
    if (best?.length === 3) break;
  }
  return best;
}

function score(graph: Graph, name: string, losses: Map<string, number>): number {
  return graph.get(name)!.size - (losses.get(name) ?? 0);
}

// Best-first order: topological where possible, net wins break ties and cycles.
export function rankOrder(graph: Graph): string[] {
  const losses = new Map<string, number>();
  for (const beaten of graph.values()) for (const n of beaten) losses.set(n, (losses.get(n) ?? 0) + 1);
  const indegree = new Map(losses);
  const remaining = new Set(graph.keys());
  const byScore = (a: string, b: string) => score(graph, b, losses) - score(graph, a, losses) || a.localeCompare(b);
  const order: string[] = [];
  while (remaining.size) {
    const ready = [...remaining].filter((n) => !indegree.get(n));
    const next = (ready.length ? ready : [...remaining]).sort(byScore)[0];
    order.push(next);
    remaining.delete(next);
    for (const beaten of graph.get(next)!) indegree.set(beaten, (indegree.get(beaten) ?? 0) - 1);
  }
  return order;
}

// Adjacent pairs in the order whose relative ranking isn't implied by any comparison.
export function undeterminedPairs(graph: Graph, order: string[]): [string, string][] {
  const pairs: [string, string][] = [];
  for (let i = 0; i + 1 < order.length; i++) {
    if (!reaches(graph, order[i], order[i + 1])) pairs.push([order[i], order[i + 1]]);
  }
  return pairs;
}

function shuffle<T>(items: T[], random: () => number): T[] {
  const a = [...items];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function nextRound(graph: Graph, size = 4, random: () => number = Math.random): Round {
  const cycle = shortestCycle(graph);
  if (cycle) return { kind: "cycle", names: cycle.slice(0, size) };

  const touched = new Set<string>();
  for (const [winner, beaten] of graph) {
    if (beaten.size) touched.add(winner);
    for (const n of beaten) touched.add(n);
  }
  const unseen = [...graph.keys()].filter((n) => !touched.has(n));
  if (unseen.length && graph.size > 1) {
    const names = shuffle(unseen, random).slice(0, size);
    const fill = shuffle([...touched], random).slice(0, size - names.length);
    return { kind: "new", names: [...names, ...fill] };
  }

  const names: string[] = [];
  for (const pair of shuffle(undeterminedPairs(graph, rankOrder(graph)), random)) {
    for (const n of pair) if (names.length < size && !names.includes(n)) names.push(n);
    if (names.length >= size) break;
  }
  return names.length ? { kind: "refine", names } : { kind: "done", names: [] };
}

// Cards that sit on some cycle (a successor can reach back to them).
export function cycleMembers(graph: Graph): Set<string> {
  return new Set([...graph.keys()].filter((n) => [...graph.get(n)!].some((next) => reaches(graph, next, n))));
}
