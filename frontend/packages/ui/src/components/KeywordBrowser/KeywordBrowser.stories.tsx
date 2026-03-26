import type { Meta, StoryObj } from "@storybook/react-vite";
import { KeywordBrowser } from "./KeywordBrowser";
import { keywordsResponse } from "@/fixtures";

const meta: Meta<typeof KeywordBrowser> = {
  title: "Reference/KeywordBrowser",
  component: KeywordBrowser,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-2xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof KeywordBrowser>;

export const Default: Story = {
  args: { keywords: keywordsResponse },
};
