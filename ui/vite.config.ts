import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: Number(process.env.INTELLI_UI_PORT || 3000),
    proxy: {
      '/api': {
        target: process.env.INTELLI_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
