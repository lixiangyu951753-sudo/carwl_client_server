---
name: flask-mongodb-dev
description: Flask + MongoDB 项目开发助手。用于 API 创建、数据库集成、Docker 部署和故障排查。适用于 Flask + MongoDB 项目的开发指导。
---

# Flask + MongoDB Development Assistant

参考以下最佳实践协助开发 Flask + MongoDB 项目：

## 1. 项目结构
- Flask Blueprint 模块化 API
- 环境变量管理 MongoDB 连接
- 合理的目录结构

## 2. MongoDB 连接

```python
from pymongo import MongoClient
import os

mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
mongo_client = MongoClient(mongo_uri)
db = mongo_client['your_database']
```

## 3. API 开发
- 使用 Flask Blueprints 组织路由
- 实现标准 CRUD 操作
- 请求验证和错误响应处理
- RESTful API 设计

## 4. Docker 部署
- Dockerfile 基于 python:3.11-slim
- docker-compose.yml 编排 web + mongo 服务
- 环境变量容器内管理
- 网络和服务发现配置

## 5. 安全问题
- 输入验证和清理
- 环境变量不硬编码密钥
- 数据库访问控制
- 认证与授权

## 6. 常见问题
- **连接拒绝**: 检查 MongoDB 服务状态、连接字符串、网络访问
- **容器无法连接 MongoDB**: 使用 docker-compose 网络、检查环境变量
- **慢查询**: 添加索引、优化查询模式、使用投影
