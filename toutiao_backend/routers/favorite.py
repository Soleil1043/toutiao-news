from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from config.db_conf import get_db
from crud import favorite
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse, FavoriteNewsItemResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


# 检查新闻的收藏状态
@router.get("/check")
async def check_favorite_status(news_id: int = Query(..., alias="newsId"),
                                user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)) -> JSONResponse:
    is_favorite = await favorite.is_news_favorite(db, user.id, news_id)
    response_data = FavoriteCheckResponse(isFavorite=is_favorite)
    return success_response(message="检查收藏状态成功", data=response_data)


# 添加收藏
@router.post("/add")
async def add_favorite(
        data: FavoriteAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)) -> JSONResponse:
    result = await favorite.add_news_favorite(db, user.id, data.news_id)
    response_data = result
    return success_response(message="添加收藏成功", data=response_data)


# 取消收藏
@router.delete("/remove")
async def remove_favorite(news_id:int = Query(..., alias="newsId"),
                          user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)) -> JSONResponse:
    remove_result = await favorite.remove_news_favorite(db, user.id, news_id)
    if not remove_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏不存在")
    return success_response(message="取消收藏成功",data=None)


# 获取收藏列表
@router.get("/list")
async def get_favorite_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)) -> JSONResponse:
    rows, total = await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list = [
        FavoriteNewsItemResponse.model_validate({
            "id": news.id,
            "title": news.title,
            "description": news.description,
            "image": news.image,
            "author": news.author,
            "category_id": news.category_id,
            "views": news.views,
            "publish_time": news.publish_time,
            "favorite_id": favorite_id,
            "favorite_time": favorite_time,
        })
        for news, favorite_time, favorite_id in rows
    ]

    has_more = total > (page * page_size)
    data = FavoriteListResponse(items=favorite_list, total=total, hasMore=has_more)
    return success_response(message="获取收藏列表成功",data=data)



# 清空收藏列表
@router.delete("/clear")
async def clear_favorite_list(user: User = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)) -> JSONResponse:
    clear_count = await favorite.remove_all_favorite(db, user.id)
    return success_response(message=f"已清空{clear_count}条收藏", data=None)