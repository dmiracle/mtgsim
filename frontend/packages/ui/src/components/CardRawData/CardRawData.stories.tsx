import type { Meta, StoryObj } from "@storybook/react-vite";
import { CardRawData } from "./CardRawData";
import { cardDetail } from "@/fixtures";

const meta: Meta<typeof CardRawData> = {
  title: "CardDetail/CardRawData",
  component: CardRawData,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-lg"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CardRawData>;

export const Default: Story = {
  args: {
    uuid: cardDetail.uuid,
    data: cardDetail as unknown as Record<string, unknown>,
  },
};
