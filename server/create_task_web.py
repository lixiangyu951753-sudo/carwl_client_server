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


def create_shop_task(shop_url: str, source_id: str = "src_1688_default", max_items: int = 200):
    """店铺采集任务"""
    data = {
        "taskType": "shop",
        "sourceId": source_id,
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


def create_single_url_task(url: str, source_id: str = "src_1688_default"):
    """单链接采集任务"""
    data = {
        "taskType": "single_url",
        "sourceId": source_id,
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


def create_batch_url_task(urls: list, source_id: str = "src_1688_default", max_items: int = 100):
    """批量链接采集任务"""
    data = {
        "taskType": "batch_url",
        "sourceId": source_id,
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


def create_keyword_task(keyword: str, source_id: str = "src_1688_default", max_items: int = 100):
    """关键词采集任务"""
    data = {
        "taskType": "keyword",
        "sourceId": source_id,
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
    print("# 运营工作台 - 创建采集任务测试脚本")
    print("#" * 60)

    print("\n--- 1. 查看可用的采集源 ---")
    sources = list_sources()

    # print("\n--- 2. 预解析一个商品链接 ---")
    # preview_url("https://detail.1688.com/offer/123456789.html")

    print("\n--- 3. 创建店铺采集任务 ---")
    shop_result = create_shop_task(
        shop_url="https://xindeyi.1688.com/page/offerlist.htm",
        max_items=200
    )
    shop_task_id = shop_result["data"]["taskId"]

    # print("\n--- 4. 创建单链接采集任务 ---")
    # single_result = create_single_url_task(
    #     url="https://detail.1688.com/offer/987654321.html"
    # )
    # single_task_id = single_result["data"]["taskId"]

    # print("\n--- 5. 创建批量链接采集任务 ---")
    # batch_result = create_batch_url_task(
    #     urls=[
    #         "https://detail.1688.com/offer/111111.html",
    #         "https://detail.1688.com/offer/222222.html",
    #         "https://detail.1688.com/offer/333333.html"
    #     ],
    #     max_items=50
    # )
    # batch_task_id = batch_result["data"]["taskId"]

    # print("\n--- 6. 创建关键词采集任务 ---")
    # keyword_result = create_keyword_task(
    #     keyword="moissanite necklace",
    #     max_items=100
    # )
    # keyword_task_id = keyword_result["data"]["taskId"]

    print("\n--- 7. 查询所有任务列表 ---")
    list_tasks()

    print("\n--- 8. 查询 pending 状态的任务 ---")
    list_tasks(status="pending")

    # print("\n--- 9. 查询店铺采集任务详情 ---")
    # query_task_detail(shop_task_id)

    # print("\n--- 10. 取消关键词采集任务 ---")
    # cancel_task(keyword_task_id)

    # print("\n--- 11. 查看取消后的任务列表 ---")
    # list_tasks(status="canceled")

    print("\n" + "#" * 60)
    print("# 测试完成！")
    print("#" * 60)

    # shop_result = create_shop_task(
    #     shop_url="https://xindeyi.1688.com/page/offerlist.htm",
    #     max_items=200
    # )
    # print(shop_result)
