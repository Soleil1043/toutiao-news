from datetime import datetime, timedelta
import uuid

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import security


# 根据用户名查询数据库
async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# 根据手机号查询用户
async def get_user_by_phone(db: AsyncSession, phone: str) -> User | None:
    query = select(User).where(User.phone == phone)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# 创建用户
async def create_user(db: AsyncSession, user_data: UserRequest) -> User:
    # 先密码加密处理➡️add
    hashed_password = security.get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)  # 从数据库读回最新的user
    return user

# 生成token
async def create_token(db: AsyncSession, user: User) -> str:
    # 生成token➕设置过期时间➡️查询数据库当前用户是否有token➡️有就更新；没有就添加
    token = str(uuid.uuid4())
    # 可以更加具体：timedelta(days=7,hours=2,minutes=30,seconds=10)
    expires_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user.id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user.id, token=token, expires_at=expires_at)
        db.add(user_token)
    await db.commit()
    return token

# 验证用户名和密码
async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not security.verify_password(password, user.password):
        return None
    return user

# 根据Token查询用户。验证Token➡️查询用户
async def get_user_by_token(db: AsyncSession, token: str) -> User | None:
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()
    if not db_token:
        return None
    if db_token.expires_at < datetime.now():
        return None
    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# 更新用户信息
async def update_user(db: AsyncSession, user_name: str, user_data: UserUpdateRequest) -> User | None:
    # 手机号唯一性校验：不能与其他账号重复
    if user_data.phone:
        phone_user = await get_user_by_phone(db, user_data.phone)
        if phone_user and phone_user.username != user_name:
            raise HTTPException(status_code=400, detail="手机号已被其他账号使用")
    query = update(User).where(User.username == user_name).values(**user_data.model_dump(
        exclude_unset=True,  # 没有传递值的字段，不要更新
        exclude_none=True))
    result = await db.execute(query)
    await db.commit()
    # 如果没有更新任何行，则抛出异常
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 获取更新后的用户
    updated_user = await get_user_by_username(db, user_name)
    return updated_user

# 更新用户密码
async def update_user_password(db: AsyncSession, user: User, old_password: str, new_password: str) -> bool:
    # 验证旧密码是否正确，否则不可以更改
    if not security.verify_password(old_password, user.password):
        return False
    hashed_new_password = security.get_hash_password(new_password)
    user.password = hashed_new_password
    # 更新用户密码：由SQLAlchemy自动更新，确保commit成功
    # 规避session过期或关闭导致的问题
    db.add(user)
    await db.commit()
    return True