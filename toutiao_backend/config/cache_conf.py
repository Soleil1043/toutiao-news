import json
import os
from typing import Any

import redis.asyncio as redis

from config.env_loader import load_dotenv

# 模块导入时立即加载 .env：Redis 连接信息统一放在 .env 管理（避免密码硬编码进代码）
load_dotenv()

# Redis 配置：通过 .env 的 REDIS_* 变量读取（见 .env / .env.example）
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))


# 创建redis的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,  # Redis服务器地址
    port=REDIS_PORT,  # Redis服务器端口
    password=REDIS_PASSWORD,  # Redis服务器密码
    db=REDIS_DB,  # 使用的Redis数据库（0-15）
    decode_responses=True  # 是否自动解码字符串
)


# 封装:设置 和 读取 (字符串 和 列表或字典)
# 读取: 字符串
async def get_cache(key: str) -> str | None:
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None

# 读取: 列表或字典
async def get_json_cache(key: str) -> dict | list | None:
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)  # 将字符串转换为字典或列表(序列化)
        return None
    except Exception as e:
        print(f"获取 JSON 缓存失败: {e}")
        return None

# 设置
async def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    try:
        if isinstance(value, (dict, list)):  # 如果value是字典或列表，则序列化为字符串
            value = json.dumps(value, ensure_ascii=False)  # 序列化为字符串,保留中文不转义
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False
