import type { Meta, StoryObj } from "@storybook/react";
import { ImageCarousel } from "./ImageCarousel";

const meta: Meta<typeof ImageCarousel> = {
  title: "App-v2/ImageCarousel",
  component: ImageCarousel,
  decorators: [
    (Story) => (
      <div className="max-w-[400px] mx-auto bg-bg-secondary rounded-xl overflow-hidden">
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof ImageCarousel>;

export const SingleImage: Story = {
  args: {
    images: [
      { url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg", label: "M10" },
    ],
  },
};

export const MultiplePrintings: Story = {
  args: {
    images: [
      { url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg", label: "M10" },
      { url: "https://cards.scryfall.io/normal/front/1/9/1920dae4-fb92-4f19-ae4b-eb3276b8571e.jpg", label: "M11" },
      { url: "https://cards.scryfall.io/normal/front/6/9/69daba76-96e8-4bcc-ab79-2f00189ad8fb.jpg", label: "MH3" },
    ],
  },
};

export const NoImages: Story = {
  args: {
    images: [],
  },
};
