# AceFlow AI 工作流整合方案

> 将 MCP Tools 与契约管理功能整合成完整的 AI 驱动开发工作流

## 📋 目录

1. [整合架构](#整合架构)
2. [工作流阶段设计](#工作流阶段设计)
3. [MCP Tools 扩展](#mcp-tools-扩展)
4. [AI 指导策略](#ai-指导策略)
5. [实施计划](#实施计划)

---

## 🏗️ 整合架构

### 当前状态

```
现有功能模块:
├── MCP Tools (AI 接口)
│   ├── aceflow_init        # 项目初始化
│   ├── aceflow_stage       # 阶段管理
│   ├── aceflow_validate    # 验证
│   └── aceflow_template    # 模板管理
│
└── CLI Tools (人工命令行)
    ├── aceflow init        # 配置初始化
    ├── aceflow feature     # Feature 管理
    ├── aceflow contract    # 契约管理
    └── aceflow mock        # Mock Server
```

### 目标架构

```
┌─────────────────────────────────────────────────────────┐
│                    AI Client (Claude/Cursor)            │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│              AceFlow MCP Server (统一入口)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔧 Workflow Tools (工作流驱动)                         │
│  ├── aceflow_init_project     # 项目初始化              │
│  ├── aceflow_define_feature   # 定义功能需求            │
│  ├── aceflow_design_api       # 设计 API契约            │
│  ├── aceflow_generate_code    # 生成代码                │
│  ├── aceflow_setup_mock       # 启动 Mock Server        │
│  ├── aceflow_validate_impl    # 验证实现                │
│  └── aceflow_review_complete  # 完成审查                │
│                                                         │
│  📄 Contract Tools (契约管理)                           │
│  ├── aceflow_contract_generate                          │
│  ├── aceflow_contract_push                              │
│  ├── aceflow_contract_pull                              │
│  └── aceflow_contract_validate                          │
│                                                         │
│  🎭 Development Tools (开发辅助)                        │
│  ├── aceflow_mock_start                                 │
│  ├── aceflow_mock_stop                                  │
│  └── aceflow_mock_test                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│              Backend Services (底层服务)                 │
├─────────────────────────────────────────────────────────┤
│  • CLI Tools         (契约管理 CLI)                     │
│  • Git Operations    (版本控制)                         │
│  • Prism Mock Server (API模拟)                          │
│  • Email Notifier    (邮件通知)                         │
│  • File System       (配置存储)                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 工作流阶段设计

### 完整开发流程 (Contract-First + AI-Driven)

#### Phase 1: 项目初始化 (Setup)

**目标**: 建立项目基础设施和配置

**AI Actions**:
```python
# 1. 初始化项目
aceflow_init_project(
    project_name="User Service",
    workflow_mode="contract_first",  # 新模式
    openapi_url="http://localhost:8080/v3/api-docs",
    repo_url="git@github.com:org/contracts.git"
)

# 2. 配置团队信息
aceflow_config_team(
    backend_team=["backend@example.com"],
    frontend_team=["frontend@example.com"],
    notification_enabled=True
)
```

**输出**:
- ✅ `.aceflow/config.yaml` 创建
- ✅ Git 仓库初始化
- ✅ 团队通知配置

---

#### Phase 2: 功能定义 (Feature Definition)

**目标**: 定义功能需求和 API 边界

**AI Actions**:
```python
# 1. 创建功能定义
aceflow_define_feature(
    feature_name="user-authentication",
    description="用户登录、注册、登出功能",
    api_scope={
        "type": "prefix",
        "pattern": "/api/auth/"
    },
    requirements=[
        "支持邮箱密码登录",
        "支持 JWT Token",
        "支持记住我功能"
    ]
)
```

**输出**:
- ✅ Feature 配置添加到 `.aceflow/config.yaml`
- ✅ 需求文档生成
- ✅ API 范围定义

---

#### Phase 3: API 契约设计 (Contract Design)

**目标**: 设计 OpenAPI 契约规范

**AI Workflow**:

```python
# 1. 设计 API 端点
aceflow_design_api(
    feature="user-authentication",
    endpoints=[
        {
            "path": "/api/auth/login",
            "method": "POST",
            "request_body": {
                "email": "string",
                "password": "string",
                "remember_me": "boolean"
            },
            "responses": {
                "200": {"token": "string", "user": "object"},
                "401": {"error": "string"}
            }
        },
        {
            "path": "/api/auth/register",
            "method": "POST",
            # ... 更多定义
        }
    ]
)

# 2. 生成并验证契约
aceflow_contract_generate(
    feature="user-authentication",
    apply_smart_completion=True
)

# 3. 推送契约到 Git (触发前端通知)
aceflow_contract_push(
    feature="user-authentication",
    message="feat: add user authentication APIs"
)
```

**输出**:
- ✅ OpenAPI 契约文件生成
- ✅ 智能补全示例值
- ✅ 推送到 Git 仓库
- ✅ 邮件通知前端团队

---

#### Phase 4: 并行开发 (Parallel Development)

##### 4a. 后端实现 (Backend Implementation)

**AI Actions**:
```python
# 1. 生成 Spring Boot 代码框架
aceflow_generate_backend(
    feature="user-authentication",
    framework="spring-boot",
    generate_files=[
        "controller",    # AuthController.java
        "service",       # AuthService.java
        "dto",          # LoginRequest.java, LoginResponse.java
        "entity",       # User.java
        "repository"    # UserRepository.java
    ]
)

# 2. 实现业务逻辑
# AI 辅助编写代码...

# 3. 更新 OpenAPI 注解
# AI 添加 @Operation, @ApiResponse 等注解

# 4. 验证 API 契约一致性
aceflow_validate_contract(
    feature="user-authentication",
    actual_openapi_url="http://localhost:8080/v3/api-docs"
)
```

##### 4b. 前端开发 (Frontend Development)

**AI Actions**:
```python
# 1. 前端拉取最新契约
aceflow_contract_pull(
    feature="user-authentication"
)

# 2. 启动 Mock Server
aceflow_mock_start(
    feature="user-authentication",
    port=4010
)

# 3. 生成 TypeScript 类型定义
aceflow_generate_types(
    feature="user-authentication",
    language="typescript",
    output="src/types/auth.ts"
)

# 4. 生成 API 客户端
aceflow_generate_client(
    feature="user-authentication",
    library="axios",
    output="src/api/authApi.ts"
)

# 5. 实现 UI 组件
# AI 辅助编写 React/Vue 组件...
```

---

#### Phase 5: 集成测试 (Integration)

**AI Actions**:
```python
# 1. 验证后端实现
aceflow_validate_impl(
    feature="user-authentication",
    tests=[
        "contract_compliance",   # 契约一致性
        "api_responses",         # 响应格式
        "error_handling"         # 错误处理
    ]
)

# 2. 前端切换到真实后端
aceflow_mock_stop(port=4010)

# 3. 执行端到端测试
aceflow_run_e2e_tests(
    feature="user-authentication",
    scenarios=["login", "register", "logout"]
)
```

---

#### Phase 6: 审查和发布 (Review & Release)

**AI Actions**:
```python
# 1. 代码审查
aceflow_review_complete(
    feature="user-authentication",
    checklist=[
        "契约一致性验证",
        "单元测试覆盖率 > 80%",
        "集成测试通过",
        "代码规范检查",
        "安全审查"
    ]
)

# 2. 生成变更日志
aceflow_generate_changelog(
    feature="user-authentication",
    version="1.1.0"
)

# 3. 归档契约
aceflow_contract_archive(
    feature="user-authentication",
    version="1.1.0",
    tag="release-1.1.0"
)
```

---

## 🔧 MCP Tools 扩展

### 新增 MCP Tools 设计

#### 1. aceflow_init_project

```python
def aceflow_init_project(
    project_name: str,
    workflow_mode: str = "contract_first",  # minimal/standard/contract_first
    openapi_url: Optional[str] = None,
    repo_url: Optional[str] = None,
    team_config: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    初始化 AceFlow 项目，结合工作流和契约管理。

    工作流模式:
    - minimal: 快速原型 (Implementation → Test → Demo)
    - standard: 标准流程 (User Stories → ... → Demo)
    - contract_first: 契约优先 (Define → Design → Implement → Integrate)

    Returns:
        {
            "success": True,
            "config_path": ".aceflow/config.yaml",
            "mode": "contract_first",
            "next_steps": [
                "Define your first feature using aceflow_define_feature",
                "Design API contract using aceflow_design_api"
            ]
        }
    """
    # 实现逻辑:
    # 1. 调用 CLI: aceflow init
    # 2. 创建工作流状态文件
    # 3. 初始化 Git 仓库配置
    # 4. 返回指导信息
```

#### 2. aceflow_define_feature

```python
def aceflow_define_feature(
    feature_name: str,
    description: str,
    api_scope: Dict[str, str],
    requirements: List[str],
    dev_team: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    定义新功能需求和 API 边界。

    Args:
        feature_name: 功能名称 (kebab-case)
        description: 功能描述
        api_scope: API 范围定义
            {
                "type": "prefix|exact|regex",
                "pattern": "/api/user/"
            }
        requirements: 功能需求列表
        dev_team: 开发团队邮箱列表

    Returns:
        {
            "success": True,
            "feature": "user-authentication",
            "config_updated": True,
            "next_step": "Design API contract using aceflow_design_api"
        }
    """
    # 实现逻辑:
    # 1. 调用 CLI: aceflow feature add
    # 2. 创建需求文档 (.aceflow/requirements/{feature}.md)
    # 3. 更新工作流状态
```

#### 3. aceflow_design_api

```python
def aceflow_design_api(
    feature: str,
    endpoints: List[Dict[str, Any]],
    base_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    设计 API 契约端点（AI 辅助设计）。

    Args:
        feature: 功能名称
        endpoints: API 端点定义列表

    Returns:
        {
            "success": True,
            "endpoints_count": 3,
            "contract_file": ".aceflow/contracts/user-auth.json",
            "preview": "... OpenAPI spec preview ..."
        }
    """
    # 实现逻辑:
    # 1. 从 endpoints 构建 OpenAPI spec
    # 2. 应用智能补全规则
    # 3. 保存到临时文件
    # 4. 返回预览
```

#### 4. aceflow_contract_generate

```python
def aceflow_contract_generate(
    feature: str,
    apply_smart_completion: bool = True,
    output_format: str = "json"
) -> Dict[str, Any]:
    """
    从 Spring Boot OpenAPI Spec 生成契约。

    Returns:
        {
            "success": True,
            "contract_file": ".aceflow/contracts/user-auth.json",
            "apis_count": 5,
            "examples_added": 12
        }
    """
    # 调用 CLI: aceflow contract generate --feature {feature}
```

#### 5. aceflow_contract_push

```python
def aceflow_contract_push(
    feature: str,
    message: Optional[str] = None,
    notify_team: bool = True
) -> Dict[str, Any]:
    """
    推送契约到 Git 仓库并通知团队。

    Returns:
        {
            "success": True,
            "commit_hash": "abc1234",
            "notified": ["frontend@example.com"],
            "contract_url": "https://github.com/org/contracts/blob/main/..."
        }
    """
    # 调用 CLI: aceflow contract push --feature {feature}
```

#### 6. aceflow_mock_start

```python
def aceflow_mock_start(
    feature: str,
    port: int = 4010,
    dynamic: bool = True,
    validate: bool = True
) -> Dict[str, Any]:
    """
    启动 Mock Server for frontend development.

    Returns:
        {
            "success": True,
            "mock_url": "http://localhost:4010",
            "contract": "user-auth.json",
            "pid": 12345,
            "message": "Frontend can now develop against this Mock Server"
        }
    """
    # 调用 CLI: aceflow mock start --feature {feature} --port {port}
```

#### 7. aceflow_validate_contract

```python
def aceflow_validate_contract(
    feature: str,
    actual_openapi_url: str
) -> Dict[str, Any]:
    """
    验证后端实现与契约一致性。

    Returns:
        {
            "success": True,
            "compliant": True,
            "differences": [],
            "missing_endpoints": [],
            "extra_endpoints": []
        }
    """
    # 实现逻辑:
    # 1. 读取契约文件
    # 2. 获取实际 OpenAPI spec
    # 3. 对比差异
```

---

## 🤖 AI 指导策略

### Prompt 模板设计

#### 1. 项目启动 Prompt

```markdown
# AceFlow Contract-First Development Workflow

You are now using AceFlow, a Contract-First development workflow tool.

## Current Phase: Initialization

### Available Actions:
1. `aceflow_init_project` - Initialize project with contract management
2. `aceflow_define_feature` - Define new feature requirements

### Recommended Flow:
1. Initialize the project with OpenAPI URL and Git repository
2. Define your first feature with API scope
3. Design API endpoints with clear contracts
4. Generate contracts and push to Git
5. Start Mock Server for frontend development

### Best Practices:
- Always define contracts before implementation
- Use meaningful feature names (kebab-case)
- Keep API scopes focused and clear
- Enable team notifications for collaboration

Ready to start? Let's initialize your project!
```

#### 2. Feature Development Prompt

```markdown
## Current Phase: Feature Development - {feature_name}

### Workflow Checklist:
- [x] Feature defined
- [ ] API contract designed
- [ ] Contract pushed to Git
- [ ] Backend implementation started
- [ ] Mock Server running
- [ ] Frontend development started
- [ ] Integration testing
- [ ] Review complete

### Next Actions:
Based on your current phase, I recommend:
{dynamic_recommendations}

### Available Tools:
- `aceflow_design_api` - Design API endpoints
- `aceflow_contract_generate` - Generate from Spring Boot
- `aceflow_contract_push` - Push to Git and notify team
- `aceflow_mock_start` - Start Mock Server
- `aceflow_validate_contract` - Validate implementation

What would you like to do next?
```

#### 3. 并行开发协调 Prompt

```markdown
## Parallel Development Mode Active

### Backend Team:
Status: Implementing {feature_name}
Next: Validate contract compliance

### Frontend Team:
Status: Developing UI against Mock Server
Mock URL: http://localhost:4010
Contract Version: v1.2.0

### Synchronization Points:
- Contract changes require team notification
- Mock Server reflects latest contract
- Integration testing before merge

I'm monitoring both streams and will alert on conflicts.
```

---

## 📅 实施计划

### Phase 1: MCP Tools 扩展 (Week 1-2)

**任务**:
1. ✅ 创建新的 MCP Tools 文件 `aceflow_mcp_server/contract_tools.py`
2. ✅ 实现 7 个核心 MCP Tools
3. ✅ 集成到现有 MCP Server
4. ✅ 编写 Tools 文档

**交付物**:
- `contract_tools.py` (新文件)
- 更新的 `server.py` 注册新 tools
- Tools API 文档

### Phase 2: Workflow State Machine (Week 3)

**任务**:
1. 设计工作流状态机
2. 实现状态跟踪 (`.aceflow/workflow.json`)
3. 添加进度检查点
4. 实现自动化建议

**交付物**:
- `workflow_engine.py`
- 状态文件格式定义
- 进度追踪 UI

### Phase 3: AI Prompts Integration (Week 4)

**任务**:
1. 设计 AI 指导 Prompts
2. 实现上下文感知推荐
3. 添加工作流可视化
4. 集成到 MCP Resources

**交付物**:
- Prompt 模板库
- 动态推荐引擎
- 工作流可视化

### Phase 4: 真实场景测试 (Week 5)

**任务**:
1. 选择试点项目
2. 完整工作流测试
3. 收集反馈
4. 迭代优化

**交付物**:
- 测试报告
- 用户反馈
- 优化建议

---

## 🎯 成功指标

### 开发效率提升

- ⏱️ **契约到实现时间**: < 2 小时
- 🔄 **前后端并行度**: > 80%
- 📉 **契约冲突率**: < 5%
- ✅ **一次性集成成功率**: > 90%

### AI 辅助质量

- 🤖 **AI 建议采纳率**: > 70%
- 📝 **契约自动化程度**: > 85%
- 🎯 **智能补全准确率**: > 95%

### 团队协作

- 📧 **通知及时性**: < 1 分钟
- 🔍 **契约可追溯性**: 100%
- 👥 **团队满意度**: > 4.5/5

---

## 📚 参考资料

### 相关文档

- [MVP Development Plan](MVP_DEVELOPMENT_PLAN.md)
- [Frontend-Backend Collaboration](FRONTEND_BACKEND_COLLABORATION_FINAL_DESIGN.md)
- [README](../aceflow-mcp-server/README.md)

### 技术栈

- **MCP Protocol**: Model Context Protocol
- **FastMCP**: MCP 服务器实现
- **OpenAPI 3.0**: API 契约标准
- **Prism**: Mock Server
- **Git**: 版本控制

---

**Created by**: AceFlow Team
**Last Updated**: 2025-01-04
**Status**: Draft - Pending Implementation
