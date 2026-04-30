from flask import Blueprint

bp = Blueprint('client', __name__)


def _collector_task_to_instruction(task):
    task_type = task.get("taskType", "single_url")
    options = task.get("options", {})
    params = {}

    if task_type == "single_url":
        params["shop_url"] = task.get("targetUrls", [""])[0] if task.get("targetUrls") else ""
        params["instruction"] = "start_crawl"
    elif task_type == "batch_url":
        params["shop_url"] = task.get("targetUrls", [""])[0] if task.get("targetUrls") else ""
        params["target_urls"] = task.get("targetUrls", [])
        params["instruction"] = "start_crawl"
    elif task_type == "shop":
        params["shop_url"] = task.get("shopUrl", "")
        params["instruction"] = "start_crawl"
    elif task_type == "shop_price":
        params["shop_url"] = task.get("shopUrl", "")
        params["instruction"] = "start_crawl"
    elif task_type == "shop_image":
        params["shop_url"] = task.get("shopUrl", "")
        params["instruction"] = "start_crawl"
    elif task_type == "keyword":
        params["keyword"] = task.get("keyword", "")
        params["instruction"] = "start_crawl"

    params["max_items"] = options.get("maxItems", 0)
    params["concurrency"] = options.get("concurrency", 1)
    params["save_raw_html"] = options.get("saveRawHtml", False)
    params["save_images_to_oss"] = options.get("saveImagesToOss", True)
    params["timeout_seconds"] = options.get("timeoutSeconds", 30)
    params["retry_times"] = options.get("retryTimes", 2)
    params["dedupe_strategy"] = options.get("dedupeStrategy", "platform_product_id")

    return {
        "instruction": "start_crawl",
        "task_id": task["taskId"],
        "params": params,
        "_source": "collector_task"
    }


@bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    from flask import request, jsonify
    from app.models import update_client_heartbeat, get_pending_task_for_client, get_pending_collector_task

    data = request.get_json()
    client_id = data.get('client_id')
    status = data.get('status', 'idle')
    current_task = data.get('current_task')
    client_type = data.get('client_type')
    client_capabilities = data.get('client_capabilities')

    if not client_id:
        return jsonify({"code": 400, "message": "client_id is required"}), 400

    update_client_heartbeat(client_id, status, current_task, client_type=client_type, client_capabilities=client_capabilities)

    # 检查客户端当前执行的任务是否被取消
    if current_task:
        collector_task = db.collector_tasks.find_one({"taskId": current_task})
        if collector_task and collector_task.get("status") == "canceled":
            return jsonify({
                "code": 200,
                "message": "success",
                "data": {
                    "instruction": "stop_crawl",
                    "task_id": current_task,
                    "reason": "task_canceled_by_server"
                }
            })

    collector_task = get_pending_collector_task(client_id, client_type, client_capabilities)
    if collector_task:
        instruction_data = _collector_task_to_instruction(collector_task)
    else:
        task = get_pending_task_for_client(client_id)
        if task:
            instruction_data = {
                "instruction": task.get("instruction", "start_crawl"),
                "task_id": task.get("task_id"),
                "params": task.get("params", {}),
                "_source": "task"
            }
        else:
            instruction_data = {
                "instruction": "none"
            }

    return jsonify({
        "code": 200,
        "message": "success",
        "data": instruction_data
    })

@bp.route('/task_report', methods=['POST'])
def task_report():
    from flask import request, jsonify
    from app.models import update_task_progress, add_log
    from app import db
    from datetime import datetime

    data = request.get_json()
    client_id = data.get('client_id')
    task_id = data.get('task_id')
    status = data.get('status', 'running')
    progress = data.get('progress')
    error = data.get('error')

    if not task_id:
        return jsonify({"code": 400, "message": "task_id is required"}), 400

    collector_task = db.collector_tasks.find_one({"taskId": task_id})
    if collector_task:
        update_data = {
            "status": status,
            "updatedAt": datetime.now().isoformat()
        }
        if progress:
            if isinstance(progress, dict):
                if "current_product" in progress:
                    update_data["successCount"] = progress.get("current_product", 0)
                if "current_page" in progress:
                    update_data["progress"] = min(99, int(progress.get("current_page", 0) / max(progress.get("total_pages", 1), 1) * 100))
            else:
                update_data["progress"] = progress
        if error:
            update_data["errorMessage"] = error
        if status in ["completed", "succeeded"]:
            update_data["status"] = "succeeded"
            update_data["finishedAt"] = datetime.now().isoformat()
            update_data["progress"] = 100
        elif status == "failed":
            update_data["status"] = "failed"
            update_data["finishedAt"] = datetime.now().isoformat()
        db.collector_tasks.update_one(
            {"taskId": task_id},
            {"$set": update_data}
        )
    else:
        update_task_progress(task_id, status, progress, error)

    if error:
        add_log(task_id, "error", error)

    return jsonify({
        "code": 200,
        "message": "success"
    })

@bp.route('/task_result', methods=['POST'])
def task_result():
    from flask import request, jsonify
    from app.models import update_task_result, update_task_progress, add_log
    from app import db
    from datetime import datetime
    import uuid

    data = request.get_json()
    client_id = data.get('client_id')
    task_id = data.get('task_id')
    batch_id = data.get('batch_id')
    products = data.get('products', [])

    if not task_id:
        return jsonify({"code": 400, "message": "task_id is required"}), 400

    collector_task = db.collector_tasks.find_one({"taskId": task_id})
    if collector_task:
        platform = collector_task.get("taskType", "shop")
        source_id = collector_task.get("sourceId", "")

        for product in products:
            source_url = product.get("url", "")
            source_product_id = ""
            dedupe_key = ""

            if "1688.com" in source_url:
                import re
                match = re.search(r'offer/(\d+)', source_url)
                if match:
                    source_product_id = match.group(1)
                    dedupe_key = f"1688:{source_product_id}"

            if not dedupe_key:
                dedupe_key = f"unknown:{source_url}"

            image_urls = product.get("images", [])
            main_image_url = image_urls[0] if image_urls else ""

            item = {
                "itemId": f"item_{uuid.uuid4().hex[:8]}",
                "taskId": task_id,
                "platform": "1688",
                "sourceUrl": source_url,
                "sourceProductId": source_product_id,
                "dedupeKey": dedupe_key,
                "title": product.get("title", ""),
                "subTitle": "",
                "description": product.get("description", ""),
                "mainImageUrl": main_image_url,
                "imageUrls": image_urls,
                "priceMin": product.get("priceMin", ""),
                "priceMax": product.get("priceMax", ""),
                "currency": "CNY",
                "supplierName": product.get("supplierName", ""),
                "supplierUrl": product.get("supplierUrl", ""),
                "shopName": product.get("shopName", ""),
                "rawData": product.get("rawData", {}),
                "normalizedData": {},
                "parseStatus": "parsed",
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }
            db.collector_items.insert_one(item)

        success_count = len(products)
        db.collector_tasks.update_one(
            {"taskId": task_id},
            {"$set": {
                "status": "succeeded",
                "progress": 100,
                "successCount": success_count,
                "totalCount": max(collector_task.get("totalCount", 0), success_count),
                "finishedAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }}
        )
    else:
        result = {
            "batch_id": batch_id,
            "products": products,
            "products_count": len(products)
        }
        update_task_result(task_id, result)
        update_task_progress(task_id, "completed")

    add_log(task_id, "info", f"任务完成，共 {len(products)} 个商品")

    return jsonify({
        "code": 200,
        "message": "success"
    })
