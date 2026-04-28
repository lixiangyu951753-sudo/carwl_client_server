from pymongo import MongoClient
from datetime import datetime
import uuid
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.environ.get("MONGO_DB", "crawler_db")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

now = datetime.now().isoformat()


def insert_test_sources():
    sources = [
        {
            "sourceId": "src_1688_default",
            "sourceCode": "SRC_1688_DEFAULT",
            "sourceName": "1688默认采集源",
            "platform": "1688",
            "sourceType": "url",
            "entryUrl": "https://www.1688.com",
            "parserCode": "1688_offer_v1",
            "config": {
                "rateLimitPerMinute": 60,
                "timeoutSeconds": 30,
                "retryTimes": 2,
                "saveRawHtml": False,
                "saveImagesToOss": True,
                "proxyProfileId": "proxy_default",
                "cookieProfileId": "cookie_1688_default"
            },
            "status": "enabled",
            "isDeleted": False,
            "createdBy": "admin",
            "updatedBy": "admin",
            "createdAt": now,
            "updatedAt": now
        },
        {
            "sourceId": "src_taobao_default",
            "sourceCode": "SRC_TAOBAO_DEFAULT",
            "sourceName": "淘宝默认采集源",
            "platform": "taobao",
            "sourceType": "url",
            "entryUrl": "https://www.taobao.com",
            "parserCode": "taobao_item_v1",
            "config": {
                "rateLimitPerMinute": 30,
                "timeoutSeconds": 45,
                "retryTimes": 3,
                "saveRawHtml": False,
                "saveImagesToOss": True
            },
            "status": "enabled",
            "isDeleted": False,
            "createdBy": "admin",
            "updatedBy": "admin",
            "createdAt": now,
            "updatedAt": now
        },
        {
            "sourceId": "src_disabled_test",
            "sourceCode": "SRC_DISABLED_TEST",
            "sourceName": "已停用测试采集源",
            "platform": "1688",
            "sourceType": "shop",
            "entryUrl": "https://testshop.1688.com",
            "parserCode": "1688_shop_v1",
            "config": {
                "rateLimitPerMinute": 20,
                "timeoutSeconds": 60,
                "retryTimes": 1
            },
            "status": "disabled",
            "isDeleted": False,
            "createdBy": "admin",
            "updatedBy": "admin",
            "createdAt": now,
            "updatedAt": now
        }
    ]

    db.collector_sources.delete_many({})
    db.collector_sources.insert_many(sources)
    print(f"已插入 {len(sources)} 条采集源数据")


def insert_test_tasks():
    tasks = [
        {
            "taskId": f"task_{uuid.uuid4().hex[:8]}",
            "taskNo": f"COL{datetime.now().strftime('%Y%m%d')}0001",
            "sourceId": "src_1688_default",
            "taskType": "shop",
            "status": "pending",
            "progress": 0,
            "totalCount": 200,
            "successCount": 0,
            "failedCount": 0,
            "duplicateCount": 0,
            "ignoredCount": 0,
            "shopUrl": "https://xindeyi.1688.com/page/offerlist.htm",
            "options": {
                "maxItems": 200,
                "concurrency": 3,
                "saveImagesToOss": True,
                "saveRawHtml": False,
                "timeoutSeconds": 30,
                "retryTimes": 2
            },
            "errorCode": None,
            "errorMessage": None,
            "operatorId": "admin",
            "startedAt": None,
            "finishedAt": None,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "taskId": f"task_{uuid.uuid4().hex[:8]}",
            "taskNo": f"COL{datetime.now().strftime('%Y%m%d')}0002",
            "sourceId": "src_1688_default",
            "taskType": "single_url",
            "status": "running",
            "progress": 45,
            "totalCount": 1,
            "successCount": 0,
            "failedCount": 0,
            "duplicateCount": 0,
            "ignoredCount": 0,
            "targetUrls": ["https://detail.1688.com/offer/123456789.html"],
            "options": {
                "maxItems": 1,
                "concurrency": 1,
                "saveImagesToOss": True,
                "dedupeStrategy": "platform_product_id"
            },
            "errorCode": None,
            "errorMessage": None,
            "operatorId": "admin",
            "startedAt": now,
            "finishedAt": None,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "taskId": f"task_{uuid.uuid4().hex[:8]}",
            "taskNo": f"COL{datetime.now().strftime('%Y%m%d')}0003",
            "sourceId": "src_1688_default",
            "taskType": "batch_url",
            "status": "succeeded",
            "progress": 100,
            "totalCount": 3,
            "successCount": 3,
            "failedCount": 0,
            "duplicateCount": 0,
            "ignoredCount": 0,
            "targetUrls": [
                "https://detail.1688.com/offer/111111.html",
                "https://detail.1688.com/offer/222222.html",
                "https://detail.1688.com/offer/333333.html"
            ],
            "options": {
                "maxItems": 3,
                "concurrency": 2,
                "saveImagesToOss": True
            },
            "errorCode": None,
            "errorMessage": None,
            "operatorId": "admin",
            "startedAt": now,
            "finishedAt": now,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "taskId": f"task_{uuid.uuid4().hex[:8]}",
            "taskNo": f"COL{datetime.now().strftime('%Y%m%d')}0004",
            "sourceId": "src_1688_default",
            "taskType": "keyword",
            "status": "failed",
            "progress": 20,
            "totalCount": 50,
            "successCount": 10,
            "failedCount": 5,
            "duplicateCount": 0,
            "ignoredCount": 0,
            "keyword": "moissanite necklace",
            "options": {
                "maxItems": 50,
                "concurrency": 3,
                "saveImagesToOss": True
            },
            "errorCode": "CRAWL_TIMEOUT",
            "errorMessage": "爬取超时，目标网站响应缓慢",
            "operatorId": "admin",
            "startedAt": now,
            "finishedAt": now,
            "createdAt": now,
            "updatedAt": now
        }
    ]

    db.collector_tasks.delete_many({})
    db.collector_tasks.insert_many(tasks)
    print(f"已插入 {len(tasks)} 条采集任务数据")
    return tasks


def insert_test_items(tasks):
    succeeded_task = None
    for t in tasks:
        if t["status"] == "succeeded":
            succeeded_task = t
            break

    if not succeeded_task:
        print("没有成功的任务，跳过采集结果插入")
        return

    items = [
        {
            "itemId": f"item_{uuid.uuid4().hex[:8]}",
            "taskId": succeeded_task["taskId"],
            "platform": "1688",
            "sourceUrl": "https://detail.1688.com/offer/111111.html",
            "sourceProductId": "111111",
            "dedupeKey": "1688:111111",
            "title": "莫桑石项链女 925银镀金锁骨链",
            "subTitle": "厂家直销 支持定制",
            "description": "高品质莫桑石，火彩闪耀，925银镀金工艺",
            "mainImageUrl": "https://cbu01.alicdn.com/img/ibank/O1CN01abc123_111111.jpg",
            "imageUrls": [
                "https://cbu01.alicdn.com/img/ibank/O1CN01abc123_111111.jpg",
                "https://cbu01.alicdn.com/img/ibank/O1CN01def456_111111.jpg",
                "https://cbu01.alicdn.com/img/ibank/O1CN01ghi789_111111.jpg"
            ],
            "priceMin": "28.50",
            "priceMax": "68.00",
            "currency": "CNY",
            "supplierName": "义乌市某某饰品厂",
            "supplierUrl": "https://shop123456.1688.com",
            "shopName": "某某饰品旗舰店",
            "rawData": {},
            "normalizedData": {},
            "parseStatus": "parsed",
            "createdAt": now,
            "updatedAt": now
        },
        {
            "itemId": f"item_{uuid.uuid4().hex[:8]}",
            "taskId": succeeded_task["taskId"],
            "platform": "1688",
            "sourceUrl": "https://detail.1688.com/offer/222222.html",
            "sourceProductId": "222222",
            "dedupeKey": "1688:222222",
            "title": "S925纯银莫桑石戒指 女款开口可调节",
            "subTitle": "一件代发 支持混批",
            "description": "S925纯银材质，莫桑石主石，开口设计可调节大小",
            "mainImageUrl": "https://cbu01.alicdn.com/img/ibank/O1CN01jkl012_222222.jpg",
            "imageUrls": [
                "https://cbu01.alicdn.com/img/ibank/O1CN01jkl012_222222.jpg",
                "https://cbu01.alicdn.com/img/ibank/O1CN01mno345_222222.jpg"
            ],
            "priceMin": "35.00",
            "priceMax": "89.00",
            "currency": "CNY",
            "supplierName": "义乌市某某饰品厂",
            "supplierUrl": "https://shop123456.1688.com",
            "shopName": "某某饰品旗舰店",
            "rawData": {},
            "normalizedData": {},
            "parseStatus": "parsed",
            "createdAt": now,
            "updatedAt": now
        },
        {
            "itemId": f"item_{uuid.uuid4().hex[:8]}",
            "taskId": succeeded_task["taskId"],
            "platform": "1688",
            "sourceUrl": "https://detail.1688.com/offer/333333.html",
            "sourceProductId": "333333",
            "dedupeKey": "1688:333333",
            "title": "莫桑石耳钉女 气质简约防过敏",
            "subTitle": "工厂直供 量大优惠",
            "description": "莫桑石耳钉，简约设计，防过敏材质",
            "mainImageUrl": "https://cbu01.alicdn.com/img/ibank/O1CN01pqr678_333333.jpg",
            "imageUrls": [
                "https://cbu01.alicdn.com/img/ibank/O1CN01pqr678_333333.jpg"
            ],
            "priceMin": "18.00",
            "priceMax": "45.00",
            "currency": "CNY",
            "supplierName": "义乌市某某饰品厂",
            "supplierUrl": "https://shop123456.1688.com",
            "shopName": "某某饰品旗舰店",
            "rawData": {},
            "normalizedData": {},
            "parseStatus": "parsed",
            "createdAt": now,
            "updatedAt": now
        }
    ]

    db.collector_items.delete_many({})
    db.collector_items.insert_many(items)
    print(f"已插入 {len(items)} 条采集结果数据")


def insert_test_logs(tasks):
    logs = []
    for task in tasks:
        task_id = task["taskId"]
        status = task["status"]

        logs.append({
            "logId": f"log_{uuid.uuid4().hex[:8]}",
            "taskId": task_id,
            "level": "info",
            "eventCode": "TASK_CREATED",
            "message": f"任务 {task['taskNo']} 创建成功",
            "context": {"taskType": task["taskType"]},
            "createdAt": now
        })

        if status in ["running", "succeeded", "failed"]:
            logs.append({
                "logId": f"log_{uuid.uuid4().hex[:8]}",
                "taskId": task_id,
                "level": "info",
                "eventCode": "TASK_STARTED",
                "message": "任务开始执行",
                "context": {},
                "createdAt": now
            })

        if status == "running":
            logs.append({
                "logId": f"log_{uuid.uuid4().hex[:8]}",
                "taskId": task_id,
                "level": "info",
                "eventCode": "CRAWL_PAGE_START",
                "message": "开始爬取第 1 页",
                "context": {"page": 1, "totalPages": 10},
                "createdAt": now
            })

        if status == "succeeded":
            logs.append({
                "logId": f"log_{uuid.uuid4().hex[:8]}",
                "taskId": task_id,
                "level": "info",
                "eventCode": "TASK_COMPLETED",
                "message": f"任务完成，共采集 {task['successCount']} 个商品",
                "context": {"successCount": task["successCount"]},
                "createdAt": now
            })

        if status == "failed":
            logs.append({
                "logId": f"log_{uuid.uuid4().hex[:8]}",
                "taskId": task_id,
                "level": "error",
                "eventCode": "TASK_FAILED",
                "message": task["errorMessage"],
                "context": {"errorCode": task["errorCode"]},
                "createdAt": now
            })

    db.collector_task_logs.delete_many({})
    db.collector_task_logs.insert_many(logs)
    print(f"已插入 {len(logs)} 条任务日志数据")


def insert_test_clients():
    clients = [
        {
            "client_id": "client_001",
            "name": "爬虫客户端-01",
            "ip_address": "192.168.1.100",
            "status": "online",
            "last_heartbeat": datetime.now(),
            "current_task": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "client_id": "client_002",
            "name": "爬虫客户端-02",
            "ip_address": "192.168.1.101",
            "status": "busy",
            "last_heartbeat": datetime.now(),
            "current_task": "task_running_test",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

    db.clients.delete_many({})
    db.clients.insert_many(clients)
    print(f"已插入 {len(clients)} 条客户端数据")


if __name__ == "__main__":
    print("=" * 50)
    print("开始插入测试数据...")
    print("=" * 50)

    insert_test_sources()
    tasks = insert_test_tasks()
    insert_test_items(tasks)
    insert_test_logs(tasks)
    insert_test_clients()

    print("=" * 50)
    print("测试数据插入完成！")
    print("=" * 50)

    print("\n数据概览：")
    print(f"  采集源: {db.collector_sources.count_documents({})} 条")
    print(f"  采集任务: {db.collector_tasks.count_documents({})} 条")
    print(f"  采集结果: {db.collector_items.count_documents({})} 条")
    print(f"  任务日志: {db.collector_task_logs.count_documents({})} 条")
    print(f"  客户端: {db.clients.count_documents({})} 条")
