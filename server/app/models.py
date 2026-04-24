from datetime import datetime

def get_db():
    from app import db
    return db

def create_client(client_id, name=None, ip_address=None):
    db = get_db()
    existing = db.clients.find_one({"client_id": client_id})
    if existing:
        return existing
    
    doc = {
        "client_id": client_id,
        "name": name or client_id,
        "ip_address": ip_address,
        "status": "online",
        "last_heartbeat": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    db.clients.insert_one(doc)
    return doc

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

def create_task(instruction, params, client_id=None):
    db = get_db()
    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    doc = {
        "task_id": task_id,
        "client_id": client_id,
        "status": "pending",
        "instruction": instruction,
        "params": params,
        "result": None,
        "progress": None,
        "started_at": None,
        "completed_at": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    db.tasks.insert_one(doc)
    return doc

def get_pending_task_for_client(client_id):
    db = get_db()
    task = db.tasks.find_one_and_update(
        {"status": "pending", "$or": [{"client_id": None}, {"client_id": client_id}]},
        {"$set": {"status": "running", "client_id": client_id, "started_at": datetime.now(), "updated_at": datetime.now()}},
        sort=[("created_at", 1)]
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

def cancel_task(task_id):
    db = get_db()
    db.tasks.update_one(
        {"task_id": task_id, "status": {"$in": ["pending", "running"]}},
        {"$set": {"status": "cancelled", "updated_at": datetime.now()}}
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
