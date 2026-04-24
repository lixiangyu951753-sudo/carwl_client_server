import os

CLIENT_ID = 'client_001'
SERVER_URL = 'http://localhost:5000/api'
HEARTBEAT_INTERVAL = 5

BASE_PATH = r'D:\works\crawl\1688'

OSS_ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID', '')
OSS_ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET', '')
OSS_BUCKET = 'nexus-crawl-raw-dev'
OSS_REGION = 'cn-shenzhen'
OSS_FOLDER = 'temp/'
