from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import users
from models.users import User

# 整合 根据 token 查询用户，返回用户
async def get_current_user(authorization: str = Header(..., alias="Authorization"),
                           db: AsyncSession = Depends(get_db)
) -> User | None:
    # 请求头中的格式：“Bearer token”，先拆分校验格式再取 token
    parts = authorization.split(" ")
    if len(parts) != 2 or not parts[1]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的Token格式")
    token = parts[1]
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效或已经过期的Token")
    return user
