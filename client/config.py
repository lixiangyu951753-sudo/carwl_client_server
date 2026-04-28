import os

CLIENT_ID = 'client_001'
SERVER_URL = 'http://localhost:5001'
HEARTBEAT_INTERVAL = 5

BASE_PATH = r'D:\client_001_output'

OSS_ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID', '')
OSS_ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET', '')
OSS_BUCKET = 'nexus-crawl-raw-dev'
OSS_REGION = 'cn-shenzhen'
OSS_FOLDER = 'temp/'
