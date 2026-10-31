import type { Meta, StoryObj } from "@storybook/react-vite";
import { cards } from "../fixtures";
import { RankingResults } from "./RankingResults";

const meta: Meta<typeof RankingResults> = {
  title: "Mobile/RankingResults",
  component: RankingResults,
  decorators: [(Story) => <div className="p-4"><Story /></div>],
};
export default meta;

export const Mixed: StoryObj<typeof RankingResults> = {
  args: {
    rows: [
      { card: cards[2], inCycle: false, undetermined: false },
      { card: cards[0], inCycle: true, undetermined: false },
      { card: cards[1], inCycle: true, undetermined: true },
      { card: cards[3], inCycle: false, undetermined: false },
    ],
  },
};
