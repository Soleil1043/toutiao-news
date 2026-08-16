# 新闻头条前端（Vue 3 + Vite）

> ⚠️ **本项目是后端 FastAPI 服务的配套前端，不能独立运行。**
> 所有新闻、用户、收藏、历史、AI 对话等数据接口均来自后端（`../toutiao_backend`）。使用前请先启动后端，否则前端仅能展示静态页面，无法登录或加载数据。

---

## 目录

- [1. 配套后端（必读）](#1-配套后端必读)
- [2. 技术栈](#2-技术栈)
- [3. 环境要求](#3-环境要求)
- [4. 快速开始](#4-快速开始)
- [5. 与后端联调](#5-与后端联调)
- [6. 项目结构](#6-项目结构)
- [7. 构建与部署](#7-构建与部署)

---

## 1. 配套后端（必读）

| 项目 | 位置 | 说明 |
| --- | --- | --- |
| **后端（FastAPI）** | `../toutiao_backend` | 本项目所有 API 的来源，必须先运行 |
| 前端（本仓库） | `toutiao_frontend/` | Vue 3 移动端前端 |

- 前端通过 `/api` 前缀调用后端接口（如 `/api/users/login`、`/api/news/list`、`/api/chat/stream`）。
- 后端默认监听 `http://127.0.0.1:8000`。
- 接口详细定义见后端 Swagger 文档（后端启动后访问 `http://127.0.0.1:8000/docs`）。
- 后端启动方式见 `../toutiao_backend/README.md`。

## 2. 技术栈

| 分类 | 选型 |
| --- | --- |
| 框架 | Vue 3（`<script setup>`） |
| 构建工具 | Vite |
| 状态管理 | Pinia + pinia-plugin-persistedstate（登录态 `user` store 持久化到 sessionStorage，其余 store 走 localStorage 默认） |
| UI 组件库 | Vant 4（移动端） |
| 路由 | vue-router 4 |
| 国际化 | vue-i18n（zh-CN / en-US） |
| HTTP 客户端 | axios |
| 内容渲染 | marked + DOMPurify（Markdown 渲染与安全过滤） |

## 3. 环境要求

- **Node.js 20.19+ 或 22.12+**（Vite 7 已不支持 Node 18）
- 包管理器：npm（或 pnpm/yarn）
- 一个**已启动的后端 FastAPI 服务**（见第 1 节）

## 4. 快速开始

```bash
# 1. 安装依赖
npm install

# 2. 启动开发服务器（默认 http://localhost:5173）
npm run dev

# 3. 生产构建
npm run build        # 产物输出到 dist/

# 4. 本地预览构建产物
npm run preview
```

> 开发模式下，前端通过 Vite 代理把 `/api` 转发到 `http://127.0.0.1:8000`（见 `vite.config.js`），**无需任何额外配置即可联调**。请确保后端已在该地址运行。

## 5. 与后端联调

- **请求地址**：`src/config/api.js` 中 `apiConfig.baseURL` 当前为**空字符串**，所有请求走同源相对路径 `/api/...`。
- **开发代理**：`vite.config.js` 将 `/api` 代理到 `http://127.0.0.1:8000`，避免跨域、无需硬编码后端地址。
- **认证**：登录成功后，token 通过 Pinia（`user` store，持久化到 `sessionStorage`）保存，并由 `src/api/request.js` 的请求拦截器在每次请求自动附带 `Authorization: Bearer <token>`。
- **失效处理**：响应拦截器捕获 `401` 后清空本地 token，并派发 `auth:unauthorized` 事件（`main.js` 监听后跳转登录页），实现统一登出。
- **AI 对话**：`/api/chat/stream` 为 SSE 流式接口，由后端代理转发大模型；前端按 `data: {...}` 行实时渲染（内容取 `choices[0].delta.content`），`data: [DONE]` 表示结束。

> 生产环境调整后端地址：可直接修改 `src/config/api.js` 的 `baseURL`（如 `https://your-api.com`），或在 Web 服务器配置反向代理将 `/api` 转发到后端（推荐，见第 7 节）。

## 6. 项目结构

```
toutiao_frontend/
├── index.html              # 入口 HTML
├── vite.config.js          # Vite 配置（/api 开发代理、生产清理 console）
├── package.json
│
├── src/
│   ├── main.js             # 应用入口：挂载 Pinia/VueRouter/i18n，监听 401
│   ├── App.vue
│   ├── style.css
│   │
│   ├── api/
│   │   └── request.js      # axios 实例 + 请求/响应拦截器（Bearer token、401 处理）
│   ├── config/
│   │   └── api.js          # baseURL 配置（开发留空走 /api 代理）
│   │
│   ├── store/              # Pinia 状态（user 登录态、theme 主题、language 语言、modules/）
│   │   ├── index.js  user.js  theme.js  language.js  modules/
│   │
│   ├── router/             # vue-router 路由（含登录守卫）
│   ├── i18n/               # vue-i18n 国际化资源（locales/zh-CN.js、en-US.js）
│   ├── views/              # 页面组件（登录/首页/详情/历史/收藏/AI对话/我的等）
│   ├── components/         # 通用组件
│   └── assets/             # 静态资源
│
└── dist/                   # 生产构建产物（npm run build 生成）
```

## 7. 构建与部署

1. `npm run build` 生成 `dist/`（构建时会自动清理 `console` / `debugger`，避免敏感日志泄露）。
2. 将 `dist/` 部署到任意静态服务器（Nginx、对象存储、CDN 等）。
3. **生产环境必须保证 `/api` 能到达后端**：
   - **方式一（推荐）**：在 Web 服务器配置反向代理，将 `/api` 转发到后端地址（如 `http://127.0.0.1:8000`），前端代码无需改动；
   - **方式二**：修改 `src/config/api.js` 的 `baseURL` 为后端地址（如 `https://your-api.com`），再重新 `npm run build`。
