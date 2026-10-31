import type { Preview } from '@storybook/react-vite';
import '../src/index.css';

const preview: Preview = {
  parameters: { layout: 'fullscreen', viewport: { defaultViewport: 'mobile1' } },
  decorators: [(Story) => <div className="min-h-dvh bg-bg text-fg"><Story /></div>],
};
export default preview;
