import requests
from datetime import datetime


class CollectorAPIClient:
    def __init__(self, base_url: str = "http://localhost:5000/api/v1"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            result = response.json()
            if result.get("code") != "OK":
                raise Exception(result.get("message", "请求失败"))
            return result.get("data")
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            raise

    def _get(self, path: str, params: dict = None):
        return self._request("GET", path, params=params)

    def _post(self, path: str, json: dict = None):
        return self._request("POST", path, json=json)

    def health(self):
        return self._get("/health")

    def list_sources(self, page=1, page_size=20, keyword=None, platform=None, source_type=None, status=None):
        params = {"page": page, "pageSize": page_size}
        if keyword:
            params["keyword"] = keyword
        if platform:
            params["platform"] = platform
        if source_type:
            params["sourceType"] = source_type
        if status:
            params["status"] = status
        return self._get("/sources", params=params)

    def get_source_detail(self, source_id: str):
        return self._get("/sources/detail", params={"sourceId": source_id})

    def create_source(self, source_code: str, source_name: str, platform: str,
                     source_type: str = "url", entry_url: str = None,
                     parser_code: str = None, config: dict = None, **kwargs):
        data = {
            "sourceCode": source_code,
            "sourceName": source_name,
            "platform": platform,
            "sourceType": source_type,
        }
        if entry_url:
            data["entryUrl"] = entry_url
        if parser_code:
            data["parserCode"] = parser_code
        if config:
            data["config"] = config
        data.update(kwargs)
        return self._post("/sources/create", json=data)

    def update_source(self, source_id: str, **kwargs):
        data = {"sourceId": source_id}
        data.update(kwargs)
        return self._post("/sources/update", json=data)

    def enable_source(self, source_id: str):
        return self._post("/sources/enable", json={"sourceId": source_id})

    def disable_source(self, source_id: str):
        return self._post("/sources/disable", json={"sourceId": source_id})

    def delete_source(self, source_id: str):
        return self._post("/sources/delete", json={"sourceId": source_id})

    def parse_preview(self, url: str):
        return self._post("/parse-preview", json={"url": url})

    def create_task(self, task_type: str, source_id: str = None,
                   target_urls: list = None, options: dict = None,
                   operator_id: str = None, idempotency_key: str = None, **kwargs):
        data = {"taskType": task_type}
        if source_id:
            data["sourceId"] = source_id
        if target_urls:
            data["targetUrls"] = target_urls
        if options:
            data["options"] = options
        if operator_id:
            data["operatorId"] = operator_id
        if idempotency_key:
            data["idempotencyKey"] = idempotency_key
        data.update(kwargs)
        return self._post("/tasks/create", json=data)

    def list_tasks(self, page=1, page_size=20, status=None, task_type=None,
                   source_id=None, keyword=None, created_at_start=None, created_at_end=None):
        params = {"page": page, "pageSize": page_size}
        if status:
            params["status"] = status
        if task_type:
            params["taskType"] = task_type
        if source_id:
            params["sourceId"] = source_id
        if keyword:
            params["keyword"] = keyword
        if created_at_start:
            params["createdAtStart"] = created_at_start
        if created_at_end:
            params["createdAtEnd"] = created_at_end
        return self._get("/tasks", params=params)

    def get_task_detail(self, task_id: str):
        return self._get("/tasks/detail", params={"taskId": task_id})

    def cancel_task(self, task_id: str):
        return self._post("/tasks/cancel", json={"taskId": task_id})

    def retry_task(self, task_id: str):
        return self._post("/tasks/retry", json={"taskId": task_id})

    def list_items(self, page=1, page_size=20, task_id=None, platform=None,
                   parse_status=None, keyword=None):
        params = {"page": page, "pageSize": page_size}
        if task_id:
            params["taskId"] = task_id
        if platform:
            params["platform"] = platform
        if parse_status:
            params["parseStatus"] = parse_status
        if keyword:
            params["keyword"] = keyword
        return self._get("/items", params=params)

    def get_item_detail(self, item_id: str):
        return self._get("/items/detail", params={"itemId": item_id})

    def reparse_item(self, item_id: str):
        return self._post("/items/reparse", json={"itemId": item_id})

    def ignore_item(self, item_id: str):
        return self._post("/items/ignore", json={"itemId": item_id})

    def restore_item(self, item_id: str):
        return self._post("/items/restore", json={"itemId": item_id})


if __name__ == "__main__":
    client = CollectorAPIClient("http://localhost:5000/api/v1")

    print("=" * 50)
    print("Collector API 调用示例")
    print("=" * 50)

    print("\n1. 健康检查...")
    health = client.health()
    print(f"   服务状态: {health['status']}")
    print(f"   数据库: {health['dependencies']['database']}")

    print("\n2. 获取采集源列表...")
    sources = client.list_sources(page=1, page_size=10)
    print(f"   总数: {sources['total']}")
    print(f"   当前页: {sources['page']}")
    for item in sources.get("items", []):
        print(f"   - {item['sourceCode']}: {item['sourceName']} ({item['status']})")

    print("\n3. 创建采集源...")
    new_source = client.create_source(
        source_code=f"SRC_TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        source_name="测试采集源",
        platform="1688",
        source_type="url",
        entry_url="https://example.1688.com"
    )
    print(f"   创建成功: {new_source['sourceId']}")

    print("\n4. 获取采集源详情...")
    detail = client.get_source_detail(new_source["sourceId"])
    print(f"   名称: {detail['sourceName']}")
    print(f"   平台: {detail['platform']}")

    print("\n5. 创建采集任务...")
    new_task = client.create_task(
        task_type="shop",
        source_id=new_source["sourceId"],
        options={"maxItems": 100, "concurrency": 3}
    )
    print(f"   任务ID: {new_task['taskId']}")
    print(f"   任务号: {new_task['taskNo']}")
    print(f"   状态: {new_task['status']}")

    print("\n6. 获取任务列表...")
    tasks = client.list_tasks(status="pending", page=1, page_size=5)
    print(f"   总数: {tasks['total']}")

    print("\n7. 获取任务详情...")
    task_detail = client.get_task_detail(new_task["taskId"])
    print(f"   任务类型: {task_detail['taskType']}")
    print(f"   进度: {task_detail['progress']}%")

    print("\n8. 取消任务...")
    client.cancel_task(new_task["taskId"])
    print("   取消成功")

    print("\n9. 获取采集结果列表...")
    items = client.list_items(page=1, page_size=10)
    print(f"   总数: {items['total']}")

    print("\n" + "=" * 50)
    print("示例完成")
    print("=" * 50)
