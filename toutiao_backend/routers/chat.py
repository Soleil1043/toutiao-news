"""
AI 聊天路由：将前端对话流式转发到 AI 服务（OpenAI 兼容接口），返回 SSE 流。

设计说明
--------
- 前端（AIChat.vue）通过 vite 代理把请求发到本接口，本接口作为中转代理，
  代替前端直接调用 AI 服务，避免把 API Key 暴露在浏览器端。
- 采用"流式透传"（stream=True）：AI 服务逐段生成内容时，后端边收边转发，
  前端可以实时看到打字机效果，而不是等全部生成完。
- 返回格式与 OpenAI /v1/chat/completions 完全一致，前端按标准 OpenAI SSE 解析即可。
- 默认对接 DeepSeek，但通过 .env（见 config/ai_conf.py）可切换任意
  OpenAI 兼容服务商，无需改本文件代码。

接口约定
--------
前端调用：POST /api/chat/stream
请求体：  {"messages": [{"role": "user", "content": "..."}]}
响应：    text/event-stream，data: {...} 形式的 OpenAI 兼容 chunk，
         流结束以 "data: [DONE]" 结尾。
鉴权：    需要登录，请求头携带 Authorization: Bearer <token>（见 utils/auth.py）。
"""
import json
from typing import AsyncGenerator

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from starlette import status

from config.ai_conf import (
    AI_SYSTEM_PROMPT,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
)
from models.users import User
from schemas.chat import ChatRequest
from utils.auth import get_current_user

# 创建 chat 子路由：
# - prefix="/api/chat"：本文件内所有路径都自动带上前缀
# - tags=["chat"]：在 FastAPI 自动生成的 Swagger 文档中分组显示
# 最终路由在 main.py 中通过 app.include_router(chat.router) 挂载到应用
router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(
    data: ChatRequest,
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    转发对话到 AI 服务，流式返回 SSE（OpenAI 兼容格式）。

    参数说明
    --------
    - data: 请求体，包含 messages 消息列表（由 Pydantic 自动校验格式）
    - user: 当前登录用户，通过 get_current_user 依赖注入获取；
            未登录或 token 无效时，FastAPI 会在此直接返回 401/422，
            不会进入函数体。

    返回值
    ------
    StreamingResponse：SSE 流式响应，媒体类型为 text/event-stream。
    """
    # 安全校验：服务端必须配置了密钥才能调用 AI 服务。
    # 密钥从 .env 读取（见 config/ai_conf.py），避免硬编码进代码。
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务端未配置 OPENAI_API_KEY",
        )

    # 构造发给 AI 服务的请求体（OpenAI 兼容格式）：
    # - model: 模型名，从环境变量读取，默认 deepseek-v4-flash
    # - messages: 过滤掉前端传入的 system 消息（统一由后端注入），
    #   在最前面插入后端配置的 AI_SYSTEM_PROMPT（角色与风格集中管理，
    #   前端无法篡改，改文案只需改 .env / ai_conf.py，无需改前端代码），
    #   其余真实对话历史（user/assistant）按时间顺序透传
    # - stream: True 表示启用流式返回，AI 服务会分多次推送内容
    history_messages = [
        msg.model_dump() for msg in data.messages if msg.role != "system"
    ]
    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "system", "content": AI_SYSTEM_PROMPT}, *history_messages],
        "stream": True,
    }
    # AI 服务接口要求的请求头：Bearer 认证 + JSON 内容类型
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    # 异步生成器：真正发起 AI 请求并逐步产出 SSE 数据。
    # StreamingResponse 会迭代这个生成器，每 yield 一次就向客户端发送一段数据，
    # 因此生成器内部的所有异常路径都必须以 yield（而非 return 值）结束，否则流会中断。
    async def event_stream() -> AsyncGenerator[str, None]:
        # 创建独立的异步 HTTP 客户端：
        # - 整体 300 秒超时（长对话生成较慢）
        # - 建立连接 10 秒超时（防止网络不可达时长时间挂起）
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(300.0, connect=10.0)
        ) as client:
            # 以流式方式请求 AI 服务（client.stream 不会一次性读入全部响应体）
            async with client.stream(
                "POST", OPENAI_BASE_URL, json=payload, headers=headers
            ) as resp:
                # AI 服务返回非 200 时（如密钥失效、模型名错误、余额不足等）：
                # 读取错误详情并以 SSE 格式发给前端，方便前端提示用户，
                # 而不是让前端拿到一个莫名中断的空流。
                if resp.status_code != 200:
                    error_body = (await resp.aread()).decode("utf-8", errors="replace")
                    yield f'data: {json.dumps({"error": error_body}, ensure_ascii=False)}\n\n'
                    return

                # 正常情况下：把 AI 服务返回的 SSE 流按文本块原样透传给前端。
                # 每块已经是 "data: {...}\n\n" 的完整片段，前端自行按 OpenAI 格式解析。
                async for chunk in resp.aiter_text():
                    yield chunk

    # 返回 SSE 流式响应：
    # - media_type="text/event-stream"：声明这是 SSE 流，浏览器/客户端按流处理
    # - Cache-Control: no-cache：禁止缓存，保证每次都拿到最新流
    # - X-Accel-Buffering: no：若生产环境使用 nginx 反代，禁用其缓冲，
    #   否则 nginx 会攒够一定量才转发，破坏流式实时性
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
