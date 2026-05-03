import requests
import time
from datetime import datetime


class ClientAPI:
    def __init__(self, client_id: str, server_url: str, client_capabilities: dict = None):
        self.client_id = client_id
        self.server_url = server_url.rstrip('/')
        self.client_capabilities = client_capabilities or {}
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
            "client_capabilities": self.client_capabilities if self.client_capabilities else None,
            "timestamp": datetime.now().isoformat()
        }
        data = {k: v for k, v in data.items() if v is not None}
        try:
            resp = self.session.post(
                f"{self.server_url}/client/heartbeat",
                json=data, timeout=10
            )
            result = resp.json()
            if result.get('code') == 200:
                return result.get('data', {})
            return {"instruction": "none", "error": result.get('message', '未知错误')}
        except requests.exceptions.ConnectionError:
            print("[心跳] 无法连接服务端，等待重连...")
            return {"instruction": "none", "error": "connection_error"}
        except requests.exceptions.Timeout:
            print("[心跳] 请求超时")
            return {"instruction": "none", "error": "timeout"}
        except Exception as e:
            print(f"[心跳] 错误: {e}")
            return {"instruction": "none", "error": str(e)}

    def accept_task(self, task_id: str) -> bool:
        try:
            resp = self.session.post(
                f"{self.server_url}/client/task_report",
                json={
                    "client_id": self.client_id,
                    "task_id": task_id,
                    "status": "running",
                    "progress": {"status": "accepted", "timestamp": datetime.now().isoformat()},
                    "timestamp": datetime.now().isoformat()
                }, timeout=10
            )
            result = resp.json()
            return result.get('code') == 200
        except Exception as e:
            print(f"[任务确认] 确认接收失败: {e}")
            return False

    def reject_task(self, task_id: str, reason: str = "") -> bool:
        try:
            resp = self.session.post(
                f"{self.server_url}/client/task_report",
                json={
                    "client_id": self.client_id,
                    "task_id": task_id,
                    "status": "rejected",
                    "error": reason,
                    "timestamp": datetime.now().isoformat()
                }, timeout=10
            )
            result = resp.json()
            return result.get('code') == 200
        except Exception as e:
            print(f"[任务拒绝] 拒绝任务失败: {e}")
            return False

    def report_progress(self, task_id: str, status: str, progress: dict = None, error: str = None) -> bool:
        data = {
            "client_id": self.client_id,
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        for attempt in range(3):
            try:
                resp = self.session.post(
                    f"{self.server_url}/client/task_report",
                    json=data, timeout=10
                )
                result = resp.json()
                if result.get('code') == 200:
                    return True
                if result.get('message') == 'status transition rejected':
                    print(f"[进度上报] 状态转移被拒绝: {task_id} status={status}")
                    return False
            except Exception as e:
                if attempt < 2:
                    print(f"[进度上报] 重试 {attempt+1}/3: {e}")
                    time.sleep(1)
                else:
                    print(f"[进度上报] 最终错误: {e}")
        return False

    def report_result(self, task_id: str, batch_id: str, products: list) -> bool:  
        data = {
            "client_id": self.client_id,
            "task_id": task_id,
            "batch_id": batch_id,
            "products": products,
            "timestamp": datetime.now().isoformat()
        }
        for attempt in range(3):
            try:
                resp = self.session.post(
                    f"{self.server_url}/client/task_result",
                    json=data, timeout=30
                )
                result = resp.json()
                if result.get('code') == 200:
                    print(f"[结果上报] 成功，共 {len(products)} 个商品")
                    return True
            except Exception as e:
                if attempt < 2:
                    print(f"[结果上报] 重试 {attempt+1}/3: {e}")
                    time.sleep(2)
                else:
                    print(f"[结果上报] 最终错误: {e}")
        return False
