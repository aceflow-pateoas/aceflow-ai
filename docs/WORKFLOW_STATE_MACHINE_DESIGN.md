# Workflow State Machine Design

> Contract-First 工作流状态机设计文档

**版本**: v1.0.0
**日期**: 2025-01-04
**状态**: Phase 2 Implementation

---

## 📋 目录

1. [状态机概览](#状态机概览)
2. [状态定义](#状态定义)
3. [状态转换规则](#状态转换规则)
4. [检查点和验证](#检查点和验证)
5. [自动化建议](#自动化建议)
6. [状态文件格式](#状态文件格式)

---

## 🎯 状态机概览

### Contract-First 工作流阶段

```
┌─────────────┐
│   Setup     │ 初始化项目和配置
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Define    │ 定义功能需求和 API 边界
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Design    │ 设计 OpenAPI 契约
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Implement  │ 后端实现 API
└──────┬──────┘
       │
       ├──────────────────────────┐
       │                          │
       ▼                          ▼
┌─────────────┐          ┌─────────────┐
│  Contract   │          │   Frontend  │
│   Push      │          │   Develop   │
└──────┬──────┘          └──────┬──────┘
       │                        │
       │      (Mock Server)     │
       │◄───────────────────────┘
       │
       ▼
┌─────────────┐
│  Validate   │ 验证契约一致性
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Integration │ 前后端集成测试
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Review    │ 代码审查和发布
└─────────────┘
```

---

## 📊 状态定义

### 状态枚举

```python
class WorkflowStage(Enum):
    """Contract-First 工作流阶段"""

    # Phase 1: 项目初始化
    SETUP = "setup"

    # Phase 2: 功能定义
    DEFINE = "define"

    # Phase 3: API 设计
    DESIGN = "design"

    # Phase 4: 后端实现
    IMPLEMENT = "implement"

    # Phase 5: 契约推送
    CONTRACT_PUSH = "contract_push"

    # Phase 6: 前端开发 (并行)
    FRONTEND_DEV = "frontend_dev"

    # Phase 7: 契约验证
    VALIDATE = "validate"

    # Phase 8: 集成测试
    INTEGRATION = "integration"

    # Phase 9: 审查发布
    REVIEW = "review"

    # 完成状态
    COMPLETED = "completed"
```

### 状态详情

#### 1. Setup (初始化)

**目标**: 建立项目基础设施和配置

**必需操作**:
- ✅ 执行 `aceflow_init_project`
- ✅ 配置 OpenAPI URL
- ✅ 配置 Git 契约仓库
- ✅ 配置团队通知

**输出**:
- `.aceflow/config.yaml`
- `.aceflow/workflow.json`
- 项目配置完成

**验证条件**:
```python
{
    "config_exists": True,
    "openapi_url_configured": True,
    "repo_url_configured": True
}
```

**下一步建议**:
> "项目初始化完成！下一步：定义您的第一个功能模块"
> 使用工具: `aceflow_define_feature`

---

#### 2. Define (功能定义)

**目标**: 定义功能需求和 API 边界

**必需操作**:
- ✅ 执行 `aceflow_define_feature`
- ✅ 定义 API 范围 (prefix/exact/regex)
- ✅ 列出功能需求
- ✅ 指定开发团队

**输出**:
- `.aceflow/requirements/{feature}.md`
- Feature 配置添加到 `config.yaml`

**验证条件**:
```python
{
    "feature_defined": True,
    "api_scope_valid": True,
    "requirements_documented": True
}
```

**下一步建议**:
> "功能需求已定义！下一步：设计 API 契约"
> 选择方式:
> - AI 从零设计: `aceflow_design_api`
> - 从 Spring Boot 生成: `aceflow_contract_generate` (需先实现后端)

---

#### 3. Design (API 设计)

**目标**: 设计 OpenAPI 契约规范

**必需操作 (二选一)**:
- **方式 A**: 执行 `aceflow_design_api` (AI 辅助从零设计)
- **方式 B**: 执行 `aceflow_contract_generate` (从已有后端生成)

**输出**:
- `.aceflow/contracts/{feature}.json` (或 .yaml)
- OpenAPI 3.0 规范文件

**验证条件**:
```python
{
    "contract_file_exists": True,
    "valid_openapi_spec": True,
    "endpoints_count": lambda x: x > 0,
    "smart_completion_applied": True  # 可选
}
```

**下一步建议**:
> "API 契约已设计！下一步：推送契约并通知团队"
> 使用工具: `aceflow_contract_push`

---

#### 4. Implement (后端实现)

**目标**: 实现 API 后端代码

**必需操作**:
- ✅ 编写 Spring Boot Controller/Service
- ✅ 添加 OpenAPI 注解 (@Operation, @ApiResponse)
- ✅ 实现业务逻辑
- ✅ 编写单元测试

**输出**:
- Spring Boot 代码文件
- 单元测试文件
- OpenAPI 文档可访问

**验证条件**:
```python
{
    "openapi_endpoint_accessible": True,  # http://localhost:8080/v3/api-docs
    "tests_passing": True,
    "code_quality_ok": True
}
```

**下一步建议**:
> "后端实现完成！下一步：推送契约到 Git"
> 使用工具: `aceflow_contract_push`

**并行提示**:
> "前端团队可以开始使用 Mock Server 进行开发"

---

#### 5. Contract Push (契约推送)

**目标**: 推送契约到 Git 并通知团队

**必需操作**:
- ✅ 执行 `aceflow_contract_push`
- ✅ Git commit 和 push
- ✅ 发送邮件通知

**输出**:
- 契约文件推送到 Git 仓库
- 团队邮件通知发送
- Commit hash 记录

**验证条件**:
```python
{
    "pushed_to_git": True,
    "commit_hash": lambda x: len(x) == 7,
    "team_notified": True
}
```

**下一步建议**:
> "契约已推送！"
> - 后端: 继续开发或验证契约一致性
> - 前端: 拉取契约并启动 Mock Server

---

#### 6. Frontend Dev (前端开发 - 并行)

**目标**: 前端基于 Mock Server 开发

**必需操作**:
- ✅ 执行 `aceflow_contract_pull`
- ✅ 执行 `aceflow_mock_start`
- ✅ 前端开发和测试

**输出**:
- 前端代码文件
- Mock Server 运行中
- 前端功能完成

**验证条件**:
```python
{
    "contract_pulled": True,
    "mock_server_running": True,
    "frontend_tests_passing": True
}
```

**下一步建议**:
> "前端开发完成！等待后端实现完成后进行集成测试"

---

#### 7. Validate (契约验证)

**目标**: 验证后端实现与契约一致性

**必需操作**:
- ✅ 执行 `aceflow_validate_contract`
- ✅ 检查所有端点实现
- ✅ 验证请求/响应格式

**输出**:
- 验证报告
- 差异列表 (如有)

**验证条件**:
```python
{
    "contract_compliant": True,
    "missing_endpoints": lambda x: len(x) == 0,
    "extra_endpoints": lambda x: len(x) == 0,
    "differences": lambda x: len(x) == 0
}
```

**下一步建议**:
- 如果验证通过: "契约验证通过！可以进行集成测试"
- 如果验证失败: "发现契约不一致，请先修复问题"

---

#### 8. Integration (集成测试)

**目标**: 前后端集成测试

**必需操作**:
- ✅ 停止 Mock Server (`aceflow_mock_stop`)
- ✅ 前端切换到真实后端
- ✅ 执行端到端测试
- ✅ 验证所有用户场景

**输出**:
- 集成测试报告
- 性能测试结果
- Bug 修复记录

**验证条件**:
```python
{
    "e2e_tests_passing": True,
    "performance_acceptable": True,
    "critical_bugs": lambda x: x == 0
}
```

**下一步建议**:
> "集成测试完成！下一步：代码审查和发布准备"

---

#### 9. Review (审查发布)

**目标**: 代码审查和发布

**必需操作**:
- ✅ 代码审查 (Code Review)
- ✅ 安全检查
- ✅ 文档更新
- ✅ 发布准备

**输出**:
- 审查报告
- 变更日志
- 发布文档

**验证条件**:
```python
{
    "code_reviewed": True,
    "security_checked": True,
    "docs_updated": True,
    "ready_for_release": True
}
```

**下一步建议**:
> "审查完成！项目已就绪，可以发布"

---

#### 10. Completed (完成)

**目标**: 项目完成

**状态**:
- 所有阶段完成
- 功能已发布
- 项目归档

---

## 🔄 状态转换规则

### 转换矩阵

| 当前状态 | 可转换到 | 条件 | 工具 |
|---------|---------|------|------|
| SETUP | DEFINE | 配置完成 | aceflow_define_feature |
| DEFINE | DESIGN | 功能已定义 | aceflow_design_api 或 aceflow_contract_generate |
| DESIGN | IMPLEMENT | 契约已设计 | (人工编码) |
| DESIGN | CONTRACT_PUSH | 契约已设计 | aceflow_contract_push |
| IMPLEMENT | CONTRACT_PUSH | 后端实现完成 | aceflow_contract_push |
| CONTRACT_PUSH | FRONTEND_DEV | 契约已推送 | aceflow_contract_pull + aceflow_mock_start |
| CONTRACT_PUSH | VALIDATE | 后端已实现 | aceflow_validate_contract |
| FRONTEND_DEV | INTEGRATION | 前端开发完成 + 后端验证通过 | aceflow_mock_stop |
| VALIDATE | INTEGRATION | 契约验证通过 | (运行集成测试) |
| INTEGRATION | REVIEW | 集成测试通过 | (代码审查) |
| REVIEW | COMPLETED | 审查通过 | (发布) |

### 并行状态

某些阶段可以并行执行:

```
CONTRACT_PUSH
    ├── IMPLEMENT (后端继续开发)
    └── FRONTEND_DEV (前端基于 Mock 开发)
```

### 回退规则

如果验证失败，可以回退到前一阶段:

```python
{
    "VALIDATE": "IMPLEMENT",  # 验证失败 → 修复实现
    "INTEGRATION": "IMPLEMENT",  # 集成失败 → 修复实现
    "REVIEW": "INTEGRATION"  # 审查失败 → 重新测试
}
```

---

## ✅ 检查点和验证

### 阶段完成检查点

每个阶段都有完成检查点 (Quality Gate):

```python
QUALITY_GATES = {
    "setup": {
        "required": [
            "config_file_exists",
            "openapi_url_valid",
            "repo_url_valid"
        ],
        "optional": [
            "smtp_configured"
        ]
    },
    "define": {
        "required": [
            "feature_config_exists",
            "api_scope_defined",
            "requirements_documented"
        ]
    },
    "design": {
        "required": [
            "contract_file_exists",
            "valid_openapi_spec",
            "has_endpoints"
        ],
        "optional": [
            "smart_completion_applied",
            "examples_provided"
        ]
    },
    "contract_push": {
        "required": [
            "git_commit_successful",
            "git_push_successful"
        ],
        "optional": [
            "team_notified"
        ]
    },
    "validate": {
        "required": [
            "contract_compliant",
            "no_missing_endpoints",
            "no_extra_endpoints"
        ]
    },
    "integration": {
        "required": [
            "e2e_tests_passing",
            "no_critical_bugs"
        ],
        "optional": [
            "performance_acceptable"
        ]
    }
}
```

### 自动验证

系统自动验证每个检查点:

```python
def validate_stage(stage: WorkflowStage, context: Dict) -> ValidationResult:
    """验证阶段完成条件"""
    gates = QUALITY_GATES.get(stage.value, {})

    results = {
        "stage": stage.value,
        "required_passed": [],
        "required_failed": [],
        "optional_passed": [],
        "optional_failed": [],
        "can_proceed": False
    }

    # 检查必需条件
    for check in gates.get("required", []):
        if validate_check(check, context):
            results["required_passed"].append(check)
        else:
            results["required_failed"].append(check)

    # 检查可选条件
    for check in gates.get("optional", []):
        if validate_check(check, context):
            results["optional_passed"].append(check)
        else:
            results["optional_failed"].append(check)

    # 判断是否可以继续
    results["can_proceed"] = len(results["required_failed"]) == 0

    return results
```

---

## 💡 自动化建议

### 建议引擎

根据当前状态和上下文，提供智能建议:

```python
def get_recommendations(workflow_state: WorkflowState) -> List[Recommendation]:
    """获取下一步建议"""

    current_stage = workflow_state.current_stage
    context = workflow_state.context

    recommendations = []

    if current_stage == WorkflowStage.SETUP:
        if not context.get("features_defined"):
            recommendations.append({
                "priority": "high",
                "action": "Define your first feature",
                "tool": "aceflow_define_feature",
                "params": {
                    "feature_name": "example-feature",
                    "description": "Feature description",
                    "api_scope": {"type": "prefix", "pattern": "/api/"}
                }
            })

    elif current_stage == WorkflowStage.DEFINE:
        recommendations.append({
            "priority": "high",
            "action": "Design API contract",
            "tool": "aceflow_design_api",
            "alternatives": [
                {
                    "description": "Design from scratch (recommended for new features)",
                    "tool": "aceflow_design_api"
                },
                {
                    "description": "Generate from existing backend",
                    "tool": "aceflow_contract_generate",
                    "requires": "Backend already implemented with OpenAPI annotations"
                }
            ]
        })

    elif current_stage == WorkflowStage.DESIGN:
        recommendations.append({
            "priority": "high",
            "action": "Push contract to Git",
            "tool": "aceflow_contract_push",
            "benefits": [
                "Notify frontend team",
                "Start parallel development",
                "Version control for contracts"
            ]
        })

    elif current_stage == WorkflowStage.CONTRACT_PUSH:
        # 后端建议
        recommendations.append({
            "priority": "high",
            "audience": "backend",
            "action": "Implement backend APIs",
            "steps": [
                "Write Spring Boot controllers",
                "Add OpenAPI annotations",
                "Implement business logic",
                "Write unit tests"
            ]
        })

        # 前端建议
        recommendations.append({
            "priority": "high",
            "audience": "frontend",
            "action": "Start frontend development with Mock Server",
            "tools": ["aceflow_contract_pull", "aceflow_mock_start"],
            "benefits": [
                "Develop without waiting for backend",
                "Test against realistic API responses",
                "Catch integration issues early"
            ]
        })

    elif current_stage == WorkflowStage.VALIDATE:
        validation_result = context.get("validation_result", {})

        if validation_result.get("compliant"):
            recommendations.append({
                "priority": "high",
                "action": "Proceed to integration testing",
                "message": "Contract validation passed! Ready for integration."
            })
        else:
            recommendations.append({
                "priority": "critical",
                "action": "Fix contract violations",
                "issues": validation_result.get("differences", []),
                "missing": validation_result.get("missing_endpoints", []),
                "extra": validation_result.get("extra_endpoints", [])
            })

    return recommendations
```

### 上下文感知建议

建议会根据项目状态动态调整:

```python
# 检测到契约更新
if context.get("contract_updated"):
    recommendations.append({
        "priority": "medium",
        "action": "Notify affected teams",
        "tool": "aceflow_contract_push",
        "message": "Contract has been updated. Push to notify teams."
    })

# 检测到 Mock Server 运行时间过长
if context.get("mock_server_running_hours", 0) > 24:
    recommendations.append({
        "priority": "low",
        "action": "Consider switching to real backend",
        "message": "Mock Server has been running for 24+ hours. Backend might be ready."
    })

# 检测到测试失败
if context.get("tests_failing"):
    recommendations.append({
        "priority": "critical",
        "action": "Fix failing tests before proceeding",
        "failures": context.get("test_failures", [])
    })
```

---

## 📁 状态文件格式

### `.aceflow/workflow.json`

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
        "repo_url_valid": true,
        "smtp_configured": true
      },
      "outputs": [
        ".aceflow/config.yaml"
      ]
    },

    "define": {
      "status": "completed",
      "started_at": "2025-01-04T10:15:00Z",
      "completed_at": "2025-01-04T11:00:00Z",
      "duration_minutes": 45,
      "features_defined": ["user-auth", "payment"],
      "checkpoints": {
        "feature_config_exists": true,
        "api_scope_defined": true,
        "requirements_documented": true
      },
      "outputs": [
        ".aceflow/requirements/user-auth.md",
        ".aceflow/requirements/payment.md"
      ]
    },

    "design": {
      "status": "in_progress",
      "started_at": "2025-01-04T11:00:00Z",
      "current_feature": "user-auth",
      "design_method": "ai_assisted",
      "endpoints_count": 5,
      "checkpoints": {
        "contract_file_exists": true,
        "valid_openapi_spec": true,
        "has_endpoints": true,
        "smart_completion_applied": true
      },
      "outputs": [
        ".aceflow/contracts/user-auth.json"
      ]
    },

    "implement": {
      "status": "pending"
    },

    "contract_push": {
      "status": "pending"
    },

    "frontend_dev": {
      "status": "pending"
    },

    "validate": {
      "status": "pending"
    },

    "integration": {
      "status": "pending"
    },

    "review": {
      "status": "pending"
    }
  },

  "features": {
    "user-auth": {
      "status": "design",
      "created_at": "2025-01-04T10:30:00Z",
      "contract_file": ".aceflow/contracts/user-auth.json",
      "git_commits": [],
      "mock_server": {
        "running": false,
        "port": null,
        "pid": null
      },
      "validation": {
        "last_validated": null,
        "compliant": null
      }
    },

    "payment": {
      "status": "define",
      "created_at": "2025-01-04T10:45:00Z"
    }
  },

  "metrics": {
    "total_features": 2,
    "completed_features": 0,
    "in_progress_features": 1,
    "total_contracts": 1,
    "total_apis": 5,
    "mock_servers_running": 0
  },

  "context": {
    "project_name": "E-Commerce API",
    "openapi_url": "http://localhost:8080/v3/api-docs",
    "repo_url": "git@github.com:company/contracts.git",
    "team_size": 8,
    "last_recommendation": {
      "action": "Push contract to Git",
      "tool": "aceflow_contract_push",
      "timestamp": "2025-01-04T15:30:00Z"
    }
  }
}
```

### 状态值

```python
class StageStatus(Enum):
    """阶段状态"""
    PENDING = "pending"       # 未开始
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"   # 已完成
    BLOCKED = "blocked"       # 被阻塞
    FAILED = "failed"         # 失败
    SKIPPED = "skipped"       # 跳过
```

---

## 🎯 实现优先级

### Phase 2 实施顺序

1. **基础结构** ✅
   - 定义状态枚举
   - 设计状态文件格式
   - 创建 WorkflowState 类

2. **状态管理** ⏳
   - 实现状态读取/写入
   - 实现状态转换逻辑
   - 添加验证功能

3. **检查点系统** ⏳
   - 实现 Quality Gates
   - 自动验证机制
   - 阻塞条件检查

4. **建议引擎** ⏳
   - 基础建议生成
   - 上下文感知
   - 动态调整

5. **MCP 集成** ⏳
   - 创建状态管理 MCP Tools
   - 集成到现有工作流
   - 测试和文档

---

## 📚 参考资料

- [AI Workflow Integration](AI_WORKFLOW_INTEGRATION.md)
- [MCP Contract Tools Guide](MCP_CONTRACT_TOOLS_GUIDE.md)
- [MVP Development Plan](MVP_DEVELOPMENT_PLAN.md)

---

**Created by**: AceFlow Team
**Last Updated**: 2025-01-04
**Status**: Phase 2 Design
