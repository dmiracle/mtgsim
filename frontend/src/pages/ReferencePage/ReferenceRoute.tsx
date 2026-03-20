import { useKeywords } from "@/api/hooks";
import { ReferencePage } from "./ReferencePage";
import { keywordsResponse as fallback } from "@/fixtures";

const glossary = [
  { term: "Battlefield", definition: "The zone where permanents exist.", category: "Zone" },
  { term: "Commander", definition: "A 100-card singleton format led by a legendary creature.", category: "Format" },
  { term: "Creature", definition: "A card type representing beings that can attack and block.", category: "Card Type" },
  { term: "Exile", definition: "A zone for cards removed from the game.", category: "Zone" },
  { term: "Graveyard", definition: "A player's discard pile.", category: "Zone" },
  { term: "Instant", definition: "A card type that can be cast at any time you have priority.", category: "Card Type" },
  { term: "Modern", definition: "A constructed format using cards from Eighth Edition forward.", category: "Format" },
  { term: "Standard", definition: "A rotating constructed format using the most recent sets.", category: "Format" },
];

export function ReferenceRoute() {
  const { data: keywords } = useKeywords();
  return <ReferencePage keywords={keywords ?? fallback} glossary={glossary} />;
}
