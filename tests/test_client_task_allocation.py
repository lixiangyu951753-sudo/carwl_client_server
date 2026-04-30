import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'client'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'client2'))

from api_client import ClientAPI
from task_manager import TaskManager


class TestClientAPI(unittest.TestCase):

    def setUp(self):
        self.capabilities = {"platform": "1688", "capabilities": ["image"]}
        self.api = ClientAPI("test_client", "http://localhost:5001", self.capabilities)

    def test_init_with_capabilities(self):
        self.assertEqual(self.api.client_id, "test_client")
        self.assertEqual(self.api.client_capabilities, self.capabilities)

    def test_init_without_capabilities(self):
        api = ClientAPI("test_client", "http://localhost:5001")
        self.assertEqual(api.client_capabilities, {})

    @patch('api_client.requests.Session.post')
    def test_heartbeat_with_capabilities(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 200, "data": {"instruction": "none"}}
        mock_post.return_value = mock_resp

        result = self.api.heartbeat(status="idle", client_type="shop_image")

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        sent_data = call_args[1]['json']
        self.assertEqual(sent_data['client_id'], "test_client")
        self.assertEqual(sent_data['client_capabilities'], self.capabilities)
        self.assertEqual(result, {"instruction": "none"})

    @patch('api_client.requests.Session.post')
    def test_heartbeat_connection_error(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()

        result = self.api.heartbeat(status="idle")

        self.assertEqual(result.get("instruction"), "none")
        self.assertEqual(result.get("error"), "connection_error")

    @patch('api_client.requests.Session.post')
    def test_heartbeat_timeout(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        result = self.api.heartbeat(status="idle")

        self.assertEqual(result.get("instruction"), "none")
        self.assertEqual(result.get("error"), "timeout")

    @patch('api_client.requests.Session.post')
    def test_heartbeat_server_error(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 500, "message": "服务器内部错误"}
        mock_post.return_value = mock_resp

        result = self.api.heartbeat(status="idle")

        self.assertEqual(result.get("instruction"), "none")
        self.assertEqual(result.get("error"), "服务器内部错误")

    @patch('api_client.requests.Session.post')
    def test_accept_task_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 200}
        mock_post.return_value = mock_resp

        result = self.api.accept_task("task_123")

        self.assertTrue(result)
        call_args = mock_post.call_args
        sent_data = call_args[1]['json']
        self.assertEqual(sent_data['task_id'], "task_123")
        self.assertEqual(sent_data['status'], "accepted")

    @patch('api_client.requests.Session.post')
    def test_accept_task_failure(self, mock_post):
        mock_post.side_effect = Exception("网络错误")

        result = self.api.accept_task("task_123")

        self.assertFalse(result)

    @patch('api_client.requests.Session.post')
    def test_reject_task_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 200}
        mock_post.return_value = mock_resp

        result = self.api.reject_task("task_123", "参数校验失败")

        self.assertTrue(result)
        call_args = mock_post.call_args
        sent_data = call_args[1]['json']
        self.assertEqual(sent_data['status'], "rejected")
        self.assertEqual(sent_data['error'], "参数校验失败")

    @patch('api_client.requests.Session.post')
    def test_report_progress(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 200}
        mock_post.return_value = mock_resp

        self.api.report_progress("task_123", "running", progress={"status": "crawling"})

        mock_post.assert_called_once()

    @patch('api_client.requests.Session.post')
    def test_report_result(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 200}
        mock_post.return_value = mock_resp

        self.api.report_result("task_123", "batch_001", [{"title": "test"}])

        mock_post.assert_called_once()


class TestTaskManager(unittest.TestCase):

    def setUp(self):
        self.api = MagicMock(spec=ClientAPI)
        self.api.client_id = "test_client"
        self.api.server_url = "http://localhost:5001"
        self.api.client_capabilities = {"platform": "1688", "capabilities": ["image"]}
        self.api.accept_task.return_value = True
        self.api.heartbeat.return_value = {"instruction": "none"}
        self.manager = TaskManager(self.api, heartbeat_interval=1)

    def test_validate_task_valid(self):
        is_valid, msg = self.manager._validate_task("task_123", {"shop_url": "https://xxx.1688.com", "instruction": "start_crawl"})
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")

    def test_validate_task_empty_id(self):
        is_valid, msg = self.manager._validate_task("", {"shop_url": "https://xxx.1688.com"})
        self.assertFalse(is_valid)
        self.assertEqual(msg, "任务ID为空")

    def test_validate_task_empty_params(self):
        is_valid, msg = self.manager._validate_task("task_123", {})
        self.assertFalse(is_valid)
        self.assertEqual(msg, "任务参数为空")

    def test_validate_task_none_params(self):
        is_valid, msg = self.manager._validate_task("task_123", None)
        self.assertFalse(is_valid)

    def test_validate_task_missing_required_params(self):
        is_valid, msg = self.manager._validate_task("task_123", {"instruction": "start_crawl"})
        self.assertFalse(is_valid)
        self.assertIn("缺少必要参数", msg)

    def test_validate_task_with_keyword(self):
        is_valid, msg = self.manager._validate_task("task_123", {"keyword": "手机", "instruction": "start_crawl"})
        self.assertTrue(is_valid)

    def test_validate_task_with_target_urls(self):
        is_valid, msg = self.manager._validate_task("task_123", {"target_urls": ["https://xxx.1688.com"], "instruction": "start_crawl"})
        self.assertTrue(is_valid)

    def test_start_task_reject_invalid(self):
        self.manager.start_task("", {"shop_url": "https://xxx.1688.com"})
        self.api.reject_task.assert_called_once()

    def test_start_task_accept_valid(self):
        callback = MagicMock(return_value={"batch_id": "b1", "products": []})
        self.manager.set_crawl_callback(callback)

        self.manager.start_task("task_123", {"shop_url": "https://xxx.1688.com", "instruction": "start_crawl"})

        self.api.accept_task.assert_called_once_with("task_123")
        self.api.report_progress.assert_called()
        callback.assert_called_once()

    def test_start_task_accept_failure(self):
        self.api.accept_task.return_value = False

        self.manager.start_task("task_123", {"shop_url": "https://xxx.1688.com", "instruction": "start_crawl"})

        self.assertFalse(self.manager.running)

    def test_start_task_retry_on_failure(self):
        import config as test_config
        callback = MagicMock(side_effect=Exception("爬取失败"))
        self.manager.set_crawl_callback(callback)

        self.manager.start_task("task_123", {"shop_url": "https://xxx.1688.com", "instruction": "start_crawl"})

        self.assertEqual(callback.call_count, test_config.TASK_MAX_RETRIES + 1)
        self.api.report_progress.assert_called()

    def test_stop_task(self):
        self.manager.current_task_id = "task_123"
        self.manager.running = True

        self.manager.stop_task()

        self.api.report_progress.assert_called_with("task_123", "canceled", progress={"status": "stopped_by_server"})
        self.assertFalse(self.manager.running)

    def test_heartbeat_fail_count_reset(self):
        self.api.heartbeat.return_value = {"instruction": "none"}
        
        self.manager._heartbeat_fail_count = 2
        
        resp = self.api.heartbeat(status="idle")
        
        self.manager._heartbeat_fail_count = 0


class TestTaskAllocationCompatibility(unittest.TestCase):

    def test_client1_capabilities(self):
        capabilities = {"platform": "1688", "capabilities": ["image"]}
        api = ClientAPI("client_1688_image_01", "http://localhost:5001", capabilities)
        self.assertEqual(api.client_capabilities["platform"], "1688")
        self.assertIn("image", api.client_capabilities["capabilities"])

    def test_client2_capabilities(self):
        capabilities = {"platform": "1688", "capabilities": ["price"]}
        api = ClientAPI("client_1688_price_01", "http://localhost:5001", capabilities)
        self.assertEqual(api.client_capabilities["platform"], "1688")
        self.assertIn("price", api.client_capabilities["capabilities"])

    def test_old_client_compatibility(self):
        api = ClientAPI("client_old_01", "http://localhost:5001")
        self.assertEqual(api.client_capabilities, {})

    @patch('api_client.requests.Session.post')
    def test_heartbeat_sends_capabilities_when_present(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 200, "data": {"instruction": "none"}}
        mock_post.return_value = mock_resp

        capabilities = {"platform": "1688", "capabilities": ["image"]}
        api = ClientAPI("client_1688_image_01", "http://localhost:5001", capabilities)
        api.heartbeat(status="idle", client_type="shop_image")

        call_args = mock_post.call_args
        sent_data = call_args[1]['json']
        self.assertIn('client_capabilities', sent_data)
        self.assertEqual(sent_data['client_capabilities'], capabilities)

    @patch('api_client.requests.Session.post')
    def test_heartbeat_no_capabilities_when_empty(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 200, "data": {"instruction": "none"}}
        mock_post.return_value = mock_resp

        api = ClientAPI("client_old_01", "http://localhost:5001")
        api.heartbeat(status="idle", client_type="shop_image")

        call_args = mock_post.call_args
        sent_data = call_args[1]['json']
        self.assertNotIn('client_capabilities', sent_data)


if __name__ == '__main__':
    unittest.main()
