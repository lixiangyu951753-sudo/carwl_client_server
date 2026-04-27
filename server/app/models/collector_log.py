from datetime import datetime
import uuid


def add_collector_log(task_id: str, level: str, event_code: str, message: str, context: dict = None) -> dict:
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
