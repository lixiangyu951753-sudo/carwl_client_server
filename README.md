# 分布式爬虫采集系统

## 项目概述

本系统是一套**分布式爬虫采集平台**，支持多客户端管理、任务调度、实时进度监控和数据采集。

### 核心功能

- **多客户端管理**：支持多台机器同时运行爬虫客户端
- **任务下发**：通过 API 创建采集任务，自动分配给空闲客户端
- **实时监控**：客户端心跳检测，任务进度实时上报
- **数据采集**：支持 1688 店铺、商品详情、关键词等多种采集模式
- **数据存储**：采集数据自动保存到 MongoDB，支持灵活扩展

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      运营工作台 (Web)                        │
│                  http://127.0.0.1:5001                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Flask 服务端                           │
│                   /api/v1/* (collector)                     │
│                   /api/client/* (client)                    │
│                   /api/* (admin)                            │
└─────────────────────────────────────────────────────────────┘
          │                                    │
          ▼                                    ▼
┌─────────────────────┐          ┌─────────────────────┐
│     MongoDB         │          │     客户端 1        │
│   crawler_db        │◄────────►│   DrissionPage     │
│  - collector_tasks  │          │   1688 爬虫         │
│  - collector_items  │          └─────────────────────┘
│  - collector_sources │
│  - clients          │          ┌─────────────────────┐
│  - tasks            │◄────────►│     客户端 2        │
└─────────────────────┘          │   1688 爬虫         │
                                  └─────────────────────┘
```

---

## 项目结构

```
carwl_client_server/
├── client/                      # 爬虫客户端
│   ├── main.py                  # 程序入口
│   ├── config.py                # 配置（修改此文件设置客户端参数）
│   ├── api_client.py             # 服务端通信
│   ├── task_manager.py           # 任务管理（心跳、回调）
│   └── requirements.txt         # 依赖
│
├── client2/                     # 第二个客户端（示例）
│
├── server/                      # Flask 服务端
│   ├── run.py                   # 启动入口
│   ├── requirements.txt         # 服务端依赖
│   ├── create_task_web.py       # Web 端任务创建示例
│   ├── insert_test_data.py      # 测试数据插入
│   └── app/
│       ├── __init__.py          # Flask 应用初始化
│       ├── models/              # 数据模型
│       │   ├── collector_task.py
│       │   ├── collector_item.py
│       │   ├── collector_source.py
│       │   └── collector_log.py
│       └── routes/               # API 路由
│           ├── collector.py     # /api/v1/* (采集相关)
│           ├── client.py        # /api/client/* (客户端通信)
│           └── admin.py         # /api/* (管理后台)
│
├── docs/                        # 文档
│   ├── API接口文档.md
│   ├── 项目优化建议.md
│   └── ...
│
└── docker-compose.yml           # Docker 部署配置
```

---

## 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 启动所有服务（MongoDB + 服务端）
docker-compose up -d

# 查看日志
docker-compose logs -f server

# 停止服务
docker-compose down
```

访问 http://127.0.0.1:5001/api/v1/health 验证服务状态。

### 方式二：手动部署

**1. 启动 MongoDB**

```bash
# Docker 方式
docker run -d --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin123 \
  mongo:latest
```

**2. 启动服务端**

```bash
cd server
pip install -r requirements.txt
python run.py
```

**3. 启动客户端**

```bash
cd client
pip install -r requirements.txt
python main.py
```

---

## 配置说明

### 服务端环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MONGO_URI` | `mongodb://admin:admin123@localhost:27017/` | MongoDB 连接地址 |
| `MONGO_DB` | `crawler_db` | 数据库名 |
| `SECRET_KEY` | `crawler-secret-key-2026` | Flask 密钥 |

### 客户端配置 (client/config.py)

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `CLIENT_ID` | `client_001` | 客户端唯一标识 |
| `SERVER_URL` | `http://localhost:5001` | 服务端地址 |
| `HEARTBEAT_INTERVAL` | `5` | 心跳间隔（秒） |
| `BASE_PATH` | `D:\client_001_output` | 本地存储路径 |

---

## API 文档

### 1. 采集任务 API (`/api/v1`)

#### 创建任务

```http
POST /api/v1/tasks/create
Content-Type: application/json

{
    "taskType": "shop",
    "sourceId": "src_1688_default",
    "shopUrl": "https://xindeyi.1688.com/page/offerlist.htm",
    "options": {
        "maxItems": 200,
        "concurrency": 3,
        "saveImagesToOss": true
    },
    "operatorId": "admin"
}
```

**任务类型 (`taskType`)**：
- `shop` - 店铺采集（需要 `shopUrl`）
- `single_url` - 单链接采集（需要 `targetUrls`）
- `batch_url` - 批量链接采集（需要 `targetUrls`）
- `keyword` - 关键词搜索（需要 `keyword`）

#### 查询任务列表

```http
GET /api/v1/tasks?status=pending&taskType=shop&page=1&pageSize=20
```

#### 查询任务详情

```http
GET /api/v1/tasks/detail?taskId=task_55319ffe
```

#### 取消任务

```http
POST /api/v1/tasks/cancel
Content-Type: application/json

{"taskId": "task_55319ffe"}
```

#### 查询采集结果

```http
GET /api/v1/items?taskId=task_55319ffe&page=1&pageSize=20
GET /api/v1/items?keyword=莫桑石&platform=1688
```

### 2. 客户端通信 API (`/api/client`)

#### 心跳上报

```http
POST /api/client/heartbeat
Content-Type: application/json

{
    "client_id": "client_001",
    "status": "idle",
    "current_task": null
}
```

**响应**（有待执行任务时）：
```json
{
    "code": 200,
    "data": {
        "instruction": "start_crawl",
        "task_id": "task_xxx",
        "params": {
            "shop_url": "https://xindeyi.1688.com/...",
            "max_items": 200,
            "concurrency": 3
        }
    }
}
```

#### 进度上报

```http
POST /api/client/task_report
Content-Type: application/json

{
    "client_id": "client_001",
    "task_id": "task_xxx",
    "status": "running",
    "progress": {"current_page": 1, "current_product": 10}
}
```

#### 结果上报

```http
POST /api/client/task_result
Content-Type: application/json

{
    "client_id": "client_001",
    "task_id": "task_xxx",
    "batch_id": "20260428120000",
    "products": [
        {
            "title": "莫桑石项链",
            "url": "https://detail.1688.com/offer/123.html",
            "images": ["url1", "url2"],
            "priceMin": "28.50",
            "priceMax": "68.00",
            "supplierName": "义乌某厂"
        }
    ]
}
```

---

## 数据模型

### collector_tasks（采集任务）

| 字段 | 类型 | 说明 |
|------|------|------|
| taskId | string | 任务ID |
| taskNo | string | 任务编号 |
| taskType | string | 任务类型 |
| status | string | pending/running/succeeded/failed/canceled |
| shopUrl | string | 店铺URL（shop类型） |
| targetUrls | array | 目标URL列表（batch_url类型） |
| keyword | string | 关键词（keyword类型） |
| progress | int | 进度百分比 |
| successCount | int | 成功数量 |
| clientId | string | 执行的客户端ID |
| createdAt | datetime | 创建时间 |
| finishedAt | datetime | 完成时间 |

### collector_items（采集结果）

| 字段 | 类型 | 说明 |
|------|------|------|
| itemId | string | 商品ID |
| taskId | string | 所属任务ID |
| platform | string | 平台（1688/淘宝等） |
| title | string | 商品标题 |
| mainImageUrl | string | 主图 |
| imageUrls | array | 所有图片 |
| priceMin | string | 最低价 |
| priceMax | string | 最高价 |
| supplierName | string | 供应商名称 |
| supplierUrl | string | 供应商链接 |
| extraData | object | 额外字段（灵活扩展） |
| createdAt | datetime | 创建时间 |

### clients（客户端）

| 字段 | 类型 | 说明 |
|------|------|------|
| client_id | string | 客户端ID |
| status | string | online/busy/offline |
| last_heartbeat | datetime | 最后心跳时间 |
| current_task | string | 当前执行的任务ID |

---

## Web 端任务创建示例

参考 `server/create_task_web.py`：

```python
import requests

BASE_URL = "http://127.0.0.1:5001/api/v1"

# 创建店铺采集任务
resp = requests.post(f"{BASE_URL}/tasks/create", json={
    "taskType": "shop",
    "sourceId": "src_1688_default",
    "shopUrl": "https://xindeyi.1688.com/page/offerlist.htm",
    "options": {"maxItems": 200, "concurrency": 3},
    "operatorId": "admin"
})
print(resp.json())

# 查询采集结果
resp = requests.get(f"{BASE_URL}/items", params={"taskId": "task_xxx"})
print(resp.json())
```

---

## 运营工作台对接

系统已对接运营工作台 API，支持：

- 创建采集任务 → `/api/v1/tasks/create`
- 查询任务状态 → `/api/v1/tasks/detail`
- 查询采集结果 → `/api/v1/items`
- 取消任务 → `/api/v1/tasks/cancel`
- 重试任务 → `/api/v1/tasks/retry`

详细对接方案见 `docs/服务端对接collector-service改造方案.md`

---

## 目录结构设计

```
客户端数据目录结构：
D:\client_001_output\
├── tasks.json                    # 任务状态记录
├── batch.json                    # 批次状态记录
└── {商品ID}/
    ├── {商品标题}/               # 每个商品一个文件夹
    │   ├── image1.webp
    │   ├── image2.webp
    │   └── factory/              # 工厂图
    │       └── ...
    └── {商品标题}.html           # 页面快照
```

---

## 常见问题

### Q: 客户端无法连接服务端

1. 检查服务端是否运行：`curl http://127.0.0.1:5001/api/v1/health`
2. 检查 `client/config.py` 中的 `SERVER_URL` 是否正确
3. 检查防火墙设置

### Q: 任务创建后客户端没有领取

1. 检查客户端是否在线（心跳是否正常）
2. 检查是否有 pending 状态的任务
3. 查看服务端日志

### Q: 采集数据没有保存到服务端

1. 确保调用了 `api.report_result()` 上报结果
2. 检查 `task_result` 接口是否正常
3. 查看 MongoDB 中 `collector_items` 集合

---

## 开发指南

### 添加新的任务类型

1. 在 `server/app/routes/collector.py` 的 `create_task()` 添加类型处理
2. 在 `server/app/routes/client.py` 的 `_collector_task_to_instruction()` 添加指令转换
3. 在 `client/main.py` 添加对应的爬取逻辑
4. 在 `client/task_manager.py` 的 `crawl_callback` 中处理

### 添加新的采集字段

1. 客户端 `shop_detail()` 返回新字段
2. 服务端 `task_result()` 提取并保存字段
3. 自动存入 `extraData`（无需修改结构）

---

## License

Private Project - Internal Use Only
