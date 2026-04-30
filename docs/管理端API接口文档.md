# 管理端API接口文档

## 基础信息

- **Base URL**: `http://localhost:5000/api`
- **数据格式**: JSON
- **通用响应结构**:
```json
{
    "code": 200,
    "message": "success",
    "data": {}
}
```

---

## 1. 任务管理

### 1.1 获取任务列表

```
GET /api/tasks
```

**Query参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 否 | 筛选状态：pending/running/completed/failed/cancelled |
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认20 |

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 100,
        "page": 1,
        "size": 20,
        "list": [
            {
                "task_id": "task_20260424100000",
                "client_id": "client_001",
                "status": "running",
                "instruction": "start_crawl",
                "params": {
                    "shop_url": "https://xindeyi.1688.com",
                    "max_pages": 5
                },
                "progress": {
                    "current_page": 2,
                    "total_pages": 5
                },
                "created_at": "2026-04-24T10:00:00",
                "updated_at": "2026-04-24T10:05:00"
            }
        ]
    }
}
```

---

### 1.2 创建任务

```
POST /api/v1/tasks/create
```

**请求体:**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| taskType | string | 是 | - | 任务类型: single_url, batch_url, shop, keyword, shop_price, shop_image |
| sourceId | string | 否 | - | 采集源ID，指定后自动继承源的 platform 和 capability |
| platform | string | 否 | - | 平台标识，如: 1688, jd, pdd |
| capability | string | 否 | - | 能力标签，如: price, image |
| shopUrl | string | 否 | - | 店铺URL（shop类型需要） |
| targetUrls | array | 否 | - | 目标URL列表（single_url/batch_url类型需要） |
| keyword | string | 否 | - | 关键词（keyword类型需要） |
| options | object | 否 | `{}` | 任务选项（maxItems, concurrency等） |
| operatorId | string | 否 | - | 操作人ID |

**请求示例（指定 platform 和 capability）:**
```json
{
    "taskType": "shop_price",
    "sourceId": "src_9deb2db5",
    "platform": "1688",
    "capability": "price",
    "shopUrl": "https://xindeyi.1688.com/page/offerlist.htm",
    "options": {
        "maxItems": 200,
        "concurrency": 3,
        "saveImagesToOss": true,
        "timeoutSeconds": 30,
        "retryTimes": 2
    },
    "operatorId": "admin"
}
```

**请求示例（从采集源自动继承）:**
```json
{
    "taskType": "shop_image",
    "sourceId": "src_a1b2c3d4",
    "shopUrl": "https://xindeyi.1688.com/page/offerlist.htm",
    "options": {
        "maxItems": 200
    },
    "operatorId": "admin"
}
```

**响应示例:**
```json
{
    "code": "OK",
    "message": "success",
    "data": {
        "taskId": "task_4ea6c2fb",
        "taskNo": "TASK20260430140022",
        "status": "pending",
        "createdAt": "2026-04-30T14:00:22"
    }
}
```

**任务分配说明:**

| 任务配置 | 接收的客户端 |
|---------|-------------|
| platform=1688, capability=price | client_capabilities 中 platform=1688 且 capabilities 包含 price 的客户端 |
| platform=1688, capability=image | client_capabilities 中 platform=1688 且 capabilities 包含 image 的客户端 |
| 未指定 platform/capability | 仅旧版未配置 client_capabilities 的客户端可接收 |

---

### 1.3 获取任务详情

```
GET /api/tasks/<task_id>
```

**路径参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID |

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "task_id": "task_20260424100000",
        "client_id": "client_001",
        "status": "completed",
        "instruction": "start_crawl",
        "params": {
            "shop_url": "https://xindeyi.1688.com",
            "max_pages": 5
        },
        "result": {
            "batch_id": "20260424100000",
            "products_count": 30,
            "products": [
                {
                    "task_id": "a1b2c3d4e5f6",
                    "title": "商品标题",
                    "url": "https://detail.1688.com/offer/982121207497.html",
                    "status": "completed"
                }
            ]
        },
        "progress": {
            "current_page": 5,
            "total_pages": 5,
            "current_product": 30
        },
        "started_at": "2026-04-24T10:00:00",
        "completed_at": "2026-04-24T10:30:00",
        "created_at": "2026-04-24T10:00:00",
        "updated_at": "2026-04-24T10:30:00"
    }
}
```

---

### 1.4 取消任务

```
POST /api/tasks/<task_id>/cancel
```

**路径参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID |

**说明:** 只能取消pending或running状态的任务。

**响应示例:**
```json
{
    "code": 200,
    "message": "success"
}
```

---

## 2. 客户端管理

### 2.1 获取客户端列表

```
GET /api/clients
```

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "client_id": "client_001",
            "name": "client_001",
            "ip_address": "192.168.1.100",
            "status": "online",
            "current_task": "task_20260424100000",
            "last_heartbeat": "2026-04-24T10:05:00",
            "created_at": "2026-04-23T08:00:00",
            "updated_at": "2026-04-24T10:05:00"
        }
    ]
}
```

**status状态说明:**

| 状态 | 说明 |
|------|------|
| offline | 离线（超过30秒无心跳） |
| online | 在线空闲 |
| busy | 正在执行任务 |

---

### 2.2 获取客户端状态

```
GET /api/clients/<client_id>/status
```

**路径参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| client_id | string | 是 | 客户端ID |

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "client_id": "client_001",
        "name": "client_001",
        "ip_address": "192.168.1.100",
        "status": "busy",
        "current_task": "task_20260424100000",
        "last_heartbeat": "2026-04-24T10:05:00",
        "created_at": "2026-04-23T08:00:00",
        "updated_at": "2026-04-24T10:05:00",
        "recent_tasks": [
            {
                "task_id": "task_20260424100000",
                "status": "running",
                "created_at": "2026-04-24T10:00:00"
            }
        ]
    }
}
```

---

## 3. 监控面板

### 3.1 获取仪表盘数据

```
GET /api/dashboard
```

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "tasks": {
            "total": 100,
            "pending": 5,
            "running": 2,
            "completed": 90,
            "failed": 3
        },
        "clients": {
            "total": 10,
            "online": 8
        }
    }
}
```

---

## 4. 错误码

| code | 说明 |
|------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

**错误响应示例:**
```json
{
    "code": 404,
    "message": "task not found",
    "data": null
}
```
