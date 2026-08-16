# 存放新闻相关的缓存方法：新闻分类的读取和写入
from types import CoroutineType
from typing import Any, Optional

from fastapi.encoders import jsonable_encoder

from config.cache_conf import get_json_cache, set_cache

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news:list"


# 读取-新闻分类-缓存
async def  get_cached_categories() -> dict[Any, Any] | list[Any] | None:
    return await get_json_cache(CATEGORIES_KEY)

# 设置-新闻分类-缓存: 缓存的数据 + 过期的时间
# 分类、配置的expire：7200秒（2小时）；列表：600秒（10分钟）；详情：1800秒（30分钟）；验证码：120秒（2分钟）
async def set_cached_categories(data: list[dict[str, Any]], expire: int = 7200) -> bool:
    return await set_cache(CATEGORIES_KEY, data, expire)


# 写入-缓存-新闻列表: key = news_list:分类id:页码:每页数量
async def set_cached_news_list(category_id: Optional[int], page: int, page_size: int,
                               data: list[dict[str, Any]], expire: int = 600) -> bool:
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}:{category_part}:{page}:{page_size}"
    set_cache_result =  await set_cache(key, data, expire)
    return set_cache_result

# 读取-缓存-新闻列表
async def get_cached_news_list(
        category_id: Optional[int], page: int, page_size: int
) -> dict[Any, Any] | list[Any] | None:
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}:{category_part}:{page}:{page_size}"
    get_cache_result = await get_json_cache(key)
    return get_cache_result


# 读取-缓存-新闻详情
async def get_cached_news_detail(news_id: int) -> dict[Any, Any] | list[Any] | None:
    key = f"news:detail:{news_id}"
    cache_result = await get_json_cache(key)
    return cache_result

# 写入-缓存-新闻详情
async def set_cached_news_detail(news_id: int, data: dict[str, Any], expire: int = 1800) -> bool:
    key = f"news:detail:{news_id}"
    value = jsonable_encoder(data)
    set_cache_result = await set_cache(key, value, expire)
    return set_cache_result


# 读取-缓存-相关新闻
async def get_cached_related_news(news_id: int, category_id: int, limit: int = 5) -> dict[Any, Any] | list[Any] | None:
    key = f"news:related:{news_id}:{category_id}:{limit}"
    cache_result = await get_json_cache(key)
    return cache_result

# 写入-缓存-相关新闻
async def set_cached_related_news(news_id: int, category_id: int,
                                  data: list[dict[str, Any]], limit: int = 5, ) -> bool:
    key = f"news:related:{news_id}:{category_id}:{limit}"
    set_cache_result = await set_cache(key, data, 600)
    return set_cache_result




