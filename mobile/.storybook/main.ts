import type { StorybookConfig } from '@storybook/react-vite';

const config: StorybookConfig = {
  stories: ['../src/**/*.stories.@(ts|tsx)'],
  framework: '@storybook/react-vite',
  // The PWA plugin from vite.config.ts would try to precache Storybook's own bundles.
  viteFinal: (config) => ({
    ...config,
    plugins: config.plugins?.flat().filter((p) => !(p && 'name' in p && p.name.startsWith('vite-plugin-pwa'))),
  }),
};
export default config;
