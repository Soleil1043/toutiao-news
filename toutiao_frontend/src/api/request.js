import axios from 'axios'
import { apiConfig } from '../config/api'

// 统一请求实例：baseURL 由环境变量驱动（见 src/config/api.js）
const request = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: 10000,
})

// 使用模块级变量保存 token，避免与 user store 形成循环依赖
let authToken = ''

export function setAuthToken(token) {
  authToken = token || ''
}

export function clearAuthToken() {
  authToken = ''
}

// 请求拦截器：自动注入 Authorization
request.interceptors.request.use(
  (config) => {
    if (authToken) {
      config.headers.Authorization = `Bearer ${authToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一处理 401（token 失效）
request.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // 清空本地 token，并通知应用跳转登录页（由 main.js 监听处理，避免与 router 形成循环依赖）
      clearAuthToken()
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }
    return Promise.reject(error)
  }
)

export default request
