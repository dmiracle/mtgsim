import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import { cards } from "../fixtures";
import type { Scores } from "../types";
import { ReviewScreen } from "./ReviewScreen";

const meta: Meta<typeof ReviewScreen> = { title: "Mobile/ReviewScreen", component: ReviewScreen };
export default meta;

export const Swipeable: StoryObj = {
  render: () => {
    const [index, setIndex] = useState(0);
    return (
      <ReviewScreen
        card={cards[index]}
        index={index}
        total={cards.length}
        summary="TRK · common · W · Mana value ↑"
        onSeek={setIndex}
        onExit={() => {}}
      />
    );
  },
};

export const Loading: StoryObj = {
  render: () => <ReviewScreen card={undefined} index={40} total={120} summary="TRK" onSeek={() => {}} onExit={() => {}} />,
};

export const NoMatches: StoryObj = {
  render: () => <ReviewScreen card={undefined} index={0} total={0} summary="TRK · mythic · price ≥ $500" onSeek={() => {}} onExit={() => {}} />,
};

export const Grading: StoryObj = {
  render: () => {
    const [index, setIndex] = useState(0);
    const [grades, setGrades] = useState<Record<string, string>>({ [cards[1].name]: "B+" });
    const card = cards[index];
    return (
      <ReviewScreen
        card={card}
        index={index}
        total={cards.length}
        summary="TRK · common · W · Collector # ↑"
        onSeek={setIndex}
        onExit={() => {}}
        grading={{
          listName: "TRK draft",
          grade: grades[card.name],
          onGrade: (tier) => {
            setGrades((g) => ({ ...g, [card.name]: tier ?? "" }));
            if (tier && index < cards.length - 1) setIndex(index + 1);
          },
        }}
      />
    );
  },
};

const UNRATED: Scores = { developing: null, parity: null, behind: null, ahead: null };

export const Evaluating: StoryObj = {
  render: () => {
    const [index, setIndex] = useState(0);
    const [scores, setScores] = useState<Record<string, Scores>>({
      [cards[0].name]: { developing: 2, parity: 3, behind: 1, ahead: 4 },
    });
    const card = cards[index];
    const current = scores[card.name] ?? UNRATED;
    return (
      <ReviewScreen
        card={card}
        index={index}
        total={cards.length}
        summary="TRK · common · W · Collector # ↑"
        onSeek={setIndex}
        onExit={() => {}}
        evaluating={{
          setName: "TRK draft",
          scores: current,
          onRate: (situation, stars) => setScores({ ...scores, [card.name]: { ...current, [situation]: stars } }),
        }}
      />
    );
  },
};
