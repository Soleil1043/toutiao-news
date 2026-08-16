# FastAPI 后端镜像（基于 uv 官方镜像，自带 Python 3.12）
# 构建方式：
#   docker compose build            # 配合 docker-compose.yml 使用
#   docker build -t toutiao-backend .
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# 环境变量：关闭输出缓冲、统一 UTF-8，避免中文乱码与日志丢失
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 先复制依赖清单并安装，充分利用 Docker 层缓存（改动代码不会重装依赖）
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 再复制项目源码并安装项目本体（可编辑模式）
COPY . .
RUN uv sync --frozen --no-dev --no-editable

EXPOSE 8000

# 容器内直接运行（无需 Git Bash 下的 python -m 规避技巧）
CMD ["uv", "run", "python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
