from typing import Sequence, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from cache.news_cache import get_cached_categories, set_cached_categories, get_cached_news_list, set_cached_news_list, \
    get_cached_news_detail, set_cached_news_detail, set_cached_related_news, get_cached_related_news
from models.news import Category, News
from schemas.base import NewsItemBase


# 查询新闻目录分类
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Category]:
    # 先尝试从缓存获取数据

    cached_categories = await get_cached_categories()
    if cached_categories:  # 如果缓存存在，则直接返回缓存数据
        return cached_categories
    stmt = select(Category).offset(skip).limit(limit)  # 缓存没有数据的情况下

    result = await db.execute(stmt)
    categories =  result.scalars().all()
    # 将数据写入缓存
    if categories:
        categories = jsonable_encoder(categories)  # 将数据转换为可序列化的格式
        await set_cached_categories(categories)
    # 返回
    return categories


# 查询新闻列表，确定是否需要刷新更多
async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 0) -> Sequence[News]:
    # 查询的是指定分类下的所有新闻

    # 先尝试从缓存获取数据
    # 页码 = 跳过的数量 // 每页数量 + 1
    page = skip // limit + 1
    cached_news_list = await get_cached_news_list(category_id, page, limit)
    if cached_news_list:  # 如果缓存存在，则直接返回缓存数据
        return cached_news_list

    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    # 将数据写入缓存
    if news_list:
        # 注:先把ORM格式转换为字典才能写入缓存, 即ORM转为Pydantic类型
        # news_list = jsonable_encoder(news_list)
        # by_alias=False: 不需要使用别名. 因为Redis数据是给后端用的
        news_list = [NewsItemBase.model_validate(item)
                     .model_dump(mode="json", by_alias=False) for item in news_list]
        await set_cached_news_list(category_id, page, limit, news_list)
    return news_list


# 查询新闻详情
async def get_news_detail(db: AsyncSession, news_id: int) -> News | None:

    # 先尝试从缓存获取数据
    cached_news_detail = await get_cached_news_detail(news_id)
    if cached_news_detail:  # 如果缓存存在，则直接返回缓存数据
        item = NewsItemBase.model_validate(cached_news_detail)  # 将字典转换为ORM对象
        return News(**item.model_dump(), content=cached_news_detail["content"])

    # 缓存不存在，则从数据库获取数据
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news_detail = result.scalar_one_or_none()
    if news_detail:
        # 将数据写入缓存
        cache_data = jsonable_encoder(news_detail)
        await set_cached_news_detail(news_id, cache_data)
    return news_detail


# 获取相关新闻
async def get_related_news(db: AsyncSession,
                           news_id: int,
                           category_id: int,
                           limit: int = 5) \
        -> list[Any] | dict[Any, Any] | list[dict[str, Any | None]]:
    # 先尝试从缓存获取数据
    cached_related_news = await get_cached_related_news(news_id, category_id, limit)
    # 如果缓存存在，则直接返回缓存数据（缓存里存的就是最终返回格式）
    if cached_related_news:
        return cached_related_news

    # 缓存不存在，则从数据库获取数据
    stmt = select(News).where(
        News.category_id == category_id,
        News.id != news_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    if not related_news:  # 如果没有相关新闻，则返回空列表
        return []

    # 构造最终返回格式（驼峰键 + content + publishTime 转字符串），写缓存并返回
    cache_data = [{"id": n.id,
                   "title": n.title,
                   "content": n.content,
                   "image": n.image,
                   "author": n.author,
                   "publishTime": n.publish_time.isoformat() if n.publish_time else None,
                   "categoryId": n.category_id,
                   "views": n.views} for n in related_news]
    await set_cached_related_news(news_id, category_id, cache_data, limit)
    return cache_data

