"""
AI 配置模块：从环境变量读取 AI 服务配置，避免把密钥硬编码进代码。

为什么需要本模块
----------------
- API Key 是敏感信息，绝不能写死在代码里（否则会随代码泄露）。
- 本项目不引入 python-dotenv 等额外依赖，用 config/env_loader.py 的简易加载器：
  启动时自动读取项目根目录的 .env 文件（如 OPENAI_API_KEY=sk-xxx）。
- 优先级：真实系统环境变量 > .env 文件（加载器不会覆盖已存在的变量）。

命名说明
--------
- 变量采用 OpenAI 生态标准名（OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL），
  因为本项目调用的是 OpenAI 兼容的 /v1/chat/completions 接口。
- 这样可无缝切换任意 OpenAI 兼容服务商（DeepSeek、通义千问、Moonshot、
  LiteLLM 等），多数平台本身就提供这些标准环境变量名，部署时可直接复用。

使用方式
--------
1. 复制 .env.example 为 .env，填入真实密钥：
       OPENAI_API_KEY=sk-你的密钥
2. 其他代码通过 `from config.ai_conf import OPENAI_API_KEY` 引用，
   不要直接读 os.environ，保证配置来源统一。
"""
import os

from config.env_loader import load_dotenv


# 模块导入时立即加载 .env，保证下方 os.getenv 能读到文件里的值
load_dotenv()

# API Key：调用 AI 服务接口的认证凭证（OpenAI 兼容格式）。
# 未配置时为空字符串，chat 路由会检测到并返回 500 提示，而不是带着空 key 去请求。
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 接口地址：OpenAI 兼容的 /v1/chat/completions 端点。
# - DeepSeek 默认：https://api.deepseek.com/v1/chat/completions
# - 切换其他 OpenAI 兼容服务商时，把这里改成对应端点即可
#   （如 OpenAI: https://api.openai.com/v1/chat/completions）。
OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL", "https://api.deepseek.com/v1/chat/completions"
)

# 模型名：
# - DeepSeek V4 系列：deepseek-v4-flash（快速，默认）、deepseek-v4-pro（更强）
# - 旧版 deepseek-chat / deepseek-reasoner 将于 2026-07-24 下线，请勿再使用
# - 切换其他服务商时改成对应模型名（如 gpt-4o-mini、qwen-max 等）
# 可通过环境变量 OPENAI_MODEL 覆盖，无需改代码即可切换模型
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-v4-flash")

# 系统提示词（system prompt）：定义 AI 的角色定位与回答风格。
# 由后端统一注入到每次对话 messages 的最前面（见 routers/chat.py），
# 前端无需（也不应）传 system 消息，防止被浏览器端篡改、保证 prompt 集中管理。
# 可通过环境变量 AI_SYSTEM_PROMPT 覆盖，改文案无需改代码。
AI_SYSTEM_PROMPT = os.getenv(
    "AI_SYSTEM_PROMPT", "你是AI助手，请用友好、简洁的中文回答用户问题。"
)
