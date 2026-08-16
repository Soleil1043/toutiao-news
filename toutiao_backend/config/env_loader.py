"""
通用 .env 加载器：供所有配置模块（ai_conf / db_conf / cache_conf 等）复用。

为什么需要本模块
----------------
- 配置模块在模块导入时就要读取 .env，而 .env 的加载逻辑原本只存在于
  config/ai_conf.py，db_conf / cache_conf 读不到 .env 里的值。
- 把加载逻辑抽到这里统一管理，任何配置模块只需 `from config.env_loader import load_dotenv`
  并调用一次即可，保证配置来源一致。
- 本项目不引入 python-dotenv 等额外依赖。

优先级
------
真实系统环境变量 > .env 文件（load_dotenv 不会覆盖已存在的变量）。
"""
import os
from pathlib import Path


def load_dotenv() -> None:
    """
    简易 .env 加载器。

    行为说明
    --------
    - 仅当环境变量未设置时才写入，因此真实系统环境变量优先级更高；
    - 忽略空行、以 # 开头的注释行、以及不含 "=" 的行；
    - 支持值带引号（双引号/单引号），加载时自动去除；
    - 若 .env 不存在则静默跳过，不影响程序启动。
    """
    # 定位 .env：本文件位于 config/ 子目录，上两级即项目根 toutiao_backend
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
