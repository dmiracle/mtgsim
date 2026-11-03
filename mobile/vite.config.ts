import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { VitePWA } from 'vite-plugin-pwa';
import { execSync } from 'node:child_process';

// Shown in the app's top bar so a phone can tell which build it is running;
// "+" marks a build with uncommitted changes.
const git = (cmd: string) => execSync(`git ${cmd}`).toString().trim();
const commit = git('rev-parse --short HEAD') + (git('status --porcelain --untracked-files=no') ? '+' : '');

export default defineConfig({
  define: { __COMMIT__: JSON.stringify(commit) },
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      devOptions: { enabled: true },
      // Cloudflare Access gates the manifest too, and browsers omit cookies for it by default.
      useCredentials: true,
      includeAssets: ['icon.svg', 'apple-touch-icon.png'],
      manifest: {
        name: 'MTGSim Card Review',
        short_name: 'Card Review',
        description: 'Review Magic cards one at a time, filtered and sorted your way.',
        theme_color: '#111318',
        background_color: '#111318',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        navigateFallbackDenylist: [/^\/api/],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/cards\.scryfall\.io\//,
            handler: 'CacheFirst',
            options: {
              cacheName: 'card-images',
              expiration: { maxEntries: 2000, maxAgeSeconds: 60 * 60 * 24 * 30 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          {
            urlPattern: /\/api\//,
            handler: 'NetworkFirst',
            options: { cacheName: 'api', expiration: { maxEntries: 300 } },
          },
        ],
      },
    }),
  ],
  server: {
    port: 5175,
    host: '0.0.0.0',
    allowedHosts: [
      'deltron.tail4ca9d8.ts.net',
      'dylans-macbook-pro-2.tail4ca9d8.ts.net',
      'iphone-15.tail4ca9d8.ts.net',
      'macbookpro.tail4ca9d8.ts.net',
    ],
    proxy: {
      '/api': { target: process.env.API_URL ?? 'http://0.0.0.0:8001', changeOrigin: true },
    },
  },
});
