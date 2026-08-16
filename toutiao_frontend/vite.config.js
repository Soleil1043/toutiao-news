import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // 开发环境：将 /api 代理到本地后端，避免跨域与硬编码地址
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // 生产构建清理调试日志，避免 console 泄露（含 token 存在性打印）
    esbuild: {
      drop: ['console', 'debugger'],
    },
  },
})
