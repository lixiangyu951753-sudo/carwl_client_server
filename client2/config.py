import os

CLIENT_ID = 'client_1688_price_01'

CLIENT_TYPE = 'shop_price'

CLIENT_CAPABILITIES = {
    "platform": "1688",
    "capabilities": ["price"]
}

SERVER_URL = 'http://localhost:5001/api'
HEARTBEAT_INTERVAL = 5
HEARTBEAT_TIMEOUT = 10
HEARTBEAT_MAX_RETRIES = 3

BASE_PATH = r'D:\client_002_output'

TASK_ACCEPT_TIMEOUT = 30
TASK_MAX_RETRIES = 3
TASK_RETRY_DELAY = 5
