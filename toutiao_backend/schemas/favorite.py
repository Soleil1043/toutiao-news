from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase

# 检查收藏状态响应模型类
class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")

# 添加收藏请求模型类
class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")

# 收藏新闻项响应模型类
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(alias="favoriteId")
    favorite_time: datetime = Field(alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

# 收藏列表接口响应模型类
class FavoriteListResponse(BaseModel):
    items: list[FavoriteNewsItemResponse] = Field(..., alias="list")
    total: int = Field(..., alias="total")
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


