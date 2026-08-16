from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username: str = Field(..., max_length=20, description="用户名")
    password: str = Field(..., max_length=16, description="密码")

class UserInfoBase(BaseModel):
    """
    用户信息基础模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


# user_info对应的类
class UserInfoResponse(UserInfoBase):
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")

    # 模型类配置
    model_config = ConfigDict(
        from_attributes=True  # 允许从ORM对象属性中取值
    )


# data数据类型
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., description="用户信息", alias="userInfo")

    # 模型类配置
    model_config = ConfigDict(
        populate_by_name=True,  # alias / 字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )

class UserUpdateRequest(UserInfoBase):
    phone: Optional[str] = Field(None, max_length=12, description="手机号")

class UserUpdatePasswordRequest(BaseModel):
    old_password: str = Field(..., max_length=16, description="旧密码")
    new_password: str = Field(..., max_length=16, description="新密码")