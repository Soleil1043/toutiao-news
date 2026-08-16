from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserUpdatePasswordRequest

from config.db_conf import get_db
from crud import users
from utils.response import success_response
from utils.auth import get_current_user
from utils.security import verify_password

router = APIRouter(prefix="/api/users", tags=["users"])


# 注册逻辑：校验用户名是否存在➡️创建用户➡️生成token➡️响应结果
@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)


# 登录。逻辑：查询用户➡️校验密码➡️生成token➡️响应结果
@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = await users.create_token(db, user)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功", data=response_data)


# 获取用户信息。查Token查用户➡️封装CRUD➡️功能整合成一个工具函数➡️路由导入使用
@router.get("/info")
async def get_user_info(user:User = Depends(get_current_user)) -> JSONResponse:
    response_data = UserInfoResponse.model_validate(user)
    return success_response(message="获取用户信息成功", data=response_data)


# 修改用户信息
@router.put("/update")
async def update_user_info(user_data: UserUpdateRequest, user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)) -> JSONResponse:
    updated_user = await users.update_user(db, user.username, user_data)
    response_data = UserInfoResponse.model_validate(updated_user)
    return success_response(message="更新用户信息成功", data=response_data)

# 修改用户密码
@router.put("/password")
async def update_password(password_data: UserUpdatePasswordRequest, user: User = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db)) -> JSONResponse:
    res_change_pwd = await users.update_user_password(db, user, password_data.old_password, password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败，请稍后再试")
    return success_response(message="更新用户密码成功")
