import assert from "node:assert/strict";
import { test } from "node:test";
import { colorBreakdown, histogram, largestFirst } from "./stats.ts";

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

test("colors keep WUBRG order with gold and colorless last, skipping empty ones", () => {
  const buckets = colorBreakdown({ G: 2, C: 4, W: 3 }, 1);
  assert.deepEqual(buckets.map((b) => [b.label, b.count]), [
    ["White", 3],
    ["Green", 2],
    ["Gold", 1],
    ["Colorless", 4],
  ]);
});

test("no cards means no color buckets", () => {
  assert.deepEqual(colorBreakdown({}, 0), []);
});

test("types sort largest first", () => {
  assert.deepEqual(largestFirst({ Instant: 3, Creature: 10, Land: 1 }).map((b) => b.label), ["Creature", "Instant", "Land"]);
});
