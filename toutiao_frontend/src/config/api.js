/**
 * API配置文件
 *
 * baseURL 留空时走相对路径 /api：
 * - 开发环境由 vite.config.js 的 proxy 转发到 http://127.0.0.1:8000
 * - 生产环境由同源反向代理转发
 *
 * 注意：DeepSeek 调用已由后端 /api/chat/stream 接管（密钥存放于后端 .env），
 * 前端不再需要也严禁硬编码 API Key。
 */

// API基础URL配置
export const apiConfig = {
  // 生产可设为 https://your-api.com
  // 本地直连后端可设为 http://127.0.0.1:8000
  // 留空则使用同源 /api（开发依赖 vite.config.js 的 proxy 配置，生产依赖反向代理）
  baseURL: ''
}
