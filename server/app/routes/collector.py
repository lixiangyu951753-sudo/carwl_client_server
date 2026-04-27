import re

from flask import Blueprint, request, jsonify
from datetime import datetime

bp = Blueprint('collector', __name__, url_prefix='/api/v1')


# ============ 健康检查 ============

@bp.route('/health', methods=['GET'])
def health():
    from app import db

    try:
        db.tasks.count_documents({})
        db_status = "ok"
    except Exception:
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
    from app import db
    from app.models.collector_source import create_collector_source

    data = request.get_json()
    source_code = data.get('sourceCode')
    source_name = data.get('sourceName')

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
    from app import db

    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({
            "code": "COLLECTOR_URL_REQUIRED",
            "message": "采集链接不能为空",
            "data": None
        }), 400

    platform = identify_platform(url)
    if not platform:
        return jsonify({
            "code": "COLLECTOR_URL_UNSUPPORTED",
            "message": "当前链接暂不支持采集",
            "data": None
        }), 400

    source_product_id = extract_product_id(url, platform)
    dedupe_key = f"{platform}:{source_product_id}"

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
    from app import db
    from app.models.collector_task import create_collector_task

    data = request.get_json()
    idempotency_key = data.get('idempotencyKey')
    task_type = data.get('taskType')
    source_id = data.get('sourceId')

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
    if platform == '1688':
        match = re.search(r'offer/(\d+)', url)
        if match:
            return match.group(1)

    return url
