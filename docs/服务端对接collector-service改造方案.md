# 服务端对接 collector-service API 改造方案

## 一、现有架构 vs 目标架构对比

### 1.1 现有架构

```
Web端 → admin.py (Flask Blueprint) → MongoDB
                    ↓
              client.py (心跳/任务上报)
                    ↓
              爬虫客户端
```

**现有接口：**
- `GET /admin/tasks` - 任务列表
- `POST /admin/tasks` - 创建任务
- `GET /admin/tasks/<task_id>` - 任务详情
- `POST /admin/tasks/<task_id>/cancel` - 取消任务
- `GET /admin/clients` - 客户端列表
- `GET /admin/dashboard` - 仪表盘
- `POST /client/heartbeat` - 心跳
- `POST /client/task_report` - 进度上报
- `POST /client/task_result` - 结果上报

### 1.2 目标架构（collector-service）

```
apps/web → apps/api (collector-gateway) → collector-service (Python)
                                                    ↓
                                              MongoDB (collector_*)
                                                    ↓
                                              爬虫客户端
```

**目标接口：**
- `GET /api/v1/health` - 健康检查
- `GET /api/v1/sources` - 采集源列表
- `POST /api/v1/sources/create` - 创建采集源
- `POST /api/v1/sources/update` - 更新采集源
- `POST /api/v1/sources/enable` - 启用采集源
- `POST /api/v1/sources/disable` - 禁用采集源
- `POST /api/v1/sources/delete` - 删除采集源
- `POST /api/v1/parse-preview` - 链接预解析
- `POST /api/v1/tasks/create` - 创建任务
- `GET /api/v1/tasks` - 任务列表
- `GET /api/v1/tasks/detail` - 任务详情
- `POST /api/v1/tasks/cancel` - 取消任务
- `POST /api/v1/tasks/retry` - 重试任务
- `GET /api/v1/items` - 采集结果列表
- `GET /api/v1/items/detail` - 采集结果详情
- `POST /api/v1/items/reparse` - 重新解析
- `POST /api/v1/items/ignore` - 忽略结果
- `POST /api/v1/items/restore` - 恢复结果

---

## 二、数据库改造

### 2.1 新增集合（MongoDB Collections）

| 集合名 | 用途 | 对应文档模型 |
|--------|------|--------------|
| `collector_source` | 采集源管理 | CollectorSource |
| `collector_task` | 采集任务 | CollectorTask |
| `collector_item` | 采集结果 | CollectorItem |
| `collector_item_asset` | 采集资源（图片/视频） | CollectorItemAsset |
| `collector_task_log` | 任务日志 | CollectorTaskLog |
| `collector_idempotency_key` | 幂等控制 | CollectorIdempotencyKey |
| `collector_request_log` | 请求日志 | CollectorRequestLog |

### 2.2 数据模型设计

#### 2.2.1 collector_source（采集源）

```python
{
    "sourceId": "src_001",
    "sourceCode": "SRC_1688_DEFAULT",
    "sourceName": "1688默认采集源",
    "platform": "1688",
    "sourceType": "url",
    "entryUrl": "https://www.1688.com",
    "parserCode": "1688_offer_v1",
    "config": {
        "rateLimitPerMinute": 60,
        "timeoutSeconds": 30,
        "retryTimes": 2,
        "saveRawHtml": False,
        "saveImagesToOss": True,
        "proxyProfileId": "proxy_default",
        "cookieProfileId": "cookie_1688_default"
    },
    "status": "enabled",
    "isDeleted": False,
    "createdBy": "user_001",
    "updatedBy": "user_001",
    "createdAt": "2026-04-27T15:30:00+02:00",
    "updatedAt": "2026-04-27T15:30:00+02:00"
}
```

#### 2.2.2 collector_task（采集任务）

```python
{
    "taskId": "task_001",
    "taskNo": "COL202604270001",
    "sourceId": "src_001",
    "taskType": "shop",
    "status": "running",
    "progress": 45,
    "totalCount": 100,
    "successCount": 42,
    "failedCount": 3,
    "duplicateCount": 0,
    "ignoredCount": 0,
    "options": {
        "maxItems": 200,
        "concurrency": 3,
        "saveImagesToOss": True
    },
    "errorCode": None,
    "errorMessage": None,
    "operatorId": "user_001",
    "startedAt": "2026-04-27T15:31:00+02:00",
    "finishedAt": None,
    "createdAt": "2026-04-27T15:30:00+02:00",
    "updatedAt": "2026-04-27T15:30:00+02:00"
}
```

#### 2.2.3 collector_item（采集结果）

```python
{
    "itemId": "item_001",
    "taskId": "task_001",
    "platform": "1688",
    "sourceUrl": "https://detail.1688.com/offer/123456.html",
    "sourceProductId": "123456",
    "dedupeKey": "1688:123456",
    "title": "商品标题",
    "subTitle": "副标题",
    "description": "商品描述",
    "mainImageUrl": "https://img.example.com/main.jpg",
    "imageUrls": ["https://img.example.com/1.jpg", "https://img.example.com/2.jpg"],
    "priceMin": "12.50",
    "priceMax": "18.90",
    "currency": "CNY",
    "supplierName": "供应商名称",
    "supplierUrl": "https://shop.example.com",
    "shopName": "店铺名称",
    "rawData": {},
    "normalizedData": {},
    "parseStatus": "parsed",
    "createdAt": "2026-04-27T15:30:00+02:00",
    "updatedAt": "2026-04-27T15:30:00+02:00"
}
```

#### 2.2.4 collector_task_log（任务日志）

```python
{
    "logId": "log_001",
    "taskId": "task_001",
    "level": "info",
    "eventCode": "CRAWL_PAGE_START",
    "message": "开始爬取第 3 页",
    "context": {
        "page": 3,
        "totalPages": 10
    },
    "createdAt": "2026-04-27T15:30:00+02:00"
}
```

### 2.3 现有集合映射

| 现有集合 | 目标集合 | 说明 |
|----------|----------|------|
| `tasks` | `collector_task` | 任务数据迁移 |
| `clients` | 保留 | 客户端管理独立 |
| `task_logs` | `collector_task_log` | 日志数据迁移 |

---

## 三、接口改造方案

### 3.1 路由结构调整

```
server/
├── app/
│   ├── routes/
│   │   ├── admin.py          → 保留（管理端接口，内部使用）
│   │   ├── client.py         → 保留（客户端接口，内部使用）
│   │   ├── collector.py      → 新增（对外 collector-service API）
│   │   └── __init__.py       → 修改（注册新蓝图）
│   ├── models/
│   │   ├── collector_source.py   → 新增
│   │   ├── collector_task.py     → 新增
│   │   ├── collector_item.py     → 新增
│   │   ├── collector_log.py      → 新增
│   │   └── __init__.py           → 修改
│   └── __init__.py
```

### 3.2 collector.py 蓝图设计

```python
from flask import Blueprint, request, jsonify
from datetime import datetime

bp = Blueprint('collector', __name__, url_prefix='/api/v1')

# ============ 健康检查 ============

@bp.route('/health', methods=['GET'])
def health():
    """健康检查"""
    from app import db
    
    try:
        db.tasks.count_documents({})
        db_status = "ok"
    except:
        db_status = "error"
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": {
            "status": "ok" if db_status == "ok" else "degraded",
            "service": "collector-service",
            "version": "0.1.0",
            "dependencies": {
                "database": db_status,
                "redis": "ok",
                "oss": "ok"
            },
            "time": datetime.now().isoformat()
        },
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


# ============ 采集源接口 ============

@bp.route('/sources', methods=['GET'])
def list_sources():
    """查询采集源列表"""
    from app import db
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 20))
    keyword = request.args.get('keyword')
    platform = request.args.get('platform')
    source_type = request.args.get('sourceType')
    status = request.args.get('status')
    
    query = {"isDeleted": False}
    
    if keyword:
        query["$or"] = [
            {"sourceName": {"$regex": keyword, "$options": "i"}},
            {"sourceCode": {"$regex": keyword, "$options": "i"}}
        ]
    if platform:
        query["platform"] = platform
    if source_type:
        query["sourceType"] = source_type
    if status:
        query["status"] = status
    
    total = db.collector_sources.count_documents(query)
    items = list(db.collector_sources.find(query, {"_id": 0})
                 .sort("createdAt", -1)
                 .skip((page - 1) * page_size)
                 .limit(page_size))
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": {
            "items": items,
            "page": page,
            "pageSize": page_size,
            "total": total
        },
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/sources/detail', methods=['GET'])
def get_source_detail():
    """查询采集源详情"""
    from app import db
    
    source_id = request.args.get('sourceId')
    if not source_id:
        return jsonify({
            "code": "COLLECTOR_SOURCE_ID_REQUIRED",
            "message": "采集源ID不能为空",
            "data": None
        }), 400
    
    source = db.collector_sources.find_one({"sourceId": source_id}, {"_id": 0})
    if not source:
        return jsonify({
            "code": "COLLECTOR_SOURCE_NOT_FOUND",
            "message": "采集源不存在",
            "data": None
        }), 404
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": source,
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/sources/create', methods=['POST'])
def create_source():
    """创建采集源"""
    from app import db
    from app.models.collector_source import create_collector_source
    
    data = request.get_json()
    source_code = data.get('sourceCode')
    source_name = data.get('sourceName')
    platform = data.get('platform')
    source_type = data.get('sourceType')
    
    # 参数校验
    if not source_code:
        return jsonify({
            "code": "COLLECTOR_SOURCE_CODE_REQUIRED",
            "message": "采集源编码不能为空",
            "data": None
        }), 400
    
    if not source_name:
        return jsonify({
            "code": "COLLECTOR_SOURCE_NAME_REQUIRED",
            "message": "采集源名称不能为空",
            "data": None
        }), 400
    
    # 检查是否已存在
    existing = db.collector_sources.find_one({"sourceCode": source_code})
    if existing:
        return jsonify({
            "code": "COLLECTOR_SOURCE_CODE_EXISTS",
            "message": "采集源编码已存在",
            "data": None
        }), 409
    
    source = create_collector_source(data)
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": {
            "sourceId": source["sourceId"],
            "sourceCode": source["sourceCode"],
            "status": source["status"]
        },
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/sources/update', methods=['POST'])
def update_source():
    """更新采集源"""
    from app import db
    from app.models.collector_source import update_collector_source
    
    data = request.get_json()
    source_id = data.get('sourceId')
    
    if not source_id:
        return jsonify({
            "code": "COLLECTOR_SOURCE_ID_REQUIRED",
            "message": "采集源ID不能为空",
            "data": None
        }), 400
    
    source = db.collector_sources.find_one({"sourceId": source_id})
    if not source:
        return jsonify({
            "code": "COLLECTOR_SOURCE_NOT_FOUND",
            "message": "采集源不存在",
            "data": None
        }), 404
    
    if source.get("isDeleted"):
        return jsonify({
            "code": "COLLECTOR_SOURCE_DELETED",
            "message": "采集源已删除",
            "data": None
        }), 400
    
    update_collector_source(source_id, data)
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": None,
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/sources/enable', methods=['POST'])
def enable_source():
    """启用采集源"""
    from app import db
    
    data = request.get_json()
    source_id = data.get('sourceId')
    
    if not source_id:
        return jsonify({
            "code": "COLLECTOR_SOURCE_ID_REQUIRED",
            "message": "采集源ID不能为空",
            "data": None
        }), 400
    
    source = db.collector_sources.find_one({"sourceId": source_id})
    if not source:
        return jsonify({
            "code": "COLLECTOR_SOURCE_NOT_FOUND",
            "message": "采集源不存在",
            "data": None
        }), 404
    
    if source.get("isDeleted"):
        return jsonify({
            "code": "COLLECTOR_SOURCE_DELETED",
            "message": "采集源已删除",
            "data": None
        }), 400
    
    db.collector_sources.update_one(
        {"sourceId": source_id},
        {"$set": {"status": "enabled", "updatedAt": datetime.now().isoformat()}}
    )
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": None,
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/sources/disable', methods=['POST'])
def disable_source():
    """禁用采集源"""
    from app import db
    
    data = request.get_json()
    source_id = data.get('sourceId')
    
    if not source_id:
        return jsonify({
            "code": "COLLECTOR_SOURCE_ID_REQUIRED",
            "message": "采集源ID不能为空",
            "data": None
        }), 400
    
    db.collector_sources.update_one(
        {"sourceId": source_id},
        {"$set": {"status": "disabled", "updatedAt": datetime.now().isoformat()}}
    )
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": None,
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/sources/delete', methods=['POST'])
def delete_source():
    """删除采集源（软删除）"""
    from app import db
    
    data = request.get_json()
    source_id = data.get('sourceId')
    
    if not source_id:
        return jsonify({
            "code": "COLLECTOR_SOURCE_ID_REQUIRED",
            "message": "采集源ID不能为空",
            "data": None
        }), 400
    
    db.collector_sources.update_one(
        {"sourceId": source_id},
        {"$set": {"isDeleted": True, "updatedAt": datetime.now().isoformat()}}
    )
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": None,
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


# ============ 链接预解析接口 ============

@bp.route('/parse-preview', methods=['POST'])
def parse_preview():
    """链接预解析"""
    from app import db
    
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({
            "code": "COLLECTOR_URL_REQUIRED",
            "message": "采集链接不能为空",
            "data": None
        }), 400
    
    # 识别平台
    platform = identify_platform(url)
    if not platform:
        return jsonify({
            "code": "COLLECTOR_URL_UNSUPPORTED",
            "message": "当前链接暂不支持采集",
            "data": None
        }), 400
    
    # 提取商品ID
    source_product_id = extract_product_id(url, platform)
    dedupe_key = f"{platform}:{source_product_id}"
    
    # 检查是否已采集
    existing_item = db.collector_items.find_one({"dedupeKey": dedupe_key})
    if existing_item:
        return jsonify({
            "code": "OK",
            "message": "success",
            "data": {
                "supported": True,
                "platform": platform,
                "dedupeKey": dedupe_key,
                "duplicated": True,
                "existedItemId": existing_item["itemId"],
                "title": existing_item.get("title")
            },
            "traceId": request.headers.get('X-Trace-Id', ''),
            "requestId": request.headers.get('X-Request-Id', ''),
            "timestamp": datetime.now().isoformat()
        })
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": {
            "supported": True,
            "platform": platform,
            "parserCode": f"{platform}_offer_v1",
            "sourceProductId": source_product_id,
            "canonicalUrl": url,
            "dedupeKey": dedupe_key
        },
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


# ============ 采集任务接口 ============

@bp.route('/tasks/create', methods=['POST'])
def create_task():
    """创建采集任务"""
    from app import db
    from app.models.collector_task import create_collector_task
    
    data = request.get_json()
    idempotency_key = data.get('idempotencyKey')
    task_type = data.get('taskType')
    source_id = data.get('sourceId')
    
    # 参数校验
    if not task_type:
        return jsonify({
            "code": "COLLECTOR_TASK_TYPE_REQUIRED",
            "message": "采集任务类型不能为空",
            "data": None
        }), 400
    
    valid_task_types = ['single_url', 'batch_url', 'shop', 'keyword']
    if task_type not in valid_task_types:
        return jsonify({
            "code": "COLLECTOR_TASK_TYPE_INVALID",
            "message": "采集任务类型不正确",
            "data": None
        }), 400
    
    # 检查采集源
    if source_id:
        source = db.collector_sources.find_one({"sourceId": source_id})
        if not source:
            return jsonify({
                "code": "COLLECTOR_SOURCE_NOT_FOUND",
                "message": "采集源不存在",
                "data": None
            }), 404
        if source.get("status") == "disabled":
            return jsonify({
                "code": "COLLECTOR_SOURCE_DISABLED",
                "message": "采集源已停用",
                "data": None
            }), 400
    
    # 幂等检查
    if idempotency_key:
        existing = db.collector_idempotency_keys.find_one({"idempotencyKey": idempotency_key})
        if existing:
            task = db.collector_tasks.find_one({"taskId": existing["taskId"]})
            return jsonify({
                "code": "OK",
                "message": "success",
                "data": {
                    "taskId": task["taskId"],
                    "taskNo": task["taskNo"],
                    "status": task["status"],
                    "createdAt": task["createdAt"]
                },
                "traceId": request.headers.get('X-Trace-Id', ''),
                "requestId": request.headers.get('X-Request-Id', ''),
                "timestamp": datetime.now().isoformat()
            })
    
    task = create_collector_task(data)
    
    # 记录幂等键
    if idempotency_key:
        db.collector_idempotency_keys.insert_one({
            "idempotencyKey": idempotency_key,
            "taskId": task["taskId"],
            "createdAt": datetime.now().isoformat()
        })
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": {
            "taskId": task["taskId"],
            "taskNo": task["taskNo"],
            "status": task["status"],
            "createdAt": task["createdAt"]
        },
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/tasks', methods=['GET'])
def list_tasks():
    """查询采集任务列表"""
    from app import db
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 20))
    status = request.args.get('status')
    task_type = request.args.get('taskType')
    source_id = request.args.get('sourceId')
    keyword = request.args.get('keyword')
    created_at_start = request.args.get('createdAtStart')
    created_at_end = request.args.get('createdAtEnd')
    
    query = {}
    
    if status:
        query["status"] = status
    if task_type:
        query["taskType"] = task_type
    if source_id:
        query["sourceId"] = source_id
    if keyword:
        query["$or"] = [
            {"taskNo": {"$regex": keyword, "$options": "i"}},
            {"sourceUrl": {"$regex": keyword, "$options": "i"}}
        ]
    if created_at_start:
        query["createdAt"] = {"$gte": created_at_start}
    if created_at_end:
        query.setdefault("createdAt", {})["$lte"] = created_at_end
    
    total = db.collector_tasks.count_documents(query)
    items = list(db.collector_tasks.find(query, {"_id": 0})
                 .sort("createdAt", -1)
                 .skip((page - 1) * page_size)
                 .limit(page_size))
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": {
            "items": items,
            "page": page,
            "pageSize": page_size,
            "total": total
        },
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/tasks/detail', methods=['GET'])
def get_task_detail():
    """查询任务详情"""
    from app import db
    
    task_id = request.args.get('taskId')
    if not task_id:
        return jsonify({
            "code": "COLLECTOR_TASK_ID_REQUIRED",
            "message": "任务ID不能为空",
            "data": None
        }), 400
    
    task = db.collector_tasks.find_one({"taskId": task_id}, {"_id": 0})
    if not task:
        return jsonify({
            "code": "COLLECTOR_TASK_NOT_FOUND",
            "message": "采集任务不存在",
            "data": None
        }), 404
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": task,
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/tasks/cancel', methods=['POST'])
def cancel_task():
    """取消任务"""
    from app import db
    
    data = request.get_json()
    task_id = data.get('taskId')
    
    if not task_id:
        return jsonify({
            "code": "COLLECTOR_TASK_ID_REQUIRED",
            "message": "任务ID不能为空",
            "data": None
        }), 400
    
    task = db.collector_tasks.find_one({"taskId": task_id})
    if not task:
        return jsonify({
            "code": "COLLECTOR_TASK_NOT_FOUND",
            "message": "采集任务不存在",
            "data": None
        }), 404
    
    if task["status"] not in ["pending", "running"]:
        return jsonify({
            "code": "COLLECTOR_TASK_NOT_CANCELABLE",
            "message": "当前任务状态不允许取消",
            "data": None
        }), 409
    
    db.collector_tasks.update_one(
        {"taskId": task_id},
        {"$set": {
            "status": "canceled",
            "finishedAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }}
    )
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": None,
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/tasks/retry', methods=['POST'])
def retry_task():
    """重试任务"""
    from app import db
    
    data = request.get_json()
    task_id = data.get('taskId')
    
    if not task_id:
        return jsonify({
            "code": "COLLECTOR_TASK_ID_REQUIRED",
            "message": "任务ID不能为空",
            "data": None
        }), 400
    
    task = db.collector_tasks.find_one({"taskId": task_id})
    if not task:
        return jsonify({
            "code": "COLLECTOR_TASK_NOT_FOUND",
            "message": "采集任务不存在",
            "data": None
        }), 404
    
    if task["status"] not in ["failed", "partial_failed", "canceled"]:
        return jsonify({
            "code": "COLLECTOR_TASK_NOT_RETRYABLE",
            "message": "当前任务状态不允许重试",
            "data": None
        }), 409
    
    db.collector_tasks.update_one(
        {"taskId": task_id},
        {"$set": {
            "status": "pending",
            "progress": 0,
            "successCount": 0,
            "failedCount": 0,
            "duplicateCount": 0,
            "ignoredCount": 0,
            "errorCode": None,
            "errorMessage": None,
            "startedAt": None,
            "finishedAt": None,
            "updatedAt": datetime.now().isoformat()
        }}
    )
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": None,
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


# ============ 采集结果接口 ============

@bp.route('/items', methods=['GET'])
def list_items():
    """查询采集结果列表"""
    from app import db
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 20))
    task_id = request.args.get('taskId')
    platform = request.args.get('platform')
    parse_status = request.args.get('parseStatus')
    keyword = request.args.get('keyword')
    
    query = {}
    
    if task_id:
        query["taskId"] = task_id
    if platform:
        query["platform"] = platform
    if parse_status:
        query["parseStatus"] = parse_status
    if keyword:
        query["$or"] = [
            {"title": {"$regex": keyword, "$options": "i"}},
            {"sourceUrl": {"$regex": keyword, "$options": "i"}}
        ]
    
    total = db.collector_items.count_documents(query)
    items = list(db.collector_items.find(query, {"_id": 0, "rawData": 0, "normalizedData": 0})
                 .sort("createdAt", -1)
                 .skip((page - 1) * page_size)
                 .limit(page_size))
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": {
            "items": items,
            "page": page,
            "pageSize": page_size,
            "total": total
        },
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/items/detail', methods=['GET'])
def get_item_detail():
    """查询采集结果详情"""
    from app import db
    
    item_id = request.args.get('itemId')
    if not item_id:
        return jsonify({
            "code": "COLLECTOR_ITEM_ID_REQUIRED",
            "message": "结果ID不能为空",
            "data": None
        }), 400
    
    item = db.collector_items.find_one({"itemId": item_id}, {"_id": 0})
    if not item:
        return jsonify({
            "code": "COLLECTOR_ITEM_NOT_FOUND",
            "message": "采集结果不存在",
            "data": None
        }), 404
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": item,
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/items/reparse', methods=['POST'])
def reparse_item():
    """重新解析采集结果"""
    from app import db
    
    data = request.get_json()
    item_id = data.get('itemId')
    
    if not item_id:
        return jsonify({
            "code": "COLLECTOR_ITEM_ID_REQUIRED",
            "message": "结果ID不能为空",
            "data": None
        }), 400
    
    db.collector_items.update_one(
        {"itemId": item_id},
        {"$set": {
            "parseStatus": "pending",
            "updatedAt": datetime.now().isoformat()
        }}
    )
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": None,
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/items/ignore', methods=['POST'])
def ignore_item():
    """忽略采集结果"""
    from app import db
    
    data = request.get_json()
    item_id = data.get('itemId')
    
    if not item_id:
        return jsonify({
            "code": "COLLECTOR_ITEM_ID_REQUIRED",
            "message": "结果ID不能为空",
            "data": None
        }), 400
    
    db.collector_items.update_one(
        {"itemId": item_id},
        {"$set": {
            "parseStatus": "ignored",
            "updatedAt": datetime.now().isoformat()
        }}
    )
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": None,
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


@bp.route('/items/restore', methods=['POST'])
def restore_item():
    """恢复采集结果"""
    from app import db
    
    data = request.get_json()
    item_id = data.get('itemId')
    
    if not item_id:
        return jsonify({
            "code": "COLLECTOR_ITEM_ID_REQUIRED",
            "message": "结果ID不能为空",
            "data": None
        }), 400
    
    db.collector_items.update_one(
        {"itemId": item_id},
        {"$set": {
            "parseStatus": "parsed",
            "updatedAt": datetime.now().isoformat()
        }}
    )
    
    return jsonify({
        "code": "OK",
        "message": "success",
        "data": None,
        "traceId": request.headers.get('X-Trace-Id', ''),
        "requestId": request.headers.get('X-Request-Id', ''),
        "timestamp": datetime.now().isoformat()
    })


# ============ 辅助函数 ============

def identify_platform(url: str) -> str:
    """识别URL所属平台"""
    if '1688.com' in url:
        return '1688'
    elif 'taobao.com' in url:
        return 'taobao'
    elif 'tmall.com' in url:
        return 'tmall'
    elif 'aliexpress.com' in url:
        return 'aliexpress'
    elif 'shopify.com' in url:
        return 'shopify'
    return None


def extract_product_id(url: str, platform: str) -> str:
    """从URL提取商品ID"""
    import re
    
    if platform == '1688':
        match = re.search(r'offer/(\d+)', url)
        if match:
            return match.group(1)
    
    return url
```

### 3.3 models 层改造

#### 3.3.1 collector_source.py

```python
from datetime import datetime
import uuid

def create_collector_source(data: dict) -> dict:
    """创建采集源"""
    from app import db
    
    source_id = f"src_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    
    source = {
        "sourceId": source_id,
        "sourceCode": data.get("sourceCode"),
        "sourceName": data.get("sourceName"),
        "platform": data.get("platform"),
        "sourceType": data.get("sourceType", "url"),
        "entryUrl": data.get("entryUrl"),
        "parserCode": data.get("parserCode"),
        "config": data.get("config", {}),
        "status": "enabled",
        "isDeleted": False,
        "createdBy": data.get("createdBy"),
        "updatedBy": data.get("updatedBy"),
        "createdAt": now,
        "updatedAt": now
    }
    
    db.collector_sources.insert_one(source)
    return source


def update_collector_source(source_id: str, data: dict) -> None:
    """更新采集源"""
    from app import db
    
    update_data = {k: v for k, v in data.items() 
                   if k not in ["sourceId", "sourceCode", "isDeleted"]}
    update_data["updatedAt"] = datetime.now().isoformat()
    
    db.collector_sources.update_one(
        {"sourceId": source_id},
        {"$set": update_data}
    )
```

#### 3.3.2 collector_task.py

```python
from datetime import datetime
import uuid

def create_collector_task(data: dict) -> dict:
    """创建采集任务"""
    from app import db
    
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    task_no = f"COL{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:4].upper()}"
    now = datetime.now().isoformat()
    
    task_type = data.get("taskType")
    
    task = {
        "taskId": task_id,
        "taskNo": task_no,
        "sourceId": data.get("sourceId"),
        "taskType": task_type,
        "status": "pending",
        "progress": 0,
        "totalCount": 0,
        "successCount": 0,
        "failedCount": 0,
        "duplicateCount": 0,
        "ignoredCount": 0,
        "options": data.get("options", {}),
        "errorCode": None,
        "errorMessage": None,
        "operatorId": data.get("operatorId"),
        "startedAt": None,
        "finishedAt": None,
        "createdAt": now,
        "updatedAt": now
    }
    
    # 根据任务类型设置 totalCount
    if task_type == "single_url":
        task["totalCount"] = 1
    elif task_type == "batch_url":
        task["totalCount"] = len(data.get("targetUrls", []))
    elif task_type == "shop":
        task["totalCount"] = data.get("options", {}).get("maxItems", 0)
    elif task_type == "keyword":
        task["totalCount"] = data.get("options", {}).get("maxItems", 0)
    
    db.collector_tasks.insert_one(task)
    return task
```

#### 3.3.3 collector_item.py

```python
from datetime import datetime
import uuid

def create_collector_item(data: dict) -> dict:
    """创建采集结果"""
    from app import db
    
    item_id = f"item_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    
    item = {
        "itemId": item_id,
        "taskId": data.get("taskId"),
        "platform": data.get("platform"),
        "sourceUrl": data.get("sourceUrl"),
        "sourceProductId": data.get("sourceProductId"),
        "dedupeKey": data.get("dedupeKey"),
        "title": data.get("title"),
        "subTitle": data.get("subTitle"),
        "description": data.get("description"),
        "mainImageUrl": data.get("mainImageUrl"),
        "imageUrls": data.get("imageUrls", []),
        "priceMin": data.get("priceMin"),
        "priceMax": data.get("priceMax"),
        "currency": data.get("currency"),
        "supplierName": data.get("supplierName"),
        "supplierUrl": data.get("supplierUrl"),
        "shopName": data.get("shopName"),
        "rawData": data.get("rawData", {}),
        "normalizedData": data.get("normalizedData", {}),
        "parseStatus": data.get("parseStatus", "pending"),
        "createdAt": now,
        "updatedAt": now
    }
    
    db.collector_items.insert_one(item)
    return item
```

#### 3.3.4 collector_log.py

```python
from datetime import datetime
import uuid

def add_collector_log(task_id: str, level: str, event_code: str, message: str, context: dict = None) -> dict:
    """添加任务日志"""
    from app import db
    
    log_id = f"log_{uuid.uuid4().hex[:8]}"
    
    log = {
        "logId": log_id,
        "taskId": task_id,
        "level": level,
        "eventCode": event_code,
        "message": message,
        "context": context or {},
        "createdAt": datetime.now().isoformat()
    }
    
    db.collector_task_logs.insert_one(log)
    return log
```

### 3.4 app/__init__.py 改造

```python
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # MongoDB配置
    mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    mongo_db = os.environ.get('MONGO_DB', 'crawler_db')
    
    client = MongoClient(mongo_uri)
    db = client[mongo_db]
    app.db = db
    
    # 注册蓝图
    from app.routes.admin import bp as admin_bp
    from app.routes.client import bp as client_bp
    from app.routes.collector import bp as collector_bp
    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(client_bp, url_prefix='/client')
    app.register_blueprint(collector_bp)  # 已有 /api/v1 前缀
    
    return app
```

---

## 四、接口映射对照表

### 4.1 采集源接口

| 运营工作台接口 | 现有接口 | 改造方式 |
|----------------|----------|----------|
| `GET /api/v1/sources` | 无 | 新增 |
| `GET /api/v1/sources/detail` | 无 | 新增 |
| `POST /api/v1/sources/create` | 无 | 新增 |
| `POST /api/v1/sources/update` | 无 | 新增 |
| `POST /api/v1/sources/enable` | 无 | 新增 |
| `POST /api/v1/sources/disable` | 无 | 新增 |
| `POST /api/v1/sources/delete` | 无 | 新增 |

### 4.2 采集任务接口

| 运营工作台接口 | 现有接口 | 改造方式 |
|----------------|----------|----------|
| `POST /api/v1/tasks/create` | `POST /admin/tasks` | 新增，保留旧接口 |
| `GET /api/v1/tasks` | `GET /admin/tasks` | 新增，保留旧接口 |
| `GET /api/v1/tasks/detail` | `GET /admin/tasks/<task_id>` | 新增，保留旧接口 |
| `POST /api/v1/tasks/cancel` | `POST /admin/tasks/<task_id>/cancel` | 新增，保留旧接口 |
| `POST /api/v1/tasks/retry` | 无 | 新增 |

### 4.3 采集结果接口

| 运营工作台接口 | 现有接口 | 改造方式 |
|----------------|----------|----------|
| `GET /api/v1/items` | 无 | 新增 |
| `GET /api/v1/items/detail` | 无 | 新增 |
| `POST /api/v1/items/reparse` | 无 | 新增 |
| `POST /api/v1/items/ignore` | 无 | 新增 |
| `POST /api/v1/items/restore` | 无 | 新增 |

### 4.4 其他接口

| 运营工作台接口 | 现有接口 | 改造方式 |
|----------------|----------|----------|
| `GET /api/v1/health` | 无 | 新增 |
| `POST /api/v1/parse-preview` | 无 | 新增 |

---

## 五、改造优先级

### 阶段一（核心）

1. 新增 `collector.py` 蓝图
2. 新增 `collector_source`、`collector_task`、`collector_item` 集合
3. 实现采集源 CRUD 接口
4. 实现采集任务 CRUD 接口

### 阶段二（完善）

5. 实现采集结果查询接口
6. 实现链接预解析接口
7. 实现健康检查接口
8. 实现任务日志接口

### 阶段三（优化）

9. 实现幂等控制
10. 实现重试/重新解析/忽略/恢复接口
11. 现有数据迁移到新集合
12. 内部鉴权（X-Internal-Token）

---

## 六、文件改造清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `server/app/routes/collector.py` | 新增 | collector-service 对外 API |
| `server/app/models/collector_source.py` | 新增 | 采集源模型 |
| `server/app/models/collector_task.py` | 新增 | 采集任务模型 |
| `server/app/models/collector_item.py` | 新增 | 采集结果模型 |
| `server/app/models/collector_log.py` | 新增 | 任务日志模型 |
| `server/app/routes/__init__.py` | 修改 | 注册 collector 蓝图 |
| `server/app/__init__.py` | 修改 | 注册 collector 蓝图 |
| `server/app/routes/admin.py` | 保留 | 管理端接口（内部使用） |
| `server/app/routes/client.py` | 保留 | 客户端接口（内部使用） |
