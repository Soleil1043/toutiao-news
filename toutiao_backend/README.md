# 新闻头条后端（FastAPI）

> 本项目是「AI 掘金头条新闻系统」的后端服务，为配套前端（`../toutiao_frontend`）提供新闻、用户、收藏、浏览历史与 AI 对话等 API。

---

## 目录

- [1. 技术栈](#1-技术栈)
- [2. 环境要求](#2-环境要求)
- [3. 快速开始](#3-快速开始)
- [4. 配置说明](#4-配置说明)
- [5. API 接口一览](#5-api-接口一览)
- [6. AI 对话接口](#6-ai-对话接口)
- [7. 项目结构](#7-项目结构)
- [8. 相关文档](#8-相关文档)

---

## 1. 技术栈

| 分类     | 选型                                    |
| ------ | ------------------------------------- |
| Web 框架 | FastAPI                               |
| ORM    | SQLAlchemy 2.0（异步 `async`）            |
| 数据库    | MySQL 8（驱动 `aiomysql`）                |
| 缓存     | Redis（`redis.asyncio`，用于新闻分类/列表/详情缓存） |
| AI 调用  | httpx（流式转发 OpenAI 兼容接口）               |
| 依赖管理   | uv（`pyproject.toml` + `uv.lock`）      |

## 2. 环境要求

- **Python 3.12+**（`pyproject.toml` 中 `requires-python = ">=3.12"`）
- **uv**（依赖与虚拟环境管理）
- **MySQL 8**（本地服务，默认端口 3306）
- **Redis**（本地服务，默认端口 6379）

## 3. 快速开始

```bash
# 1. 进入后端目录
cd toutiao_backend

# 2. 安装依赖（自动创建 .venv）
uv sync

# 3. 初始化数据库（创建库表，可重复执行）
#    需先保证 MySQL 已启动，连接信息在 .env 的 DB_* 变量中配置
mysql -uroot -p < database.sql

# 4. 配置环境变量（含 AI 密钥，见下方「配置说明」）
cp .env.example .env

# 5. 启动服务（开发模式，自动热重载）
#    Git Bash 下需用 `python -m` 方式启动；直接跑 uvicorn.exe 会报
#    "uv trampoline failed to canonicalize script path"
uv run python -m uvicorn main:app --reload
```

启动成功后：

- 接口文档（Swagger）：<http://127.0.0.1:8000/docs>
- 健康检查：`GET http://127.0.0.1:8000/`

> 提示：后端默认监听 `8000` 端口，配套前端通过 vite 代理把 `/api` 转发到该地址，联调时无需额外配置。

## 4. 配置说明

### 4.1 AI 服务配置（`.env`）

复制 `.env.example` 为 `.env` 并填写真实密钥（`.env` 已被 `.gitignore` 忽略，不会提交）。

```dotenv
# API Key（必填，未配置时 /api/chat/stream 返回 500）
OPENAI_API_KEY=sk-你的密钥
# 接口地址（OpenAI 兼容），默认 DeepSeek，可切换任意兼容服务商
OPENAI_BASE_URL=https://api.deepseek.com/v1/chat/completions
# 模型名，默认 deepseek-v4-flash；V4 系列还有 deepseek-v4-pro
OPENAI_MODEL=deepseek-v4-flash
# AI 系统提示词（可选）：定义 AI 角色与回答风格，后端统一注入，改文案无需改代码
AI_SYSTEM_PROMPT=你是AI助手，请用友好、简洁的中文回答用户问题。
```

变量采用 **OpenAI 生态标准名**，因此可无缝切换任意 OpenAI 兼容服务商（DeepSeek / 通义 / Moonshot / LiteLLM 等），多数平台本身就提供这套标准环境变量名，部署时可直接复用。`AI_SYSTEM_PROMPT` 为本项目扩展变量，不配置时使用 `config/ai_conf.py` 中的默认值。

优先级：**真实系统环境变量 > `.env` 文件**（`.env` 不会覆盖已存在的系统变量）。

### 4.2 数据库连接（`.env` → `config/db_conf.py`）

数据库连接信息在 `.env` 中配置（敏感项，勿提交 git），`config/db_conf.py` 启动时读取并拼装连接串：

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的数据库密码
DB_NAME=news_app
```

数据库 `news_app` 的结构由 `database.sql` 定义（`user`、`user_token`、`news_category`、`news`、`related_news`、`favorite`、`history`、`ai_chat` 共 8 张表）。

### 4.3 Redis 配置（`.env` → `config/cache_conf.py`）

缓存连接信息同样在 `.env` 中配置（敏感项，勿提交 git），`config/cache_conf.py` 启动时读取：

```dotenv
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=你的Redis密码
REDIS_DB=0
```

缓存过期策略（见 `cache/news_cache.py`）：分类 2 小时、列表 10 分钟、详情 30 分钟。Redis 不可用时缓存读写会静默降级（打印错误并返回 None），不影响接口正常返回。

### 4.4 缓存已知局限与改进计划

当前缓存实现为 **Cache-Aside（旁路缓存）读模式**：读未命中 → 回源数据库 → 回填缓存，配合过期淘汰与故障静默降级。已知局限如下，均属可接受的业务权衡，后续可迭代改进：

| 局限 | 现状 | 改进计划 |
|---|---|---|
| 写路径缓存滞后 | 浏览量 `increase_news_views` 直接更新 DB，Redis 详情缓存中的 `views` 需等 30 分钟过期后才回源刷新，存在短暂不一致（浏览量对实时性不敏感，可接受） | 更新 DB 后删除对应缓存键（Cache-Aside 标准写路径），下次读取回源回填；或浏览量走 Redis `INCR` 异步合并写库 |
| 缓存穿透 | 未对不存在的数据做空值缓存，高并发查询不存在的 ID 会直接打到 DB | 对空结果缓存空值（短过期）；或用布隆过滤器在缓存层前置拦截 |
| 缓存击穿 | 热点新闻详情无互斥保护，过期瞬间并发回源可能压垮 DB | 逻辑过期 + 互斥锁重建缓存，或热点数据永不过期 + 后台异步刷新 |
| 缓存雪崩 | 各分类/列表/详情缓存同时过期（同一时间戳写入） | 过期时间增加随机抖动（TTL ± 随机值），错开回源高峰 |
| 冷启动预热 | 服务重启后首次访问逐条回源 | 应用启动时预加载热点分类与头部新闻列表到缓存 |

> 面试提示：以上"局限 + 改进方案"为项目真实边界与可落地思路，回答缓存一致性/穿透/击穿/雪崩类问题时可主动引出。

## 5. API 接口一览

所有接口前缀为 `/api`，除登录/注册/新闻公开接口外，**均需登录**（请求头 `Authorization: Bearer <token>`）。

| 模块       | 方法     | 路径                         | 说明                |
| -------- | ------ | -------------------------- | ----------------- |
| users    | POST   | `/api/users/register`      | 注册                |
| users    | POST   | `/api/users/login`         | 登录（返回 token）      |
| users    | GET    | `/api/users/info`          | 获取当前用户信息          |
| users    | PUT    | `/api/users/update`        | 更新用户信息            |
| users    | PUT    | `/api/users/password`      | 修改密码              |
| news     | GET    | `/api/news/categories`     | 新闻分类列表（Redis 缓存）  |
| news     | GET    | `/api/news/list`           | 新闻列表（分页，Redis 缓存） |
| news     | GET    | `/api/news/detail`         | 新闻详情（Redis 缓存）    |
| favorite | GET    | `/api/favorite/check`      | 检查是否已收藏           |
| favorite | POST   | `/api/favorite/add`        | 添加收藏              |
| favorite | DELETE | `/api/favorite/remove`     | 取消收藏              |
| favorite | GET    | `/api/favorite/list`       | 收藏列表              |
| favorite | DELETE | `/api/favorite/clear`      | 清空收藏              |
| history  | POST   | `/api/history/add`         | 添加浏览记录            |
| history  | GET    | `/api/history/list`        | 浏览历史列表            |
| history  | DELETE | `/api/history/delete/{id}` | 删除单条记录            |
| history  | DELETE | `/api/history/clear`       | 清空历史              |
| chat     | POST   | `/api/chat/stream`         | AI 对话（SSE 流式，见下节） |

详细字段说明可直接查看 Swagger 文档（`/docs`）。

## 6. AI 对话接口

`POST /api/chat/stream` 把前端对话请求**流式转发**到大模型（OpenAI 兼容），返回 `text/event-stream`：

- 请求体：`{"messages": [{"role": "user", "content": "你好"}]}`（支持多轮；system 提示词由后端统一注入，前端无需传）
- 响应：`data: {...}` 形式的 SSE 分片，结束时为 `data: [DONE]`
- 内容字段：`choices[0].delta.content`（v4-flash 为推理模型，思考过程在 `reasoning_content`，最终答案在 `content`）

设计要点：

- **后端代理转发**：密钥只存在于后端 `.env`，前端不接触密钥，避免泄露；
- **流式透传**：后端边收边转发，前端可实现打字机效果；
- **可切换服务商**：只需改 `.env` 中 `OPENAI_*` 三个变量，无需改代码。

## 7. 项目结构

```
toutiao_backend/
├── main.py                  # 应用入口：CORS、路由挂载
├── pyproject.toml           # 依赖与项目元信息（uv 管理）
├── uv.lock                  # 依赖锁文件
├── database.sql             # 数据库初始化脚本（建库建表）
├── .env                     # 本地密钥配置（已 gitignore，不入库）
├── .env.example             # 配置模板
├── test_main.http           # HTTP 接口测试文件（VS Code REST Client）
│
├── config/                  # 全局配置
│   ├── db_conf.py           # MySQL 异步连接池
│   ├── cache_conf.py        # Redis 连接
│   └── ai_conf.py           # AI 配置（读取 .env 的 OPENAI_* 变量）
├── models/                  # SQLAlchemy 模型（users/news/favorite/history）
├── schemas/                 # Pydantic 请求/响应模型
├── crud/                    # 数据库操作层
├── routers/                 # 路由层（users/news/favorite/history/chat）
├── utils/                   # 工具（认证、响应封装、异常处理、密码加密）
├── cache/                   # 缓存封装（news_cache.py）
└── 文档/                    # 项目文档
```

# 
