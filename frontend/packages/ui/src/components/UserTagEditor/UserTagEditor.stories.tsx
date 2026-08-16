import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { UserTagEditor } from "./UserTagEditor";
import { userTags } from "@/fixtures";

const meta: Meta<typeof UserTagEditor> = {
  title: "UserData/UserTagEditor",
  component: UserTagEditor,
  tags: ["autodocs"],
  parameters: { layout: "padded" },
  args: {
    tags: ["removal", "wincon"],
    vocabulary: userTags,
    onAdd: fn(),
    onRemove: fn(),
  },
  decorators: [(Story) => <div className="bg-bg-primary p-4 max-w-md min-h-[300px]"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof UserTagEditor>;

export const Default: Story = {};

export const Empty: Story = {
  args: { tags: [] },
};

export const WithDefinitionEditing: Story = {
  args: { onSaveDefinition: fn() },
};

export const Interactive: Story = {
  render: () => {
    const [tags, setTags] = useState<string[]>(["removal"]);
    return (
      <UserTagEditor
        tags={tags}
        vocabulary={userTags}
        onAdd={(tag) => setTags((prev) => [...prev, tag])}
        onRemove={(tag) => setTags((prev) => prev.filter((t) => t !== tag))}
        onSaveDefinition={(tag, description) => console.log("save definition", tag, description)}
      />
    );
  },
};
