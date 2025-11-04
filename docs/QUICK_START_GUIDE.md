# AceFlow MCP Server - 快速开始指南

> 5分钟快速上手 AI 驱动的 Contract-First 开发工作流

**版本**: v1.0.0
**日期**: 2025-01-04
**适用场景**: 新项目、前后端分离项目、微服务项目

---

## 📋 目录

1. [前置条件](#前置条件)
2. [安装配置](#安装配置)
3. [5分钟快速上手](#5分钟快速上手)
4. [完整开发流程](#完整开发流程)
5. [常见场景](#常见场景)
6. [故障排除](#故障排除)

---

## 🔧 前置条件

### 必需组件

- **Python 3.8+**
- **Node.js 16+** (用于 Prism Mock Server)
- **Git**
- **Claude Desktop** (或其他 MCP 客户端)

### 可选组件

- **Spring Boot 3.x** (后端开发)
- **SMTP 服务器** (邮件通知)
- **Git 仓库** (契约版本控制)

---

## 🚀 安装配置

### Step 1: 安装 AceFlow MCP Server

```bash
# 克隆仓库
git clone https://github.com/your-org/aceflow-ai.git
cd aceflow-ai/aceflow-mcp-server

# 安装依赖
pip install -e .

# 验证安装
aceflow --version
```

### Step 2: 安装 Prism Mock Server

```bash
# 全局安装 Prism CLI
npm install -g @stoplight/prism-cli

# 验证安装
prism --version
```

### Step 3: 配置 Claude Desktop

编辑配置文件:

**macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aceflow": {
      "command": "python",
      "args": [
        "-m",
        "aceflow_mcp_server.server"
      ],
      "env": {
        "PYTHONPATH": "/path/to/aceflow-ai/aceflow-mcp-server"
      }
    }
  }
}
```

### Step 4: 重启 Claude Desktop

重启后，在 Claude Desktop 中应该能看到 AceFlow 工具可用。

---

## ⚡ 5分钟快速上手

### 场景: 开发一个用户登录功能

在 Claude Desktop 中，与 AI 对话：

**您**: 帮我初始化一个新的 API 项目，使用 Contract-First 模式

**AI** (会调用 MCP 工具):
```python
aceflow_init_project(
    project_name="My API",
    workflow_mode="contract_first",
    openapi_url="http://localhost:8080/v3/api-docs",
    repo_url="git@github.com:myorg/contracts.git"
)
```

**您**: 帮我定义一个用户登录功能

**AI**:
```python
aceflow_define_feature(
    feature_name="user-login",
    description="用户登录功能",
    api_scope={"type": "prefix", "pattern": "/api/auth/"},
    requirements=[
        "用户使用邮箱和密码登录",
        "返回 JWT Token",
        "支持记住我功能"
    ]
)
```

**您**: 帮我设计登录 API

**AI**:
```python
aceflow_design_api(
    feature="user-login",
    endpoints=[
        {
            "path": "/api/auth/login",
            "method": "POST",
            "summary": "用户登录",
            "request_body": {
                "email": "string",
                "password": "string",
                "remember_me": "boolean"
            },
            "responses": {
                "200": {"token": "string", "user": "object"},
                "401": {"error": "string"}
            }
        }
    ]
)
```

**您**: 推送契约到 Git

**AI**:
```python
aceflow_contract_push(
    feature="user-login",
    message="feat: add user login API",
    notify_team=True
)
```

**您**: 启动 Mock Server 让前端开发

**AI**:
```python
aceflow_mock_start(
    feature="user-login",
    port=4010
)
```

**完成!** 现在前端可以访问 `http://localhost:4010/api/auth/login` 进行开发，无需等待后端实现。

---

## 🔄 完整开发流程

### Phase 1: 项目初始化

```python
# 1. 初始化项目
result = aceflow_init_project(
    project_name="E-Commerce API",
    workflow_mode="contract_first",
    openapi_url="http://localhost:8080/v3/api-docs",
    repo_url="git@github.com:company/contracts.git",
    smtp_config={
        "enabled": True,
        "host": "smtp.gmail.com",
        "port": 587,
        "user": "your-email@gmail.com",
        "password": "your-app-password",
        "from": "your-email@gmail.com"
    }
)

# 2. 检查工作流状态
status = aceflow_workflow_status()
# Current stage: setup
# Progress: 10%
```

### Phase 2: 功能定义

```python
# 3. 定义功能
result = aceflow_define_feature(
    feature_name="product-catalog",
    description="商品目录管理",
    api_scope={
        "type": "prefix",
        "pattern": "/api/products/"
    },
    requirements=[
        "获取商品列表（分页、筛选、排序）",
        "获取商品详情",
        "搜索商品",
        "按分类浏览商品"
    ],
    dev_team=[
        "backend@company.com",
        "frontend@company.com"
    ]
)

# 4. 推进工作流
aceflow_workflow_advance(
    next_stage="design",
    feature_name="product-catalog"
)
```

### Phase 3: API 设计

```python
# 5. 设计 API 端点
result = aceflow_design_api(
    feature="product-catalog",
    endpoints=[
        {
            "path": "/api/products",
            "method": "GET",
            "summary": "获取商品列表",
            "request_body": None,
            "responses": {
                "200": {
                    "items": "array",
                    "total": "integer",
                    "page": "integer"
                }
            }
        },
        {
            "path": "/api/products/{id}",
            "method": "GET",
            "summary": "获取商品详情",
            "responses": {
                "200": {"id": "string", "name": "string", "price": "number"},
                "404": {"error": "string"}
            }
        }
    ],
    base_url="http://localhost:8080"
)

# 6. 标记设计阶段检查点
aceflow_workflow_checkpoint("design", "contract_file_exists", True)
aceflow_workflow_checkpoint("design", "valid_openapi_spec", True)
aceflow_workflow_checkpoint("design", "has_endpoints", True)
```

### Phase 4: 契约发布

```python
# 7. 推送契约到 Git
result = aceflow_contract_push(
    feature="product-catalog",
    message="feat: add product catalog API contract",
    notify_team=True
)

# 团队成员会收到邮件通知:
# Subject: [AceFlow] New Contract: product-catalog
# Body: Contract URL + Mock Server 启动指南
```

### Phase 5: 并行开发

#### 前端开发者

```python
# 8A. 拉取契约
aceflow_contract_pull(
    feature="product-catalog",
    branch="main"
)

# 9A. 启动 Mock Server
aceflow_mock_start(
    feature="product-catalog",
    port=4010,
    dynamic=True,
    validate=True
)

# 前端现在可以开发:
# GET http://localhost:4010/api/products
# GET http://localhost:4010/api/products/123
```

#### 后端开发者

```java
// 8B. 实现 Spring Boot Controller
@RestController
@RequestMapping("/api/products")
@Tag(name = "Product Catalog")
public class ProductController {

    @GetMapping
    @Operation(summary = "获取商品列表")
    public ResponseEntity<ProductListResponse> getProducts(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        // 实现业务逻辑
        return ResponseEntity.ok(productService.getProducts(page, size));
    }

    @GetMapping("/{id}")
    @Operation(summary = "获取商品详情")
    public ResponseEntity<Product> getProduct(@PathVariable String id) {
        return ResponseEntity.ok(productService.getProduct(id));
    }
}
```

### Phase 6: 契约验证

```python
# 10. 后端实现完成后，验证契约一致性
result = aceflow_validate_contract(
    feature="product-catalog",
    actual_openapi_url="http://localhost:8080/v3/api-docs"
)

# 如果验证失败:
# {
#   "compliant": False,
#   "missing_endpoints": ["/api/products/{id}"],
#   "extra_endpoints": [],
#   "differences": [...]
# }

# 修复后重新验证，直到通过
```

### Phase 7: 集成测试

```python
# 11. 停止 Mock Server
aceflow_mock_stop(port=4010)

# 12. 前端切换到真实后端
# 修改前端配置: http://localhost:4010 → http://localhost:8080

# 13. 运行 E2E 测试
# ... 运行测试套件 ...

# 14. 推进到 integration 阶段
aceflow_workflow_advance(next_stage="integration")
```

### Phase 8: 完成

```python
# 15. 查看最终状态
status = aceflow_workflow_status()

# {
#   "current_stage": "completed",
#   "overall_progress": 100,
#   "completed_stages": 10,
#   "total_stages": 10,
#   "features": {
#     "product-catalog": {
#       "status": "completed",
#       "contract_file": ".aceflow/contracts/product-catalog.json"
#     }
#   }
# }
```

---

## 🎯 常见场景

### 场景 1: 纯前端项目（后端未开发）

```python
# 1. 初始化项目（不需要 openapi_url）
aceflow_init_project(
    project_name="Frontend App",
    workflow_mode="contract_first",
    repo_url="git@github.com:org/contracts.git"
)

# 2. 定义功能
aceflow_define_feature(
    feature_name="user-profile",
    description="用户个人资料",
    api_scope={"type": "prefix", "pattern": "/api/user/"},
    requirements=["查看个人资料", "编辑个人资料"]
)

# 3. AI 辅助设计 API（从需求生成契约）
aceflow_design_api(
    feature="user-profile",
    endpoints=[...]
)

# 4. 启动 Mock Server
aceflow_mock_start(feature="user-profile", port=4010)

# 前端可以立即开始开发!
```

### 场景 2: 后端先行项目（已有实现）

```python
# 1. 初始化项目
aceflow_init_project(
    project_name="Existing Backend",
    workflow_mode="contract_first",
    openapi_url="http://localhost:8080/v3/api-docs",
    repo_url="git@github.com:org/contracts.git"
)

# 2. 定义功能
aceflow_define_feature(
    feature_name="order-management",
    description="订单管理",
    api_scope={"type": "prefix", "pattern": "/api/orders/"},
    requirements=["创建订单", "查询订单", "取消订单"]
)

# 3. 从现有后端生成契约
aceflow_contract_generate(
    feature="order-management",
    apply_smart_completion=True
)

# 4. 推送契约
aceflow_contract_push(
    feature="order-management",
    notify_team=True
)

# 前端可以拉取契约并开始开发!
```

### 场景 3: 多功能并行开发

```python
# 定义多个功能
features = ["user-auth", "product-catalog", "shopping-cart", "checkout"]

for feature in features:
    aceflow_define_feature(
        feature_name=feature,
        description=f"{feature} module",
        api_scope={"type": "prefix", "pattern": f"/api/{feature}/"},
        requirements=["TBD"]
    )

# 查看所有功能状态
status = aceflow_workflow_status()
print(status["features"])

# {
#   "user-auth": {"status": "completed", ...},
#   "product-catalog": {"status": "design", ...},
#   "shopping-cart": {"status": "define", ...},
#   "checkout": {"status": "pending", ...}
# }
```

### 场景 4: 使用 AI 智能建议

```python
# 不确定下一步做什么?
recommendations = aceflow_workflow_recommendations()

# {
#   "recommendations": [
#     {
#       "priority": "high",
#       "action": "Push contract to Git",
#       "tool": "aceflow_contract_push",
#       "benefits": [
#         "Notify frontend team",
#         "Enable parallel development"
#       ]
#     },
#     {
#       "priority": "medium",
#       "audience": "frontend",
#       "action": "Start Mock Server",
#       "tools": ["aceflow_contract_pull", "aceflow_mock_start"]
#     }
#   ]
# }

# 按建议执行即可!
```

---

## 🐛 故障排除

### 问题 1: Mock Server 启动失败

**症状**: `aceflow_mock_start` 返回错误

**原因**: Prism 未安装或端口被占用

**解决方案**:
```bash
# 检查 Prism 安装
prism --version

# 如果未安装
npm install -g @stoplight/prism-cli

# 检查端口占用
lsof -i :4010

# 使用其他端口
aceflow_mock_start(feature="xxx", port=4011)
```

### 问题 2: 契约推送失败

**症状**: `aceflow_contract_push` 返回 Git 错误

**原因**: Git 仓库未配置或权限问题

**解决方案**:
```bash
# 检查 Git 配置
cat .aceflow/config.yaml

# 测试 Git 访问
git clone git@github.com:your-org/contracts.git /tmp/test

# 配置 SSH Key
ssh-keygen -t ed25519 -C "your-email@example.com"
ssh-add ~/.ssh/id_ed25519
```

### 问题 3: 契约验证失败

**症状**: `aceflow_validate_contract` 报告不一致

**原因**: 后端实现与契约不匹配

**解决方案**:
```python
# 1. 查看详细差异
result = aceflow_validate_contract(
    feature="xxx",
    actual_openapi_url="http://localhost:8080/v3/api-docs"
)

print(result["differences"])
print(result["missing_endpoints"])
print(result["extra_endpoints"])

# 2. 修复后端实现
# - 添加缺失的端点
# - 删除多余的端点
# - 调整方法签名

# 3. 重新验证
```

### 问题 4: 工作流状态丢失

**症状**: `aceflow_workflow_status` 返回未初始化

**原因**: `.aceflow/workflow.json` 文件损坏或删除

**解决方案**:
```bash
# 检查文件是否存在
ls -la .aceflow/workflow.json

# 如果文件损坏，可以重新初始化
# 注意: 这会丢失历史状态
aceflow_init_project(
    project_name="Your Project",
    workflow_mode="contract_first"
)
```

---

## 📚 下一步

- [MCP Contract Tools Guide](MCP_CONTRACT_TOOLS_GUIDE.md) - 详细工具参考
- [Workflow State Management Guide](WORKFLOW_STATE_MANAGEMENT_GUIDE.md) - 工作流状态管理
- [Workflow State Machine Design](WORKFLOW_STATE_MACHINE_DESIGN.md) - 状态机设计

---

**Created by**: AceFlow Team
**Last Updated**: 2025-01-04
**Version**: 1.0.0
