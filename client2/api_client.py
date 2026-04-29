import requests
from datetime import datetime


class ClientAPI:
    def __init__(self, client_id: str, server_url: str):
        self.client_id = client_id
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-Client-ID': client_id
        })

    def heartbeat(self, status: str = 'idle', current_task: str = None, client_type: str = None) -> dict:
        data = {
            "client_id": self.client_id,
            "status": status,
            "current_task": current_task,
            "client_type": client_type,
            "timestamp": datetime.now().isoformat()
        }
        try:
            resp = self.session.post(
                f"{self.server_url}/client/heartbeat",
                json=data, timeout=10
            )
            result = resp.json()
            if result.get('code') == 200:
                return result.get('data', {})
            return {"instruction": "none"}
        except requests.exceptions.ConnectionError:
            print("[心跳] 无法连接服务端，等待重连...")
            return {"instruction": "none"}
        except Exception as e:
            print(f"[心跳] 错误: {e}")
            return {"instruction": "none"}

    def report_progress(self, task_id: str, status: str, progress: dict = None, error: str = None):
        data = {
            "client_id": self.client_id,
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        try:
            self.session.post(
                f"{self.server_url}/client/task_report",
                json=data, timeout=10
            )
        except Exception as e:
            print(f"[进度上报] 错误: {e}")

    def report_result(self, task_id: str, batch_id: str, products: list):
        data = {
            "client_id": self.client_id,
            "task_id": task_id,
            "batch_id": batch_id,
            "products": products,
            "timestamp": datetime.now().isoformat()
        }
        try:
            self.session.post(
                f"{self.server_url}/client/task_result",
                json=data, timeout=30
            )
            print(f"[结果上报] 成功，共 {len(products)} 个商品")
        except Exception as e:
            print(f"[结果上报] 错误: {e}")
