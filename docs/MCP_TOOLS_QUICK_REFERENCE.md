# AceFlow MCP Tools 速查表

## 总览

**总数**: 17 个 MCP Tools
**分类**: 通用工作流 (4) + Contract-First (13)

---

## 快速参考表

| # | Tool 名称 | 分类 | 功能 | 常用度 |
|---|----------|------|------|--------|
| 1 | `aceflow_init` | 通用 | 初始化通用项目 | ⭐ |
| 2 | `aceflow_stage` | 通用 | 管理通用阶段 | ⭐ |
| 3 | `aceflow_validate` | 通用 | 验证项目完整性 | ⭐ |
| 4 | `aceflow_template` | 通用 | 管理工作流模板 | ⭐ |
| 5 | **`aceflow_init_project`** | 初始化 | **初始化 Contract-First 项目** | ⭐⭐⭐⭐⭐ |
| 6 | **`aceflow_define_feature`** | 需求 | **定义功能和 API Scope** | ⭐⭐⭐⭐⭐ |
| 7 | `aceflow_design_api` | 设计 | AI 辅助设计 API | ⭐⭐ |
| 8 | **`aceflow_contract_generate`** | 契约 | **从后端生成契约** | ⭐⭐⭐⭐⭐ |
| 9 | **`aceflow_contract_push`** | 契约 | **推送契约到 Git** | ⭐⭐⭐⭐ |
| 10 | **`aceflow_contract_pull`** | 契约 | **从 Git 拉取契约** | ⭐⭐⭐⭐ |
| 11 | **`aceflow_mock_start`** | Mock | **启动 Mock Server** | ⭐⭐⭐⭐⭐ |
| 12 | **`aceflow_mock_stop`** | Mock | **停止 Mock Server** | ⭐⭐⭐ |
| 13 | **`aceflow_validate_contract`** | 验证 | **验证契约一致性** | ⭐⭐⭐⭐ |
| 14 | **`aceflow_workflow_status`** | 状态 | **查看工作流状态** | ⭐⭐⭐⭐⭐ |
| 15 | **`aceflow_workflow_advance`** | 状态 | **推进到下一阶段** | ⭐⭐⭐⭐ |
| 16 | `aceflow_workflow_checkpoint` | 状态 | 更新阶段检查点 | ⭐⭐⭐ |
| 17 | `aceflow_workflow_recommendations` | 状态 | 获取智能推荐 | ⭐⭐⭐ |

---

## Contract-First 核心流程（10个工具）

### 阶段 1: Setup（初始化）
```typescript
aceflow_init_project()           // 初始化项目
aceflow_workflow_status()        // 查看状态
```

### 阶段 2: Define（定义需求）
```typescript
aceflow_define_feature()         // 定义功能
aceflow_workflow_advance()       // 推进到 Design
```

### 阶段 3: Design（设计契约）
```typescript
aceflow_contract_generate()      // 生成契约
aceflow_workflow_advance()       // 推进到 Contract Push
```

### 阶段 4: Contract Push（推送契约）
```typescript
aceflow_contract_push()          // 推送到 Git
aceflow_workflow_advance()       // 推进到 Frontend Dev
```

### 阶段 5: Frontend Dev（前端开发）
```typescript
aceflow_contract_pull()          // 拉取契约
aceflow_mock_start()             // 启动 Mock Server
// ... 前端开发 ...
```

### 阶段 6: Implement（后端实现）
```typescript
// 后端开发 Spring Boot API
```

### 阶段 7: Validate（契约验证）
```typescript
aceflow_validate_contract()      // 验证一致性
aceflow_workflow_advance()       // 推进到 Integration
```

### 阶段 8: Integration（集成测试）
```typescript
aceflow_mock_stop()              // 停止 Mock Server
// ... E2E 测试 ...
```

---

## 工作流阶段

```
setup → define → design → implement → contract_push 
  ↓
frontend_dev → validate → integration → review → completed
```

---

## 使用频率分级

### ⭐⭐⭐⭐⭐ 必须掌握（5个）
1. `aceflow_init_project` - 项目初始化
2. `aceflow_define_feature` - 定义功能
3. `aceflow_contract_generate` - 生成契约
4. `aceflow_mock_start` - 启动 Mock
5. `aceflow_workflow_status` - 查看状态

### ⭐⭐⭐⭐ 常用工具（4个）
6. `aceflow_contract_push` - 推送契约
7. `aceflow_contract_pull` - 拉取契约
8. `aceflow_validate_contract` - 验证契约
9. `aceflow_workflow_advance` - 推进阶段

### ⭐⭐⭐ 辅助工具（4个）
10. `aceflow_mock_stop` - 停止 Mock
11. `aceflow_workflow_checkpoint` - 更新检查点
12. `aceflow_workflow_recommendations` - 获取推荐
13. `aceflow_design_api` - AI 设计

### ⭐ 通用工具（4个）
14. `aceflow_init` - 通用初始化
15. `aceflow_stage` - 通用阶段
16. `aceflow_validate` - 通用验证
17. `aceflow_template` - 模板管理

---

## 典型一天的使用

### 早上（后端开发者）
```typescript
// 1. 查看昨天进度
await aceflow_workflow_status()

// 2. 定义新功能
await aceflow_define_feature({
  feature_name: "data-export",
  api_scope_pattern: "/api/export/"
})

// 3. 生成契约
await aceflow_contract_generate({ feature: "data-export" })

// 4. 推送给团队
await aceflow_contract_push({ feature: "data-export" })
```

### 早上（前端开发者）
```typescript
// 1. 拉取最新契约
await aceflow_contract_pull({ feature: "data-export" })

// 2. 启动 Mock Server
await aceflow_mock_start({ 
  feature: "data-export",
  port: 4030
})

// 3. 开始前端开发
// ... 使用 http://localhost:4030 ...
```

### 下午（后端完成）
```typescript
// 1. 验证实现
await aceflow_validate_contract({
  feature: "data-export",
  actual_openapi_url: "http://localhost:8080/v3/api-docs"
})

// 2. 通知前端切换到真实 API
await aceflow_mock_stop({ port: 4030 })
```

---

## 快捷命令对照

| 操作 | MCP Tool | CLI 命令（如果有） |
|-----|----------|------------------|
| 初始化 | `aceflow_init_project()` | `aceflow init` |
| 定义功能 | `aceflow_define_feature()` | - |
| 生成契约 | `aceflow_contract_generate()` | `aceflow contract generate` |
| 推送契约 | `aceflow_contract_push()` | `aceflow contract push` |
| 拉取契约 | `aceflow_contract_pull()` | `aceflow contract pull` |
| 启动Mock | `aceflow_mock_start()` | `aceflow mock start` |
| 停止Mock | `aceflow_mock_stop()` | `aceflow mock stop` |
| 查看状态 | `aceflow_workflow_status()` | - |

---

**创建**: 2025-01-06
**用途**: 快速查找 MCP Tools
