from fastapi import FastAPI
from routers import news, users, favorite, history, chat
from fastapi.middleware.cors import CORSMiddleware

from utils.exception_handlers import register_exception_handlers

app = FastAPI()

# 注册异常处理器
register_exception_handlers(app)


# 跨域配置（COR中间件）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的域名列表（开发阶段允许所有，生存环境需要指定源）
    allow_credentials=True,  # 是否允许携带cookie
    allow_methods=["*"],  # 允许的HTTP方法列表
    allow_headers=["*"],  # 允许的HTTP请求头列表
)
@app.get("/")
async def root():
    return {"message": "Hello World"}


# 挂载路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(chat.router)