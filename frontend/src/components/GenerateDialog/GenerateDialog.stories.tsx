import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { GenerateDialog } from "./GenerateDialog";
import { setSummaries } from "@/fixtures";

const meta: Meta<typeof GenerateDialog> = {
  title: "Flashcards/GenerateDialog",
  component: GenerateDialog,
  tags: ["autodocs"],
  args: { onGenerate: fn(), onClose: fn() },
  parameters: { layout: "fullscreen" },
};

export default meta;
type Story = StoryObj<typeof GenerateDialog>;

export const Default: Story = {
  args: { sets: setSummaries },
};

export const Generating: Story = {
  args: { sets: setSummaries, generating: true },
};

export const WithResult: Story = {
  args: {
    sets: setSummaries,
    result: { created: 52, collection: "keywords_keyword_abilities" },
  },
};
