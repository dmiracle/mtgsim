import type { Meta, StoryObj } from "@storybook/react-vite";
import { cards } from "../fixtures";
import { RankRound } from "./RankRound";

const meta: Meta<typeof RankRound> = {
  title: "Mobile/RankRound",
  component: RankRound,
  decorators: [(Story) => <div className="p-4"><Story /></div>],
  args: {
    submitting: false,
    onSubmit: (names: string[]) => alert(names.join(" > ")),
    onExclude: (name: string) => alert(`Excluded ${name}`),
  },
};
export default meta;
type Story = StoryObj<typeof RankRound>;

export const FourNewCards: Story = { args: { cards, kind: "new" } };
export const ResolveCycle: Story = { args: { cards: cards.slice(0, 3), kind: "cycle" } };
