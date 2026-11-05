import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import { QuickTags } from "./QuickTags";

const meta: Meta<typeof QuickTags> = { title: "Mobile/QuickTags", component: QuickTags };
export default meta;

export const Interactive: StoryObj = {
  render: () => {
    const [tags, setTags] = useState(["removal"]);
    return (
      <div className="p-4">
        <QuickTags
          tags={tags}
          onToggle={(tag) => setTags(tags.includes(tag) ? tags.filter((t) => t !== tag) : [...tags, tag])}
        />
      </div>
    );
  },
};
