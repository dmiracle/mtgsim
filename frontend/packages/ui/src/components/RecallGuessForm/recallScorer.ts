import type { FlashcardAnswer } from "@/types/flashcards";
import type { RecallGuess } from "./RecallGuessForm";

export type AspectScore = "green" | "yellow" | "red";

export type RecallScore = {
  mana_cost: AspectScore;
  type_line: AspectScore;
  power_toughness: AspectScore;
  oracle_text: AspectScore;
};

export function scoreRecallGuess(guess: RecallGuess, answer: FlashcardAnswer): RecallScore {
  return {
    mana_cost: scoreManaCost(guess.manaCost, answer.mana_cost, answer.mana_value),
    type_line: scoreTypeLine(guess.typeLine, answer.type_line),
    power_toughness: scoreStats(guess.power, guess.toughness, answer.power, answer.toughness),
    oracle_text: scoreOracleText(guess.oracleText, answer.oracle_text),
  };
}

function normalizeManaCost(cost: string): string {
  // Extract symbols, sort colors, normalize
  const symbols = cost.match(/\{([^}]+)\}/g) ?? [];
  return symbols.map((s) => s.replace(/[{}]/g, "").toUpperCase()).sort().join(",");
}

function computeManaValue(cost: string): number {
  const symbols = cost.match(/\{([^}]+)\}/g) ?? [];
  let total = 0;
  for (const raw of symbols) {
    const sym = raw.replace(/[{}]/g, "").toUpperCase();
    const num = parseInt(sym);
    if (!isNaN(num)) total += num;
    else if (sym === "X") total += 0;
    else total += 1; // Each colored or hybrid symbol counts as 1
  }
  return total;
}

function scoreManaCost(guess: string, actual?: string, actualMV?: number): AspectScore {
  if (!guess && !actual) return "green";
  if (!guess || !actual) return "red";

  // Exact match
  if (normalizeManaCost(guess) === normalizeManaCost(actual)) return "green";

  // Same mana value but different cost
  const guessMV = computeManaValue(guess);
  const answerMV = actualMV ?? computeManaValue(actual);
  if (guessMV === answerMV) return "yellow";

  return "red";
}

function normalizeType(line: string): string[] {
  return line
    .replace(/—/g, " ")
    .split(/\s+/)
    .map((w) => w.toLowerCase().trim())
    .filter(Boolean);
}

function scoreTypeLine(guess: string, actual?: string): AspectScore {
  if (!guess && !actual) return "green";
  if (!guess || !actual) return "red";

  const guessWords = normalizeType(guess);
  const actualWords = normalizeType(actual);

  // Exact match (same words regardless of order)
  if (guessWords.sort().join(" ") === actualWords.sort().join(" ")) return "green";

  // Check overlap — how many actual words did they get?
  const matched = actualWords.filter((w) => guessWords.includes(w)).length;
  if (matched === actualWords.length) return "green";
  if (matched > 0) return "yellow";

  return "red";
}

function scoreStats(
  guessPower: string,
  guessToughness: string,
  actualPower?: string,
  actualToughness?: string,
): AspectScore {
  // No stats on actual card — any guess is fine
  if (!actualPower && !actualToughness) return "green";

  const pMatch = guessPower.trim() === (actualPower ?? "").trim();
  const tMatch = guessToughness.trim() === (actualToughness ?? "").trim();

  if (pMatch && tMatch) return "green";
  if (pMatch || tMatch) return "yellow";
  return "red";
}

function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .replace(/[.,;:!?'"(){}\[\]]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function scoreOracleText(guess: string, actual?: string): AspectScore {
  if (!guess && !actual) return "green";
  if (!guess || !actual) return "red";

  const normGuess = normalizeText(guess);
  const normActual = normalizeText(actual);

  if (normGuess === normActual) return "green";

  // Word overlap scoring
  const guessWords = new Set(normGuess.split(" "));
  const actualWords = normActual.split(" ");
  const matched = actualWords.filter((w) => guessWords.has(w)).length;
  const ratio = matched / actualWords.length;

  if (ratio >= 0.7) return "green";
  if (ratio >= 0.3) return "yellow";
  return "red";
}
