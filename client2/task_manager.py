import time
import threading
from api_client import ClientAPI


class TaskManager:
    def __init__(self, api_client: ClientAPI, heartbeat_interval: int = 5):
        self.api = api_client
        self.heartbeat_interval = heartbeat_interval
        self.current_task_id = None
        self.running = False
        self._stop_event = threading.Event()
        self._crawl_callback = None

    def set_crawl_callback(self, callback):
        self._crawl_callback = callback

    def start_task(self, task_id: str, params: dict):
        print(f"\n[任务管理] 开始执行任务: {task_id}")
        print(f"[任务管理] 参数: {params}")
        self.current_task_id = task_id
        self.running = True

        self.api.report_progress(task_id, "running", progress={"status": "starting"})

        try:
            if self._crawl_callback:
                result = self._crawl_callback(task_id, params)
                if result:
                    self.api.report_result(
                        task_id,
                        result.get("batch_id", ""),
                        result.get("products", [])
                    )
            else:
                print("[任务管理] 未设置爬取回调函数")
                self.api.report_progress(task_id, "failed", error="未设置爬取回调")
        except Exception as e:
            print(f"[任务管理] 任务执行失败: {e}")
            self.api.report_progress(task_id, "failed", error=str(e))
        finally:
            self.running = False
            self.current_task_id = None

    def stop_task(self):
        print("[任务管理] 收到停止指令")
        self._stop_event.set()
        self.running = False

    def run(self):
        print(f"[任务管理] 客户端启动，ID: {self.api.client_id}")
        print(f"[任务管理] 服务端: {self.api.server_url}")
        print(f"[任务管理] 心跳间隔: {self.heartbeat_interval}秒")
        print("=" * 50)

        while not self._stop_event.is_set():
            status = "running" if self.running else "idle"
            resp = self.api.heartbeat(status=status, current_task=self.current_task_id)

            instruction = resp.get("instruction", "none")

            if instruction == "start_crawl" and not self.running:
                task_id = resp.get("task_id")
                params = resp.get("params", {})
                self.start_task(task_id, params)
            elif instruction == "stop_crawl":
                self.stop_task()
            elif instruction == "none":
                pass

            self._stop_event.wait(self.heartbeat_interval)

        print("[任务管理] 客户端已停止")
