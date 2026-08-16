# AI 掘金头条新闻系统（toutiao-news）

[![Docker Build & Smoke Test](https://github.com/Soleil1043/toutiao-news/actions/workflows/docker.yml/badge.svg)](https://github.com/Soleil1043/toutiao-news/actions/workflows/docker.yml)

前后端分离的新闻资讯平台：后端 FastAPI 提供 RESTful API 与 SSE 流式 AI 对话接口，前端 Vue 3 移动端，覆盖用户、新闻、收藏、浏览历史与 AI 问答的完整业务闭环。

## 功能特性

- **用户系统**：注册 / 登录 / 个人信息 / 修改密码，自建 Token 表 + Bearer 鉴权，密码 bcrypt 加盐哈希
- **新闻模块**：分类、分页列表、详情（浏览量 +1）、相关新闻推荐
- **收藏与历史**：收藏 / 取消 / 列表 / 清空；浏览历史记录 / 删除 / 清空
- **AI 对话**：httpx 流式转发 DeepSeek，SSE 流式返回（打字机效果），登录鉴权，密钥仅存后端 `.env`
- **缓存**：Redis Cache-Aside（旁路缓存）三级缓存，故障静默降级不影响主流程

## 技术栈

| 分类 | 选型 |
| --- | --- |
| Web 框架 | FastAPI + Pydantic v2 |
| ORM | SQLAlchemy 2.0（异步 `async`）+ aiomysql |
| 数据库 | MySQL 8 |
| 缓存 | Redis（`redis.asyncio`） |
| AI 调用 | httpx（流式转发 OpenAI 兼容接口） |
| 前端 | Vue 3 + Vite 7 + Vant 4 + Pinia + vue-router |
| 容器化 | Dockerfile + Docker Compose（编排后端 / MySQL / Redis） |
| CI/CD | GitHub Actions（push 自动构建镜像 + compose 起服务 + 接口冒烟测试） |
| 依赖管理 | uv（后端）/ npm（前端） |

## 项目结构

```
toutiao-news/
├── .github/workflows/       # GitHub Actions CI（构建 + 冒烟测试）
├── toutiao_backend/          # FastAPI 后端
│   ├── main.py               # 应用入口（CORS、路由挂载、异常处理器）
│   ├── Dockerfile            # 后端镜像（uv 官方镜像）
│   ├── docker-compose.yml    # MySQL + Redis + 后端 编排
│   ├── .dockerignore         # 排除 .env / .venv 进镜像
│   ├── routers/              # 路由层（users / news / favorite / history / chat）
│   ├── schemas/              # Pydantic 请求/响应模型
│   ├── models/               # SQLAlchemy ORM 模型（8 张表）
│   ├── crud/                 # 数据访问层
│   ├── cache/                # Redis 缓存封装
│   ├── config/               # 配置（.env 读取：DB / Redis / AI）
│   ├── utils/                # 工具（鉴权、响应封装、异常处理）
│   └── database.sql          # 数据库初始化脚本
└── toutiao_frontend/         # Vue 3 前端
    └── src/                  # 页面、路由、状态管理、i18n
```

## 快速开始

### 环境要求

- Python 3.12+、Node.js 20.19+ / 22.12+、MySQL 8、Redis、uv

### 后端

```bash
cd toutiao_backend
uv sync                     # 安装依赖并创建 .venv
cp .env.example .env        # 配置 OPENAI_*/DB_*/REDIS_* 凭据
mysql -uroot -p < database.sql   # 初始化数据库（可重复执行）
uv run python -m uvicorn main:app --reload   # 启动（Git Bash 需 python -m 方式）
```

- Swagger 接口文档：http://127.0.0.1:8000/docs

### 前端

```bash
cd toutiao_frontend
npm install
npm run dev                 # http://localhost:5173，/api 代理到后端 8000
```

### Docker 一键启动（可选，不需要本地装 MySQL/Redis/Python）

```bash
cd toutiao_backend
docker compose up -d --build    # 拉起 MySQL(3307) + Redis(6380) + 后端(8000)
docker compose ps               # 查看三服务状态
```

- 首次启动自动执行 `database.sql` 建表；宿主机端口 3307/6380 避开本机已运行的 MySQL(3306)/Redis(6379)
- 停止：`docker compose down`（数据卷保留）；彻底清理：`docker compose down -v`

## 持续集成（CI）

GitHub Actions 工作流（`.github/workflows/docker.yml`）在每次 push 到 main 时自动：

1. 校验 `docker compose config`
2. 构建后端镜像（Dockerfile）
3. compose 起 MySQL / Redis / 后端 三服务
4. 接口冒烟测试：健康检查 → 分类接口（MySQL+Redis 链路）→ 注册接口（建表+加密+token）

可在 [Actions 页面](https://github.com/Soleil1043/toutiao-news/actions) 查看运行结果。

## 接口一览（20+）

| 模块 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| users | POST | `/api/users/register` | 注册 |
| users | POST | `/api/users/login` | 登录（返回 token） |
| users | GET | `/api/users/info` | 当前用户信息 |
| news | GET | `/api/news/categories` | 分类（Redis 缓存） |
| news | GET | `/api/news/list` | 新闻列表分页（Redis 缓存） |
| news | GET | `/api/news/detail` | 新闻详情（Redis 缓存） |
| favorite | GET/POST/DELETE | `/api/favorite/*` | 收藏检查 / 添加 / 取消 / 列表 / 清空 |
| history | POST/GET/DELETE | `/api/history/*` | 浏览记录添加 / 列表 / 删除 / 清空 |
| chat | POST | `/api/chat/stream` | AI 对话（SSE 流式，需登录） |

## 安全与配置

- 所有密钥（AI Key、数据库 / Redis 密码）仅存后端 `.env`，已被 `.gitignore` 忽略，`.env.example` 提供占位模板
- 前端不接触任何密钥，AI 请求统一经后端代理转发
- system prompt 由后端统一注入并过滤前端传入的 system 消息，防止篡改

## 详细文档

- [后端 README（环境、配置、API 明细）](toutiao_backend/README.md)
- [前端 README（联调、构建部署）](toutiao_frontend/README.md)
