import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import { GradeBar } from "./GradeBar";

const meta: Meta<typeof GradeBar> = { title: "Mobile/GradeBar", component: GradeBar };
export default meta;

export const Interactive: StoryObj = {
  render: () => {
    const [grade, setGrade] = useState<string | undefined>("B+");
    return (
      <div className="p-4">
        <GradeBar grade={grade} onGrade={(t) => setGrade(t ?? undefined)} />
      </div>
    );
  },
};
