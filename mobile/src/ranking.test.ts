import assert from "node:assert/strict";
import { test } from "node:test";
import { buildGraph, cycleMembers, nextRound, rankOrder, shortestCycle, undeterminedPairs } from "./ranking.ts";

const beat = (winner_name: string, loser_name: string) => ({ winner_name, loser_name });
const round = (...names: string[]) => names.flatMap((w, i) => names.slice(i + 1).map((l) => beat(w, l)));

test("a ranked round fully orders its cards", () => {
  const graph = buildGraph(["A", "B", "C", "D"], round("C", "A", "D", "B"));
  assert.deepEqual(rankOrder(graph), ["C", "A", "D", "B"]);
  assert.deepEqual(undeterminedPairs(graph, rankOrder(graph)), []);
  assert.equal(nextRound(graph).kind, "done");
});

test("the latest comparison of a pair wins", () => {
  const graph = buildGraph(["A", "B"], [beat("A", "B"), beat("B", "A")]);
  assert.deepEqual(rankOrder(graph), ["B", "A"]);
});

test("a cycle across rounds is detected and served as the next round", () => {
  const graph = buildGraph(["A", "B", "C", "D"], [beat("A", "B"), beat("B", "C"), beat("C", "A"), beat("D", "A")]);
  const cycle = shortestCycle(graph)!;
  assert.deepEqual([...cycle].sort(), ["A", "B", "C"]);
  assert.deepEqual([...cycleMembers(graph)].sort(), ["A", "B", "C"]);
  const next = nextRound(graph);
  assert.equal(next.kind, "cycle");
  assert.deepEqual([...next.names].sort(), ["A", "B", "C"]);
});

test("re-ranking the cycle resolves it", () => {
  const history = [beat("A", "B"), beat("B", "C"), beat("C", "A"), ...round("B", "A", "C")];
  const graph = buildGraph(["A", "B", "C"], history);
  assert.equal(shortestCycle(graph), null);
  assert.deepEqual(rankOrder(graph), ["B", "A", "C"]);
});

test("unranked cards come first, then undetermined neighbours, until done", () => {
  const names = ["A", "B", "C", "D", "E", "F", "G", "H", "I"];
  const truth = [...names].reverse();
  let comparisons: { winner_name: string; loser_name: string }[] = [];
  let rounds = 0;
  for (;;) {
    const next = nextRound(buildGraph(names, comparisons));
    if (next.kind === "done") break;
    assert.notEqual(next.kind, "cycle");
    if (rounds < 2) assert.equal(next.kind, "new");
    const ordered = [...next.names].sort((a, b) => truth.indexOf(a) - truth.indexOf(b));
    comparisons = [...comparisons, ...round(...ordered)];
    assert.ok(++rounds < 50);
  }
  assert.deepEqual(rankOrder(buildGraph(names, comparisons)), truth);
});

test("comparisons outside the pool are ignored", () => {
  const graph = buildGraph(["A", "B"], [beat("A", "Z"), beat("Z", "B")]);
  assert.equal(nextRound(graph).kind, "new");
});
