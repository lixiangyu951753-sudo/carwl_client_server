from flask import Blueprint

bp = Blueprint('admin', __name__)

@bp.route('/tasks', methods=['GET'])
def get_tasks():
    from flask import request, jsonify
    from app import db
    
    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 20))
    
    query = {}
    if status:
        query["status"] = status
    
    total = db.tasks.count_documents(query)
    tasks = list(db.tasks.find(query, {"_id": 0})
                 .sort("created_at", -1)
                 .skip((page - 1) * size)
                 .limit(size))
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "total": total,
            "page": page,
            "size": size,
            "list": tasks
        }
    })

@bp.route('/tasks', methods=['POST'])
def create_task():
    from flask import request, jsonify
    from app.models import create_task
    
    data = request.get_json()
    instruction = data.get('instruction', 'start_crawl')
    params = data.get('params', {})
    client_id = data.get('client_id')
    
    task = create_task(instruction, params, client_id)
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "task_id": task["task_id"],
            "status": task["status"]
        }
    })

@bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    from flask import jsonify
    from app import db
    
    task = db.tasks.find_one({"task_id": task_id}, {"_id": 0})
    if not task:
        return jsonify({"code": 404, "message": "task not found"}), 404
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": task
    })

@bp.route('/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    from flask import jsonify
    from app.models import cancel_task
    
    cancel_task(task_id)
    
    return jsonify({
        "code": 200,
        "message": "success"
    })

@bp.route('/clients', methods=['GET'])
def get_clients():
    from flask import jsonify
    from app import db
    
    clients = list(db.clients.find({}, {"_id": 0}))
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": clients
    })

@bp.route('/clients/<client_id>/status', methods=['GET'])
def get_client_status(client_id):
    from flask import jsonify
    from app import db
    
    client = db.clients.find_one({"client_id": client_id}, {"_id": 0})
    if not client:
        return jsonify({"code": 404, "message": "client not found"}), 404
    
    tasks = list(db.tasks.find({"client_id": client_id}, {"_id": 0})
                 .sort("created_at", -1).limit(10))
    client["recent_tasks"] = tasks
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": client
    })

@bp.route('/dashboard', methods=['GET'])
def dashboard():
    from flask import jsonify
    from app import db
    from datetime import datetime, timedelta
    
    total_tasks = db.tasks.count_documents({})
    pending_tasks = db.tasks.count_documents({"status": "pending"})
    running_tasks = db.tasks.count_documents({"status": "running"})
    completed_tasks = db.tasks.count_documents({"status": "completed"})
    failed_tasks = db.tasks.count_documents({"status": "failed"})
    
    online_clients = db.clients.count_documents({
        "last_heartbeat": {"$gte": datetime.now() - timedelta(seconds=30)}
    })
    total_clients = db.clients.count_documents({})
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "tasks": {
                "total": total_tasks,
                "pending": pending_tasks,
                "running": running_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks
            },
            "clients": {
                "total": total_clients,
                "online": online_clients
            }
        }
    })
