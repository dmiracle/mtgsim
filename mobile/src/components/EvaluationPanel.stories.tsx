import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import type { Scores } from "../types";
import { EvaluationPanel } from "./EvaluationPanel";

const meta: Meta<typeof EvaluationPanel> = { title: "Mobile/EvaluationPanel", component: EvaluationPanel };
export default meta;

function Interactive({ initial }: { initial: Scores }) {
  const [scores, setScores] = useState(initial);
  return (
    <div className="p-4">
      <EvaluationPanel scores={scores} onRate={(s, n) => setScores({ ...scores, [s]: n })} />
    </div>
  );
}

export const Unrated: StoryObj = {
  render: () => <Interactive initial={{ developing: null, parity: null, behind: null, ahead: null }} />,
};

export const RemovalSpell: StoryObj = {
  render: () => <Interactive initial={{ developing: 3, parity: 4, behind: 5, ahead: 2 }} />,
};
