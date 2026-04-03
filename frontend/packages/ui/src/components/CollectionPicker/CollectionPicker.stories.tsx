import type { Meta, StoryObj } from "@storybook/react";
import { CollectionPicker } from "./CollectionPicker";

const meta: Meta<typeof CollectionPicker> = {
  title: "Flashcards/CollectionPicker",
  component: CollectionPicker,
};
export default meta;

type Story = StoryObj<typeof CollectionPicker>;

const sampleCollections = [
  { id: 1, name: "card_oracle_FIN", card_count: 120 },
  { id: 2, name: "card_mana_cost_FIN", card_count: 120 },
  { id: 3, name: "card_stats_FIN", card_count: 45 },
  { id: 4, name: "keywords_keyword_abilities", card_count: 87 },
  { id: 5, name: "card_oracle_MKM", card_count: 200 },
];

export const WithCollections: Story = {
  args: {
    collections: sampleCollections,
    dueCount: 42,
    onStudyAll: () => console.log("Study all"),
    onStudyCollection: (name) => console.log("Study:", name),
    onBack: () => console.log("Back"),
  },
};

export const Empty: Story = {
  args: {
    collections: [],
    dueCount: 0,
    onStudyAll: () => console.log("Study all"),
    onStudyCollection: (name) => console.log("Study:", name),
    onBack: () => console.log("Back"),
  },
};

export const NoDue: Story = {
  args: {
    collections: sampleCollections,
    dueCount: 0,
    onStudyAll: () => console.log("Study all"),
    onStudyCollection: (name) => console.log("Study:", name),
  },
};
