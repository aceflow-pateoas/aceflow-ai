# AceFlow MCP Tools 使用指南 - AI助手专用

## 🎯 核心概念区分

### 1. 工作流模板 (Template) vs 工作流阶段 (Stage)

| 概念 | 说明 | 可选值 | 使用工具 |
|-----|------|--------|---------|
| **模板 (Template)** | 项目的整体工作流模式,决定项目复杂度 | `standard`, `complete` | `aceflow_init`, `aceflow_template` |
| **阶段 (Stage)** | 项目开发的具体步骤,按顺序执行 | `user_stories`, `task_breakdown`, `test_design`, 等 | `aceflow_stage` |

### 2. 工作流模板说明 (简化后)

| 模板 | 阶段数 | 适用场景 | 周期 |
|-----|--------|---------|------|
| **standard** | 7个阶段 | 大多数软件项目 | 5-10天 (推荐) |
| **complete** | 10个阶段 | 企业级项目、大型系统 | 2周以上 |

### 3. Standard模板的7个阶段

```
1. user_stories     → 用户故事分析
2. task_breakdown   → 任务分解
3. test_design      → 测试用例设计
4. implementation   → 功能实现
5. unit_test        → 单元测试
6. integration_test → 集成测试
7. code_review      → 代码审查
```

### 4. Complete模板的10个阶段

```
1. requirement_analysis  → 需求分析
2. architecture_design   → 架构设计
3. user_stories          → 用户故事分析
4. task_breakdown        → 任务分解
5. test_design           → 测试用例设计
6. implementation        → 功能实现
7. unit_test             → 单元测试
8. integration_test      → 集成测试
9. performance_test      → 性能测试 (可选)
10. code_review          → 代码审查
```

---

## 📋 工具使用流程

### 场景1: 启动新项目

```javascript
// 步骤1: 初始化项目 (选择模板)
{
  "tool": "aceflow_init",
  "parameters": {
    "mode": "standard",           // ✅ 这是模板名称
    "project_name": "package-manager",
    "directory": "./projects/package-manager"
  }
}

// 步骤2: 查看项目状态
{
  "tool": "aceflow_stage",
  "parameters": {
    "action": "status"
  }
}
// 返回: 当前阶段是 "user_stories" (这是阶段名称,不是模板名称)

// 步骤3: 查看所有阶段
{
  "tool": "aceflow_stage",
  "parameters": {
    "action": "list"
  }
}
```

### 场景2: 处理用户故事阶段

当AI看到当前阶段是 `user_stories` 时:

```javascript
// ❌ 错误做法: 把阶段名当作模板名
{
  "tool": "aceflow_template",
  "parameters": {
    "action": "apply",
    "template": "user_stories"  // ❌ 错误! user_stories 是阶段,不是模板
  }
}
// 结果: Error - 'user_stories' is not one of ['minimal', 'standard', 'complete', 'smart']

// ✅ 正确做法1: 直接处理用户故事内容
// AI应该:
// 1. 理解用户需求
// 2. 生成用户故事
// 3. 使用 aceflow_stage 推进到下一阶段

// ✅ 正确做法2: 如果需要查看模板信息
{
  "tool": "aceflow_template",
  "parameters": {
    "action": "list"  // 列出所有模板 (standard, complete)
  }
}

// ✅ 正确做法3: 推进到下一阶段
{
  "tool": "aceflow_stage",
  "parameters": {
    "action": "next"  // 完成 user_stories 后,推进到 task_breakdown
  }
}
```

---

## 🔧 常见错误和解决方案

### 错误1: 混淆模板和阶段

**错误代码**:
```javascript
// 当前阶段是 "user_stories"
{
  "tool": "aceflow_template",
  "parameters": {
    "action": "apply",
    "template": "user_stories"  // ❌ 错误
  }
}
```

**错误原因**: `user_stories` 是**阶段名称**,不是**模板名称**

**正确代码**:
```javascript
// 如果想查看或应用模板,应该使用:
{
  "tool": "aceflow_template",
  "parameters": {
    "action": "apply",
    "template": "standard"  // ✅ 正确,使用2种模板之一
  }
}
```

### 错误2: 在错误的时机切换模板

**场景**: 项目已经初始化为 `standard` 模板,进行到 `user_stories` 阶段,此时不应该再切换模板。

**正确做法**:
- 模板应该在项目初始化时选择 (`aceflow_init`)
- 项目进行中不应该随意切换模板
- 如果确实需要切换,应该先 `reset` 项目状态

### 错误3: 不理解工作流进度和状态

**场景**: AI收到状态返回:
```json
{
  "current_stage": {
    "name": "user_stories",
    "status": "pending",
    "progress": 0,
    "index": 1
  },
  "overall_progress": 0,
  "completed_stages": [],
  "next_stage": "task_breakdown",
  "total_stages": 8,
  "remaining_stages": 7,
  "workflow_mode": "standard"
}
```

**AI应该理解为**:
- ✅ 当前处于 `user_stories` 阶段 (第1个阶段,共8个)
- ✅ 阶段状态是 `pending` (待开始),进度 0%
- ✅ 总体进度是 0% (尚未开始第一个阶段)
- ✅ 下一个阶段是 `task_breakdown`
- ✅ 我应该帮助用户开始用户故事分析工作
- ✅ 工作开始时应该使用 `update_progress` 更新进度
- ✅ 完成后调用 `aceflow_stage` 的 `next` 操作推进

**正确的工作流程**:
```javascript
// 1. 查看初始状态
{
  "tool": "aceflow_stage",
  "parameters": {"action": "status"}
}
// 返回: current_stage="user_stories", status="pending", progress=0

// 2. 开始工作 - 更新进度到 25%
{
  "tool": "aceflow_stage",
  "parameters": {
    "action": "update_progress",
    "progress": 25
  }
}
// 返回: status="in_progress", stage_progress=25, overall_progress=3.13

// 3. 继续工作 - 更新进度到 100%
{
  "tool": "aceflow_stage",
  "parameters": {
    "action": "update_progress",
    "progress": 100
  }
}
// 返回: status="in_progress", stage_progress=100, overall_progress=12.5

// 4. 完成当前阶段 - 推进到下一阶段
{
  "tool": "aceflow_stage",
  "parameters": {"action": "next"}
}
// 返回: current_stage="task_breakdown", status="pending", progress=0
//       completed_stages=["user_stories"], overall_progress=12.5
```

**AI不应该**:
- ❌ 认为 `user_stories` 是一个模板
- ❌ 尝试调用 `aceflow_template` 的 `apply` 操作
- ❌ 跳过当前阶段直接进入下一阶段
- ❌ 在 `overall_progress=0` 时认为已经完成了 25%

**关键理解**:
- `stage_progress` = 当前阶段的进度 (0-100)
- `overall_progress` = 整个项目的进度 (0-100)
- `status` = 阶段状态 (pending/in_progress/completed)
- 初始状态: progress=0, status="pending"
- 工作开始: progress>0, status="in_progress"
- 推进后: 当前阶段变为下一阶段, status重置为"pending", progress重置为0

---

## 💡 推荐工作流程

### 完整的项目开发流程 (带进度跟踪)

```javascript
// === 阶段0: 项目初始化 ===
{
  "tool": "aceflow_init",
  "parameters": {
    "mode": "standard",  // 选择模板
    "project_name": "my-project"
  }
}

// === 阶段1: 用户故事 (user_stories) ===
// 步骤1: 开始工作
{
  "tool": "aceflow_stage",
  "parameters": {
    "action": "update_progress",
    "progress": 30
  }
}
// AI帮助: 分析需求,编写用户故事

// 步骤2: 完成大部分工作
{
  "tool": "aceflow_stage",
  "parameters": {
    "action": "update_progress",
    "progress": 80
  }
}

// 步骤3: 完成并推进
{
  "tool": "aceflow_stage",
  "parameters": {
    "action": "update_progress",
    "progress": 100
  }
}
{
  "tool": "aceflow_stage",
  "parameters": {"action": "next"}
}

// === 阶段2: 任务分解 (task_breakdown) ===
// AI帮助: 将用户故事拆分为开发任务
// (重复上述步骤: update_progress → next)

// === 阶段3: 测试设计 (test_design) ===
// AI帮助: 设计测试用例
// (重复上述步骤)

// === 阶段4: 实现 (implementation) ===
// AI帮助: 生成代码实现
// (重复上述步骤)

// === 阶段5-8: 测试、审查、演示 ===
// 依次推进...
```

### 随时检查状态

```javascript
// 查看当前状态
{
  "tool": "aceflow_stage",
  "parameters": {"action": "status"}
}

// 返回示例:
{
  "current_stage": "implementation",  // 当前阶段
  "progress": 50,                     // 总体进度 50%
  "completed_stages": [               // 已完成的阶段
    "user_stories",
    "task_breakdown",
    "test_design"
  ],
  "next_stage": "unit_test"           // 下一个阶段
}
```

---

## 📚 工具速查表

### aceflow_init - 初始化项目

```javascript
{
  "tool": "aceflow_init",
  "parameters": {
    "mode": "standard",              // 必需: standard | complete
    "project_name": "my-project",    // 可选: 项目名称
    "directory": "./path/to/project" // 可选: 项目目录
  }
}
```

### aceflow_stage - 管理阶段

```javascript
// 查看状态
{"tool": "aceflow_stage", "parameters": {"action": "status"}}

// 列出所有阶段
{"tool": "aceflow_stage", "parameters": {"action": "list"}}

// 更新当前阶段进度
{
  "tool": "aceflow_stage",
  "parameters": {
    "action": "update_progress",
    "progress": 50  // 0-100
  }
}

// 推进到下一阶段
{"tool": "aceflow_stage", "parameters": {"action": "next"}}

// 重置项目
{"tool": "aceflow_stage", "parameters": {"action": "reset"}}
```

### aceflow_template - 管理模板

```javascript
// 列出所有模板
{"tool": "aceflow_template", "parameters": {"action": "list"}}

// 应用模板 (通常在初始化时)
{
  "tool": "aceflow_template",
  "parameters": {
    "action": "apply",
    "template": "standard"  // standard | complete
  }
}

// 验证模板
{
  "tool": "aceflow_template",
  "parameters": {
    "action": "validate",
    "template": "standard"
  }
}
```

### aceflow_validate - 验证项目

```javascript
// 基础验证
{"tool": "aceflow_validate", "parameters": {"mode": "basic"}}

// 详细验证 + 报告
{
  "tool": "aceflow_validate",
  "parameters": {
    "mode": "detailed",
    "report": true
  }
}

// 验证并自动修复
{
  "tool": "aceflow_validate",
  "parameters": {
    "mode": "basic",
    "fix": true
  }
}
```

---

## 🎯 针对你的场景的正确做法

### 你的场景: Package Manager System MVP 需求拆分

```javascript
// 步骤1: 初始化项目 (如果还没初始化)
{
  "tool": "aceflow_init",
  "parameters": {
    "mode": "standard",  // ✅ 使用标准模式
    "project_name": "package-manager-mvp"
  }
}

// 步骤2: 查看当前状态
{
  "tool": "aceflow_stage",
  "parameters": {"action": "status"}
}
// 返回: current_stage = "user_stories", progress = 25%

// 步骤3: AI处理用户故事阶段
// AI应该:
// 1. 分析PRD文档
// 2. 生成用户故事 (US-001, US-002, US-003, US-004)
// 3. 定义验收标准
// 4. 评估故事点
// (这些工作不需要调用MCP工具,AI直接完成)

// 步骤4: 完成用户故事后,推进到下一阶段
{
  "tool": "aceflow_stage",
  "parameters": {"action": "next"}
}
// 现在进入 "task_breakdown" 阶段

// 步骤5: AI处理任务分解阶段
// AI应该:
// 1. 将用户故事拆分为技术任务
// 2. 定义任务依赖关系
// 3. 估算工作量
// (同样不需要调用MCP工具)

// 步骤6: 完成任务分解后,继续推进
{
  "tool": "aceflow_stage",
  "parameters": {"action": "next"}
}
// 现在进入 "test_design" 阶段

// ...依次推进...
```

---

## 🚨 重要提醒

1. **模板和阶段是完全不同的概念**
   - 模板 = 工作流整体模式 (standard, complete)
   - 阶段 = 工作流具体步骤 (user_stories, task_breakdown, etc.)

2. **不要混用参数**
   - `aceflow_template` 的 `template` 参数只接受 2 种模板
   - `aceflow_stage` 返回的 `current_stage` 是阶段名,不是模板名

3. **正常的工作流程**
   - 初始化时选择模板 → 按阶段依次推进 → 不需要频繁切换模板

4. **AI的核心职责**
   - 在每个阶段帮助用户完成对应的工作内容
   - 完成后调用 `aceflow_stage` 的 `next` 操作推进
   - 不是调用 `aceflow_template` 应用阶段名

---

## 📖 参考

- 完整API文档: `docs/WORKFLOW_API_REFERENCE.md`
- 快速开始: `docs/WORKFLOW_QUICK_START.md`
- MCP工具目录: `docs/MCP_TOOLS_COMPLETE_CATALOG.md`
