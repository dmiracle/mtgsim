import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { Pagination } from "./Pagination";

const meta: Meta<typeof Pagination> = {
  title: "Shared/Pagination",
  component: Pagination,
  tags: ["autodocs"],
  args: { onPageChange: fn() },
};

export default meta;
type Story = StoryObj<typeof Pagination>;

export const FirstPage: Story = {
  args: { page: 1, pages: 10, total: 500, limit: 50 },
};

export const MiddlePage: Story = {
  args: { page: 5, pages: 10, total: 500, limit: 50 },
};

export const LastPage: Story = {
  args: { page: 10, pages: 10, total: 500, limit: 50 },
};

export const FewPages: Story = {
  args: { page: 2, pages: 3, total: 150, limit: 50 },
};

export const SinglePage: Story = {
  args: { page: 1, pages: 1, total: 25, limit: 50 },
};

export const ManyPages: Story = {
  args: { page: 50, pages: 200, total: 10000, limit: 50 },
};
