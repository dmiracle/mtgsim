import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import { cards } from "../fixtures";
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
