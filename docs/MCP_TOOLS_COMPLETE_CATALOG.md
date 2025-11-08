# AceFlow MCP Tools 完整清单

> AceFlow MCP Server 提供的所有 MCP Tools 完整列表和使用说明

**版本**: v1.0.0
**日期**: 2025-01-06
**总数**: 17 个 Tools

---

## 📋 目录

1. [通用工作流工具 (4个)](#通用工作流工具)
2. [Contract-First 工作流工具 (13个)](#contract-first-工作流工具)
   - [项目初始化](#项目初始化-1个)
   - [需求定义](#需求定义-1个)
   - [API 设计](#api-设计-1个)
   - [契约管理](#契约管理-3个)
   - [Mock Server](#mock-server-2个)
   - [契约验证](#契约验证-1个)
   - [工作流状态管理](#工作流状态管理-4个)

---

## 通用工作流工具

这些工具支持标准的 AceFlow 工作流（非 Contract-First）。

### 1. aceflow_init

**功能**: 初始化 AceFlow 项目（通用模式）

**参数**:
```typescript
{
  mode: string,              // 工作流模式: "minimal" | "standard" | "contract_first"
  project_name?: string      // 项目名称（可选）
}
```

**返回**:
```json
{
  "success": true,
  "mode": "standard",
  "message": "Project initialized"
}
```

**使用场景**: 快速初始化非 Contract-First 项目

---

### 2. aceflow_stage

**功能**: 管理工作流阶段（通用工作流）

**参数**:
```typescript
{
  action: string,       // 操作: "next" | "current" | "list"
  stage?: string        // 目标阶段（可选）
}
```

**返回**:
```json
{
  "current_stage": "implementation",
  "available_stages": ["user_stories", "task_breakdown", ...]
}
```

**使用场景**: 查看或切换通用工作流阶段

---

### 3. aceflow_validate

**功能**: 验证项目完整性（通用工作流）

**参数**:
```typescript
{
  mode?: string,     // 验证模式: "basic" | "full"
  fix?: boolean      // 是否自动修复问题
}
```

**返回**:
```json
{
  "valid": true,
  "issues": [],
  "fixed": 0
}
```

**使用场景**: 检查项目配置和文件完整性

---

### 4. aceflow_template

**功能**: 管理工作流模板

**参数**:
```typescript
{
  action: string,       // 操作: "list" | "apply" | "create"
  template?: string     // 模板名称（可选）
}
```

**返回**:
```json
{
  "templates": ["minimal", "standard", "contract_first"],
  "current": "contract_first"
}
```

**使用场景**: 管理和切换工作流模板

---

## Contract-First 工作流工具

专为 Contract-First 开发模式设计的工具集。

### 项目初始化 (1个)

#### 5. aceflow_init_project

**功能**: 初始化 Contract-First 项目（推荐使用）

**参数**:
```typescript
{
  project_name: string,              // 项目名称
  workflow_mode?: string,            // 模式: "contract_first" (默认)
  openapi_url?: string,              // OpenAPI 文档 URL
  repo_url?: string,                 // 契约 Git 仓库 URL
  smtp_config?: {                    // SMTP 配置（可选）
    enabled: boolean,
    host: string,
    port: number,
    user: string,
    password: string,
    from: string
  }
}
```

**返回**:
```json
{
  "success": true,
  "config_file": ".aceflow/config.yaml",
  "workflow_file": ".aceflow/workflow.json",
  "current_stage": "setup",
  "next_steps": [
    "Define your first feature using aceflow_define_feature",
    "Configure OpenAPI URL if not provided"
  ]
}
```

**使用场景**:
- 开始新的 Contract-First 项目
- 配置契约仓库和通知
- 初始化工作流状态

**示例**:
```typescript
await aceflow_init_project({
  project_name: "datasource-management-system",
  workflow_mode: "contract_first",
  openapi_url: "http://localhost:8080/v3/api-docs",
  repo_url: "git@gitlab:contracts/datasource.git"
})
```

---

### 需求定义 (1个)

#### 6. aceflow_define_feature

**功能**: 定义功能需求和 API Scope

**参数**:
```typescript
{
  feature_name: string,              // 功能名称（kebab-case）
  description: string,               // 功能描述
  api_scope_type: string,            // 过滤类型: "prefix" | "regex" | "exact"
  api_scope_pattern: string,         // API 路径匹配模式
  dev_team?: string[],               // 开发团队成员（可选）
  priority?: string                  // 优先级: "high" | "medium" | "low"
}
```

**返回**:
```json
{
  "success": true,
  "feature": "datasource-management",
  "api_scope": {
    "type": "prefix",
    "pattern": "/api/datasources"
  },
  "config_updated": true,
  "message": "Feature defined successfully"
}
```

**使用场景**:
- 定义新功能需求
- 配置 API 过滤规则
- 设置开发团队

**示例**:
```typescript
await aceflow_define_feature({
  feature_name: "user-authentication",
  description: "User login and registration system",
  api_scope_type: "prefix",
  api_scope_pattern: "/api/auth/",
  dev_team: ["backend@example.com", "frontend@example.com"],
  priority: "high"
})
```

---

### API 设计 (1个)

#### 7. aceflow_design_api

**功能**: AI 辅助设计 API（从零开始）

**参数**:
```typescript
{
  feature: string,              // 功能名称
  endpoints: list,              // API 端点列表
  requirements?: string         // 需求描述（可选）
}
```

**返回**:
```json
{
  "success": true,
  "contract_file": "aceflow_result/contracts/user-auth.json",
  "endpoints": 5,
  "schemas": 3
}
```

**使用场景**:
- AI 辅助从头设计 API
- 根据需求生成 OpenAPI 契约

**注意**: 这个工具主要用于 AI 辅助设计，实际项目中更常用 `aceflow_contract_generate`

---

### 契约管理 (3个)

#### 8. aceflow_contract_generate

**功能**: 从后端 OpenAPI 生成契约

**参数**:
```typescript
{
  feature: string,                    // 功能名称
  apply_smart_completion?: boolean,   // 是否应用智能补全（默认 true）
  output_format?: string              // 输出格式: "json" | "yaml"
}
```

**返回**:
```json
{
  "success": true,
  "contract_file": "aceflow_result/contracts/datasource-management.json",
  "matched_paths": 9,
  "total_paths": 45,
  "matched_operations": 9,
  "total_operations": 120,
  "smart_completion_applied": true,
  "message": "Contract generated successfully"
}
```

**使用场景**:
- 从 Spring Boot 后端生成契约
- 应用智能补全规则
- 过滤特定功能的 API

**工作流**:
1. 连接到配置的 `openapi_url`
2. 根据 `api_scope` 过滤端点
3. 应用智能补全规则
4. 保存到 `aceflow_result/contracts/`

**示例**:
```typescript
await aceflow_contract_generate({
  feature: "datasource-management",
  apply_smart_completion: true,
  output_format: "json"
})
```

---

#### 9. aceflow_contract_push

**功能**: 推送契约到 Git 仓库

**参数**:
```typescript
{
  feature: string,            // 功能名称
  message?: string,           // Commit 消息（可选）
  branch?: string             // Git 分支（默认: main）
}
```

**返回**:
```json
{
  "success": true,
  "commit_hash": "abc1234",
  "branch": "main",
  "notification_sent": true,
  "recipients": ["frontend@example.com"],
  "message": "Contract pushed successfully"
}
```

**使用场景**:
- 推送契约到团队共享仓库
- 自动通知前端团队
- 触发 CI/CD 流程

**工作流**:
1. Clone/Pull 契约仓库
2. 复制契约文件到仓库
3. Commit 并 Push
4. 发送邮件通知（如果配置了 SMTP）

**示例**:
```typescript
await aceflow_contract_push({
  feature: "datasource-management",
  message: "feat: add datasource management API contract",
  branch: "main"
})
```

---

#### 10. aceflow_contract_pull

**功能**: 从 Git 仓库拉取契约

**参数**:
```typescript
{
  feature: string,            // 功能名称
  branch?: string             // Git 分支（默认: main）
}
```

**返回**:
```json
{
  "success": true,
  "contract_file": ".aceflow/contracts/user-auth.json",
  "branch": "main",
  "last_commit": "abc1234",
  "message": "Contract pulled successfully"
}
```

**使用场景**:
- 前端拉取最新契约
- 同步团队契约变更
- 准备启动 Mock Server

**工作流**:
1. Clone/Pull 契约仓库
2. 复制契约文件到本地 `.aceflow/contracts/`
3. 准备 Mock Server 使用

**示例**:
```typescript
await aceflow_contract_pull({
  feature: "datasource-management",
  branch: "develop"
})
```

---

### Mock Server (2个)

#### 11. aceflow_mock_start

**功能**: 启动 Mock Server

**参数**:
```typescript
{
  feature: string,              // 功能名称
  port?: number,                // 端口号（默认: 4010）
  dynamic?: boolean,            // 动态响应生成（默认: true）
  validate?: boolean            // 请求验证（默认: true）
}
```

**返回**:
```json
{
  "success": true,
  "feature": "datasource-management",
  "port": 4020,
  "url": "http://localhost:4020",
  "pid": 12345,
  "contract_file": "aceflow_result/contracts/datasource-management.json",
  "message": "Mock Server started successfully"
}
```

**使用场景**:
- 前端开发环境
- 并行开发（后端未完成时）
- API 测试

**工作流**:
1. 查找契约文件
2. 使用 Prism 启动 Mock Server
3. 记录 PID 到 `.aceflow/mock/`
4. 更新工作流状态

**示例**:
```typescript
await aceflow_mock_start({
  feature: "datasource-management",
  port: 4020,
  dynamic: true,
  validate: true
})
```

---

#### 12. aceflow_mock_stop

**功能**: 停止 Mock Server

**参数**:
```typescript
{
  port?: number,              // 端口号（二选一）
  stop_all?: boolean          // 停止所有（二选一）
}
```

**返回**:
```json
{
  "success": true,
  "stopped": [
    {
      "port": 4020,
      "feature": "datasource-management",
      "pid": 12345
    }
  ],
  "message": "Mock Server(s) stopped"
}
```

**使用场景**:
- 切换到真实后端
- 释放端口
- 清理测试环境

**示例**:
```typescript
// 停止特定端口
await aceflow_mock_stop({ port: 4020 })

// 停止所有
await aceflow_mock_stop({ stop_all: true })
```

---

### 契约验证 (1个)

#### 13. aceflow_validate_contract

**功能**: 验证后端实现与契约一致性

**参数**:
```typescript
{
  feature: string,                // 功能名称
  actual_openapi_url: string      // 后端实际 OpenAPI URL
}
```

**返回**:
```json
{
  "success": true,
  "compliant": true,
  "missing_endpoints": [],
  "extra_endpoints": [],
  "schema_differences": [],
  "message": "Contract validation passed"
}
```

**返回（验证失败）**:
```json
{
  "success": true,
  "compliant": false,
  "missing_endpoints": [
    "/api/datasources/{id}/test"
  ],
  "extra_endpoints": [
    "/api/datasources/export"
  ],
  "schema_differences": [
    {
      "path": "/api/datasources",
      "field": "datasource_type",
      "expected": "enum [FTP, SFTP]",
      "actual": "string"
    }
  ],
  "message": "Contract validation failed: 1 missing, 1 extra, 1 schema diff"
}
```

**使用场景**:
- 后端实现完成后验证
- CI/CD 自动化测试
- 确保前后端一致性

**工作流**:
1. 读取本地契约文件
2. 获取后端实际 OpenAPI
3. 对比差异
4. 生成详细报告

**示例**:
```typescript
await aceflow_validate_contract({
  feature: "datasource-management",
  actual_openapi_url: "http://localhost:8080/v3/api-docs"
})
```

---

### 工作流状态管理 (4个)

#### 14. aceflow_workflow_status

**功能**: 获取工作流状态和进度

**参数**: 无

**返回**:
```json
{
  "success": true,
  "current_stage": "design",
  "workflow_mode": "contract_first",
  "overall_progress": 30,
  "completed_stages": 3,
  "total_stages": 10,
  "features": {
    "datasource-management": {
      "status": "design",
      "contract_file": "aceflow_result/contracts/datasource-management.json",
      "mock_server": {
        "running": true,
        "port": 4020
      }
    }
  },
  "metrics": {
    "total_features": 1,
    "in_progress_features": 1,
    "completed_features": 0,
    "mock_servers_running": 1
  },
  "recommendations": [
    {
      "priority": "high",
      "action": "Push contract to Git",
      "tool": "aceflow_contract_push"
    }
  ],
  "message": "Currently at design stage (30% complete)"
}
```

**使用场景**:
- 查看项目当前进度
- 了解下一步操作
- 团队状态同步

**示例**:
```typescript
const status = await aceflow_workflow_status()
console.log(`Current stage: ${status.current_stage}`)
console.log(`Progress: ${status.overall_progress}%`)
```

---

#### 15. aceflow_workflow_advance

**功能**: 推进到下一阶段

**参数**:
```typescript
{
  next_stage: string,              // 目标阶段
  feature_name?: string            // 功能名称（可选）
}
```

**阶段列表**:
- `setup` - 初始化
- `define` - 需求定义
- `design` - API 设计
- `implement` - 后端实现
- `contract_push` - 契约推送
- `frontend_dev` - 前端开发
- `validate` - 契约验证
- `integration` - 集成测试
- `review` - 代码审查
- `completed` - 完成

**返回**:
```json
{
  "success": true,
  "previous_stage": "define",
  "current_stage": "design",
  "started_at": "2025-01-06T08:00:00Z",
  "message": "Advanced from define to design"
}
```

**返回（验证失败）**:
```json
{
  "success": false,
  "error": "Current stage not ready for transition",
  "message": "Please complete required checkpoints first",
  "validation": {
    "stage": "define",
    "required_failed": ["requirements_documented"],
    "can_proceed": false
  },
  "current_stage": "define"
}
```

**使用场景**:
- 完成一个阶段后推进
- 触发自动化流程
- 更新团队进度

**示例**:
```typescript
await aceflow_workflow_advance({
  next_stage: "design",
  feature_name: "datasource-management"
})
```

---

#### 16. aceflow_workflow_checkpoint

**功能**: 更新阶段检查点

**参数**:
```typescript
{
  stage: string,              // 阶段名称
  checkpoint: string,         // 检查点名称
  value: boolean              // 检查点值
}
```

**常用检查点**:

**Setup 阶段**:
- `config_file_exists` - 配置文件存在
- `openapi_url_valid` - OpenAPI URL 有效
- `repo_url_valid` - Git 仓库 URL 有效
- `smtp_configured` - SMTP 已配置（可选）

**Define 阶段**:
- `feature_config_exists` - 功能配置存在
- `api_scope_defined` - API Scope 已定义
- `requirements_documented` - 需求已文档化

**Design 阶段**:
- `contract_file_exists` - 契约文件存在
- `valid_openapi_spec` - OpenAPI 规范有效
- `has_endpoints` - 包含端点
- `smart_completion_applied` - 智能补全已应用（可选）

**Contract Push 阶段**:
- `git_commit_successful` - Git 提交成功
- `git_push_successful` - Git 推送成功
- `team_notified` - 团队已通知（可选）

**Validate 阶段**:
- `contract_compliant` - 契约符合规范
- `no_missing_endpoints` - 无缺失端点
- `no_extra_endpoints` - 无额外端点

**Integration 阶段**:
- `e2e_tests_passing` - E2E 测试通过
- `no_critical_bugs` - 无严重 Bug
- `performance_acceptable` - 性能可接受（可选）

**返回**:
```json
{
  "success": true,
  "stage": "design",
  "checkpoint": "contract_file_exists",
  "value": true,
  "message": "Checkpoint 'contract_file_exists' set to true for stage 'design'"
}
```

**使用场景**:
- 标记完成条件
- 自动化流程验证
- Quality Gates

**示例**:
```typescript
await aceflow_workflow_checkpoint({
  stage: "design",
  checkpoint: "contract_file_exists",
  value: true
})
```

---

#### 17. aceflow_workflow_recommendations

**功能**: 获取智能推荐操作

**参数**: 无

**返回**:
```json
{
  "success": true,
  "recommendations": [
    {
      "priority": "high",
      "action": "Push contract to Git and notify team",
      "tool": "aceflow_contract_push",
      "benefits": [
        "Notify frontend team",
        "Enable parallel development",
        "Version control for contracts"
      ]
    },
    {
      "priority": "high",
      "audience": "backend",
      "action": "Implement backend APIs",
      "message": "Write Spring Boot controllers and add OpenAPI annotations"
    },
    {
      "priority": "high",
      "audience": "frontend",
      "action": "Start frontend development with Mock Server",
      "tools": ["aceflow_contract_pull", "aceflow_mock_start"],
      "message": "Pull contract and start Mock Server"
    }
  ],
  "message": "3 recommendations available"
}
```

**使用场景**:
- AI 助手获取下一步建议
- 引导用户工作流
- 自动化决策

**示例**:
```typescript
const recs = await aceflow_workflow_recommendations()
for (const rec of recs.recommendations) {
  console.log(`[${rec.priority}] ${rec.action}`)
}
```

---

## 📊 工具分类总结

### 按功能分类

| 类别 | 工具数量 | 工具列表 |
|-----|---------|---------|
| **通用工作流** | 4 | aceflow_init, aceflow_stage, aceflow_validate, aceflow_template |
| **项目初始化** | 1 | aceflow_init_project |
| **需求管理** | 1 | aceflow_define_feature |
| **API 设计** | 1 | aceflow_design_api |
| **契约管理** | 3 | aceflow_contract_generate, aceflow_contract_push, aceflow_contract_pull |
| **Mock Server** | 2 | aceflow_mock_start, aceflow_mock_stop |
| **契约验证** | 1 | aceflow_validate_contract |
| **状态管理** | 4 | aceflow_workflow_status, aceflow_workflow_advance, aceflow_workflow_checkpoint, aceflow_workflow_recommendations |

### 按使用频率分类

**高频工具** (常用):
1. `aceflow_init_project` - 项目初始化
2. `aceflow_define_feature` - 定义功能
3. `aceflow_contract_generate` - 生成契约
4. `aceflow_mock_start` - 启动 Mock
5. `aceflow_workflow_status` - 查看状态

**中频工具** (阶段性):
6. `aceflow_contract_push` - 推送契约
7. `aceflow_contract_pull` - 拉取契约
8. `aceflow_validate_contract` - 验证契约
9. `aceflow_workflow_advance` - 推进阶段
10. `aceflow_mock_stop` - 停止 Mock

**低频工具** (辅助):
11. `aceflow_workflow_checkpoint` - 更新检查点
12. `aceflow_workflow_recommendations` - 获取推荐
13. `aceflow_design_api` - AI 设计
14. `aceflow_init` - 通用初始化
15. `aceflow_stage` - 通用阶段
16. `aceflow_validate` - 通用验证
17. `aceflow_template` - 模板管理

---

## 🚀 典型工作流示例

### Contract-First 完整流程

```typescript
// 1. 初始化项目
await aceflow_init_project({
  project_name: "datasource-management-system",
  workflow_mode: "contract_first",
  openapi_url: "http://localhost:8080/v3/api-docs",
  repo_url: "git@gitlab:contracts/datasource.git"
})

// 2. 定义功能
await aceflow_define_feature({
  feature_name: "datasource-management",
  description: "数据源管理系统",
  api_scope_type: "prefix",
  api_scope_pattern: "/api/datasources"
})

// 3. 推进到 Design 阶段
await aceflow_workflow_advance({
  next_stage: "design"
})

// 4. 生成契约
await aceflow_contract_generate({
  feature: "datasource-management"
})

// 5. 推送契约
await aceflow_contract_push({
  feature: "datasource-management",
  message: "feat: add datasource management API"
})

// 6. 前端拉取契约
await aceflow_contract_pull({
  feature: "datasource-management"
})

// 7. 启动 Mock Server（前端开发）
await aceflow_mock_start({
  feature: "datasource-management",
  port: 4020
})

// 8. 后端实现完成后验证
await aceflow_validate_contract({
  feature: "datasource-management",
  actual_openapi_url: "http://localhost:8080/v3/api-docs"
})

// 9. 停止 Mock Server
await aceflow_mock_stop({
  port: 4020
})

// 10. 查看最终状态
await aceflow_workflow_status()
```

---

## 📚 相关文档

- [MCP Tools 测试指南](./MCP_TOOLS_TESTING_GUIDE.md)
- [Contract-First 工作流验证报告](./ACEFLOW_WORKFLOW_VALIDATION_REPORT.md)
- [工作流状态管理](./WORKFLOW_STATE_TRACKING_CORRECTION.md)
- [Quick Start Guide](/home/chenjing/AI/aceflow-ai/docs/QUICK_START_GUIDE.md)

---

**创建时间**: 2025-01-06
**维护者**: AceFlow Team
**版本**: v1.0.0
