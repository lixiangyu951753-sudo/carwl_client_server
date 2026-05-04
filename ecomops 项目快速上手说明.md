# ecomops 项目快速上手说明

## 1. 项目定位

`ecomops` 是一个电商运营中台项目，采用 Monorepo 管理，当前主要包含：

```text
运营工作台 Workbench
管理后台 Admin
BFF API
商品中心
用户中心 / 权限中心
文件服务
AIGC 内容工厂
采集系统接入边界
系统网关 / 运行监控

```

当前项目已经进入多模块并行开发阶段。所有开发必须基于最新 `origin/main`，不能基于旧分支或旧本地 main 开发。

---

# 2. 当前事实源

团队协作时，所有人和 AI 工具都必须以以下文件为当前事实源：

```text
GitHub origin/main
docs/engineering/project-current-state-report.md
docs/engineering/module-status-matrix.md
docs/project-knowledge-audit/current/09_claude_project_memory.md
docs/engineering/git-worktree-task-standard.md
.claude/commands/*

```

注意：

```text
docs/project-knowledge-audit/archive/** 只用于历史追溯，不作为当前状态依据。
旧聊天记录、旧 PR 报告、旧项目记忆不能直接作为当前事实源。

```
---

# 3. 新任务启动规则

所有新任务必须基于最新 `origin/main` 创建独立 worktree。

## 3.1 标准启动命令

```bash
cd D:/projects/repo

git checkout main
git fetch origin --prune
git pull --ff-only origin main

git status --short
git rev-parse HEAD
git rev-parse origin/main

```

必须确认：

```text
git status --short 为空
HEAD == origin/main

```

然后创建独立 worktree：

```bash
git worktree add D:/projects/repo-<task-name> -b <branch-name> main
cd D:/projects/repo-<task-name>

git branch --show-current
git status --short
git log --oneline -1

```

## 3.2 禁止事项

禁止：

```text
基于旧 main 开发
基于 feature 分支创建新任务
在 main 直接开发
复用已有任务 worktree 开新任务
main 未同步 origin/main 就开始修改

```
---

# 4. 项目目录结构

当前核心目录：

```text
apps/
  web/                 # 运营工作台前端
  admin/               # 管理后台前端
  api/                 # BFF API

services/
  product-center/      # 商品中心服务
  user-center/         # 用户中心 / 权限服务
  file-service/        # 文件服务
  aigc-service/        # AIGC 内容工厂服务
  collector-service/   # 已剥离，仅保留外部采集服务占位说明

packages/
  contracts/           # 统一 DTO / ErrorCodes / 类型契约
  service-sdk/         # BFF 调用后端服务的 SDK

docs/
  engineering/         # 工程规范、模块设计、当前状态报告
  project-knowledge-audit/
    current/           # 当前 ClaudeCode 项目记忆
    archive/           # 历史文档归档

.claude/
  commands/            # ClaudeCode 执行命令规范

```
---

# 5. 两个前端系统边界

## 5.1 运营工作台 Workbench

路径：

```text
apps/web

```

当前只承载业务运营能力：

```text
工作台
产品采集
商品中台中心
AIGC
素材中心
渠道发布

```

Workbench 不再承载：

```text
系统设置
角色权限
字典管理
状态映射
模型 / 渠道配置
文件服务测试入口
Provider 密钥配置

```

## 5.2 管理后台 Admin

路径：

```text
apps/admin

```

当前承载系统治理能力：

```text
系统概览
用户与权限
系统运行
集成与凭证
文件治理

```

Admin 负责：

```text
用户管理
角色管理
权限管理
系统运行状态
API / BFF / 服务状态
平台凭证
AIGC Provider 配置
文件中心

```
---

# 6. BFF 与服务边界

前端不直接调用后端服务，统一走 BFF。

```text
Workbench / Admin
        ↓
apps/api BFF
        ↓
services/*

```

主要 BFF Gateway：

```text
auth
user-gateway
products-gateway
file-gateway
aigc-gateway
crawl-gateway
system-gateway

```

边界原则：

```text
前端只调用 BFF
BFF 不直接写数据库
BFF 负责鉴权、权限、转发、错误统一
业务规则优先放在对应 service
contracts 负责统一 DTO / ErrorCodes
service-sdk 负责服务间调用封装

```
---

# 7. 权限体系当前状态

权限体系已经形成闭环：

```text
系统访问权限
菜单 / 页面权限
BFF 读接口权限
BFF 写接口权限
v-permission 按钮权限机制
Admin 角色-权限编辑页
User Center 服务端角色保护

```

## 7.1 账号类型

当前共用一套账号体系，但按权限区分系统入口：

```text
管理员账号：可进入 Admin + Workbench
运营账号：只可进入 Workbench

```

核心权限：

```text
admin:access
workbench:access

```

## 7.2 SUPER\_ADMIN 服务端保护

以下权限不可被服务端移除：

```text
admin:access
workbench:access
admin:user-center:roles:assign-permissions

```

## 7.3 OPERATOR 服务端限制

OPERATOR 不允许被分配：

```text
admin:*

```

即使绕过前端直接调 API，也会被 User Center 拦截。

---

# 8. AIGC 当前状态

AIGC 当前是 Active 状态。

已完成：

```text
LinkFox Provider Adapter
Admin AIGC Provider 管理页面
Provider credentials 由 Admin 管理
Workbench 只使用 Provider
Brand Prompt
Prompt Template variablesSchema
Prompt Rendering
Task inputJson
Prompt Snapshot
Mock Provider 回归

```

当前 AIGC 输入链路：

```text
Brand Prompt
→ Prompt Template
→ Variables
→ Prompt Rendering
→ inputJson
→ promptSnapshotJson
→ Provider Payload
→ Provider Result

```

后续小修项：

```text
GET /generation-tasks/:id response 返回 promptSnapshotJson
{{negativePrompt}} 自动绑定 brandPrompt.negativePrompt
修复 externalTaskId / snake_case mapping

```

AIGC 相关文档：

```text
docs/engineering/aigc-input-architecture.md
docs/engineering/aigc-linkfox-provider-integration.md
docs/engineering/admin-aigc-provider-management.md

```
---

# 9. 采集系统当前状态

采集系统当前状态：

```text
External pending

```

已完成：

```text
旧内置 services/collector-service 已剥离
compose 不再包含 collector-service
compose 不再包含 mongo-collector
services/collector-service 仅保留 README 占位说明
BFF crawl-gateway 保留为外部服务接入边界
Web 产品采集页面保留

```

未配置外部采集服务时：

```text
HTTP 503
COLLECTOR_SERVICE_NOT_CONFIGURED
采集服务尚未接入

```

同事接入外部 Python 采集服务时，需要提供：

```text
Python 服务代码
Dockerfile
启动命令
端口
health endpoint
API 文档
数据库依赖
鉴权方式
示例请求 / 响应

```

采集相关文档：

```text
docs/engineering/collector-service-decoupling.md

```
---

# 10. 文件服务当前状态

文件服务当前是 Active 状态。

当前能力：

```text
文件上传
文件列表
文件详情
预览 URL
下载 URL
元数据刷新
逻辑删除 / 归档
操作日志
Admin 文件中心一期

```

原则：

```text
前端不直接访问 OSS
所有上传 / 预览 / 下载必须经过 file-service
Admin 负责文件治理
Workbench 后续只使用业务上传组件

```
---

# 11. 商品中心当前状态

商品中心当前是 Active 状态。

当前覆盖模块包括：

```text
商品列表
新建商品
类目管理
品牌管理
属性管理
属性模板管理
SPU 管理
SKU 管理
价格
库存快照
商品审核
操作日志

```

商品中心相关边界：

```text
Workbench 承载商品业务运营
Product Center Service 负责业务规则
BFF products-gateway 负责前端入口和权限
contracts 统一 DTO

```
---

# 12. 当前开发和 PR 要求

每个 PR 必须说明：

```text
base commit
branch
worktree
修改文件范围
是否修改 DB / migration
是否修改 compose / nginx / pnpm-lock
是否修改权限 / seed
build 结果
smoke 结果
runtime 结果
风险与遗留问题

```

禁止混入：

```text
.env
.env.development
真实密钥
测试账号文件
node_modules
dist
.turbo
.remember
无关业务文件

```
---

# 13. 常用验证命令

## 13.1 构建

按任务范围选择：

```bash
pnpm --filter web build-only
pnpm --filter admin build
pnpm --filter @repo/api build
pnpm --filter @repo/contracts build
pnpm --filter service-sdk build
pnpm --filter user-center build
pnpm --filter product-center build
pnpm --filter file-service build
pnpm --filter aigc-service build

```

## 13.2 Smoke

```bash
pnpm smoke:critical
pnpm smoke:nginx

```

## 13.3 CI 检查

```bash
bash scripts/ci/check-restful-paths.sh
bash scripts/ci/check-forbidden-files.sh

```

## 13.4 Docker

```bash
docker compose config --services
docker compose build <service>
docker compose up -d <service> nginx
docker compose ps

```
---

# 14. 什么时候需要更新项目状态文档

如果任务改变模块状态，必须更新：

```text
docs/engineering/module-status-matrix.md

```

如果任务改变项目整体状态，必须更新：

```text
docs/engineering/project-current-state-report.md

```

如果任务改变长期项目认知，必须更新：

```text
docs/project-knowledge-audit/current/09_claude_project_memory.md

```

例如以下任务必须更新状态文档：

```text
新增模块
删除模块
修改模块边界
新增服务
修改 compose / nginx
新增 DB migration
修改权限体系
接入外部服务
AIGC / Collector / Product Center 关键状态变化

```

小 bug、文案、局部样式、局部修复一般不需要更新 Current Baseline，但最终报告需要说明原因。

---

# 15. 人与 ClaudeCode 的分工

## 15.1 人负责

```text
产品方向
模块边界确认
技术路线最终决策
是否合并高风险 PR
生产环境密钥和部署
同事接口契约确认

```

## 15.2 ClaudeCode 负责

```text
同步最新 main
创建 worktree
扫描文档和代码
执行开发任务
跑 build / smoke / checker
创建 PR
生成最终报告
按规则更新状态文档
合并收口时清理 worktree / branch

```
---

# 16. 新同事快速开始步骤

## Step 1：拉取仓库

```bash
git clone <repo-url>
cd repo

```

## Step 2：阅读当前事实源

先读：

```text
docs/engineering/project-current-state-report.md
docs/engineering/module-status-matrix.md
docs/project-knowledge-audit/current/09_claude_project_memory.md
docs/engineering/git-worktree-task-standard.md

```

## Step 3：同步 main

```bash
git checkout main
git fetch origin --prune
git pull --ff-only origin main
git status --short
git rev-parse HEAD
git rev-parse origin/main

```

确认：

```text
HEAD == origin/main

```

## Step 4：创建 worktree

```bash
git worktree add D:/projects/repo-<task-name> -b <branch-name> main
cd D:/projects/repo-<task-name>

```

## Step 5：按模块阅读补充文档

AIGC：

```text
docs/engineering/aigc-input-architecture.md
docs/engineering/aigc-linkfox-provider-integration.md
docs/engineering/admin-aigc-provider-management.md

```

权限：

```text
docs/engineering/auth-permission-model-design.md

```

采集：

```text
docs/engineering/collector-service-decoupling.md

```

菜单 / 模块边界：

```text
docs/engineering/module-boundary-and-menu-reorg.md

```

## Step 6：开发、验证、提交 PR

开发完成后至少检查：

```bash
bash scripts/ci/check-forbidden-files.sh
bash scripts/ci/check-restful-paths.sh

```

按任务类型补充 build / smoke / runtime 验证。

---

# 17. 当前注意事项

```text
1. 旧 collector-service 已剥离，不要基于旧内置采集服务开发。
2. Workbench 不再做系统设置和文件服务测试。
3. Provider 凭证只允许 Admin 管理。
4. 权限体系已形成闭环，不要绕过 User Center 服务端规则。
5. 新任务必须基于最新 origin/main。
6. archive 下旧文档不能作为当前事实源。
7. 真实密钥不允许写入代码、文档、PR 描述。
8. 任何修改 compose / nginx / DB / 权限 seed 的任务，都必须单独说明风险和验证方式。

```
---

# 18. 推荐使用的 ClaudeCode 命令

如果使用 ClaudeCode，优先使用：

```text
.claude/commands/start-worktree-task.md
.claude/commands/ecomops-task-start.md
.claude/commands/ecomops-module-start.md
.claude/commands/ecomops-parallel-start.md

```

后续如果任务收口命令已落地，也使用：

```text
.claude/commands/ecomops-task-close.md
.claude/commands/ecomops-pr-close.md
.claude/commands/ecomops-baseline-refresh.md

```
---

# 19. 最简上手总结

```text
先同步最新 main
先读 current baseline
新任务必须独立 worktree
前端只走 BFF
系统治理放 Admin
业务运营放 Workbench
权限规则已经闭环
AIGC 已进入输入架构阶段
采集服务等待外部 Python 接入
任何模块状态变化都要更新状态文档

```