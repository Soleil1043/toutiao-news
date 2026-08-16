"""
聊天接口的请求模型（Schema）。

作用
----
定义 POST /api/chat/stream 的请求体结构，FastAPI 会自动：
1. 校验前端传来的 JSON 是否符合本文件定义的格式；
2. 格式非法时直接返回 422，并把错误信息返回给前端；
3. 校验通过后，把 JSON 自动转换成对应的 Pydantic 对象供路由使用。

字段命名与 OpenAI 官方 chat/completions 接口保持一致（role / content / messages），
便于前端按标准格式组包，也便于未来兼容其他 OpenAI 兼容服务商。
"""
from __future__ import annotations

from pydantic import BaseModel


class ChatMessage(BaseModel):
    """
    单条聊天消息。

    属性说明
    --------
    - role: 消息角色，DeepSeek/OpenAI 支持三种：
        "system"    系统指令，用于设定 AI 的角色、行为边界（可选）
        "user"      用户输入
        "assistant" AI 的历史回复（多轮对话时需要回传，AI 才能记住上下文）
    - content: 消息正文文本。
    """

    role: str
    content: str


class ChatRequest(BaseModel):
    """
    AI 聊天请求体：包含整段对话的消息列表。

    前端示例
    --------
    {
      "messages": [
        {"role": "system", "content": "你是新闻助手"},
        {"role": "user", "content": "今天有什么新闻？"},
        {"role": "assistant", "content": "为您找到以下热点..."},
        {"role": "user", "content": "再多给我看几条"}
      ]
    }

    说明：messages 按时间顺序排列，列表越长上下文越完整，
    但也会消耗更多 token（与计费相关），建议前端控制历史条数。
    """

    messages: list[ChatMessage]
