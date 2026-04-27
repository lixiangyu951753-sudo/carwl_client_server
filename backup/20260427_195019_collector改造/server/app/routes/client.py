from flask import Blueprint

bp = Blueprint('client', __name__)

@bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    from flask import request, jsonify
    from app.models import update_client_heartbeat, get_pending_task_for_client
    
    data = request.get_json()
    client_id = data.get('client_id')
    status = data.get('status', 'idle')
    current_task = data.get('current_task')
    
    if not client_id:
        return jsonify({"code": 400, "message": "client_id is required"}), 400
    
    update_client_heartbeat(client_id, status, current_task)
    
    task = get_pending_task_for_client(client_id)
    
    if task:
        instruction_data = {
            "instruction": task.get("instruction", "start_crawl"),
            "task_id": task["task_id"],
            "params": task.get("params", {})
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
    
    data = request.get_json()
    client_id = data.get('client_id')
    task_id = data.get('task_id')
    status = data.get('status', 'running')
    progress = data.get('progress')
    error = data.get('error')
    
    if not task_id:
        return jsonify({"code": 400, "message": "task_id is required"}), 400
    
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
    
    data = request.get_json()
    client_id = data.get('client_id')
    task_id = data.get('task_id')
    batch_id = data.get('batch_id')
    products = data.get('products', [])
    
    if not task_id:
        return jsonify({"code": 400, "message": "task_id is required"}), 400
    
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
