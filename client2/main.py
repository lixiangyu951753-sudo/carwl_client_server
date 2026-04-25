import os
import json
from datetime import datetime

from api_client import ClientAPI
from task_manager import TaskManager
import config

# 确保输出目录存在
if not os.path.exists(config.BASE_PATH):
    os.makedirs(config.BASE_PATH)

tasks_file = os.path.join(config.BASE_PATH, 'tasks.json')
batch_file = os.path.join(config.BASE_PATH, 'batch.json')

api = ClientAPI(config.CLIENT_ID, config.SERVER_URL)
manager = TaskManager(api, config.HEARTBEAT_INTERVAL)

def gen_batch_id() -> str:
    return datetime.now().strftime('%Y%m%d%H%M%S')

def load_batch() -> dict:
    if os.path.exists(batch_file):
        with open(batch_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_batch(batch_id: str, status: str, product_count: int = 0):
    batches = load_batch()
    batches[batch_id] = {
        'status': status,
        'product_count': product_count,
        'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump(batches, f, ensure_ascii=False, indent=2)

def load_tasks() -> dict:
    if os.path.exists(tasks_file):
        with open(tasks_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_task(task_id: str, status: str, file_name: str = None, url: str = None, batch_id: str = None, error: str = None):
    tasks = load_tasks()
    tasks[task_id] = {
        'status': status,
        'file_name': file_name,
        'url': url,
        'batch_id': batch_id,
        'error': error,
        'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(tasks_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def is_task_completed(task_id: str) -> bool:
    tasks = load_tasks()
    if task_id in tasks:
        return tasks[task_id].get('status') == 'completed'
    return False

# ==================== 爬虫逻辑（留空，由用户填充） ====================

def shop_detail(batch_id: str, server_task_id: str = None):
    """爬取单个商品详情"""
    # TODO: 实现商品详情爬取逻辑
    print("[爬虫] 爬取商品详情（待实现）")
    return {
        "task_id": "temp_task_id",
        "title": "测试商品",
        "url": "https://example.com/product",
        "status": "completed",
        "local_folder": "test"
    }

def shop_list(server_task_id: str = None):
    """爬取店铺商品列表"""
    # TODO: 实现商品列表爬取逻辑
    print("[爬虫] 爬取商品列表（待实现）")
    batch_id = gen_batch_id()
    save_batch(batch_id, 'running')
    
    # 模拟爬取结果
    products = [
        {
            "task_id": "test_1",
            "title": "测试商品1",
            "url": "https://example.com/product1",
            "status": "completed",
            "local_folder": "test1"
        },
        {
            "task_id": "test_2",
            "title": "测试商品2",
            "url": "https://example.com/product2",
            "status": "completed",
            "local_folder": "test2"
        }
    ]
    
    save_batch(batch_id, 'completed', product_count=len(products))
    print(f"[爬虫] 批次 {batch_id} 完成，共爬取 {len(products)} 个商品")
    
    return {
        "batch_id": batch_id,
        "products": products
    }

# ====================================================================

def crawl_callback(task_id: str, params: dict):
    """任务管理器回调函数"""
    shop_url = params.get('shop_url')
    max_pages = params.get('max_pages')

    if shop_url:
        print(f"[爬虫] 打开店铺: {shop_url}")
        # TODO: 实现打开店铺的逻辑

    result = shop_list(server_task_id=task_id)
    return result

def main():
    print("=" * 50)
    print("  1688远程控制爬虫客户端 (Client-002)")
    print("=" * 50)

    manager.set_crawl_callback(crawl_callback)
    manager.run()

if __name__ == '__main__':
    main()
