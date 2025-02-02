import path from 'path';
import { NodeGlobalsPolyfillPlugin } from '@esbuild-plugins/node-globals-polyfill';
import replace from '@rollup/plugin-replace';
import react from '@vitejs/plugin-react';
import rollupNodePolyFill from 'rollup-plugin-polyfill-node';
import { defineConfig } from 'vite';
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons';

const alias = {
  '@': '/src',
};

export default defineConfig({
  plugins: [
    react(),
    replace({
      preventAssignment: true,
      __buildVersion: () => JSON.stringify(new Date()),
    }),
    createSvgIconsPlugin({
      // Specify the icon folder to be cached
      iconDirs: [path.resolve(process.cwd(), 'src/icons')],
      // Specify symbolId format
      symbolId: 'icon-[dir]-[name]',
    }),
  ],

  resolve: {
    alias,
  },
  build: {
    rollupOptions: {
      plugins: [rollupNodePolyFill()],
    },
    assetsInlineLimit: 1024,
  },
  optimizeDeps: {
    esbuildOptions: {
      target: 'esnext',
      define: {
        global: 'globalThis',
      },
      supported: {
        bigint: true,
      },
      plugins: [
        NodeGlobalsPolyfillPlugin({
          buffer: true,
          process: true,
        }),
      ],
    },
  },

  server: {
    host: '0.0.0.0',
    port: 8080,
    proxy: {
      '/api': {
        target: 'https://c2a.puppy9.com',
        changeOrigin: true,
        cookiePathRewrite: {
          '*': '/',
        },
      },
    },
    watch: {
      usePolling: true,
    },
  },
});
