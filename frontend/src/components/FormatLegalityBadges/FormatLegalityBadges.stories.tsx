import type { Meta, StoryObj } from "@storybook/react-vite";
import { FormatLegalityBadges } from "./FormatLegalityBadges";

const meta: Meta<typeof FormatLegalityBadges> = {
  title: "Shared/FormatLegalityBadges",
  component: FormatLegalityBadges,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6 max-w-xl">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof FormatLegalityBadges>;

export const MixedLegality: Story = {
  args: {
    legalities: {
      standard: "not_legal",
      pioneer: "not_legal",
      modern: "legal",
      legacy: "legal",
      vintage: "legal",
      commander: "legal",
      brawl: "not_legal",
      historic: "not_legal",
      pauper: "legal",
    },
  },
};

export const AllLegal: Story = {
  args: {
    legalities: {
      standard: "legal",
      pioneer: "legal",
      modern: "legal",
      legacy: "legal",
      vintage: "legal",
      commander: "legal",
    },
  },
};

export const WithBanned: Story = {
  args: {
    legalities: {
      standard: "banned",
      modern: "banned",
      legacy: "legal",
      vintage: "restricted",
      commander: "legal",
      pioneer: "not_legal",
    },
  },
};

export const AllNotLegal: Story = {
  args: {
    legalities: {
      standard: "not_legal",
      pioneer: "not_legal",
      modern: "not_legal",
      legacy: "not_legal",
    },
  },
};
