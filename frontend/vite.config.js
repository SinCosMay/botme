import { defineConfig } from 'vite'

const backendTarget = process.env.VITE_BACKEND_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  server: {
    proxy: {
      '/v1': {
        target: backendTarget,
        changeOrigin: true,
      },
    },
  },
})
