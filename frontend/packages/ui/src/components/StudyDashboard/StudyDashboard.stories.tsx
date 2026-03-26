import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { StudyDashboard } from "./StudyDashboard";
import { flashcardStats } from "@/fixtures/flashcards";

const meta: Meta<typeof StudyDashboard> = {
  title: "Flashcards/StudyDashboard",
  component: StudyDashboard,
  tags: ["autodocs"],
  args: { onStudyAll: fn(), onStudyCollections: fn(), onDeleteCollection: fn(), onGenerate: fn() },
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-2xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof StudyDashboard>;

export const Default: Story = {
  args: { stats: flashcardStats },
};

export const Empty: Story = {
  args: {
    stats: { total_cards: 0, cards_due: 0, cards_new: 0, reviews_today: 0, collections: [] },
  },
};

export const NoDue: Story = {
  args: {
    stats: { ...flashcardStats, cards_due: 0 },
  },
};
