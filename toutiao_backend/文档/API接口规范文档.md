# API 接口文档

## 概述

本文档详细描述了新闻系统的API接口，包括用户管理、新闻浏览、收藏、历史记录和AI对话等功能模块。

## 基础URL

```
http://localhost:8000
```

## 认证方式

大部分接口需要认证，认证通过在请求头中添加 `Authorization` 字段实现：

```
Authorization: Bearer <token>
```

> 注意：token 前必须带 `Bearer ` 前缀（含一个空格），格式非法时后端返回 401。

## 响应格式

所有接口返回JSON格式数据，通用响应结构如下：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 接口详情

### 用户管理模块

#### 1. 用户注册

- **接口地址**: `POST /api/user/register`
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

- **请求示例**:

```json
{
  "username": "example_user",
  "password": "example_password"
}
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "token": "用户访问令牌",
    "userInfo": {
      "id": 1,
      "username": "example_user",
      "bio": "这个人很懒，什么都没留下",
      "avatar": "https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
    }
  }
}
```

#### 2. 用户登录

- **接口地址**: `POST /api/user/login`
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

- **请求示例**:

```json
{
  "username": "example_user",
  "password": "example_password"
}
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "用户访问令牌",
    "userInfo": {
      "id": 1,
      "username": "example_user",
      "nickname": null,
      "avatar": "https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg",
      "bio": "这个人很懒，什么都没留下"
    }
  }
}
```

#### 3. 获取用户信息

- **接口地址**: `GET /api/user/info`
- **请求头**: 需要认证
- **响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "example_user",
    "nickname": null,
    "avatar": "https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg",
    "gender": "unknown",
    "bio": "这个人很懒，什么都没留下"
  }
}
```

#### 4. 更新用户信息

- **接口地址**: `PUT /api/user/update`
- **请求头**: 需要认证
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| nickname | string | 否 | 昵称 |
| avatar | string | 否 | 头像URL |
| gender | string | 否 | 性别 |
| bio | string | 否 | 个人简介 |
| phone | string | 否 | 手机号 |

- **请求示例**:

```json
{
  "bio": "这是我的个人简介"
}
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "username": "example_user",
    "nickname": null,
    "avatar": "https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg",
    "gender": "unknown",
    "bio": "这是我的个人简介"
  }
}
```

#### 5. 修改用户密码

- **接口地址**: `PUT /api/user/password`
- **请求头**: 需要认证
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| oldPassword | string | 是 | 当前密码 |
| newPassword | string | 是 | 新密码 |

- **请求示例**:

```json
{
  "oldPassword": "current_password",
  "newPassword": "new_password"
}
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

### 新闻模块

#### 1. 获取新闻分类列表

- **接口地址**: `GET /api/news/categories`
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skip | integer | 否 | 跳过的记录数，默认为0 |
| limit | integer | 否 | 返回的记录数限制，默认为100 |

- **请求示例**:

```
GET /api/news/categories
GET /api/news/categories?skip=0&limit=10
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00",
      "name": "科技",
      "sort_order": 0
    }
  ]
}
```

#### 2. 获取新闻列表

- **接口地址**: `GET /api/news/list`
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| categoryId | integer | 是 | 分类ID |
| page | integer | 否 | 页码，默认为1 |
| pageSize | integer | 否 | 每页显示的新闻数量，最大值为100，默认为10 |

- **请求示例**:

```
GET /api/news/list?categoryId=1
GET /api/news/list?categoryId=1&page=2&pageSize=20
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "publish_time": "2023-01-01T00:00:00",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
        "category": null,
        "title": "新闻标题",
        "description": "新闻简介",
        "content": "新闻内容",
        "image": null,
        "author": null,
        "category_id": 1,
        "views": 0
      }
    ],
    "total": 100,
    "hasMore": true
  }
}
```

#### 3. 获取新闻详情

- **接口地址**: `GET /api/news/detail`
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 新闻ID |

- **请求示例**:

```
GET /api/news/detail?id=1
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "新闻标题",
    "content": "新闻内容",
    "image": null,
    "author": null,
    "publishTime": "2023-01-01T00:00:00",
    "categoryId": 1,
    "views": 1,
    "relatedNews": []
  }
}
```

### 收藏模块

#### 1. 检查新闻收藏状态

- **接口地址**: `GET /api/favorite/check`
- **请求头**: 需要认证
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| newsId | integer | 是 | 新闻ID |

- **请求示例**:

```
GET /api/favorite/check?newsId=1
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "isFavorite": true
  }
}
```

#### 2. 添加收藏

- **接口地址**: `POST /api/favorite/add`
- **请求头**: 需要认证
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| newsId | integer | 是 | 新闻ID |

- **请求示例**:

```json
{
  "newsId": 1
}
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "收藏成功",
  "data": {
    "id": 1,
    "userId": 1,
    "newsId": 1,
    "createTime": "2023-01-01T00:00:00"
  }
}
```

#### 3. 取消收藏

- **接口地址**: `DELETE /api/favorite/remove`
- **请求头**: 需要认证
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| newsId | integer | 是 | 新闻ID |

- **请求示例**:

```
DELETE /api/favorite/remove?newsId=1
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "取消收藏成功",
  "data": null
}
```

#### 4. 获取收藏列表

- **接口地址**: `GET /api/favorite/list`
- **请求头**: 需要认证
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认为1 |
| pageSize | integer | 否 | 每页条数，默认为10，最大值为100 |

- **请求示例**:

```
GET /api/favorite/list
GET /api/favorite/list?page=1&pageSize=10
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "title": "新闻标题",
        "description": "",
        "image": "",
        "author": "",
        "publishTime": "2023-01-01T00:00:00",
        "categoryId": 1,
        "views": 1,
        "favoriteTime": "2023-01-01T00:00:00"
      }
    ],
    "total": 1,
    "hasMore": false
  }
}
```

#### 5. 清空所有收藏

- **接口地址**: `DELETE /api/favorite/clear`
- **请求头**: 需要认证
- **响应示例**:

```json
{
  "code": 200,
  "message": "成功删除1条收藏记录",
  "data": null
}
```

### 浏览历史模块

#### 1. 添加浏览记录

- **接口地址**: `POST /api/history/add`
- **请求头**: 需要认证
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| newsId | integer | 是 | 新闻ID |

- **请求示例**:

```json
{
  "newsId": 1
}
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 1,
    "userId": 1,
    "newsId": 1,
    "viewTime": "2023-01-01T00:00:00"
  }
}
```

#### 2. 获取浏览历史列表

- **接口地址**: `GET /api/history/list`
- **请求头**: 需要认证
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认为1 |
| pageSize | integer | 否 | 每页条数，默认为10，最大值为100 |

- **请求示例**:

```
GET /api/history/list
GET /api/history/list?page=1&pageSize=10
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "title": "新闻标题",
        "description": "",
        "image": "",
        "author": "",
        "publishTime": "2023-01-01T00:00:00",
        "categoryId": 1,
        "views": 1,
        "viewTime": "2023-01-01T00:00:00"
      }
    ],
    "total": 1,
    "hasMore": false
  }
}
```

#### 3. 删除单条浏览记录

- **接口地址**: `DELETE /api/history/delete/{history_id}`
- **请求头**: 需要认证
- **路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| history_id | integer | 是 | 历史记录ID |

- **请求示例**:

```
DELETE /api/history/delete/1
```

- **响应示例**:

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

#### 4. 清空浏览历史

- **接口地址**: `DELETE /api/history/clear`
- **请求头**: 需要认证
- **响应示例**:

```json
{
  "code": 200,
  "message": "清空成功",
  "data": null
}
```

### AI 对话模块

#### 1. AI 对话（流式）

- **接口地址**: `POST /api/chat/stream`
- **请求头**: 需要认证（`Authorization: Bearer <token>`）
- **功能说明**: 将前端对话请求**流式转发**到大模型（OpenAI 兼容服务商），返回 SSE 流，前端可实时渲染（打字机效果）。转发逻辑见 `routers/chat.py`，服务商/密钥/模型通过 `.env` 的 `OPENAI_*` 变量配置（见 `config/ai_conf.py`），可切换任意 OpenAI 兼容服务商。
- **请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| messages | array | 是 | 消息列表，按时间顺序排列；每条消息包含 role 与 content 两个字段 |

`messages` 数组中每条消息的子字段：

| 子字段 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| role | string | 是 | 消息角色：`user`（用户输入）/ `assistant`（AI 历史回复，多轮对话时需回传） |
| content | string | 是 | 消息正文 |

> **system 消息不需要前端传**：AI 的系统提示词（角色定位与回答风格）由后端统一注入（`config/ai_conf.py` 的 `AI_SYSTEM_PROMPT`，可通过 `.env` 的 `AI_SYSTEM_PROMPT` 覆盖）。即使前端传了 `role: "system"` 的消息，后端也会过滤掉并替换为自己的配置，防止被浏览器端篡改。

- **请求示例**:

```json
{
  "messages": [
    { "role": "user", "content": "今天有什么新闻？" },
    { "role": "assistant", "content": "为您找到以下热点..." },
    { "role": "user", "content": "再多给我看几条" }
  ]
}
```

- **响应说明**: 本接口为 **SSE 流式响应**（`Content-Type: text/event-stream`），**不是**普通 JSON。响应格式与 OpenAI `/v1/chat/completions` 一致，前端需按标准 OpenAI SSE 格式解析：

| 数据形态 | 含义 |
|----------|------|
| `data: {...}` | 每个数据块为一段 JSON（含 `choices[].delta.content` 等标准字段） |
| `data: [DONE]` | 流正常结束的标志 |
| `data: {"error": "..."}` | AI 服务返回非 200 时（如密钥失效、模型名错误、余额不足），后端把错误详情以 SSE 格式返回，便于前端提示用户 |

- **响应示例**（实际为多行 SSE 数据，每行以空行分隔）：

```
data: {"id":"chatcmpl-xxx","choices":[{"delta":{"content":"你"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","choices":[{"delta":{"content":"好"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","choices":[{"delta":{"content":""},"finish_reason":"stop"}]}

data: [DONE]
```

- **错误码**:

| 错误码 | 触发场景 |
|--------|----------|
| 401 | 未登录或 token 无效 |
| 422 | 请求体格式非法（如缺少 messages、role/content 非字符串） |
| 500 | 服务端未配置 `OPENAI_API_KEY`（返回 `{"detail": "服务端未配置 OPENAI_API_KEY"}`） |