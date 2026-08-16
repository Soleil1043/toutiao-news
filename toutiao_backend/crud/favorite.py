from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import select, delete, func, Row
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


# 检查新闻收藏状态
async def is_news_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None

# 把新闻增加收藏
async def add_news_favorite(db: AsyncSession, user_id: int, news_id: int) -> Favorite:
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

# 取消新闻收藏
async def remove_news_favorite(db: AsyncSession, user_id: int, news_id: int) -> None:
    query = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

# 获取收藏列表（分页）
async def get_favorite_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10) \
        -> tuple[Sequence[Row[tuple[Any, datetime, int]]], Any]:
    # 总量 + 收藏的新闻列表
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()  # 总量

    # 获取收藏列表：联表查询+分页+排序(按收藏时间)
    offset = (page - 1) * page_size
    # 别名: favorite_time, favorite_id
    # [
    #   (新闻对象，收藏时间，收藏id)
    # ]
    query = (select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
             .join(Favorite, Favorite.news_id == News.id)
             .where(Favorite.user_id == user_id).order_by(Favorite.created_at.desc())
             .offset(offset).limit(page_size))
    result_list = await db.execute(query)
    rows = result_list.all()
    return rows, total

# 移除收藏列表
async def remove_all_favorite(db: AsyncSession, user_id: int) -> int | Any:
    query = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    # 需要返回删除的数量
    return result.rowcount or 0