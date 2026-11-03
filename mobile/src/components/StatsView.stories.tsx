import type { Meta, StoryObj } from "@storybook/react-vite";
import { cardStats } from "../fixtures";
import { StatsView } from "./StatsView";

const meta: Meta<typeof StatsView> = {
  title: "Mobile/StatsView",
  component: StatsView,
  decorators: [(Story) => <div className="p-4"><Story /></div>],
};
export default meta;

export const StarTrekCommons: StoryObj<typeof StatsView> = { args: { stats: cardStats } };

export const NoCreatures: StoryObj<typeof StatsView> = {
  args: {
    stats: {
      total: 3,
      mana_curve: { "1": 1, "2": 2 },
      type_distribution: { Instant: 2, Sorcery: 1 },
      power_distribution: {},
      toughness_distribution: {},
    },
  },
};
