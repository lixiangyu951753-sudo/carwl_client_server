import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5001/api/v1"

HEADERS = {
    "Content-Type": "application/json",
    "X-Trace-Id": "trace_web_" + datetime.now().strftime("%Y%m%d%H%M%S"),
    "X-Request-Id": "req_" + datetime.now().strftime("%Y%m%d%H%M%S")
}


def print_response(label: str, resp: requests.Response):
    print(f"\n{'=' * 60}")
    print(f"{label}")
    print(f"URL: {resp.request.method} {resp.request.url}")
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), ensure_ascii=False, indent=2)}")
    print(f"{'=' * 60}")


def create_source(source_code: str, source_name: str, platform: str, capability: str = "", source_type: str = "url", entry_url: str = None):
    """创建采集源"""
    data = {
        "sourceCode": source_code,
        "sourceName": source_name,
        "platform": platform,
        "capability": capability,
        "sourceType": source_type,
    }
    if entry_url:
        data["entryUrl"] = entry_url
    resp = requests.post(f"{BASE_URL}/sources/create", json=data, headers=HEADERS)
    print_response("创建采集源", resp)
    return resp.json()


def create_shop_task(shop_url: str, source_id: str = "", platform: str = "", capability: str = "", max_items: int = 200):
    """店铺采集任务"""
    data = {
        "taskType": "shop_price",
        "sourceId": source_id,
        "platform": platform,
        "capability": capability,
        "shopUrl": shop_url,
        "options": {
            "maxItems": max_items,
            "concurrency": 3,
            "saveImagesToOss": True,
            "saveRawHtml": False,
            "timeoutSeconds": 30,
            "retryTimes": 2
        },
        "operatorId": "admin"
    }
    resp = requests.post(f"{BASE_URL}/tasks/create", json=data, headers=HEADERS)
    print_response("店铺采集任务", resp)
    return resp.json()


def create_single_url_task(url: str, source_id: str = "", platform: str = "", capability: str = ""):
    """单链接采集任务"""
    data = {
        "taskType": "single_url",
        "sourceId": source_id,
        "platform": platform,
        "capability": capability,
        "targetUrls": [url],
        "options": {
            "maxItems": 1,
            "concurrency": 1,
            "saveImagesToOss": True,
            "dedupeStrategy": "platform_product_id"
        },
        "operatorId": "admin"
    }
    resp = requests.post(f"{BASE_URL}/tasks/create", json=data, headers=HEADERS)
    print_response("单链接采集任务", resp)
    return resp.json()


def create_batch_url_task(urls: list, source_id: str = "", platform: str = "", capability: str = "", max_items: int = 100):
    """批量链接采集任务"""
    data = {
        "taskType": "batch_url",
        "sourceId": source_id,
        "platform": platform,
        "capability": capability,
        "targetUrls": urls,
        "options": {
            "maxItems": max_items,
            "concurrency": 3,
            "saveImagesToOss": True,
            "timeoutSeconds": 30,
            "retryTimes": 2
        },
        "operatorId": "admin"
    }
    resp = requests.post(f"{BASE_URL}/tasks/create", json=data, headers=HEADERS)
    print_response("批量链接采集任务", resp)
    return resp.json()


def create_keyword_task(keyword: str, source_id: str = "", platform: str = "", capability: str = "", max_items: int = 100):
    """关键词采集任务"""
    data = {
        "taskType": "keyword",
        "sourceId": source_id,
        "platform": platform,
        "capability": capability,
        "keyword": keyword,
        "options": {
            "maxItems": max_items,
            "concurrency": 3,
            "saveImagesToOss": True,
            "timeoutSeconds": 30,
            "retryTimes": 2
        },
        "operatorId": "admin"
    }
    resp = requests.post(f"{BASE_URL}/tasks/create", json=data, headers=HEADERS)
    print_response("关键词采集任务", resp)
    return resp.json()


def query_task_detail(task_id: str):
    """查询任务详情"""
    resp = requests.get(f"{BASE_URL}/tasks/detail", params={"taskId": task_id}, headers=HEADERS)
    print_response(f"任务详情 - {task_id}", resp)
    return resp.json()


def list_tasks(status: str = None, task_type: str = None, page: int = 1, page_size: int = 20):
    """查询任务列表"""
    params = {"page": page, "pageSize": page_size}
    if status:
        params["status"] = status
    if task_type:
        params["taskType"] = task_type
    resp = requests.get(f"{BASE_URL}/tasks", params=params, headers=HEADERS)
    print_response(f"任务列表 - status={status}, type={task_type}", resp)
    return resp.json()


def cancel_task(task_id: str):
    """取消任务"""
    data = {"taskId": task_id}
    resp = requests.post(f"{BASE_URL}/tasks/cancel", json=data, headers=HEADERS)
    print_response(f"取消任务 - {task_id}", resp)
    return resp.json()


def retry_task(task_id: str):
    """重试任务"""
    data = {"taskId": task_id}
    resp = requests.post(f"{BASE_URL}/tasks/retry", json=data, headers=HEADERS)
    print_response(f"重试任务 - {task_id}", resp)
    return resp.json()


def query_items(task_id: str, page: int = 1, page_size: int = 20):
    """查询采集结果"""
    resp = requests.get(
        f"{BASE_URL}/items",
        params={"taskId": task_id, "page": page, "pageSize": page_size},
        headers=HEADERS
    )
    print_response(f"采集结果 - {task_id}", resp)
    return resp.json()


def preview_url(url: str):
    """链接预解析"""
    data = {"url": url}
    resp = requests.post(f"{BASE_URL}/parse-preview", json=data, headers=HEADERS)
    print_response(f"链接预解析 - {url}", resp)
    return resp.json()


def list_sources(keyword: str = None, platform: str = None, status: str = None):
    """查询采集源列表"""
    params = {}
    if keyword:
        params["keyword"] = keyword
    if platform:
        params["platform"] = platform
    if status:
        params["status"] = status
    resp = requests.get(f"{BASE_URL}/sources", params=params, headers=HEADERS)
    print_response("采集源列表", resp)
    return resp.json()


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# 运营工作台 - 多客户端采集任务测试脚本")
    print("#" * 60)

    print("\n--- 1. 查看已有的采集源 ---")
    sources = list_sources()

    print("\n--- 2. 创建多平台采集源 ---")
    
    # 1688 价格采集源
    # source_1688_price = create_source(
    #     source_code="src_1688_price",
    #     source_name="1688价格采集源",
    #     platform="1688",
    #     capability="price",
    #     entry_url="https://www.1688.com"
    # )
    
    # # 1688 图片采集源
    # source_1688_image = create_source(
    #     source_code="src_1688_image",
    #     source_name="1688图片采集源",
    #     platform="1688",
    #     capability="image",
    #     entry_url="https://www.1688.com"
    # )
    
    # # 京东价格采集源
    # source_jd_price = create_source(
    #     source_code="src_jd_price",
    #     source_name="京东价格采集源",
    #     platform="jd",
    #     capability="price",
    #     entry_url="https://www.jd.com"
    # )
    
    # # PDD采集源
    # source_pdd = create_source(
    #     source_code="src_pdd",
    #     source_name="拼多多采集源",
    #     platform="pdd",
    #     capability="price",
    #     entry_url="https://www.pinduoduo.com"
    # )

    # print("\n--- 3. 创建不同平台的采集任务 ---")
    
    # # 1688 价格采集任务
    task_1688_price = create_shop_task(
        shop_url="https://xindeyi.1688.com/page/offerlist.htm",
        source_id='src_9deb2db5',
        platform="1688",
        capability="image",
        max_items=200
    )
    
    # # 1688 图片采集任务
    # task_1688_image = create_shop_task(
    #     shop_url="https://xindeyi.1688.com/page/offerlist.htm",
    #     source_id=source_1688_image.get("data", {}).get("sourceId", ""),
    #     platform="1688",
    #     capability="image",
    #     max_items=200
    # )
    
    # # 京东价格采集任务
    # task_jd_price = create_keyword_task(
    #     keyword="手机",
    #     source_id=source_jd_price.get("data", {}).get("sourceId", ""),
    #     platform="jd",
    #     capability="price",
    #     max_items=100
    # )
    
    # # PDD采集任务
    # task_pdd = create_keyword_task(
    #     keyword="衣服",
    #     source_id=source_pdd.get("data", {}).get("sourceId", ""),
    #     platform="pdd",
    #     capability="price",
    #     max_items=100
    # )

    # print("\n--- 4. 查询所有任务列表 ---")
    # list_tasks()

    # print("\n--- 5. 查询 pending 状态的任务 ---")
    # list_tasks(status="pending")

    # print("\n" + "#" * 60)
    # print("# 测试完成！")
    # print("# 客户端心跳请求示例：")
    # print("# 1688价格客户端: {'client_id': 'client_1688_price_01', 'client_capabilities': {'platform': '1688', 'capabilities': ['price']}}")
    # print("# 1688图片客户端: {'client_id': 'client_1688_image_01', 'client_capabilities': {'platform': '1688', 'capabilities': ['image']}}")
    # print("# 京东价格客户端: {'client_id': 'client_jd_price_01', 'client_capabilities': {'platform': 'jd', 'capabilities': ['price']}}")
    # print("# PDD客户端: {'client_id': 'client_pdd_01', 'client_capabilities': {'platform': 'pdd', 'capabilities': ['price']}}")
    # print("#" * 60)
