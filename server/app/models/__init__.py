from datetime import datetime

from app.models.collector_source import create_collector_source, update_collector_source
from app.models.collector_task import create_collector_task
from app.models.collector_item import create_collector_item
from app.models.collector_log import add_collector_log


def get_db():
    from app import db
    return db


def update_client_heartbeat(client_id, status="online", current_task=None, ip_address=None):
    db = get_db()
    update_data = {
        "status": status if status != "idle" else "online",
        "last_heartbeat": datetime.now(),
        "updated_at": datetime.now()
    }
    if current_task:
        update_data["current_task"] = current_task
    if ip_address:
        update_data["ip_address"] = ip_address

    if status == "running":
        update_data["status"] = "busy"

    db.clients.update_one(
        {"client_id": client_id},
        {"$set": update_data},
        upsert=True
    )


def get_pending_task_for_client(client_id):
    db = get_db()
    task = db.tasks.find_one_and_update(
        {"status": "pending", "$or": [{"client_id": None}, {"client_id": client_id}]},
        {"$set": {"status": "running", "client_id": client_id, "started_at": datetime.now(), "updated_at": datetime.now()}},
        sort=[("created_at", 1)]
    )
    return task


def get_pending_collector_task(client_id, client_type=None):
    db = get_db()
    query = {"status": "pending"}
    if client_type:
        query["taskType"] = client_type
    task = db.collector_tasks.find_one_and_update(
        query,
        {"$set": {
            "status": "running",
            "clientId": client_id,
            "startedAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }},
        sort=[("createdAt", 1)]
    )
    return task


def update_task_progress(task_id, status, progress=None, error=None):
    db = get_db()
    update_data = {
        "status": status,
        "updated_at": datetime.now()
    }
    if progress:
        update_data["progress"] = progress
    if error:
        update_data["error"] = error
    if status == "completed":
        update_data["completed_at"] = datetime.now()

    db.tasks.update_one(
        {"task_id": task_id},
        {"$set": update_data}
    )


def update_task_result(task_id, result):
    db = get_db()
    db.tasks.update_one(
        {"task_id": task_id},
        {"$set": {"result": result, "updated_at": datetime.now()}}
    )


def add_log(task_id, level, message):
    db = get_db()
    doc = {
        "task_id": task_id,
        "level": level,
        "message": message,
        "created_at": datetime.now()
    }
    db.task_logs.insert_one(doc)
