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
