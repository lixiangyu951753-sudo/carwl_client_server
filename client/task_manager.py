import time
import threading
from api_client import ClientAPI
import config


class TaskManager:
    def __init__(self, api_client: ClientAPI, heartbeat_interval: int = 5):
        self.api = api_client
        self.heartbeat_interval = heartbeat_interval
        self.current_task_id = None
        self.running = False
        self._stop_event = threading.Event()
        self._crawl_callback = None
        self._heartbeat_fail_count = 0
        self._max_heartbeat_fails = config.HEARTBEAT_MAX_RETRIES

    def set_crawl_callback(self, callback):
        self._crawl_callback = callback

    def _validate_task(self, task_id: str, params: dict) -> tuple:
        if not task_id:
            return False, "任务ID为空"
        
        if not params:
            return False, "任务参数为空"
        
        shop_url = params.get('shop_url') or params.get('source_url')
        keyword = params.get('keyword')
        target_urls = params.get('target_urls', [])
        
        task_type = params.get('instruction', '')
        if task_type == 'start_crawl':
            if not shop_url and not keyword and not target_urls:
                return False, "缺少必要参数：shop_url/keyword/target_urls"
        
        return True, ""

    def start_task(self, task_id: str, params: dict):
        print(f"\n[任务管理] 收到任务: {task_id}")
        print(f"[任务管理] 参数: {params}")

        is_valid, error_msg = self._validate_task(task_id, params)
        if not is_valid:
            print(f"[任务管理] 任务参数校验失败: {error_msg}")
            self.api.reject_task(task_id, f"参数校验失败: {error_msg}")
            return

        accepted = self.api.accept_task(task_id)
        if not accepted:
            print(f"[任务管理] 任务确认接收失败，可能已被其他客户端处理")
            return

        print(f"[任务管理] 任务已确认接收: {task_id}")
        self.current_task_id = task_id
        self.running = True

        self.api.report_progress(task_id, "running", progress={"status": "starting"})

        retry_count = 0
        max_retries = config.TASK_MAX_RETRIES

        while retry_count <= max_retries:
            try:
                if self._crawl_callback:
                    result = self._crawl_callback(task_id, params)
                    if result:
                        if result.get("error"):
                            self.api.report_progress(task_id, "failed", error=result.get("error"))
                        else:
                            self.api.report_result(
                                task_id,
                                result.get("batch_id", ""),
                                result.get("products", [])
                            )
                    break
                else:
                    print("[任务管理] 未设置爬取回调函数")
                    self.api.report_progress(task_id, "failed", error="未设置爬取回调")
                    break
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                print(f"[任务管理] 任务执行失败 (第{retry_count}次): {error_msg}")
                
                if retry_count <= max_retries:
                    print(f"[任务管理] {config.TASK_RETRY_DELAY}秒后重试...")
                    self.api.report_progress(task_id, "running", progress={
                        "status": "retrying",
                        "retry_count": retry_count,
                        "max_retries": max_retries,
                        "error": error_msg
                    })
                    time.sleep(config.TASK_RETRY_DELAY)
                else:
                    print(f"[任务管理] 任务重试{max_retries}次后仍然失败")
                    self.api.report_progress(task_id, "failed", error=f"重试{max_retries}次后失败: {error_msg}")
            finally:
                if retry_count > max_retries or self._crawl_callback:
                    self.running = False
                    self.current_task_id = None

    def stop_task(self):
        print("[任务管理] 收到停止指令")
        task_to_cancel = self.current_task_id
        self.current_task_id = None
        self.running = False
        self._stop_event.set()
        if task_to_cancel:
            self.api.report_progress(task_to_cancel, "canceled", progress={"status": "stopped_by_server"})

    def run(self):
        print(f"[任务管理] 客户端启动，ID: {self.api.client_id}")
        print(f"[任务管理] 服务端: {self.api.server_url}")
        print(f"[任务管理] 心跳间隔: {self.heartbeat_interval}秒")
        
        capabilities = self.api.client_capabilities
        if capabilities:
            print(f"[任务管理] 平台: {capabilities.get('platform', 'N/A')}")
            print(f"[任务管理] 能力: {capabilities.get('capabilities', [])}")
        
        print("=" * 50)

        while not self._stop_event.is_set():
            status = "running" if self.running else "idle"
            resp = self.api.heartbeat(
                status=status,
                current_task=self.current_task_id,
                client_type=config.CLIENT_TYPE
            )

            instruction = resp.get("instruction", "none")
            error = resp.get("error")

            if error:
                self._heartbeat_fail_count += 1
                if error == "connection_error":
                    print(f"[任务管理] 服务端连接失败 ({self._heartbeat_fail_count}/{self._max_heartbeat_fails})")
                elif error == "timeout":
                    print(f"[任务管理] 心跳超时 ({self._heartbeat_fail_count}/{self._max_heartbeat_fails})")
                
                if self._heartbeat_fail_count >= self._max_heartbeat_fails:
                    print(f"[任务管理] 连续{self._heartbeat_fail_count}次心跳失败，进入等待重连模式")
                    wait_time = min(self.heartbeat_interval * (2 ** min(self._heartbeat_fail_count - self._max_heartbeat_fails, 4)), 120)
                    print(f"[任务管理] 等待 {wait_time}秒 后重试...")
                    self._stop_event.wait(wait_time)
                    continue
            else:
                self._heartbeat_fail_count = 0

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
