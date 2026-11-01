import assert from "node:assert/strict";
import { test } from "node:test";
import { histogram, largestFirst } from "./stats.ts";

test("fills gaps from zero and merges values at the cap", () => {
  assert.deepEqual(histogram({ "1": 2, "3": 1, "7": 1, "9": 2 }, 7), [
    { label: "0", count: 0 },
    { label: "1", count: 2 },
    { label: "2", count: 0 },
    { label: "3", count: 1 },
    { label: "4", count: 0 },
    { label: "5", count: 0 },
    { label: "6", count: 0 },
    { label: "7+", count: 3 },
  ]);
});

test("keeps negative values and puts star values last", () => {
  assert.deepEqual(histogram({ "*": 1, "-1": 1, "1": 2, "1+*": 1 }, 7), [
    { label: "-1", count: 1 },
    { label: "0", count: 0 },
    { label: "1", count: 2 },
    { label: "*", count: 1 },
    { label: "1+*", count: 1 },
  ]);
});

test("empty distribution has no buckets", () => {
  assert.deepEqual(histogram({}, 7), []);
});

test("types sort largest first", () => {
  assert.deepEqual(largestFirst({ Instant: 3, Creature: 10, Land: 1 }).map((b) => b.label), ["Creature", "Instant", "Land"]);
});
