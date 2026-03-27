import type { Meta, StoryObj } from "@storybook/react";
import { StudyFeed, StudyFeedEmpty, StudyFeedLoading } from "./StudyFeed";

const meta: Meta<typeof StudyFeed> = {
  title: "App-v2/StudyFeed",
  component: StudyFeed,
};
export default meta;

type Story = StoryObj<typeof StudyFeed>;

export const WithCard: Story = {
  args: {
    collection: "card_oracle_FIN",
    onBack: () => console.log("Back"),
    children: (
      <div className="bg-bg-secondary border border-border rounded-xl p-8 text-center text-text-muted text-sm">
        FlashcardCard renders here
      </div>
    ),
  },
};

export const NoCollection: Story = {
  args: {
    onBack: () => console.log("Back"),
    children: (
      <div className="bg-bg-secondary border border-border rounded-xl p-8 text-center text-text-muted text-sm">
        Studying all due cards
      </div>
    ),
  },
};

export const AllCaughtUp: Story = {
  render: () => <StudyFeedEmpty onBack={() => console.log("Back")} />,
};

export const Loading: Story = {
  render: () => <StudyFeedLoading />,
};
