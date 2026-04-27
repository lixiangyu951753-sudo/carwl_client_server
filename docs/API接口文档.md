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
  | timestamp | string | 否 | - | 时间戳 (ISO 8601 格式) |

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

- **URL**: `POST /api/tasks`
- **请求体**:
  | 字段 | 类型 | 必填 | 默认值 | 说明 |
  |------|------|------|--------|------|
  | instruction | string | 否 | `start_crawl` | 任务指令 |
  | params | object | 否 | `{}` | 任务参数 |
  | client_id | string | 否 | - | 指定客户端执行 |

- **params 字段示例**:
  ```json
  {
    "shop_url": "https://example.com/shop",
    "max_pages": 10
  }
  ```

- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "task_id": "task_20260425120000",
      "status": "pending"
    }
  }
  ```

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

### 5.1 创建爬取任务

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "start_crawl",
    "params": {
      "shop_url": "https://example.com/shop",
      "max_pages": 5
    }
  }'
```

### 5.2 客户端心跳

```bash
curl -X POST http://localhost:5000/api/client/heartbeat \
  -H "Content-Type: application/json" \
  -H "X-Client-ID: client-001" \
  -d '{
    "client_id": "client-001",
    "status": "idle"
  }'
```

### 5.3 获取系统状态

```bash
curl http://localhost:5000/api/dashboard
```

### 5.4 获取任务列表（分页）

```bash
curl "http://localhost:5000/api/tasks?page=1&size=10&status=pending"
```
