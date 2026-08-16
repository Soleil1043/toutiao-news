from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase

# 添加浏览记录请求模型类
class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")


# 浏览记录响应模型类
class HistoryNewsItemResponse(NewsItemBase):
    view_time: datetime = Field(alias="viewTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

# 浏览记录列表响应模型类
class HistoryListResponse(BaseModel):
    items: list[HistoryNewsItemResponse] = Field(..., alias="list")
    total: int = Field(..., alias="total")
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )
