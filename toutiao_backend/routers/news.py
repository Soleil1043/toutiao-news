from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import news, news_cache
from config.db_conf import get_db

# 创建APIRouter示例
router = APIRouter(prefix="/api/news", tags=["news"])


# 路由：获取新闻所有分类
@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100) -> dict[str, Any]:
    categories = await news_cache.get_categories(db, skip, limit)
    return {
        "code": 200,
        "msg": "success",
        "data": categories
    }


# 路由：获取新闻列表
@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId"),
    page: int = 1,
    page_size: int = Query(10, alias="pageSize", le=100),
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    # 思路：处理分页规则，查询新闻列表，计算总量，计算是否还有更多
    offset = (page - 1) * page_size
    news_list = await news_cache.get_news_list(db, category_id, offset, page_size)
    total = await news.get_news_count(db, category_id)
    has_more = total > (offset + len(news_list))
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": has_more
        }
    }


# 路由：获取新闻详情
@router.get("/detail")
async def get_news_detail(
        news_id: int = Query(..., alias="id"),
        db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    # 获取新闻详情 + 浏览量+1 + 获取相关新闻
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")
    views_res = await news.increase_news_views(db, news_id)
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻不存在")
    related_news = await news.get_related_news(db, news_detail.id, news_detail.category_id, limit=5)
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news
            }
    }


