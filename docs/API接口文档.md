# 远程控制爬虫系统 API 文档

## 基本信息

- **基础路径**: `http://localhost:5001/api`
- **数据格式**: JSON
- **统一响应格式**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {}
  }
  ```

---

## 一、客户端接口 (`/api/client`)

客户端用于爬虫客户端与服务器通信，实现心跳、进度上报和结果提交。

### 1.1 心跳接口

客户端定期发送心跳，接收服务器分配的任务。

- **URL**: `POST /api/client/heartbeat`
- **请求头**:
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | Content-Type | string | `application/json` |
  | X-Client-ID | string | 客户端ID |

- **请求体**:
  | 字段 | 类型 | 必填 | 默认值 | 说明 |
  |------|------|------|--------|------|
  | client_id | string | 是 | - | 客户端唯一标识 |
  | status | string | 否 | `idle` | 客户端状态: idle, busy, running |
  | current_task | string | 否 | - | 当前执行的任务ID |
  | client_type | string | 否 | - | 客户端类型（兼容旧版），如: shop_price, shop_image |
  | client_capabilities | object | 否 | - | 客户端平台与能力标签，用于精确任务分配 |
  | timestamp | string | 否 | - | 时间戳 (ISO 8601 格式) |

- **client_capabilities 字段说明**:
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | platform | string | 平台标识，如: 1688, jd, pdd |
  | capabilities | array | 能力列表，如: ["price"], ["image"], ["price", "image"] |

- **请求示例**:
  ```json
  {
    "client_id": "client_1688_price_01",
    "status": "idle",
    "client_type": "shop_price",
    "client_capabilities": {
      "platform": "1688",
      "capabilities": ["price"]
    }
  }
  ```

- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "instruction": "start_crawl",
      "task_id": "task_20260425120000",
      "params": {
        "shop_url": "https://example.com/shop",
        "max_pages": 10
      }
    }
  }
  ```

- **任务分配规则**:
  | 客户端配置 | 匹配的任务 |
  |-----------|-----------|
  | `client_capabilities.platform=1688, capabilities=["price"]` | platform=1688 且 capability=price 的任务 |
  | `client_capabilities.platform=1688, capabilities=["image"]` | platform=1688 且 capability=image 的任务 |
  | 仅 client_type=shop_price（旧版） | taskType=shop_price 的任务 |

- **指令说明**:
  | instruction | 说明 |
  |-------------|------|
  | `start_crawl` | 开始爬取任务 |
  | `stop_crawl` | 停止当前任务 |
  | `none` | 无任务，保持空闲 |

---

### 1.2 任务进度上报

上报任务执行进度和状态。

- **URL**: `POST /api/client/task_report`
- **请求头**:
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | Content-Type | string | `application/json` |
  | X-Client-ID | string | 客户端ID |

- **请求体**:
  | 字段 | 类型 | 必填 | 默认值 | 说明 |
  |------|------|------|--------|------|
  | client_id | string | 否 | - | 客户端ID |
  | task_id | string | 是 | - | 任务ID |
  | status | string | 否 | `running` | 任务状态: running, completed, failed |
  | progress | object | 否 | - | 进度信息 |
  | error | string | 否 | - | 错误信息 |
  | timestamp | string | 否 | - | 时间戳 |

- **progress 字段示例**:
  ```json
  {
    "current_page": 5,
    "current_product": 50,
    "status": "crawling"
  }
  ```

- **响应**:
  ```json
  {
    "code": 200,
    "message": "success"
  }
  ```

---

### 1.3 任务结果提交

提交任务最终结果。

- **URL**: `POST /api/client/task_result`
- **请求头**:
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | Content-Type | string | `application/json` |
  | X-Client-ID | string | 客户端ID |

- **请求体**:
  | 字段 | 类型 | 必填 | 默认值 | 说明 |
  |------|------|------|--------|------|
  | client_id | string | 否 | - | 客户端ID |
  | task_id | string | 是 | - | 任务ID |
  | batch_id | string | 否 | - | 批次ID |
  | products | array | 否 | `[]` | 爬取的商品数据列表 |
  | timestamp | string | 否 | - | 时间戳 |

- **products 数组元素示例**:
  ```json
  {
    "task_id": "prod_abc123",
    "title": "商品标题",
    "url": "https://example.com/product/123",
    "status": "completed",
    "local_folder": "/path/to/folder"
  }
  ```

- **响应**:
  ```json
  {
    "code": 200,
    "message": "success"
  }
  ```

---

## 二、管理接口 (`/api`)

管理接口用于管理员管理任务和监控客户端。

---

## 三、采集源管理接口 (`/api/v1`)

采集源是任务的模板，定义了平台、能力等基础配置。创建任务时可指定 sourceId 自动继承这些配置。

### 3.1 创建采集源

- **URL**: `POST /api/v1/sources/create`
- **请求体**:
  | 字段 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | sourceCode | string | 是 | 采集源编码，如: src_1688_price |
  | sourceName | string | 是 | 采集源名称，如: 1688价格采集源 |
  | platform | string | 是 | 平台标识，如: 1688, jd, pdd |
  | capability | string | 否 | 能力标签，如: price, image |
  | sourceType | string | 否 | 源类型，默认: url |
  | entryUrl | string | 否 | 入口URL |

- **请求示例**:
  ```json
  {
    "sourceCode": "src_1688_price",
    "sourceName": "1688价格采集源",
    "platform": "1688",
    "capability": "price",
    "entryUrl": "https://www.1688.com"
  }
  ```

- **响应**:
  ```json
  {
    "code": "OK",
    "message": "success",
    "data": {
      "sourceId": "src_9deb2db5",
      "sourceCode": "src_1688_price",
      "status": "enabled"
    }
  }
  ```

### 3.2 查询采集源列表

- **URL**: `GET /api/v1/sources`
- **查询参数**:
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | keyword | string | 否 | 搜索关键词（匹配名称或编码） |
  | platform | string | 否 | 按平台筛选 |
  | status | string | 否 | 按状态筛选: enabled, disabled |
  | page | int | 否 | 页码，默认1 |
  | pageSize | int | 否 | 每页数量，默认20 |

- **响应**:
  ```json
  {
    "code": "OK",
    "message": "success",
    "data": {
      "items": [
        {
          "sourceId": "src_9deb2db5",
          "sourceCode": "src_1688_price",
          "sourceName": "1688价格采集源",
          "platform": "1688",
          "capability": "price",
          "sourceType": "url",
          "status": "enabled",
          "createdAt": "2026-04-30T10:00:00",
          "updatedAt": "2026-04-30T10:00:00"
        }
      ],
      "page": 1,
      "pageSize": 20,
      "total": 1
    }
  }
  ```

---

## 四、采集任务接口 (`/api/v1`)

### 2.1 获取任务列表

获取所有任务，支持分页和状态过滤。

- **URL**: `GET /api/tasks`
- **查询参数**:
  | 参数 | 类型 | 必填 | 默认值 | 说明 |
  |------|------|------|--------|------|
  | status | string | 否 | - | 按状态过滤: pending, running, completed, failed |
  | page | integer | 否 | `1` | 页码 |
  | size | integer | 否 | `20` | 每页数量 |

- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "total": 100,
      "page": 1,
      "size": 20,
      "list": [
        {
          "task_id": "task_20260425120000",
          "client_id": "client-001",
          "status": "completed",
          "instruction": "start_crawl",
          "params": {
            "shop_url": "https://example.com/shop"
          },
          "result": null,
          "progress": null,
          "created_at": "2026-04-25T12:00:00",
          "started_at": "2026-04-25T12:01:00",
          "completed_at": "2026-04-25T12:30:00"
        }
      ]
    }
  }
  ```

---

### 2.2 创建任务

创建新的爬虫任务。

- **URL**: `POST /api/v1/tasks/create`
- **请求体**:
  | 字段 | 类型 | 必填 | 默认值 | 说明 |
  |------|------|------|--------|------|
  | taskType | string | 是 | - | 任务类型: single_url, batch_url, shop, keyword, shop_price, shop_image |
  | sourceId | string | 否 | - | 采集源ID，指定后自动继承源的 platform 和 capability |
  | platform | string | 否 | - | 平台标识，如: 1688, jd, pdd。不指定时从 sourceId 继承 |
  | capability | string | 否 | - | 能力标签，如: price, image。不指定时从 sourceId 继承 |
  | shopUrl | string | 否 | - | 店铺URL（shop/shop_price/shop_image 类型需要） |
  | targetUrls | array | 否 | - | 目标URL列表（single_url/batch_url 类型需要） |
  | keyword | string | 否 | - | 关键词（keyword 类型需要） |
  | options | object | 否 | `{}` | 任务选项 |
  | operatorId | string | 否 | - | 操作人ID |

- **options 字段说明**:
  | 字段 | 类型 | 默认值 | 说明 |
  |------|------|--------|------|
  | maxItems | int | 200 | 最大采集数量 |
  | concurrency | int | 3 | 并发数 |
  | saveImagesToOss | bool | true | 是否保存图片到OSS |
  | saveRawHtml | bool | false | 是否保存原始HTML |
  | timeoutSeconds | int | 30 | 超时时间（秒） |
  | retryTimes | int | 2 | 重试次数 |
  | dedupeStrategy | string | platform_product_id | 去重策略 |

- **请求示例（指定 platform 和 capability）**:
  ```json
  {
    "taskType": "shop_price",
    "sourceId": "src_9deb2db5",
    "platform": "1688",
    "capability": "price",
    "shopUrl": "https://xindeyi.1688.com/page/offerlist.htm",
    "options": {
      "maxItems": 200,
      "concurrency": 3,
      "saveImagesToOss": true,
      "saveRawHtml": false,
      "timeoutSeconds": 30,
      "retryTimes": 2
    },
    "operatorId": "admin"
  }
  ```

- **请求示例（从采集源自动继承 platform/capability）**:
  ```json
  {
    "taskType": "shop_image",
    "sourceId": "src_a1b2c3d4",
    "shopUrl": "https://xindeyi.1688.com/page/offerlist.htm",
    "options": {
      "maxItems": 200
    },
    "operatorId": "admin"
  }
  ```

- **响应**:
  ```json
  {
    "code": "OK",
    "message": "success",
    "data": {
      "taskId": "task_4ea6c2fb",
      "taskNo": "TASK20260430140022",
      "status": "pending",
      "createdAt": "2026-04-30T14:00:22"
    }
  }
  ```

- **任务分配说明**:
  创建任务时指定的 `platform` 和 `capability` 决定了哪个客户端会接收该任务：

  | 任务配置 | 接收的客户端 |
  |---------|-------------|
  | platform=1688, capability=price | client_capabilities 中包含 platform=1688 且 capabilities 包含 price 的客户端 |
  | platform=1688, capability=image | client_capabilities 中包含 platform=1688 且 capabilities 包含 image 的客户端 |
  | platform=jd, capability=price | client_capabilities 中包含 platform=jd 且 capabilities 包含 price 的客户端 |

  如果任务未指定 `platform` 或 `capability`，则只有未配置 `client_capabilities` 的旧版客户端才能接收。

---

### 2.3 获取任务详情

获取单个任务的详细信息。

- **URL**: `GET /api/tasks/<task_id>`
- **路径参数**:
  | 参数 | 类型 | 说明 |
  |------|------|------|
  | task_id | string | 任务ID |

- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "task_id": "task_20260425120000",
      "client_id": "client-001",
      "status": "completed",
      "instruction": "start_crawl",
      "params": {},
      "result": {
        "batch_id": "20260425120000",
        "products": [],
        "products_count": 50
      },
      "progress": null,
      "created_at": "2026-04-25T12:00:00",
      "started_at": "2026-04-25T12:01:00",
      "completed_at": "2026-04-25T12:30:00"
    }
  }
  ```

- **错误响应** (404):
  ```json
  {
    "code": 404,
    "message": "task not found"
  }
  ```

---

### 2.4 取消任务

取消正在执行或待执行的任务。

- **URL**: `POST /api/tasks/<task_id>/cancel`
- **路径参数**:
  | 参数 | 类型 | 说明 |
  |------|------|------|
  | task_id | string | 任务ID |

- **响应**:
  ```json
  {
    "code": 200,
    "message": "success"
  }
  ```

---

### 2.5 获取客户端列表

获取所有已注册的客户端。

- **URL**: `GET /api/clients`

- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": [
      {
        "client_id": "client-001",
        "name": "爬虫客户端1",
        "ip_address": "192.168.1.100",
        "status": "online",
        "current_task": "task_20260425120000",
        "last_heartbeat": "2026-04-25T12:30:00",
        "created_at": "2026-04-20T10:00:00"
      }
    ]
  }
  ```

---

### 2.6 获取客户端状态

获取单个客户端的状态和最近执行的任务。

- **URL**: `GET /api/clients/<client_id>/status`
- **路径参数**:
  | 参数 | 类型 | 说明 |
  |------|------|------|
  | client_id | string | 客户端ID |

- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "client_id": "client-001",
      "name": "爬虫客户端1",
      "status": "busy",
      "current_task": "task_20260425120000",
      "last_heartbeat": "2026-04-25T12:30:00",
      "recent_tasks": [
        {
          "task_id": "task_20260425120000",
          "status": "running",
          "created_at": "2026-04-25T12:00:00"
        }
      ]
    }
  }
  ```

- **错误响应** (404):
  ```json
  {
    "code": 404,
    "message": "client not found"
  }
  ```

---

### 2.7 获取系统仪表板

获取系统整体运行状态概览。

- **URL**: `GET /api/dashboard`

- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "tasks": {
        "total": 500,
        "pending": 10,
        "running": 5,
        "completed": 470,
        "failed": 15
      },
      "clients": {
        "total": 10,
        "online": 7
      }
    }
  }
  ```

---

## 三、错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源未找到 |
| 500 | 服务器内部错误 |

---

## 四、状态说明

### 任务状态 (`status`)

| 状态 | 说明 |
|------|------|
| `pending` | 待执行 |
| `running` | 执行中 |
| `completed` | 已完成 |
| `failed` | 执行失败 |

### 客户端状态 (`status`)

| 状态 | 说明 |
|------|------|
| `idle` | 空闲 |
| `busy` | 忙碌 |
| `running` | 运行中 |
| `online` | 在线 |

---

## 五、使用示例

### 5.1 创建采集源

```bash
curl -X POST http://localhost:5001/api/v1/sources/create \
  -H "Content-Type: application/json" \
  -d '{
    "sourceCode": "src_1688_price",
    "sourceName": "1688价格采集源",
    "platform": "1688",
    "capability": "price",
    "entryUrl": "https://www.1688.com"
  }'
```

### 5.2 创建采集任务（指定 platform/capability）

```bash
curl -X POST http://localhost:5001/api/v1/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "taskType": "shop_price",
    "sourceId": "src_9deb2db5",
    "platform": "1688",
    "capability": "price",
    "shopUrl": "https://xindeyi.1688.com/page/offerlist.htm",
    "options": {
      "maxItems": 200,
      "concurrency": 3
    },
    "operatorId": "admin"
  }'
```

### 5.3 客户端心跳（带能力标签）

```bash
curl -X POST http://localhost:5001/api/client/heartbeat \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_1688_price_01",
    "status": "idle",
    "client_type": "shop_price",
    "client_capabilities": {
      "platform": "1688",
      "capabilities": ["price"]
    }
  }'
```

### 5.4 获取任务列表

```bash
curl "http://localhost:5001/api/v1/tasks?page=1&pageSize=10&status=pending"
```

### 5.5 多平台多客户端配置示例

| 客户端 | client_id | platform | capabilities | 接收的任务 |
|--------|-----------|----------|--------------|-----------|
| 1688图片采集 | client_1688_image_01 | 1688 | ["image"] | platform=1688, capability=image |
| 1688价格采集 | client_1688_price_01 | 1688 | ["price"] | platform=1688, capability=price |
| 京东价格采集 | client_jd_price_01 | jd | ["price"] | platform=jd, capability=price |
| PDD采集 | client_pdd_01 | pdd | ["price"] | platform=pdd, capability=price |
