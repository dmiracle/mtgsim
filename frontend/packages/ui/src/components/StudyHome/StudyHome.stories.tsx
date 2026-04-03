import type { Meta, StoryObj } from "@storybook/react";
import { StudyHome } from "./StudyHome";

const meta: Meta<typeof StudyHome> = {
  title: "Flashcards/StudyHome",
  component: StudyHome,
};
export default meta;

type Story = StoryObj<typeof StudyHome>;

export const Default: Story = {
  args: {
    modes: [
      {
        key: "flashcards",
        label: "Flashcard Study",
        description: "SRS-scheduled review from your collections",
        iconClass: "ms ms-flashback",
        badge: 42,
      },
      {
        key: "recall",
        label: "Card Recall",
        description: "Pick sets and test your card knowledge",
        iconClass: "ms ms-creature",
      },
    ],
    onSelect: (key) => console.log("Selected:", key),
  },
};

export const SingleMode: Story = {
  args: {
    modes: [
      {
        key: "flashcards",
        label: "Flashcard Study",
        description: "SRS-scheduled review from your collections",
        iconClass: "ms ms-flashback",
        badge: 12,
      },
    ],
    onSelect: (key) => console.log("Selected:", key),
  },
};

export const NoDue: Story = {
  args: {
    modes: [
      {
        key: "flashcards",
        label: "Flashcard Study",
        description: "SRS-scheduled review from your collections",
        iconClass: "ms ms-flashback",
        badge: 0,
      },
    ],
    onSelect: (key) => console.log("Selected:", key),
  },
};
