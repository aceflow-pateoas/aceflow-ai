# Workflow State Management - 使用指南

> AI 驱动的 Contract-First 工作流状态跟踪和管理

**版本**: v1.0.0
**日期**: 2025-01-04
**Phase**: Phase 2 Complete

---

## 📋 目录

1. [概述](#概述)
2. [MCP Tools 列表](#mcp-tools-列表)
3. [快速开始](#快速开始)
4. [完整示例](#完整示例)
5. [状态文件说明](#状态文件说明)
6. [最佳实践](#最佳实践)

---

## 🎯 概述

Workflow State Management 提供了完整的工作流状态跟踪和管理功能，让 AI 能够：

- ✅ 自动跟踪项目进度
- ✅ 验证阶段完成条件
- ✅ 提供智能化建议
- ✅ 管理多个功能的并行开发
- ✅ 持久化工作流状态

### 核心功能

| 功能 | 说明 |
|------|------|
| **状态跟踪** | 自动跟踪当前阶段和进度 |
| **质量门控** | 验证阶段完成条件 |
| **智能建议** | 基于上下文提供下一步建议 |
| **检查点系统** | 细粒度的进度跟踪 |
| **功能级管理** | 支持多功能并行开发 |

---

## 🔧 MCP Tools 列表

### 1. aceflow_workflow_status

**功能**: 获取当前工作流状态和进度

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "current_stage": "design",
  "workflow_mode": "contract_first",
  "overall_progress": 30,
  "completed_stages": 3,
  "total_stages": 10,
  "features": {...},
  "metrics": {...},
  "recommendations": [...]
}
```

**使用场景**:
- 查看当前项目进度
- 了解当前所处阶段
- 获取下一步建议

**示例**:
```python
# AI 调用
status = aceflow_workflow_status()

print(f"当前阶段: {status['current_stage']}")
print(f"整体进度: {status['overall_progress']}%")
print(f"建议: {status['recommendations']}")
```

---

### 2. aceflow_workflow_advance

**功能**: 推进工作流到下一阶段

**参数**:
- `next_stage` (required): 目标阶段名称
  - setup / define / design / implement / contract_push /
    frontend_dev / validate / integration / review / completed
- `feature_name` (optional): 功能名称（用于功能级跟踪）

**返回值**:
```json
{
  "success": true,
  "previous_stage": "design",
  "current_stage": "implement",
  "message": "Advanced from design to implement"
}
```

**使用场景**:
- 完成当前阶段后推进到下一阶段
- 开始新的开发阶段

**示例**:
```python
# 完成设计阶段，推进到实现阶段
result = aceflow_workflow_advance(
    next_stage="implement",
    feature_name="user-authentication"
)

if result["success"]:
    print(f"已推进到 {result['current_stage']} 阶段")
```

---

### 3. aceflow_workflow_checkpoint

**功能**: 更新阶段检查点状态

**参数**:
- `stage` (required): 阶段名称
- `checkpoint` (required): 检查点名称
- `value` (required): 检查点值 (True/False)

**检查点列表**:

#### Setup 阶段:
- `config_file_exists` - 配置文件已创建
- `openapi_url_valid` - OpenAPI URL 有效
- `repo_url_valid` - Git 仓库 URL 有效
- `smtp_configured` - SMTP 已配置（可选）

#### Define 阶段:
- `feature_config_exists` - 功能配置已创建
- `api_scope_defined` - API 范围已定义
- `requirements_documented` - 需求已文档化

#### Design 阶段:
- `contract_file_exists` - 契约文件已创建
- `valid_openapi_spec` - 有效的 OpenAPI 规范
- `has_endpoints` - 包含端点定义
- `smart_completion_applied` - 智能补全已应用（可选）

#### Contract Push 阶段:
- `git_commit_successful` - Git commit 成功
- `git_push_successful` - Git push 成功
- `team_notified` - 团队已通知（可选）

#### Validate 阶段:
- `contract_compliant` - 契约一致
- `no_missing_endpoints` - 无缺失端点
- `no_extra_endpoints` - 无额外端点

#### Integration 阶段:
- `e2e_tests_passing` - E2E 测试通过
- `no_critical_bugs` - 无严重bug
- `performance_acceptable` - 性能可接受（可选）

**返回值**:
```json
{
  "success": true,
  "stage": "design",
  "checkpoint": "contract_file_exists",
  "value": true
}
```

**使用场景**:
- 标记阶段完成条件
- 跟踪细粒度进度

**示例**:
```python
# 标记契约文件已创建
result = aceflow_workflow_checkpoint(
    stage="design",
    checkpoint="contract_file_exists",
    value=True
)
```

---

### 4. aceflow_workflow_recommendations

**功能**: 获取智能化的下一步建议

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "count": 2,
  "recommendations": [
    {
      "priority": "high",
      "action": "Push contract to Git",
      "tool": "aceflow_contract_push",
      "benefits": [
        "Notify frontend team",
        "Enable parallel development"
      ]
    },
    {
      "priority": "medium",
      "audience": "frontend",
      "action": "Pull contract and start Mock Server"
    }
  ]
}
```

**使用场景**:
- 不确定下一步做什么时
- 需要AI指导时
- 查看可选操作时

**示例**:
```python
# 获取建议
result = aceflow_workflow_recommendations()

for rec in result["recommendations"]:
    print(f"{rec['priority']}: {rec['action']}")
    if "tool" in rec:
        print(f"  使用工具: {rec['tool']}")
```

---

## 🚀 快速开始

### Step 1: 初始化项目（自动初始化工作流）

```python
result = aceflow_init_project(
    project_name="My API",
    workflow_mode="contract_first",
    openapi_url="http://localhost:8080/v3/api-docs",
    repo_url="git@github.com:org/contracts.git"
)

# 工作流自动初始化
print(result["workflow_initialized"])  # True
print(result["current_stage"])  # "setup"
print(result["workflow_file"])  # ".aceflow/workflow.json"
```

### Step 2: 查看当前状态

```python
status = aceflow_workflow_status()

print(f"当前阶段: {status['current_stage']}")
print(f"进度: {status['overall_progress']}%")

# 查看建议
for rec in status["recommendations"]:
    print(f"建议: {rec['action']}")
```

### Step 3: 定义功能并更新状态

```python
# 定义功能
feature_result = aceflow_define_feature(
    feature_name="user-auth",
    description="User authentication",
    api_scope={"type": "prefix", "pattern": "/api/auth/"},
    requirements=["Login", "Register"]
)

# 推进到下一阶段
advance_result = aceflow_workflow_advance(
    next_stage="design",
    feature_name="user-auth"
)
```

### Step 4: 追踪进度

```python
# 更新检查点
aceflow_workflow_checkpoint(
    stage="design",
    checkpoint="contract_file_exists",
    value=True
)

# 查看更新后的进度
status = aceflow_workflow_status()
print(f"新进度: {status['overall_progress']}%")
```

---

## 📖 完整示例

### 场景: 完整的 Contract-First 工作流

```python
# ==================== Phase 1: Setup ====================
print("Phase 1: 项目初始化")

result = aceflow_init_project(
    project_name="E-Commerce API",
    workflow_mode="contract_first",
    openapi_url="http://localhost:8080/v3/api-docs",
    repo_url="git@github.com:company/contracts.git"
)

print(f"✅ 项目已初始化，当前阶段: {result['current_stage']}")

# ==================== Phase 2: Define ====================
print("\nPhase 2: 功能定义")

# 推进到 define 阶段
aceflow_workflow_advance(next_stage="define")

# 定义功能
aceflow_define_feature(
    feature_name="payment-processing",
    description="Payment processing system",
    api_scope={"type": "prefix", "pattern": "/api/payment/"},
    requirements=[
        "支持支付宝",
        "支持微信支付",
        "支持退款"
    ]
)

# 标记检查点
aceflow_workflow_checkpoint("define", "feature_config_exists", True)
aceflow_workflow_checkpoint("define", "api_scope_defined", True)
aceflow_workflow_checkpoint("define", "requirements_documented", True)

print("✅ 功能定义完成")

# ==================== Phase 3: Design ====================
print("\nPhase 3: API 设计")

# 推进到 design 阶段
aceflow_workflow_advance(
    next_stage="design",
    feature_name="payment-processing"
)

# 设计 API
aceflow_design_api(
    feature="payment-processing",
    endpoints=[
        {
            "path": "/api/payment/create",
            "method": "POST",
            "request_body": {"amount": "number", "method": "string"},
            "responses": {"200": {"payment_id": "string"}}
        }
    ]
)

# 标记检查点
aceflow_workflow_checkpoint("design", "contract_file_exists", True)
aceflow_workflow_checkpoint("design", "valid_openapi_spec", True)
aceflow_workflow_checkpoint("design", "has_endpoints", True)

print("✅ API 设计完成")

# ==================== Phase 4: Contract Push ====================
print("\nPhase 4: 推送契约")

# 推进到 contract_push 阶段
aceflow_workflow_advance(next_stage="contract_push")

# 推送契约
aceflow_contract_push(
    feature="payment-processing",
    message="feat: add payment processing API"
)

# 标记检查点
aceflow_workflow_checkpoint("contract_push", "git_commit_successful", True)
aceflow_workflow_checkpoint("contract_push", "git_push_successful", True)
aceflow_workflow_checkpoint("contract_push", "team_notified", True)

print("✅ 契约已推送")

# ==================== 查看最终状态 ====================
print("\n最终状态:")

status = aceflow_workflow_status()
print(f"当前阶段: {status['current_stage']}")
print(f"整体进度: {status['overall_progress']}%")
print(f"完成阶段: {status['completed_stages']}/{status['total_stages']}")

# 查看建议
print("\n下一步建议:")
recommendations = aceflow_workflow_recommendations()
for rec in recommendations["recommendations"]:
    print(f"- [{rec['priority']}] {rec['action']}")
```

---

## 📁 状态文件说明

### .aceflow/workflow.json

工作流状态文件自动创建和更新，包含：

```json
{
  "version": "1.0.0",
  "workflow_mode": "contract_first",
  "current_stage": "design",
  "created_at": "2025-01-04T10:00:00Z",
  "updated_at": "2025-01-04T15:30:00Z",

  "stages": {
    "setup": {
      "status": "completed",
      "started_at": "2025-01-04T10:00:00Z",
      "completed_at": "2025-01-04T10:15:00Z",
      "duration_minutes": 15,
      "checkpoints": {
        "config_file_exists": true,
        "openapi_url_valid": true,
        "repo_url_valid": true
      }
    },
    "define": {
      "status": "completed",
      ...
    },
    "design": {
      "status": "in_progress",
      ...
    }
  },

  "features": {
    "user-auth": {
      "status": "design",
      "created_at": "...",
      ...
    }
  },

  "metrics": {
    "total_features": 1,
    "completed_features": 0,
    "in_progress_features": 1
  },

  "context": {
    "project_name": "My API",
    "openapi_url": "...",
    "repo_url": "..."
  }
}
```

### 自动更新时机

状态文件在以下情况自动更新：

1. ✅ `aceflow_init_project` - 初始化工作流
2. ✅ `aceflow_workflow_advance` - 推进阶段
3. ✅ `aceflow_workflow_checkpoint` - 更新检查点
4. ✅ `aceflow_define_feature` - 添加功能
5. ✅ 其他契约管理操作

---

## 💡 最佳实践

### 1. 始终先检查状态

```python
# 开始任何操作前
status = aceflow_workflow_status()

if not status["success"]:
    print("工作流未初始化，请先运行 aceflow_init_project")
else:
    print(f"当前在 {status['current_stage']} 阶段")
```

### 2. 使用建议系统

```python
# 不确定下一步做什么时
recommendations = aceflow_workflow_recommendations()

for rec in recommendations["recommendations"]:
    if rec["priority"] == "high":
        print(f"高优先级: {rec['action']}")
        if "tool" in rec:
            # 执行建议的工具
            pass
```

### 3. 验证阶段完成条件

```python
# 推进阶段前，确保检查点都已标记
aceflow_workflow_checkpoint("design", "contract_file_exists", True)
aceflow_workflow_checkpoint("design", "valid_openapi_spec", True)
aceflow_workflow_checkpoint("design", "has_endpoints", True)

# 然后推进
result = aceflow_workflow_advance(next_stage="implement")

if not result["success"]:
    print(f"无法推进: {result['error']}")
    # 检查缺失的检查点
```

### 4. 功能级跟踪

```python
# 为每个功能指定名称
aceflow_workflow_advance(
    next_stage="design",
    feature_name="user-auth"  # 指定功能名称
)

# 查看功能状态
status = aceflow_workflow_status()
print(status["features"]["user-auth"])
```

### 5. 监控多功能并行开发

```python
status = aceflow_workflow_status()

for feature_name, feature_data in status["features"].items():
    print(f"{feature_name}: {feature_data['status']}")

print(f"总功能: {status['metrics']['total_features']}")
print(f"进行中: {status['metrics']['in_progress_features']}")
```

---

## 🔗 相关文档

- [Workflow State Machine Design](WORKFLOW_STATE_MACHINE_DESIGN.md) - 状态机设计文档
- [MCP Contract Tools Guide](MCP_CONTRACT_TOOLS_GUIDE.md) - 契约管理工具指南
- [AI Workflow Integration](AI_WORKFLOW_INTEGRATION.md) - AI 工作流集成设计

---

**Created by**: AceFlow Team
**Last Updated**: 2025-01-04
**Status**: Phase 2 Complete
