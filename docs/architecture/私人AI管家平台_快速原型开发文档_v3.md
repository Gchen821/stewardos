**私人 AI 管家平台  
开发文档（快速原型 V2）**

面向快速上架的 MVP / 重点前置权限控制与安全可靠性

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>文档适用范围<br />
</strong>本文件用于指导 0→1 开发第一版平台。V1
功能范围聚焦：主控管家对话、Agent 仓库、Skills
仓库、上下线切换、聊天页选择主控管家或子
Agent；同时把权限控制模块前置到第一阶段，作为平台上线前的基础能力。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

版本：V2（在 V1 基础上补充权限控制、数据库表结构、页面原型字段清单、API
详细设计、WSL + Docker 本地开发软件清单）

# 1. 产品目标与第一版范围

产品目标：构建一个“私人大管家 + 可管理子 Agent/Skills
仓库”的平台。用户通过聊天界面与主控管家或某个子 Agent
互动；平台提供可视化仓库管理、上线/下线控制，以及可扩展的安全边界。

第一版主要功能：

> **•**
> 主控管家对话：统一接收用户指令，支持基础问答、任务理解与结果汇总。
>
> **•** Agent 仓库：新增、编辑、查看、上线、下线、归档子 Agent。
>
> **•** Skills 仓库：注册 Skill、配置元数据、查看被哪些 Agent 绑定。
>
> **•** 聊天页角色切换：用户可选择“主控管家”或某个子 Agent
> 作为当前对话对象。
>
> **•** 安全与权限控制：V1
> 即提供权限模型、上线前校验、动作审计、风险级别和最小权限控制。

第一版明确不做：

> **•** 自动创建高危 Agent 并直接执行。
>
> **•** 真机桌面高权限控制、任意 Shell、任意文件系统写入。
>
> **•** 复杂多租户计费、开放市场、公开插件分发。

# 2. 第一阶段必须前置的权限控制与安全模块

设计原则：平台先保证“安全可控”，再扩展“能力丰富”。因此权限控制不是二期补充，而是第一阶段的基础模块。

| **模块**       | **V1 必须实现内容**                          | **上线价值**           |
|----------------|----------------------------------------------|------------------------|
| 身份认证       | 账号登录、会话鉴权、接口级用户身份校验       | 防止匿名访问和越权操作 |
| 角色与权限     | 用户 / 管理员 / 系统角色；页面和接口级鉴权   | 保证后台操作可控       |
| Agent 权限边界 | Agent 仅拥有显式授予的 Skill 与资源范围      | 避免单 Agent 过权      |
| Risk Level     | L0-L3 风险等级；高风险动作默认拒绝或需确认   | 降低误触发风险         |
| 上线前校验     | Agent 上线前校验绑定 Skill、策略、状态与依赖 | 防止错误配置进入运行池 |
| 审计日志       | 记录上线/下线、配置变更、会话与执行结果      | 保证事后可追溯         |
| 运行白名单     | 仅允许 V1 白名单 Skill 进入执行              | 降低攻击面             |

V1 权限控制最小闭环：

> **•** 用户登录后，访问聊天页、Agent 仓库、Skills
> 仓库、管理接口都要经过身份校验。
>
> **•** 系统中的 Agent 只能调用绑定且启用的
> Skill，不能自由请求未注册能力。
>
> **•** Agent 上线前必须通过策略校验：状态有效、至少绑定一个可用
> Skill、没有冲突配置。
>
> **•**
> 聊天和执行全链路写入审计日志，至少保留发起人、对象、时间、动作、结果。

# 3. 推荐开发语言、框架与技术栈

| **层**     | **推荐方案**                                            | **说明**                                    |
|------------|---------------------------------------------------------|---------------------------------------------|
| 前端       | TypeScript + Next.js + React + Tailwind CSS + shadcn/ui | 开发快，适合聊天界面和后台管理              |
| 后端 API   | TypeScript + NestJS                                     | 模块化强，适合权限、仓库、审计等业务服务    |
| AI Runtime | Python 3.11 + FastAPI                                   | 适合 Agent 编排、Prompt、模型调用和工具协议 |
| 数据库     | PostgreSQL                                              | 关系清晰，适合仓库、会话、权限、审计        |
| 缓存/队列  | Redis                                                   | 会话缓存、任务状态、轻量队列                |
| 对象存储   | MinIO（开发）/ S3 兼容（线上）                          | 存截图、日志快照、导入导出文件              |
| 鉴权       | JWT + Refresh Token                                     | 前后端分离方案简单直接                      |
| ORM        | Prisma + SQLModel                                       | 兼顾开发效率与演进                          |
| 测试       | Vitest / Playwright / Jest / Pytest                     | 覆盖前端、后端、运行时                      |
| 部署       | WSL2 + Docker Compose（开发）；云主机/容器平台（上线）  | 快速原型成本低                              |

# 4. 开发环境、测试环境与上线环境

开发环境：Windows 11 + WSL2 + Docker Compose。推荐在 WSL 的 Ubuntu
环境内统一执行 Node、Python、数据库脚本和容器命令，减少宿主机差异。

测试环境：

> **•** 本地 Dev：开发者个人机器，使用 Docker Compose 启动
> PostgreSQL、Redis、MinIO；前后端可本地热更新。
>
> **•** 集成
> SIT：部署一套共享测试环境，验证登录、聊天、仓库管理、上下线和权限控制。
>
> **•** 预发布
> Staging：尽量贴近正式环境，接入真实模型网关和正式配置模板。
>
> **•** 生产 Prod：第一版先做单区部署，要求可灰度、可回滚、可审计。

# 5. WSL + Docker 需要下载安装的软件

| **软件**              | **建议用途**        | **安装位置 / 备注**                              |
|-----------------------|---------------------|--------------------------------------------------|
| Windows 11            | 宿主系统            | 建议支持 WSL2                                    |
| WSL2                  | Linux 开发环境      | 启用适用于 Linux 的 Windows 子系统               |
| Ubuntu 22.04/24.04    | 主要开发环境        | 建议在 WSL 内开发与运行命令                      |
| Docker Desktop        | 容器管理            | 启用 WSL 集成                                    |
| Git                   | 代码管理            | Windows 与 WSL 都建议安装                        |
| VS Code               | 主编辑器            | 安装 Remote - WSL、Docker、Python、ESLint 等插件 |
| Node.js 20 LTS        | 前端/后端 JS 运行时 | 安装在 WSL 内                                    |
| pnpm                  | JS 包管理           | 统一依赖管理                                     |
| Python 3.11           | AI Runtime          | 安装在 WSL 内                                    |
| uv 或 Poetry          | Python 依赖管理     | 二选一即可                                       |
| DBeaver / psql        | 数据库调试          | 宿主机或 WSL 均可                                |
| Postman / Bruno       | API 调试            | 任选其一                                         |
| Redis Insight（可选） | 缓存查看            | 排查任务状态方便                                 |

建议安装顺序：启用 WSL2 → 安装 Ubuntu → 安装 Docker Desktop 并启用 WSL
Integration → 在 WSL 中安装 Git、Node.js、pnpm、Python、uv/Poetry →
克隆项目并使用 Docker Compose 启动依赖服务。

# 6. 第一版系统架构

> **•** Web 前端：聊天页、Agent 仓库页、Skills
> 仓库页、系统设置页、登录页。
>
> **•** BFF / API：统一鉴权、用户信息、Agent/Skill
> CRUD、上下线切换、消息接口、审计查询。
>
> **•** AI Runtime：主控管家、子 Agent 会话入口、路由逻辑、已注册 Skill
> 调用协议。
>
> **•** Policy 模块：负责角色权限、Agent 上线前校验、Skill 可用性校验。
>
> **•** Task / Log 模块：记录执行过程、运行结果、错误与审计日志。
>
> **•** Data Layer：PostgreSQL + Redis + MinIO。

# 7. 数据库表结构（V1）

建议按业务拆表，先保证关系清晰和可审计。以下为 V1 必要表。字段类型以
PostgreSQL 为基准。

## 7.1 用户与认证

| **表名**           | **字段**                                                               | **说明**                          |
|--------------------|------------------------------------------------------------------------|-----------------------------------|
| users              | id, email, password_hash, display_name, status, created_at, updated_at | 平台用户，status：active/disabled |
| user_sessions      | id, user_id, refresh_token_hash, expires_at, created_at                | 刷新令牌与会话管理                |
| roles              | id, code, name, description                                            | 角色定义：admin/user/system       |
| user_role_bindings | id, user_id, role_id                                                   | 用户与角色多对多绑定              |

## 7.2 Agent、Skill 与绑定关系

| **表名**             | **字段**                                                                                                                                      | **说明**                                     |
|----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| agents               | id, owner_user_id, name, code, type, status, description, system_prompt, icon, version, is_builtin, created_at, updated_at                    | status：draft/offline/online/paused/archived |
| skills               | id, name, code, category, description, version, entrypoint, input_schema_json, output_schema_json, risk_level, status, created_at, updated_at | status：active/inactive/deprecated           |
| agent_skill_bindings | id, agent_id, skill_id, enabled, config_json, sort_order, created_at                                                                          | Agent 与 Skill 绑定关系                      |
| agent_status_history | id, agent_id, old_status, new_status, operator_user_id, reason, created_at                                                                    | 记录上线/下线等状态切换                      |

## 7.3 权限与策略

| **表名**                 | **字段**                                                                                                     | **说明**                                |
|--------------------------|--------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| permissions              | id, code, name, description, scope_type                                                                      | 如 agent.manage、skill.manage、chat.use |
| role_permission_bindings | id, role_id, permission_id                                                                                   | 角色拥有的后台权限                      |
| agent_policies           | id, agent_id, allow_online, allow_chat_select, max_risk_level, skill_whitelist_json, config_json, updated_at | Agent 的运行策略                        |
| skill_policies           | id, skill_id, allowed_roles_json, risk_level, requires_confirm, enabled                                      | Skill 的基础可用策略                    |

## 7.4 聊天、执行与审计

| **表名**      | **字段**                                                                                                     | **说明**                           |
|---------------|--------------------------------------------------------------------------------------------------------------|------------------------------------|
| conversations | id, user_id, target_type, target_id, title, created_at, updated_at                                           | target_type：butler/agent          |
| messages      | id, conversation_id, sender_role, sender_id, content, message_type, created_at                               | sender_role：user/assistant/system |
| job_runs      | id, user_id, agent_id, conversation_id, status, input_json, output_json, error_message, started_at, ended_at | 执行记录                           |
| audit_logs    | id, user_id, entity_type, entity_id, action, detail_json, ip, created_at                                     | 管理和运行态审计日志               |

数据库索引建议：

> **•** users(email) 唯一索引；agents(owner_user_id, status) 组合索引。
>
> **•** skills(code) 唯一索引；agent_skill_bindings(agent_id, enabled)
> 组合索引。
>
> **•** conversations(user_id, target_type, updated_at desc)
> 索引，提升聊天列表查询。
>
> **•** messages(conversation_id, created_at) 索引，提升消息流读取。
>
> **•** audit_logs(entity_type, entity_id, created_at desc)
> 索引，提升追溯效率。

# 8. 页面原型字段清单

## 8.1 登录页

| **字段/控件** | **类型** | **说明**     |
|---------------|----------|--------------|
| email         | 输入框   | 用户邮箱     |
| password      | 密码框   | 登录密码     |
| remember_me   | 复选框   | 记住登录状态 |
| login_button  | 按钮     | 提交登录     |
| error_message | 提示文本 | 认证失败提示 |

## 8.2 聊天页

| **字段/控件**     | **类型** | **说明**                            |
|-------------------|----------|-------------------------------------|
| conversation_list | 左侧列表 | 展示当前用户的对话                  |
| target_selector   | 下拉框   | 可选主控管家或已上线子 Agent        |
| agent_status_tag  | 标签     | 显示当前目标在线/离线状态           |
| message_stream    | 消息区域 | 展示聊天内容                        |
| input_box         | 多行输入 | 发送消息内容                        |
| send_button       | 按钮     | 发送消息                            |
| new_chat_button   | 按钮     | 发起新对话                          |
| switch_warning    | 提示条   | 切换到离线 Agent 时禁止选择或弹提示 |

## 8.3 Agent 仓库页

| **字段/控件**       | **类型** | **说明**                             |
|---------------------|----------|--------------------------------------|
| search_keyword      | 输入框   | 按名称/编码搜索 Agent                |
| status_filter       | 下拉框   | online/offline/draft/paused/archived |
| create_agent_button | 按钮     | 新建 Agent                           |
| agent_table         | 表格     | 名称、类型、状态、版本、更新时间     |
| online_toggle       | 开关     | 上线/下线切换                        |
| edit_button         | 按钮     | 编辑 Agent                           |
| view_detail         | 按钮     | 查看详情与绑定 Skills                |
| archive_button      | 按钮     | 归档 Agent                           |

## 8.4 Agent 编辑页

| **字段/控件**     | **类型**  | **说明**                 |
|-------------------|-----------|--------------------------|
| name              | 输入框    | Agent 名称               |
| code              | 输入框    | 唯一编码                 |
| type              | 下拉框    | butler/subagent/system   |
| description       | 多行输入  | 功能描述                 |
| system_prompt     | 多行输入  | 系统提示词               |
| icon              | 上传/选择 | 图标                     |
| bound_skills      | 多选列表  | 已绑定 Skills            |
| allow_chat_select | 开关      | 是否允许在聊天页直接选择 |
| max_risk_level    | 下拉框    | 允许最高风险等级         |
| save_button       | 按钮      | 保存 Agent 配置          |

## 8.5 Skills 仓库页

| **字段/控件**         | **类型** | **说明**                         |
|-----------------------|----------|----------------------------------|
| skill_search          | 输入框   | 按名称/编码搜索 Skill            |
| skill_category        | 下拉框   | 文本/文件/浏览器/系统等分类      |
| risk_filter           | 下拉框   | L0-L3 风险过滤                   |
| register_skill_button | 按钮     | 注册 Skill                       |
| skill_table           | 表格     | 名称、分类、版本、风险级别、状态 |
| bind_count            | 数字标签 | 被多少个 Agent 使用              |
| enable_toggle         | 开关     | 启用/停用 Skill                  |
| view_schema_button    | 按钮     | 查看输入输出 schema              |

## 8.6 审计日志页

| **字段/控件**   | **类型** | **说明**                             |
|-----------------|----------|--------------------------------------|
| entity_type     | 下拉框   | agent/skill/conversation/job         |
| action_filter   | 下拉框   | create/update/online/offline/execute |
| operator_search | 输入框   | 按操作人查询                         |
| time_range      | 日期范围 | 按时间过滤                           |
| log_table       | 表格     | 动作、对象、结果、时间               |
| detail_drawer   | 侧边抽屉 | 查看 detail_json 明细                |

# 9. API 详细设计（V1）

接口风格建议：REST 为主，聊天流式返回可使用 SSE。所有接口统一前缀
/api/v1，除登录接口外默认需要 JWT。

## 9.1 认证与用户

| **方法** | **路径**      | **说明**                                     |
|----------|---------------|----------------------------------------------|
| POST     | /auth/login   | 用户登录，返回 access_token 和 refresh_token |
| POST     | /auth/refresh | 刷新 access_token                            |
| POST     | /auth/logout  | 注销当前会话                                 |
| GET      | /users/me     | 获取当前登录用户信息                         |

登录接口示例请求体：{ email, password }；响应体建议包含
user、access_token、refresh_token、expires_in。

## 9.2 Agent 仓库

| **方法** | **路径**                      | **说明**                                    |
|----------|-------------------------------|---------------------------------------------|
| GET      | /agents                       | 查询 Agent 列表，支持 keyword、status、type |
| POST     | /agents                       | 创建 Agent，初始状态建议为 offline 或 draft |
| GET      | /agents/{id}                  | 查询 Agent 详情                             |
| PUT      | /agents/{id}                  | 更新 Agent 基本信息                         |
| POST     | /agents/{id}/online           | 上线 Agent，执行上线前校验                  |
| POST     | /agents/{id}/offline          | 下线 Agent                                  |
| POST     | /agents/{id}/archive          | 归档 Agent                                  |
| GET      | /agents/{id}/skills           | 查询 Agent 绑定的 Skills                    |
| POST     | /agents/{id}/skills           | 绑定 Skill 到 Agent                         |
| DELETE   | /agents/{id}/skills/{skillId} | 解除 Skill 绑定                             |

上线接口关键校验：Agent 非 archived；至少绑定一个 enabled Skill；Agent
policy 合法；调用者拥有 agent.manage 权限。

## 9.3 Skills 仓库

| **方法** | **路径**             | **说明**                      |
|----------|----------------------|-------------------------------|
| GET      | /skills              | 查询 Skill 列表               |
| POST     | /skills              | 注册 Skill                    |
| GET      | /skills/{id}         | 查询 Skill 详情               |
| PUT      | /skills/{id}         | 更新 Skill 元数据             |
| POST     | /skills/{id}/enable  | 启用 Skill                    |
| POST     | /skills/{id}/disable | 停用 Skill                    |
| GET      | /skills/{id}/agents  | 查看哪些 Agent 绑定了该 Skill |

注册 Skill 时建议校验：code 唯一、risk_level
必填、input_schema_json/output_schema_json 可解析、entrypoint 合法。

## 9.4 聊天与消息

| **方法** | **路径**                     | **说明**                                            |
|----------|------------------------------|-----------------------------------------------------|
| GET      | /conversations               | 获取当前用户会话列表                                |
| POST     | /conversations               | 新建会话，指定 target_type 和 target_id             |
| GET      | /conversations/{id}/messages | 分页获取消息                                        |
| POST     | /chat/send                   | 发送消息到主控管家或某个子 Agent，可选 SSE 流式返回 |

chat/send 请求体建议：{ conversation_id, target_type, target_id, content
}。处理逻辑：校验对话归属 → 校验 target 是否允许聊天选择 → 若 target 为
agent，则必须 status=online。

## 9.5 权限、策略与审计

| **方法** | **路径**            | **说明**                                           |
|----------|---------------------|----------------------------------------------------|
| GET      | /permissions/me     | 查看当前用户权限                                   |
| GET      | /agents/{id}/policy | 查询 Agent 策略                                    |
| PUT      | /agents/{id}/policy | 更新 Agent 策略                                    |
| GET      | /audit-logs         | 查询审计日志，支持 entity_type、action、time_range |
| GET      | /job-runs           | 查询执行记录                                       |
| GET      | /job-runs/{id}      | 查询单次执行详情                                   |

# 10. 第一版接口状态码与错误约定

> **•** 200：成功；201：创建成功；204：删除或解绑成功。
>
> **•** 400：参数校验失败；401：未登录或 Token 无效；403：没有权限。
>
> **•** 404：对象不存在；409：状态冲突，如重复 code、Agent
> 状态不允许上线。
>
> **•** 422：业务校验失败，如没有可用 Skill 不能上线。
>
> **•** 500：系统异常。

统一错误体建议：{ code, message, details, trace_id
}。前端所有失败提示优先使用 message，trace_id 用于日志追踪。

# 11. 快速原型阶段拆分（建议 6 周）

| **阶段** | **目标**           | **关键产出**                                                 |
|----------|--------------------|--------------------------------------------------------------|
| 第 1 周  | 基础工程与权限模块 | 登录鉴权、角色权限、数据库初始化、项目脚手架、Docker Compose |
| 第 2 周  | Agent 仓库         | Agent CRUD、上线/下线、列表与详情页                          |
| 第 3 周  | Skills 仓库        | Skill 注册/启停、绑定关系、Schema 展示                       |
| 第 4 周  | 聊天页             | 主控管家对话、会话列表、角色切换、消息持久化                 |
| 第 5 周  | 运行时联通         | 主控管家与子 Agent 路由、job_runs、基础审计                  |
| 第 6 周  | 联调与上线准备     | E2E、权限回归、部署脚本、监控与上线清单                      |

# 12. 第一阶段开发任务拆解（优先保证可上架）

## 12.1 前端

> **•** 完成登录页、聊天页、Agent 仓库页、Skills 仓库页、审计页骨架。
>
> **•** 聊天页先支持纯文本对话，不做复杂工具面板。
>
> **•** Agent 与 Skill 表格页优先可用，不追求复杂交互动画。
>
> **•** 所有状态变更统一通过确认弹窗，避免误操作。

## 12.2 后端

> **•** 落地认证、角色权限、Agent/Skill CRUD、上线下线接口。
>
> **•** 实现聊天会话存储与消息表。
>
> **•** 实现 audit_logs 与 job_runs 的基础写入。
>
> **•** 对关键状态机增加业务校验，避免非法切换。

## 12.3 AI Runtime

> **•** 先实现主控管家与文本型子 Agent 两类入口。
>
> **•** Skill 先作为声明型能力接入，真实高危工具调用放到二期。
>
> **•** 主控管家只路由到已上线且允许聊天选择的 Agent。

## 12.4 测试与运维

> **•** 接口集成测试覆盖登录、Agent 上线下线、Skill 启停、聊天发送。
>
> **•** E2E 覆盖：登录 → 创建 Agent → 绑定 Skill → 上线 → 聊天选择。
>
> **•** 准备本地、测试、预发三个 compose 配置文件或环境变量模板。

# 13. V1 上线前检查清单

> **•** 所有后台页面已做登录与权限保护。
>
> **•** 离线 Agent 不可在聊天页被直接选择执行。
>
> **•** 停用 Skill 的 Agent 在下次上线前必须重新校验。
>
> **•** 所有 create/update/online/offline/execute 动作都有审计日志。
>
> **•** 数据库有最基础备份方案；关键环境变量不写死在仓库。
>
> **•** Docker Compose 一键可启动开发环境。

# 14. 二期方向（为未来预留）

> **•** 大管家发起“创建 Agent 申请”，用户批准后自动装配。
>
> **•** 审批中心、细粒度资源权限、风险确认流。
>
> **•** 浏览器、文件、桌面、日历、邮件等更多 Skill 类型。
>
> **•** 更强的可观测性：链路追踪、截图回放、执行证据。

V3 补充说明

在 V2 基础上继续补充：SQL 建表脚本、OpenAPI
接口规范、页面线框说明，以及大模型 API 配置与多模型接入设计。V1
仍然保持快速原型目标，但从第一阶段开始内置模型网关、模型配置和权限控制。

# 14. 大模型 API 配置与多模型接入设计

设计目标：允许平台同时接入多家大模型提供方（OpenAI
兼容接口、自建模型网关、第三方云模型），并支持系统默认模型、主控管家模型、子
Agent 专属模型、备用模型和熔断切换。

• 统一接入层：后端提供 Model
Gateway，对上暴露统一调用接口，对下适配不同供应商 API。

• 配置分层：系统级默认模型、Agent 级覆盖模型、会话级临时指定模型。

• 密钥隔离：API Key
仅保存在服务端，前端不回显明文；数据库保存密文或引用外部密钥管理。

• 路由能力：按模型能力标签（chat / reasoning / vision / embedding /
tool_call）和成本策略做选择。

•
高可用：主模型失败时，按路由规则切换备用模型；写入模型调用日志，便于成本和故障分析。

• 权限约束：只有拥有 system.model.manage
权限的用户才能管理模型提供方、Key 和路由策略。

## 14.1 推荐模型接入策略（V1）

• 先支持 OpenAI 兼容协议，能够快速兼容
OpenAI、OneAPI、自建网关和部分国产模型代理。

• V1
只做文本聊天模型的统一接入；向量、重排序、视觉模型在表结构中预留字段，但实现放到后续阶段。

• 主控管家默认绑定“高稳定、长上下文”的聊天模型；子 Agent
可按用途绑定更便宜或更快的模型。

• 聊天发送接口允许传
model_override，但只有具备权限且命中白名单的情况下才能生效。

## 14.2 模型网关调用流程

• 前端发起聊天请求，指定
target_type、target_id；若未显式指定模型，则由后端根据路由规则自动选择。

• BFF 校验用户权限、目标 Agent 状态、会话归属和是否允许模型覆盖。

• Model Gateway 根据 provider、model_code、能力标签、超时和 fallback
规则选择最终模型。

• 请求通过适配器发往供应商；响应统一转成标准结构返回，并写入
llm_call_logs。

• 若主模型失败且
fallback_enabled=true，则按优先级切换备用模型，并记录切换原因。

# 15. 数据库补充：大模型、多模型接入与配置表

以下表为对 V2 数据库的增量设计，建议和 users / agents / audit_logs
放在同一个 PostgreSQL 实例中。

## 15.1 llm_providers（模型提供方）

• id UUID PK

• code VARCHAR(64) UNIQUE，提供方编码，如 openai / oneapi / azure_openai
/ custom_gateway

• name VARCHAR(128)，显示名称

• base_url VARCHAR(512)，接口基地址

• api_protocol VARCHAR(32)，默认 openai_compatible

• status VARCHAR(20)，online / offline / disabled

• config_json JSONB，公共配置

• created_at / updated_at TIMESTAMP

## 15.2 llm_provider_keys（提供方密钥）

• id UUID PK

• provider_id UUID FK -\> llm_providers.id

• key_name VARCHAR(128)

• api_key_ciphertext TEXT，密文存储

• key_mask VARCHAR(32)，页面展示用掩码

• is_default BOOLEAN

• status VARCHAR(20)

• created_by UUID FK -\> users.id

• created_at / updated_at TIMESTAMP

## 15.3 llm_models（可用模型）

• id UUID PK

• provider_id UUID FK

• model_code VARCHAR(128) UNIQUE，内部唯一编码

• provider_model_name VARCHAR(128)，供应商真实模型名

• display_name VARCHAR(128)

• model_type VARCHAR(32)，chat / reasoning / vision / embedding

• capabilities JSONB

• context_window INT

• max_output_tokens INT

• price_config_json JSONB

• status VARCHAR(20)

• is_default BOOLEAN

• created_at / updated_at TIMESTAMP

## 15.4 llm_routing_rules（模型路由规则）

• id UUID PK

• rule_name VARCHAR(128)

• target_scope VARCHAR(32)，system / butler / agent / conversation

• target_id UUID NULL

• primary_model_id UUID FK -\> llm_models.id

• fallback_model_id UUID NULL

• priority INT

• enabled BOOLEAN

• constraints_json JSONB（成本、能力、地区、是否允许覆盖）

• created_at / updated_at TIMESTAMP

## 15.5 agent_model_bindings（Agent 模型绑定）

• id UUID PK

• agent_id UUID FK -\> agents.id

• model_id UUID FK -\> llm_models.id

• binding_type VARCHAR(32)，primary / fallback / reasoning / summary

• enabled BOOLEAN

• temperature NUMERIC(3,2)

• top_p NUMERIC(3,2)

• max_output_tokens INT

• tool_choice_mode VARCHAR(32)

• created_at / updated_at TIMESTAMP

## 15.6 llm_call_logs（模型调用日志）

• id UUID PK

• conversation_id UUID NULL

• message_id UUID NULL

• agent_id UUID NULL

• provider_id UUID

• model_id UUID

• request_id VARCHAR(128)

• status VARCHAR(20)

• latency_ms INT

• prompt_tokens INT

• completion_tokens INT

• total_tokens INT

• cost_estimate NUMERIC(12,6)

• fallback_used BOOLEAN

• error_code VARCHAR(64)

• error_message TEXT

• created_at TIMESTAMP

# 16. SQL 建表脚本（V1 + 模型配置增量）

以下 SQL
为快速原型可直接落地的基础脚本。生产环境可再补充审计分区、软删除和迁移版本管理。

> CREATE EXTENSION IF NOT EXISTS "pgcrypto";
>
> CREATE TABLE IF NOT EXISTS llm_providers (
>
> id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
>
> code VARCHAR(64) NOT NULL UNIQUE,
>
> name VARCHAR(128) NOT NULL,
>
> base_url VARCHAR(512) NOT NULL,
>
> api_protocol VARCHAR(32) NOT NULL DEFAULT 'openai_compatible',
>
> status VARCHAR(20) NOT NULL DEFAULT 'online',
>
> config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
>
> created_at TIMESTAMP NOT NULL DEFAULT NOW(),
>
> updated_at TIMESTAMP NOT NULL DEFAULT NOW()
>
> );
>
> CREATE TABLE IF NOT EXISTS llm_provider_keys (
>
> id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
>
> provider_id UUID NOT NULL REFERENCES llm_providers(id),
>
> key_name VARCHAR(128) NOT NULL,
>
> api_key_ciphertext TEXT NOT NULL,
>
> key_mask VARCHAR(32) NOT NULL,
>
> is_default BOOLEAN NOT NULL DEFAULT FALSE,
>
> status VARCHAR(20) NOT NULL DEFAULT 'active',
>
> created_by UUID,
>
> created_at TIMESTAMP NOT NULL DEFAULT NOW(),
>
> updated_at TIMESTAMP NOT NULL DEFAULT NOW()
>
> );
>
> CREATE TABLE IF NOT EXISTS llm_models (
>
> id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
>
> provider_id UUID NOT NULL REFERENCES llm_providers(id),
>
> model_code VARCHAR(128) NOT NULL UNIQUE,
>
> provider_model_name VARCHAR(128) NOT NULL,
>
> display_name VARCHAR(128) NOT NULL,
>
> model_type VARCHAR(32) NOT NULL DEFAULT 'chat',
>
> capabilities JSONB NOT NULL DEFAULT '\[\]'::jsonb,
>
> context_window INT,
>
> max_output_tokens INT,
>
> price_config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
>
> status VARCHAR(20) NOT NULL DEFAULT 'online',
>
> is_default BOOLEAN NOT NULL DEFAULT FALSE,
>
> created_at TIMESTAMP NOT NULL DEFAULT NOW(),
>
> updated_at TIMESTAMP NOT NULL DEFAULT NOW()
>
> );
>
> CREATE TABLE IF NOT EXISTS llm_routing_rules (
>
> id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
>
> rule_name VARCHAR(128) NOT NULL,
>
> target_scope VARCHAR(32) NOT NULL,
>
> target_id UUID,
>
> primary_model_id UUID NOT NULL REFERENCES llm_models(id),
>
> fallback_model_id UUID REFERENCES llm_models(id),
>
> priority INT NOT NULL DEFAULT 100,
>
> enabled BOOLEAN NOT NULL DEFAULT TRUE,
>
> constraints_json JSONB NOT NULL DEFAULT '{}'::jsonb,
>
> created_at TIMESTAMP NOT NULL DEFAULT NOW(),
>
> updated_at TIMESTAMP NOT NULL DEFAULT NOW()
>
> );
>
> CREATE TABLE IF NOT EXISTS agent_model_bindings (
>
> id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
>
> agent_id UUID NOT NULL,
>
> model_id UUID NOT NULL REFERENCES llm_models(id),
>
> binding_type VARCHAR(32) NOT NULL DEFAULT 'primary',
>
> enabled BOOLEAN NOT NULL DEFAULT TRUE,
>
> temperature NUMERIC(3,2),
>
> top_p NUMERIC(3,2),
>
> max_output_tokens INT,
>
> tool_choice_mode VARCHAR(32) NOT NULL DEFAULT 'auto',
>
> created_at TIMESTAMP NOT NULL DEFAULT NOW(),
>
> updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
>
> UNIQUE(agent_id, model_id, binding_type)
>
> );
>
> CREATE TABLE IF NOT EXISTS llm_call_logs (
>
> id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
>
> conversation_id UUID,
>
> message_id UUID,
>
> agent_id UUID,
>
> provider_id UUID NOT NULL REFERENCES llm_providers(id),
>
> model_id UUID NOT NULL REFERENCES llm_models(id),
>
> request_id VARCHAR(128),
>
> status VARCHAR(20) NOT NULL,
>
> latency_ms INT,
>
> prompt_tokens INT,
>
> completion_tokens INT,
>
> total_tokens INT,
>
> cost_estimate NUMERIC(12,6),
>
> fallback_used BOOLEAN NOT NULL DEFAULT FALSE,
>
> error_code VARCHAR(64),
>
> error_message TEXT,
>
> created_at TIMESTAMP NOT NULL DEFAULT NOW()
>
> );
>
> CREATE INDEX IF NOT EXISTS idx_llm_models_provider_status ON
> llm_models(provider_id, status);
>
> CREATE INDEX IF NOT EXISTS idx_llm_routing_rules_scope_priority ON
> llm_routing_rules(target_scope, priority);
>
> CREATE INDEX IF NOT EXISTS idx_llm_call_logs_created_at ON
> llm_call_logs(created_at DESC);

# 17. OpenAPI 接口规范（核心接口草案）

以下为可直接转成 openapi.yaml 的核心片段，便于前后端并行开发。

> openapi: 3.0.3
>
> info:
>
> title: Butler Platform API
>
> version: 1.0.0
>
> paths:
>
> /api/v1/auth/login:
>
> post:
>
> summary: 用户登录
>
> /api/v1/agents:
>
> get:
>
> summary: 获取 Agent 列表
>
> post:
>
> summary: 创建 Agent
>
> /api/v1/agents/{agentId}/online:
>
> post:
>
> summary: Agent 上线
>
> /api/v1/agents/{agentId}/offline:
>
> post:
>
> summary: Agent 下线
>
> /api/v1/skills:
>
> get:
>
> summary: 获取 Skill 列表
>
> post:
>
> summary: 注册 Skill
>
> /api/v1/chat/send:
>
> post:
>
> summary: 发送聊天消息
>
> /api/v1/model/providers:
>
> get:
>
> summary: 获取模型提供方列表
>
> post:
>
> summary: 新增模型提供方
>
> /api/v1/model/providers/{providerId}/keys:
>
> post:
>
> summary: 新增提供方密钥
>
> /api/v1/model/models:
>
> get:
>
> summary: 获取模型列表
>
> post:
>
> summary: 注册模型
>
> /api/v1/model/routing-rules:
>
> get:
>
> summary: 获取路由规则
>
> post:
>
> summary: 创建路由规则
>
> /api/v1/model/agent-bindings:
>
> post:
>
> summary: 绑定 Agent 与模型
>
> components:
>
> schemas:
>
> Agent:
>
> type: object
>
> properties:
>
> id: { type: string, format: uuid }
>
> name: { type: string }
>
> status: { type: string, enum: \[draft, offline, online, paused,
> archived\] }
>
> ModelProvider:
>
> type: object
>
> properties:
>
> id: { type: string, format: uuid }
>
> code: { type: string }
>
> base_url: { type: string }
>
> status: { type: string }
>
> Model:
>
> type: object
>
> properties:
>
> id: { type: string, format: uuid }
>
> model_code: { type: string }
>
> display_name: { type: string }
>
> model_type: { type: string }
>
> capabilities:
>
> type: array
>
> items: { type: string }

# 18. API 详细设计补充

## 18.1 模型提供方管理

• GET /api/v1/model/providers：查询提供方列表，支持 status、code 搜索。

• POST /api/v1/model/providers：创建提供方；请求体 { code, name,
base_url, api_protocol, config_json }。

• PATCH /api/v1/model/providers/{providerId}：更新
base_url、状态、公共配置。

• POST /api/v1/model/providers/{providerId}/keys：新增 Key；请求体 {
key_name, api_key_plaintext, is_default }。

• PATCH /api/v1/model/provider-keys/{keyId}/status：启用/停用 Key。

## 18.2 模型管理

• GET /api/v1/model/models：查询模型列表；支持
provider_id、model_type、status 过滤。

• POST /api/v1/model/models：注册模型；请求体 { provider_id, model_code,
provider_model_name, display_name, model_type, capabilities,
context_window, max_output_tokens, price_config_json }。

• PATCH /api/v1/model/models/{modelId}：更新模型元信息与状态。

## 18.3 路由与绑定

• GET /api/v1/model/routing-rules：查询路由规则。

• POST /api/v1/model/routing-rules：创建规则；请求体 { rule_name,
target_scope, target_id, primary_model_id, fallback_model_id, priority,
enabled, constraints_json }。

• POST /api/v1/model/agent-bindings：绑定 Agent 与模型；请求体 {
agent_id, model_id, binding_type, temperature, top_p, max_output_tokens
}。

• DELETE /api/v1/model/agent-bindings/{bindingId}：删除绑定。

## 18.4 聊天接口补充

• POST /api/v1/chat/send：新增可选字段 { model_override, stream,
metadata }。

• 当 target_type=butler 时，优先命中 butler 路由规则；当
target_type=agent 时，优先命中 agent_model_bindings。

• 若 model_override
存在，后端仍需校验当前用户是否有会话级覆写权限，以及该模型是否在线。

# 19. 页面线框图说明与字段清单补充

## 19.1 聊天页（主控管家 / 子 Agent 切换）

• 左侧：会话列表、目标选择器（主控管家 / 子 Agent）、Agent
在线状态标识。

• 中部：消息流、输入框、发送按钮、流式状态。

• 右侧可选信息栏：当前目标简介、已绑定 Skills、当前模型、最近调用日志。

•
字段：conversation_id、target_type、target_id、target_status、selected_model（只读或可覆盖）、input_text。

## 19.2 Agent 仓库页

•
表格字段：name、code、type、status、chat_selectable、risk_level、bound_skill_count、bound_model、updated_at。

• 操作：查看、编辑、上线、下线、归档、绑定模型。

## 19.3 Skills 仓库页

•
表格字段：name、code、version、risk_level、status、entrypoint、bound_agent_count、updated_at。

• 操作：注册、编辑、启停、查看被引用关系。

## 19.4 模型配置页（新增）

• 页签一：模型提供方；字段 name、code、base_url、api_protocol、status。

• 页签二：模型列表；字段
display_name、model_code、provider、model_type、capabilities、context_window、status、is_default。

• 页签三：Agent 模型绑定；字段
agent_name、binding_type、model_name、temperature、top_p、max_output_tokens、enabled。

• 页签四：路由规则；字段
rule_name、target_scope、target_id、primary_model、fallback_model、priority、enabled。

## 19.5 系统设置 / 权限页

•
字段：allow_model_override、allow_custom_provider、default_chat_model_id、default_butler_model_id、audit_retention_days。

•
权限项：system.model.manage、agent.manage、skill.manage、audit.read、chat.use_agent。

# 20. WSL + Docker 需下载安装的软件清单（详细版）

• Windows 11（建议 22H2 及以上）

• WSL2 + Ubuntu 22.04 LTS

• Docker Desktop（启用 WSL Integration）

• Visual Studio Code + Remote - WSL + Docker + ESLint + Prettier 插件

• Git

• Node.js 20 LTS

• pnpm 9.x

• Python 3.11

• uv 或 Poetry（二选一，建议 uv）

• Postman 或 Bruno（调试 API）

• DBeaver 或 TablePlus（查看 PostgreSQL）

• pgAdmin 可选

• Google Chrome（联调聊天和后台页面）

• Redis Insight 可选（查看缓存）

• Make 或 just（二选一，统一项目命令）

## 20.1 建议安装命令（WSL 内）

> sudo apt update && sudo apt upgrade -y
>
> sudo apt install -y build-essential curl git unzip ca-certificates
>
> curl -fsSL https://deb.nodesource.com/setup_20.x \| sudo -E bash -
>
> sudo apt install -y nodejs python3 python3-pip python3-venv
>
> npm install -g pnpm
>
> curl -LsSf https://astral.sh/uv/install.sh \| sh

# 21. 第一阶段建议新增的安全验收标准

• 未登录用户无法访问聊天页、Agent 仓库、Skills 仓库、模型配置页。

• 离线 Agent 不可被聊天页选中执行；强行调用返回 403 或 422。

• 未绑定模型的 Agent 不允许上线，除非系统显式允许继承默认模型。

• 模型配置页中的 API Key 不回显明文，只展示掩码。

• 所有模型切换、路由变更、上线下线、权限变更都写入 audit_logs。

• 当主模型失败并发生 fallback 时，llm_call_logs 能明确记录
fallback_used=true。
