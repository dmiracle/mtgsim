import type { Meta, StoryObj } from "@storybook/react-vite";
import { ManaSymbols } from "./ManaSymbols";

const meta: Meta<typeof ManaSymbols> = {
  title: "Shared/ManaSymbols",
  component: ManaSymbols,
  tags: ["autodocs"],
  argTypes: {
    size: { control: "radio", options: ["sm", "md", "lg"] },
  },
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-8 text-2xl">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof ManaSymbols>;

export const SingleRed: Story = {
  args: { cost: "{R}" },
};

export const MultiColor: Story = {
  args: { cost: "{2}{W}{U}" },
};

export const AllFiveColors: Story = {
  args: { cost: "{W}{U}{B}{R}{G}" },
};

export const HighGeneric: Story = {
  args: { cost: "{7}{G}{G}" },
};

export const Colorless: Story = {
  args: { cost: "{3}" },
};

export const WithX: Story = {
  args: { cost: "{X}{R}{R}" },
};

export const HybridMana: Story = {
  args: { cost: "{W/U}{W/U}{W/U}" },
};

export const PhyrexianMana: Story = {
  args: { cost: "{W/P}{U/P}{B/P}" },
};

export const SnowMana: Story = {
  args: { cost: "{S}{S}{S}" },
};

export const SmallSize: Story = {
  args: { cost: "{2}{W}{U}", size: "sm" },
};

export const LargeSize: Story = {
  args: { cost: "{2}{W}{U}", size: "lg" },
};

export const NoShadow: Story = {
  args: { cost: "{B}{R}{G}", shadow: false },
};

export const ComplexCost: Story = {
  args: { cost: "{X}{X}{U}{U}{B}{B}" },
};

export const Empty: Story = {
  args: { cost: "" },
};
