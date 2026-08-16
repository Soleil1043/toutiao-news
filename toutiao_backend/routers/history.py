from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from config.db_conf import get_db
from crud import history
from models.users import User
from schemas.history import HistoryAddRequest, HistoryListResponse, HistoryNewsItemResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


# 添加浏览记录
@router.post("/add")
async def add_history(data: HistoryAddRequest,
                      user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)) -> JSONResponse:
    result = await history.add_history(db, user.id, data.news_id)
    response_data = result
    return success_response(message="添加浏览记录成功", data=response_data)


# 获取浏览历史记录
@router.get("/list")
async def get_history_list(page: int = Query(1, ge=1, description="页码"),
                           page_size: int = Query(10, ge=1, le=100, description="每页数量"),
                           user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)) -> JSONResponse:
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    history_list = [
        HistoryNewsItemResponse.model_validate({
            "id": news.id,
            "title": news.title,
            "description": news.description,
            "image": news.image,
            "author": news.author,
            "category_id": news.category_id,
            "views": news.views,
            "publish_time": news.publish_time,
            "view_time": view_time,
        })
        for news, view_time in rows
    ]
    has_more = page * page_size < total
    response_data = HistoryListResponse(items=history_list, total=total, has_more=has_more)
    return success_response(message="获取浏览历史记录成功", data=response_data)


# 删除单条浏览记录
@router.delete("/delete/{history_id}")
async def delete_history(history_id: int,
                         user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)) -> JSONResponse:
    clear_result = await history.remove_history(db, user.id, history_id)
    if not clear_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="浏览记录不存在")
    return success_response(message="删除浏览记录成功", data=None)


# 清空浏览记录列表
@router.delete("/clear")
async def clear_history(user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)) -> JSONResponse:
    await history.remove_all_history(db, user.id)
    return success_response(message="清空浏览记录成功", data=None)