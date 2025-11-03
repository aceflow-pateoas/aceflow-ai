# AceFlow MCP Contract Tools - 使用指南

> AI 驱动的 Contract-First 开发工作流 MCP Tools

## 📋 目录

1. [快速开始](#快速开始)
2. [工具列表](#工具列表)
3. [完整工作流示例](#完整工作流示例)
4. [工具详细说明](#工具详细说明)
5. [最佳实践](#最佳实践)

---

## 🚀 快速开始

### 前置条件

1. **安装 AceFlow MCP Server**
   ```bash
   cd aceflow-mcp-server
   pip install -e .
   ```

2. **配置 MCP 客户端**

   在 Claude Desktop 或 Cursor 的 MCP 配置中添加：
   ```json
   {
     "mcpServers": {
       "aceflow": {
         "command": "python",
         "args": ["-m", "aceflow_mcp_server.server"],
         "env": {}
       }
     }
   }
   ```

3. **安装依赖工具**
   ```bash
   # Prism Mock Server (用于 Mock API)
   npm install -g @stoplight/prism-cli
   ```

### 5 分钟快速体验

```python
# 1. 初始化项目
aceflow_init_project(
    project_name="My API Project",
    workflow_mode="contract_first",
    openapi_url="http://localhost:8080/v3/api-docs",
    repo_url="git@github.com:org/contracts.git"
)

# 2. 定义功能
aceflow_define_feature(
    feature_name="user-auth",
    description="User authentication APIs",
    api_scope={"type": "prefix", "pattern": "/api/auth/"},
    requirements=["Login", "Register", "Logout"]
)

# 3. 设计 API
aceflow_design_api(
    feature="user-auth",
    endpoints=[{
        "path": "/api/auth/login",
        "method": "POST",
        "request_body": {"email": "string", "password": "string"},
        "responses": {"200": {"token": "string"}}
    }]
)

# 4. 推送契约
aceflow_contract_push(feature="user-auth")

# 5. 启动 Mock Server
aceflow_mock_start(feature="user-auth", port=4010)
```

---

## 🔧 工具列表

### 核心工作流工具 (4 个现有工具)

| 工具名称 | 功能 | 阶段 |
|---------|------|------|
| `aceflow_init` | 初始化项目基础结构 | Setup |
| `aceflow_stage` | 管理工作流阶段 | All |
| `aceflow_validate` | 验证项目合规性 | All |
| `aceflow_template` | 管理工作流模板 | Setup |

### Contract-First 工作流工具 (9 个新工具)

| 工具名称 | 功能 | 适用角色 | 阶段 |
|---------|------|---------|------|
| `aceflow_init_project` | 初始化契约管理项目 | 所有人 | Setup |
| `aceflow_define_feature` | 定义功能需求和 API 边界 | PM/后端 | Define |
| `aceflow_design_api` | 设计 OpenAPI 契约 | 后端/架构师 | Design |
| `aceflow_contract_generate` | 从 Spring Boot 生成契约 | 后端 | Implement |
| `aceflow_contract_push` | 推送契约到 Git | 后端 | Implement |
| `aceflow_contract_pull` | 从 Git 拉取契约 | 前端 | Develop |
| `aceflow_mock_start` | 启动 Mock Server | 前端 | Develop |
| `aceflow_mock_stop` | 停止 Mock Server | 前端 | Develop |
| `aceflow_validate_contract` | 验证实现与契约一致性 | 后端 | Validate |

---

## 📖 完整工作流示例

### Phase 1: 项目初始化 (Backend Lead)

```python
# 初始化项目并配置契约管理
result = aceflow_init_project(
    project_name="E-Commerce API",
    workflow_mode="contract_first",
    openapi_url="http://localhost:8080/v3/api-docs",
    repo_url="git@github.com:company/api-contracts.git",
    smtp_config={
        "enabled": True,
        "host": "smtp.gmail.com",
        "port": 587,
        "user": "noreply@company.com",
        "password": "${SMTP_PASSWORD}",
        "from": "API Team <api@company.com>"
    }
)

print(result["message"])
# => "Project 'E-Commerce API' initialized successfully in contract_first mode"

print(result["next_steps"])
# => ["Define your first feature using aceflow_define_feature", ...]
```

### Phase 2: 功能定义 (Product Manager + Backend)

```python
# 定义用户认证功能
result = aceflow_define_feature(
    feature_name="user-authentication",
    description="Complete user authentication system with JWT",
    api_scope={
        "type": "prefix",
        "pattern": "/api/auth/"
    },
    requirements=[
        "支持邮箱密码登录",
        "支持 JWT Token 认证",
        "支持刷新 Token",
        "支持用户注册",
        "支持密码找回"
    ],
    dev_team=[
        "backend-team@company.com",
        "frontend-team@company.com",
        "qa-team@company.com"
    ]
)

print(result["message"])
# => "Feature 'user-authentication' defined successfully"

print(result["requirements_file"])
# => ".aceflow/requirements/user-authentication.md"
```

### Phase 3: API 契约设计 (Backend Architect)

#### 方式 1: AI 辅助从零设计

```python
# AI 辅助设计 API 端点
result = aceflow_design_api(
    feature="user-authentication",
    endpoints=[
        {
            "path": "/api/auth/login",
            "method": "POST",
            "summary": "User login",
            "description": "Authenticate user with email and password",
            "request_body": {
                "email": "string",
                "password": "string",
                "remember_me": "boolean"
            },
            "responses": {
                "200": {
                    "token": "string",
                    "refresh_token": "string",
                    "expires_in": "integer",
                    "user": "object"
                },
                "401": {
                    "error": "string",
                    "message": "string"
                }
            }
        },
        {
            "path": "/api/auth/register",
            "method": "POST",
            "summary": "User registration",
            "request_body": {
                "email": "string",
                "password": "string",
                "name": "string"
            },
            "responses": {
                "201": {
                    "user_id": "string",
                    "email": "string",
                    "message": "string"
                },
                "400": {
                    "error": "string",
                    "validation_errors": "array"
                }
            }
        },
        {
            "path": "/api/auth/refresh",
            "method": "POST",
            "summary": "Refresh access token",
            "request_body": {
                "refresh_token": "string"
            },
            "responses": {
                "200": {
                    "token": "string",
                    "expires_in": "integer"
                }
            }
        }
    ],
    base_url="http://localhost:8080"
)

print(result["message"])
# => "API contract designed for 'user-authentication' with 3 endpoints"

print(result["contract_file"])
# => ".aceflow/contracts/user-authentication.json"
```

#### 方式 2: 从现有 Spring Boot 生成

```python
# 假设后端已实现并添加了 @Operation 注解

# 从 Spring Boot 生成契约
result = aceflow_contract_generate(
    feature="user-authentication",
    apply_smart_completion=True,  # 自动添加示例值
    output_format="json"
)

print(result["message"])
# => "Contract generated for 'user-authentication' with 5 APIs"

print(result["apis_count"])
# => 5
```

### Phase 4: 推送契约并通知团队 (Backend)

```python
# 推送契约到 Git 仓库
result = aceflow_contract_push(
    feature="user-authentication",
    message="feat: add user authentication API contract",
    notify_team=True  # 自动发送邮件通知前端团队
)

print(result["message"])
# => "Contract for 'user-authentication' pushed to Git successfully"

print(result["notified"])
# => ["frontend-team@company.com", "qa-team@company.com"]

print(result["contract_url"])
# => "https://github.com/company/api-contracts/blob/main/contracts/active/user-authentication.json"
```

### Phase 5: 前端开发 (Frontend Team)

#### 5.1 拉取契约

```python
# 前端开发者收到邮件通知后，拉取最新契约
result = aceflow_contract_pull(
    feature="user-authentication",
    branch="main"
)

print(result["message"])
# => "Contract for 'user-authentication' pulled successfully from Git"

print(result["contract_file"])
# => ".aceflow/contracts/user-authentication.json"
```

#### 5.2 启动 Mock Server

```python
# 启动 Mock Server 进行前端开发
result = aceflow_mock_start(
    feature="user-authentication",
    port=4010,
    dynamic=True,      # 动态生成响应
    validate=True      # 验证请求/响应格式
)

print(result["message"])
# => "Mock Server started for 'user-authentication' at http://localhost:4010"

print(result["mock_url"])
# => "http://localhost:4010"

# 前端现在可以使用 http://localhost:4010/api/auth/login 进行开发
```

#### 5.3 前端开发代码

```javascript
// 前端代码使用 Mock Server
const API_BASE = "http://localhost:4010";

async function login(email, password) {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, remember_me: false })
    });

    const data = await response.json();
    // Mock Server 会根据契约返回符合格式的响应
    return data;
}
```

### Phase 6: 后端实现 (Backend Team)

```java
// Spring Boot 实现
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @PostMapping("/login")
    @Operation(summary = "User login", description = "Authenticate user with email and password")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Login successful"),
        @ApiResponse(responseCode = "401", description = "Invalid credentials")
    })
    public ResponseEntity<LoginResponse> login(@RequestBody LoginRequest request) {
        // 实现登录逻辑
        // ...
        return ResponseEntity.ok(new LoginResponse(token, refreshToken, expiresIn, user));
    }
}
```

### Phase 7: 验证实现 (Backend QA)

```python
# 后端实现完成后，验证是否符合契约
result = aceflow_validate_contract(
    feature="user-authentication",
    actual_openapi_url="http://localhost:8080/v3/api-docs"
)

if result["compliant"]:
    print("✅ 实现完全符合契约！")
else:
    print("❌ 发现契约不一致：")
    print(f"  缺失端点: {result['missing_endpoints']}")
    print(f"  额外端点: {result['extra_endpoints']}")
    print(f"  差异: {result['differences']}")
```

### Phase 8: 集成测试 (Frontend + Backend)

```python
# 前端停止 Mock Server，切换到真实后端
result = aceflow_mock_stop(port=4010)

print(result["message"])
# => "Mock Server stopped successfully"

# 前端更新配置为真实后端 URL
# const API_BASE = "http://localhost:8080";

# 运行端到端测试...
```

---

## 🔍 工具详细说明

### 1. aceflow_init_project

**功能**: 初始化 AceFlow 项目并配置契约管理

**参数**:
- `project_name` (str, required): 项目名称
- `workflow_mode` (str, optional): 工作流模式
  - `"minimal"`: 快速原型 (Implementation → Test → Demo)
  - `"standard"`: 标准流程 (User Stories → ... → Demo)
  - `"contract_first"`: 契约优先 ⭐ **推荐**
- `openapi_url` (str, optional): Spring Boot OpenAPI URL
- `repo_url` (str, optional): Git 契约仓库 URL
- `smtp_config` (dict, optional): SMTP 配置

**返回值**:
```python
{
    "success": True,
    "config_path": ".aceflow/config.yaml",
    "mode": "contract_first",
    "project_name": "My Project",
    "next_steps": [...]
}
```

**示例**:
```python
aceflow_init_project(
    project_name="My API",
    workflow_mode="contract_first",
    openapi_url="http://localhost:8080/v3/api-docs",
    repo_url="git@github.com:org/contracts.git"
)
```

---

### 2. aceflow_define_feature

**功能**: 定义功能需求和 API 边界

**参数**:
- `feature_name` (str, required): 功能名称 (kebab-case)
- `description` (str, required): 功能描述
- `api_scope` (dict, required): API 范围定义
  ```python
  {
      "type": "prefix|exact|regex",
      "pattern": "/api/user/"
  }
  ```
- `requirements` (list, required): 功能需求列表
- `dev_team` (list, optional): 开发团队邮箱列表

**返回值**:
```python
{
    "success": True,
    "feature": "user-management",
    "config_updated": True,
    "requirements_file": ".aceflow/requirements/user-management.md",
    "next_step": "Design API contract using aceflow_design_api"
}
```

**示例**:
```python
aceflow_define_feature(
    feature_name="payment-processing",
    description="Payment processing with multiple providers",
    api_scope={
        "type": "prefix",
        "pattern": "/api/payment/"
    },
    requirements=[
        "支持支付宝支付",
        "支持微信支付",
        "支持退款功能",
        "支持订单查询"
    ],
    dev_team=["backend@company.com", "frontend@company.com"]
)
```

---

### 3. aceflow_design_api

**功能**: 从零设计 API 契约 (AI 辅助)

**适用场景**:
- 新功能开发，后端尚未实现
- 需要前后端同时开始工作
- 架构师设计 API 规范

**参数**:
- `feature` (str, required): 功能名称
- `endpoints` (list, required): API 端点定义列表
- `base_url` (str, optional): API 基础 URL

**端点定义格式**:
```python
{
    "path": "/api/resource/{id}",
    "method": "GET|POST|PUT|DELETE",
    "summary": "端点描述",
    "description": "详细说明",
    "request_body": {
        "field1": "string",
        "field2": "integer",
        "field3": "boolean"
    },
    "responses": {
        "200": {
            "field1": "string",
            "field2": "object"
        },
        "400": {
            "error": "string"
        }
    }
}
```

**返回值**:
```python
{
    "success": True,
    "endpoints_count": 5,
    "contract_file": ".aceflow/contracts/feature-name.json",
    "preview": "... OpenAPI spec preview ..."
}
```

---

### 4. aceflow_contract_generate

**功能**: 从 Spring Boot OpenAPI Spec 生成契约

**适用场景**:
- 后端已实现 API 并添加了 @Operation 注解
- 需要更新契约以匹配实现

**参数**:
- `feature` (str, required): 功能名称
- `apply_smart_completion` (bool, optional): 是否应用智能补全 (默认: True)
- `output_format` (str, optional): 输出格式 "json" 或 "yaml" (默认: "json")

**智能补全规则**:
- `userId` → 示例值: `12345`
- `email` → 示例值: `user@example.com`
- `phone` → 示例值: `13800138000`
- `createDate` → 示例值: `2025-01-01`
- `uuid` → 示例值: `550e8400-e29b-41d4-a716-446655440000`

**返回值**:
```python
{
    "success": True,
    "contract_file": ".aceflow/contracts/user-auth.json",
    "apis_count": 5,
    "smart_completion_applied": True,
    "next_step": "Push contract to Git using aceflow_contract_push"
}
```

---

### 5. aceflow_contract_push

**功能**: 推送契约到 Git 仓库并通知团队

**参数**:
- `feature` (str, required): 功能名称
- `message` (str, optional): 自定义 commit 消息
- `notify_team` (bool, optional): 是否发送邮件通知 (默认: True)

**自动化操作**:
1. 克隆/拉取契约仓库
2. 复制契约文件到仓库
3. Git commit 和 push
4. 发送邮件通知给 `dev_team`

**返回值**:
```python
{
    "success": True,
    "commit_hash": "abc1234",
    "notified": ["frontend@company.com"],
    "contract_url": "https://github.com/org/contracts/blob/main/...",
    "next_step": "Frontend can now pull contract and start development"
}
```

**邮件通知内容**:
```
主题: 🔔 API契约更新通知: user-authentication

开发团队，你好！

后端团队已更新以下功能的API契约：

功能: user-authentication
提交信息: feat: add user authentication APIs
Commit: abc1234
契约仓库: https://github.com/org/contracts

前端团队可以开始开发了！
...
```

---

### 6. aceflow_contract_pull

**功能**: 从 Git 仓库拉取契约到本地

**适用角色**: 前端开发者

**参数**:
- `feature` (str, required): 功能名称
- `branch` (str, optional): Git 分支 (默认: "main")

**返回值**:
```python
{
    "success": True,
    "contract_file": ".aceflow/contracts/user-auth.json",
    "next_step": "Start Mock Server using aceflow_mock_start"
}
```

---

### 7. aceflow_mock_start

**功能**: 启动 Prism Mock Server

**适用角色**: 前端开发者

**参数**:
- `feature` (str, required): 功能名称
- `port` (int, optional): 端口号 (默认: 4010)
- `dynamic` (bool, optional): 启用动态响应生成 (默认: True)
- `validate` (bool, optional): 启用请求/响应验证 (默认: True)

**Mock Server 特性**:
- ✅ 根据 OpenAPI schema 自动生成响应
- ✅ 支持所有 HTTP 方法 (GET/POST/PUT/DELETE)
- ✅ 动态生成符合 schema 的示例数据
- ✅ 验证请求参数和响应格式
- ✅ 支持路径参数、查询参数、请求体

**返回值**:
```python
{
    "success": True,
    "mock_url": "http://localhost:4010",
    "contract": "user-auth.json",
    "port": 4010,
    "pid": 12345,
    "frontend_message": "Frontend can now develop against this Mock Server"
}
```

---

### 8. aceflow_mock_stop

**功能**: 停止 Mock Server

**参数**:
- `port` (int, optional): 要停止的端口号
- `stop_all` (bool, optional): 停止所有 Mock Server (默认: False)

**返回值**:
```python
{
    "success": True,
    "stopped_ports": [4010],
    "message": "Mock Server stopped successfully"
}
```

---

### 9. aceflow_validate_contract

**功能**: 验证后端实现与契约一致性

**适用角色**: 后端开发者、QA

**参数**:
- `feature` (str, required): 功能名称
- `actual_openapi_url` (str, required): 实际后端 OpenAPI URL

**验证项**:
- ✅ 检查所有契约端点是否已实现
- ✅ 检查是否有额外的未定义端点
- ✅ 检查 HTTP 方法是否匹配
- ✅ 检查请求/响应结构

**返回值**:
```python
{
    "success": True,
    "compliant": False,
    "differences": [
        {
            "path": "/api/auth/login",
            "issue": "method_mismatch",
            "expected": ["POST"],
            "actual": ["POST", "GET"]
        }
    ],
    "missing_endpoints": ["/api/auth/refresh"],
    "extra_endpoints": ["/api/auth/debug"],
    "message": "Contract violations detected"
}
```

---

## 💡 最佳实践

### 1. 团队协作流程

#### 后端团队工作流

```python
# Step 1: 定义功能
aceflow_define_feature(...)

# Step 2A: 从零设计 (新功能)
aceflow_design_api(...)

# 或 Step 2B: 从实现生成 (已有代码)
aceflow_contract_generate(...)

# Step 3: 推送契约并通知前端
aceflow_contract_push(...)

# Step 4: 实现后端代码
# ... 编写 Spring Boot 代码 ...

# Step 5: 验证实现
aceflow_validate_contract(...)
```

#### 前端团队工作流

```python
# Step 1: 收到邮件通知后，拉取契约
aceflow_contract_pull(...)

# Step 2: 启动 Mock Server
aceflow_mock_start(...)

# Step 3: 前端开发
# ... 使用 Mock API 开发 ...

# Step 4: 集成测试准备
aceflow_mock_stop(...)

# Step 5: 切换到真实后端进行集成测试
```

### 2. 契约版本管理

```python
# 使用 Git 分支管理不同版本
aceflow_contract_push(
    feature="user-auth",
    message="feat: v2.0 - add OAuth support"
)

# 前端拉取特定版本
aceflow_contract_pull(
    feature="user-auth",
    branch="v2.0"
)
```

### 3. 多环境支持

```python
# 开发环境
aceflow_init_project(
    openapi_url="http://localhost:8080/v3/api-docs",
    ...
)

# 测试环境
aceflow_validate_contract(
    feature="user-auth",
    actual_openapi_url="https://test.api.company.com/v3/api-docs"
)

# 生产环境
aceflow_validate_contract(
    feature="user-auth",
    actual_openapi_url="https://api.company.com/v3/api-docs"
)
```

### 4. CI/CD 集成

```yaml
# .github/workflows/contract-validation.yml
name: Contract Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Start Spring Boot
        run: ./mvnw spring-boot:run &

      - name: Wait for API
        run: sleep 30

      - name: Validate Contract
        run: |
          python -c "
          from aceflow_mcp_server.contract_tools import ContractWorkflowTools
          tools = ContractWorkflowTools()
          result = tools.aceflow_validate_contract(
              feature='user-auth',
              actual_openapi_url='http://localhost:8080/v3/api-docs'
          )
          assert result['compliant'], 'Contract validation failed'
          "
```

### 5. 错误处理

```python
# 始终检查返回值
result = aceflow_contract_push(feature="user-auth")

if not result["success"]:
    print(f"❌ 错误: {result['error']}")
    print(f"消息: {result['message']}")
    # 处理错误...
else:
    print(f"✅ 成功: {result['message']}")
    # 继续流程...
```

---

## 🎯 使用场景

### 场景 1: 新项目启动

**目标**: 从零开始，建立 Contract-First 开发流程

```python
# 1. 项目经理初始化
aceflow_init_project(
    project_name="New Microservice",
    workflow_mode="contract_first",
    openapi_url="http://localhost:8080/v3/api-docs",
    repo_url="git@github.com:company/contracts.git"
)

# 2. 架构师定义功能模块
for feature in ["user-management", "order-processing", "payment"]:
    aceflow_define_feature(
        feature_name=feature,
        description=f"{feature} APIs",
        api_scope={"type": "prefix", "pattern": f"/api/{feature}/"},
        requirements=[...]
    )

# 3. 架构师设计所有 API 契约
aceflow_design_api(feature="user-management", endpoints=[...])
aceflow_design_api(feature="order-processing", endpoints=[...])
aceflow_design_api(feature="payment", endpoints=[...])

# 4. 推送所有契约
for feature in ["user-management", "order-processing", "payment"]:
    aceflow_contract_push(feature=feature)

# 5. 前后端同时开始开发
# 前端: 拉取契约 → 启动 Mock → 开发 UI
# 后端: 实现 API → 验证契约 → 集成测试
```

### 场景 2: API 更新

**目标**: 后端更新 API，通知前端同步

```python
# 1. 后端修改代码并更新 OpenAPI 注解
# ... 修改 Spring Boot 代码 ...

# 2. 重新生成契约
aceflow_contract_generate(feature="user-auth")

# 3. 推送并通知
aceflow_contract_push(
    feature="user-auth",
    message="feat: add forgot password endpoint"
)

# 4. 前端收到邮件，拉取最新契约
aceflow_contract_pull(feature="user-auth")

# 5. 重启 Mock Server
aceflow_mock_stop(port=4010)
aceflow_mock_start(feature="user-auth", port=4010)

# 6. 前端更新代码
```

### 场景 3: 多版本并行开发

**目标**: 同时开发 v1.0 (生产) 和 v2.0 (新功能)

```python
# V1.0 维护
aceflow_contract_pull(feature="user-auth", branch="v1.0")
aceflow_mock_start(feature="user-auth", port=4010)  # V1.0

# V2.0 新功能开发
aceflow_contract_pull(feature="user-auth", branch="v2.0")
aceflow_mock_start(feature="user-auth", port=4020)  # V2.0

# 前端可以同时测试两个版本
```

---

## 🔗 相关文档

- [AI Workflow Integration Design](AI_WORKFLOW_INTEGRATION.md) - 完整设计文档
- [MVP Development Plan](MVP_DEVELOPMENT_PLAN.md) - MVP 开发计划
- [Frontend-Backend Collaboration](FRONTEND_BACKEND_COLLABORATION_FINAL_DESIGN.md) - 前后端协作设计
- [README](../aceflow-mcp-server/README.md) - CLI 工具文档

---

**Created by**: AceFlow Team
**Last Updated**: 2025-01-04
**Version**: 1.0.0
