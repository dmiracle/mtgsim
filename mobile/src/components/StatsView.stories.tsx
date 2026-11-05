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

export const WithGold: StoryObj<typeof StatsView> = {
  args: {
    stats: {
      ...cardStats,
      total: 110,
      color_distribution: { U: 24, G: 24, B: 24, R: 24, W: 24, C: 10 },
      multicolor_count: 20,
    },
  },
};

export const NoCreatures: StoryObj<typeof StatsView> = {
  args: {
    stats: {
      total: 3,
      mana_curve: { "1": 1, "2": 2 },
      color_distribution: { U: 2, R: 1 },
      multicolor_count: 0,
      type_distribution: { Instant: 2, Sorcery: 1 },
      power_distribution: {},
      toughness_distribution: {},
    },
  },
};
