# 1688远程控制爬虫系统

## 项目概述

本系统是一个基于Flask服务端和Python客户端的远程控制爬虫系统，用于自动抓取1688店铺商品信息（标题、图片、视频等）。

## 项目结构

```
carwl_client_server/
├── client/                    # 爬虫客户端
│   ├── __init__.py
│   ├── main.py               # 程序入口，启动爬虫客户端
│   ├── config.py             # 配置文件
│   ├── api_client.py         # 服务端通信模块
│   ├── task_manager.py       # 任务管理模块
│   └── requirements.txt      # 客户端依赖
│
├── server/                    # Flask服务端
│   ├── run.py                # 服务启动入口
│   ├── requirements.txt       # 服务端依赖
│   └── app/
│       ├── __init__.py       # Flask应用初始化
│       ├── models.py         # 数据模型
│       └── routes/
│           ├── __init__.py
│           ├── admin.py      # 管理后台API（任务管理、客户端管理）
│           └── client.py     # 客户端API（心跳、进度上报、结果上报）
│
└── docs/
    ├── 远程控制爬虫系统设计文档.md   # 系统设计文档
    └── 管理端API接口文档.md         # 管理端API接口文档
```

## 技术栈

| 组件 | 技术 |
|------|------|
| 服务端框架 | Flask |
| 数据库 | MongoDB |
| 客户端HTTP | requests |
| 浏览器自动化 | DrissionPage (ChromiumPage) |
| 数据存储 | 阿里云OSS |

## 快速开始

### 1. 服务端部署

```bash
cd server
pip install -r requirements.txt
python run.py
```

服务启动后运行在 http://0.0.0.0:5000

### 2. 客户端部署

```bash
cd client
pip install -r requirements.txt
python main.py
```

## API接口

### 管理端API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/tasks` | GET | 获取任务列表 |
| `/api/tasks` | POST | 创建新任务 |
| `/api/tasks/<task_id>` | GET | 获取任务详情 |
| `/api/tasks/<task_id>/cancel` | POST | 取消任务 |
| `/api/clients` | GET | 获取客户端列表 |
| `/api/clients/<client_id>/status` | GET | 获取客户端状态 |
| `/api/dashboard` | GET | 获取监控仪表盘数据 |

### 客户端API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/client/heartbeat` | POST | 心跳上报，获取指令 |
| `/api/client/task_report` | POST | 任务进度上报 |
| `/api/client/task_result` | POST | 任务结果上报 |

## 核心流程

1. **客户端启动** → 每5秒发送心跳到服务端
2. **服务端分配任务** → 客户端心跳响应中带回任务指令
3. **客户端执行爬取** → 实时上报进度到服务端
4. **爬取完成** → 上传数据到OSS，上报结果到服务端
5. **管理端查看** → 通过API查看任务状态和结果

## 配置文件

### 客户端 (client/config.py)

- `CLIENT_ID`: 客户端唯一标识
- `SERVER_URL`: 服务端地址
- `HEARTBEAT_INTERVAL`: 心跳间隔（秒）
- `BASE_PATH`: 本地存储路径

### 服务端

通过环境变量或配置文件设置MongoDB连接等参数。

## 数据库表

- **clients**: 客户端信息表
- **tasks**: 任务表
- **task_logs**: 任务日志表

详见 `docs/远程控制爬虫系统设计文档.md`
