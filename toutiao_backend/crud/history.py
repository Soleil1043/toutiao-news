# 添加浏览记录
from datetime import datetime
from typing import Sequence, Any

from sqlalchemy import select, func, Row, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


# 添加浏览记录
async def add_history(db: AsyncSession, user_id: int, news_id: int) -> History:
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    history = result.scalar_one_or_none()
    if history:  # 如果有历史记录, 更新时间
        history.view_time = datetime.now()
    # 如果没有历史记录，添加记录
    else:
        history = History(user_id=user_id, news_id=news_id)
        db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


# 获取浏览历史记录列表
async def get_history_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10)\
        -> tuple[Sequence[Row[tuple[Any, datetime]]], Any]:
    # 总量 + 浏览记录列表
    count_query = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()  # 总量
    offset = (page - 1) * page_size
    query = ((select(News, History.view_time.label("view_time"))
             .join(History, History.news_id == News.id))
             .where(History.user_id == user_id).order_by(History.view_time.desc())
             .offset(offset).limit(page_size))
    result_list = await db.execute(query)
    rows = result_list.all()
    return rows, total


# 移除单条浏览记录
async def remove_history(db: AsyncSession, user_id: int, news_id: int) -> bool:
    query = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0


# 移除所有浏览记录
async def remove_all_history(db: AsyncSession, user_id: int) -> int:
    query = delete(History).where(History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount or 0