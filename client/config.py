import os

CLIENT_ID = 'client_1688_image_01'

CLIENT_TYPE = 'shop'

CLIENT_CAPABILITIES = {
    "platform": "1688",
    "capabilities": ["image"]
}

SERVER_URL = 'http://localhost:3015/api'
HEARTBEAT_INTERVAL = 5
HEARTBEAT_TIMEOUT = 10
HEARTBEAT_MAX_RETRIES = 3

BASE_PATH = r'D:\client_001_output'

TASK_ACCEPT_TIMEOUT = 30
TASK_MAX_RETRIES = 3
TASK_RETRY_DELAY = 5

OSS_ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID', '')
OSS_ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET', '')
OSS_BUCKET = 'nexus-crawl-raw-dev'
OSS_REGION = 'cn-shenzhen'
OSS_FOLDER = 'temp/'
