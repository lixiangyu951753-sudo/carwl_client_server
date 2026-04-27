from datetime import datetime
import uuid


def create_collector_task(data: dict) -> dict:
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
