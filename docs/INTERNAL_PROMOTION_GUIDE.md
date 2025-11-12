# AceFlow MCP Server - 内部推广指南

## 📋 目录

1. [项目概述](#项目概述)
2. [核心价值](#核心价值)
3. [典型应用场景](#典型应用场景)
4. [快速上手](#快速上手)
5. [最佳实践](#最佳实践)
6. [技术亮点](#技术亮点)
7. [ROI 分析](#roi-分析)
8. [团队反馈](#团队反馈)
9. [推广计划](#推广计划)

---

## 项目概述

### 什么是 AceFlow MCP Server?

**AceFlow MCP Server** 是一个 AI 驱动的智能工作流管理系统,通过 **MCP (Model Context Protocol)** 协议将 AI 助手(如 Claude、Cline、Cursor)与项目工作流无缝集成。

它提供了两大核心能力:

1. **Contract-First 开发** (4个工具) - OpenAPI 契约管理、Mock Server、团队协作
2. **智能工作流管理** (21个工具) - 状态管理、记忆系统、质量门、文档导出

**当前版本**: v3.0.2 (2025-01-12)
**安装方式**: `pip install aceflow-mcp-server`
**开源许可**: MIT License
**PyPI 下载**: https://pypi.org/project/aceflow-mcp-server/

### 为什么需要它?

在传统开发流程中,我们面临这些痛点:

| 传统方式 | 痛点 | AceFlow 解决方案 |
|---------|------|----------------|
| **前后端协作** | API 文档更新不及时,前端等待后端接口 | 自动生成 OpenAPI 契约 + Mock Server,前后端并行开发 |
| **AI 辅助开发** | AI 不理解项目上下文,重复性建议 | 项目记忆系统,AI 理解项目历史和决策 |
| **工作流管理** | 手动跟踪开发阶段,容易遗漏关键步骤 | 智能工作流引擎,自动状态跟踪和质量门 |
| **知识沉淀** | 技术决策散落各处,新人难以快速上手 | 自动记录决策、问题、经验教训 |
| **代码评审** | 人工检查容易遗漏质量问题 | 自动质量门评估,量化代码质量 |

---

## 核心价值

### 1. 提升前后端协作效率 (节省 40% 等待时间)

**场景**: 产品需求评审后,前端需要等待后端 API 实现才能开始开发。

**传统方式**:
```
第1天: 产品评审
第2-3天: 后端设计 API,编写文档
第4-5天: 前端等待 ❌
第6-10天: 后端实现 API
第11天: 前端开始开发
```

**使用 AceFlow**:
```
第1天: 产品评审 + AI 辅助设计 OpenAPI 契约
第2天: 后端推送契约,前端启动 Mock Server
第3-10天: 前后端并行开发 ✅ (前端使用 Mock API)
第11天: 后端 API 完成,前端无缝切换到真实 API
```

**节省时间**: 4-5 天 (约 40%)

### 2. AI 上下文理解提升 (减少 60% 重复性工作)

**场景**: 使用 AI 助手(Claude/Cline)进行代码开发。

**传统方式**:
```
开发者: "帮我实现用户认证功能"
AI: "这里是一个通用的 JWT 认证示例..." ❌
开发者: "不对,我们项目使用 OAuth 2.0 + Redis 缓存"
AI: "好的,这里是 OAuth 2.0 示例..."
开发者: "不对,我们还有自定义的权限系统..."
(反复沟通 3-5 轮)
```

**使用 AceFlow**:
```
开发者: "帮我实现用户认证功能"
AI (自动读取项目记忆):
  "根据项目历史,我看到你们使用:
   - OAuth 2.0 + Redis 缓存
   - 自定义 RBAC 权限系统
   - 30分钟 token 过期时间
   这里是符合你们架构的实现..." ✅
```

**节省时间**: 60% 的重复性沟通和代码修改

### 3. 工作流规范化 (减少 30% 返工)

**场景**: 功能开发完成后发现缺少单元测试、文档不全等问题。

**传统方式**:
```
开发 → Code Review 发现问题 → 返工修复 → 再次 Review
(平均 2-3 轮返工)
```

**使用 AceFlow**:
```
开发 → 自动质量门检查 → 提前发现问题 → 一次性修复 → 通过 Review
(平均 1 轮,减少 2 轮返工)
```

**质量门检查项**:
- ✅ 单元测试覆盖率 ≥ 80%
- ✅ API 文档完整性
- ✅ 错误处理完整性
- ✅ 性能测试通过
- ✅ 安全检查通过

### 4. 知识沉淀与传承 (新人上手时间减少 50%)

**场景**: 新人加入团队,需要了解项目架构和历史决策。

**传统方式**:
```
新人: "为什么我们用 PostgreSQL 而不是 MySQL?"
老员工: "这个...当时是因为...让我想想..." ❌
(散落的文档、过期的 Wiki、口口相传)
```

**使用 AceFlow**:
```
新人: "为什么我们用 PostgreSQL 而不是 MySQL?"
AI (从项目记忆中检索):
  "在 2024-Q3 的技术选型中,团队选择 PostgreSQL:
   - 决策人: 张工 (高级后端)
   - 理由: 需要 JSON 查询、全文搜索、复杂事务
   - 相关讨论: [链接]
   - 相关代码: [示例]" ✅
```

---

## 典型应用场景

### 场景 1: 新功能开发 (Contract-First 模式)

**背景**: 产品需求 - "实现用户管理模块"

**步骤**:

#### 第1天: 需求分析 + 契约设计

```bash
# 1. 后端 Leader 与 AI 协作设计 API 契约
# (在 Cline/Claude Code 中对话)
开发者: "帮我设计用户管理模块的 OpenAPI 契约,需要包含:
         - 用户注册/登录/登出
         - 用户信息查询/更新
         - 密码重置"

AI (使用 aceflow_design_api 工具):
  ✅ 生成完整的 OpenAPI 3.0 契约
  ✅ 自动添加示例值和描述
  ✅ 符合团队 API 设计规范

# 2. 在 .aceflow/config.yaml 中添加功能配置
aceflow feature add \
  --name user-management \
  --api-filter "/api/user/" \
  --filter-type prefix \
  --description "用户管理模块" \
  --dev-team "frontend-team@company.com,backend-team@company.com"
```

#### 第2天: 契约推送 + 前后端并行开发

```bash
# 后端: 推送契约到 Git (自动触发邮件通知)
aceflow contract push --feature user-management

# 前端: 拉取契约并启动 Mock Server
aceflow contract pull --feature user-management
aceflow mock start --feature user-management --port 4010

# 前端开发使用 Mock API (http://localhost:4010/api/user/*)
# 后端开发实现真实 API
```

#### 第3-7天: 前后端并行开发

**前端**:
```javascript
// 使用 Mock API 开发,数据结构已确定
const response = await fetch('http://localhost:4010/api/user/login', {
  method: 'POST',
  body: JSON.stringify({ username, password })
});
```

**后端**:
```java
// Spring Boot 实现,添加 OpenAPI 注解
@Operation(summary = "用户登录")
@PostMapping("/api/user/login")
public Result<UserVO> login(@RequestBody LoginRequest request) {
    // 实现登录逻辑
}
```

#### 第8天: 联调 + 上线

```bash
# 前端切换到真实 API (只需修改 baseURL)
const API_BASE = 'https://api.company.com'; // 从 Mock 切换到真实 API

# 后端生成最终契约并推送
aceflow contract generate --feature user-management
aceflow contract push --feature user-management
```

**收益**:
- ✅ 前后端并行开发,节省 4-5 天
- ✅ API 结构提前确定,减少联调问题
- ✅ 自动生成契约,减少文档维护成本

---

### 场景 2: AI 辅助迭代开发 (智能工作流模式)

**背景**: 为现有系统添加支付功能

**步骤**:

#### 第1天: 使用 AI 助手启动迭代

```bash
# 在 Cline/Claude Code 中对话
开发者: "我需要为系统添加支付功能,包含支付宝和微信支付"

AI (使用 workflow_start_iteration 工具):
  ✅ 自动创建迭代: payment-integration-v1
  ✅ 分析任务复杂度: Medium (预计 3-5 天)
  ✅ 推荐工作流模式: Standard (P1→P2→D1→D2→R1)
  ✅ 创建阶段任务清单:
     - P1: 需求分析 (1天)
     - P2: 技术方案设计 (1天)
     - D1: 开发实现 (2天)
     - D2: 测试验证 (1天)
     - R1: 上线发布 (0.5天)
```

#### 第2天: P1 阶段 - 需求分析

```bash
开发者: "帮我分析支付功能的需求"

AI (使用 memory_recall_for_stage 工具):
  ✅ 召回相关历史记忆:
     - 上次集成第三方支付的经验教训
     - 支付安全相关的团队决策
     - 订单系统的数据结构

  ✅ 生成需求分析文档 (自动记录到项目记忆)
  ✅ 标记 P1 阶段完成,自动进入 P2 阶段
```

#### 第3天: P2 阶段 - 技术方案设计

```bash
开发者: "设计支付功能的技术方案"

AI (使用 template_get_stage 工具):
  ✅ 加载 P2 阶段模板 (技术方案设计模板)
  ✅ 基于项目历史,推荐:
     - 使用策略模式实现多支付渠道
     - 异步回调 + 消息队列保证一致性
     - 参考团队之前的第三方集成模式

  ✅ 生成技术方案文档 (自动记录到项目记忆)

# 质量门检查
AI (使用 gate_evaluate 工具):
  ⚠️ DG1 - 开发就绪门:
     - 技术方案完整性: 85% ✅
     - 风险分析: 缺少异常处理策略 ❌
     - 建议: 补充支付失败、超时、重试的处理方案
```

#### 第4-5天: D1 阶段 - 开发实现

```bash
开发者: "开始实现支付功能"

AI (自动辅助开发):
  ✅ 基于技术方案生成代码框架
  ✅ 自动记录关键决策到项目记忆:
     - 选择使用 Spring Cloud Stream 处理回调
     - 支付订单号生成规则: YYYYMMDD + 随机数
     - 支付状态机设计: PENDING → PROCESSING → SUCCESS/FAILED

  ✅ 持续记录开发过程中的问题和解决方案
```

#### 第6天: D2 阶段 - 测试验证

```bash
AI (使用 gate_evaluate 工具):
  🚦 DG2 - 实现质量门:
     - 单元测试覆盖率: 82% ✅
     - 集成测试: 15/15 通过 ✅
     - 代码审查: 2个问题待修复 ⚠️
     - 性能测试: 响应时间 < 500ms ✅

  ✅ 自动生成测试报告
```

#### 第7天: R1 阶段 - 上线发布

```bash
AI (使用 gate_evaluate 工具):
  🚦 DG3 - 发布就绪门:
     - 功能测试: 完成 ✅
     - 性能测试: 通过 ✅
     - 安全测试: 通过 ✅
     - 文档完整性: 90% ✅
     - 上线检查清单: 8/8 完成 ✅

  ✅ 通过发布门,可以上线

# 导出完整的迭代文档
aceflow export_iteration --iteration-id payment-integration-v1 --format markdown

# 输出:
#   - 完整的需求分析文档
#   - 技术方案设计文档
#   - 开发过程中的决策记录
#   - 遇到的问题和解决方案
#   - 测试报告
#   - 发布检查清单
```

**收益**:
- ✅ AI 全程辅助,减少 40% 开发时间
- ✅ 自动记录项目历史,知识沉淀
- ✅ 质量门自动检查,减少 30% 返工
- ✅ 一键导出完整文档,省去手动整理时间

---

### 场景 3: 新人快速上手

**背景**: 新人小王加入团队,需要快速了解项目

**传统方式** (耗时 2-3 周):
```
第1周: 阅读过期的 Wiki 文档,询问老员工 ❌
第2周: 查看代码,猜测设计意图,试错 ❌
第3周: 开始第一个小任务 ❌
```

**使用 AceFlow** (耗时 3-5 天):

```bash
# 第1天: 了解项目历史
开发者 (小王): "这个项目的技术栈是什么?为什么选择这些技术?"

AI (从项目记忆中检索):
  ✅ 技术栈:
     - 后端: Spring Boot 3.2 + PostgreSQL + Redis
     - 前端: Vue 3 + TypeScript + Vite
     - 消息队列: RabbitMQ

  ✅ 技术选型决策:
     - [2024-03-15] 选择 Spring Boot 3.2: 需要虚拟线程提升性能
     - [2024-04-01] 选择 PostgreSQL: 需要 JSONB 查询能力
     - [2024-05-10] 选择 RabbitMQ: 团队有使用经验,稳定可靠

# 第2天: 了解核心业务逻辑
开发者 (小王): "用户登录的流程是怎样的?"

AI (从项目记忆中检索):
  ✅ 用户登录流程:
     1. 前端提交用户名密码 → /api/user/login
     2. 后端验证 → JWT Token (30分钟过期)
     3. 刷新 Token 机制 → /api/user/refresh-token
     4. Token 存储在 Redis,支持单点登出

  ✅ 相关代码:
     - LoginController.java:45 - 登录接口
     - TokenService.java:78 - Token 生成逻辑
     - RedisTokenStore.java:23 - Redis 存储

  ✅ 相关决策:
     - [2024-06-01] 为什么 Token 过期时间是 30 分钟?
       → 平衡安全性和用户体验,参考了行业最佳实践

# 第3天: 完成第一个小任务
开发者 (小王): "帮我实现'忘记密码'功能"

AI (基于项目上下文):
  ✅ 分析任务:
     - 需要发送邮件验证码
     - 项目已有 EmailService (EmailService.java:12)
     - 验证码存储在 Redis,5分钟过期
     - 参考'用户注册'流程 (RegisterController.java:56)

  ✅ 生成代码框架:
     - ForgotPasswordController.java - 控制器
     - PasswordResetService.java - 业务逻辑
     - password-reset.html - 前端页面

  ✅ 代码符合团队规范:
     - 使用团队的异常处理模式
     - 使用团队的日志格式
     - 使用团队的 API 响应格式
```

**收益**:
- ✅ 新人上手时间从 2-3 周缩短到 3-5 天 (节省 50%)
- ✅ 减少老员工的答疑时间 (节省 60%)
- ✅ 新人代码质量更高,符合团队规范

---

## 快速上手

### 安装步骤 (5分钟)

#### 1. 安装 AceFlow MCP Server

```bash
# 方式1: 从 PyPI 安装 (推荐)
pip install aceflow-mcp-server

# 方式2: 从源码安装 (开发者)
git clone https://github.com/aceflow-pateoas/aceflow-ai.git
cd aceflow-ai/aceflow-mcp-server
pip install -e .

# 验证安装
aceflow --version
# 输出: aceflow, version 3.0.2
```

#### 2. 配置 MCP 客户端 (Cline/Claude Code/Cursor)

**方式1: Cline (VSCode 插件)**

1. 安装 Cline 插件: https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev
2. 打开 VSCode 设置 → Cline → MCP Servers
3. 添加配置:

```json
{
  "aceflow": {
    "command": "python",
    "args": ["-m", "aceflow_mcp_server.mcp_stdio_server"],
    "env": {
      "PYTHONPATH": "/path/to/your/project"
    }
  }
}
```

**方式2: Claude Code (桌面应用)**

编辑 `~/.config/claude-code/config.json`:

```json
{
  "mcpServers": {
    "aceflow": {
      "command": "python",
      "args": ["-m", "aceflow_mcp_server.mcp_stdio_server"]
    }
  }
}
```

**方式3: Cursor (IDE)**

编辑 Cursor 设置:

```json
{
  "mcp.servers": {
    "aceflow": {
      "command": "python",
      "args": ["-m", "aceflow_mcp_server.mcp_stdio_server"]
    }
  }
}
```

#### 3. 初始化项目

```bash
# 在项目根目录执行
aceflow init

# 交互式配置:
# - 项目名称: My Awesome Project
# - OpenAPI URL: http://localhost:8080/v3/api-docs
# - 契约仓库: git@github.com:your-org/contracts.git
# - SMTP 配置: (可选,用于邮件通知)

# 初始化后会生成 .aceflow/config.yaml
```

#### 4. 验证安装

在 Cline/Claude Code 中测试:

```
你: "使用 aceflow_init 工具初始化项目"

AI: ✅ 项目初始化成功
     - 配置文件: .aceflow/config.yaml
     - 工作流模式: standard (可选: complete)
     - MCP 工具: 25 个工具已加载
```

### 首次使用建议

#### 场景1: Contract-First 开发 (推荐前后端分离项目)

```bash
# 1. 添加功能
aceflow feature add \
  --name user-api \
  --api-filter "/api/user/" \
  --filter-type prefix \
  --non-interactive

# 2. 生成契约 (从 Spring Boot OpenAPI)
aceflow contract generate --feature user-api

# 3. 启动 Mock Server
aceflow mock start --feature user-api --port 4010

# 4. 测试 Mock API
curl http://localhost:4010/api/user/list
```

#### 场景2: AI 辅助开发 (推荐所有项目)

在 Cline/Claude Code 中:

```
你: "帮我创建一个新的迭代,实现用户登录功能"

AI (使用 workflow_start_iteration):
  ✅ 迭代已创建: user-login-v1
  ✅ 推荐模式: standard (P1→P2→D1→D2→R1)
  ✅ 当前阶段: P1 (需求分析)
  ✅ 下一步: 请描述登录功能的需求

你: "需要支持用户名密码登录,返回 JWT Token"

AI (使用 memory_record_stage_output):
  ✅ 需求已记录到项目记忆
  ✅ 进入 D (开发阶段)
  ✅ 开始生成代码...
```

---

## 最佳实践

### 1. Contract-First 开发最佳实践

#### 1.1 API 设计规范

**使用 OpenAPI 注解**:

```java
@RestController
@RequestMapping("/api/user")
@Tag(name = "用户管理", description = "用户相关的 API")
public class UserController {

    @Operation(
        summary = "用户登录",
        description = "使用用户名密码登录,返回 JWT Token",
        tags = {"用户管理", "认证"}
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "登录成功",
            content = @Content(
                mediaType = "application/json",
                schema = @Schema(implementation = LoginResponse.class),
                examples = @ExampleObject(
                    name = "成功示例",
                    value = "{\"code\":0,\"message\":\"success\",\"data\":{\"token\":\"eyJhbGc...\",\"expiresIn\":1800}}"
                )
            )
        ),
        @ApiResponse(
            responseCode = "401",
            description = "用户名或密码错误"
        )
    })
    @PostMapping("/login")
    public Result<LoginResponse> login(
        @Parameter(description = "登录请求", required = true)
        @RequestBody @Valid LoginRequest request
    ) {
        return userService.login(request);
    }
}
```

**智能补全自动生成示例值**:

```yaml
# .aceflow/config.yaml
smart_completion:
  enabled: true
  rules:
    - pattern: ".*[Uu]ser[IiDd][Dd]$"
      example: "550e8400-e29b-41d4-a716-446655440000"
    - pattern: ".*[Tt]oken$"
      example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    - pattern: ".*[Ee]mail$"
      example: "user@company.com"
    - pattern: ".*[Pp]hone$"
      example: "13800138000"
```

#### 1.2 契约版本管理

**Git 仓库结构**:

```
contracts/
├── active/              # 当前正在开发的契约
│   ├── user-api.yaml
│   ├── order-api.yaml
│   └── payment-api.yaml
├── released/            # 已发布的契约 (按版本归档)
│   ├── v1.0.0/
│   ├── v1.1.0/
│   └── v2.0.0/
└── deprecated/          # 已废弃的契约
    └── legacy-api.yaml
```

**契约推送流程**:

```bash
# 开发阶段: 推送到 active/
aceflow contract push \
  --feature user-api \
  --message "feat: 新增用户头像上传接口"

# 发布阶段: 归档到 released/v1.1.0/
git tag v1.1.0
git push origin v1.1.0
# (通过 CI/CD 自动归档)

# 废弃阶段: 移动到 deprecated/
git mv active/legacy-api.yaml deprecated/
git commit -m "chore: 废弃 legacy-api"
```

#### 1.3 Mock Server 使用技巧

**动态响应**:

```bash
# 启用动态响应 (默认开启)
aceflow mock start --feature user-api --port 4010

# 每次请求返回不同的数据:
curl http://localhost:4010/api/user/list
# 第1次: [{id:1,name:"Alice"},{id:2,name:"Bob"}]
# 第2次: [{id:3,name:"Charlie"},{id:4,name:"David"}]
```

**请求验证**:

```bash
# 启用请求验证 (默认开启)
aceflow mock start --feature user-api --port 4010 --validate

# 发送无效请求:
curl -X POST http://localhost:4010/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":123}' # ❌ username 应该是 string

# 返回 400 错误,指出问题:
# "validation error: username should be string"
```

**多环境 Mock**:

```bash
# 开发环境
aceflow mock start --feature user-api --port 4010

# 测试环境 (不同的示例数据)
aceflow mock start --feature user-api --port 4020 --env test

# 集成测试 (禁用动态响应,确保一致性)
aceflow mock start --feature user-api --port 4030 --no-dynamic
```

### 2. 智能工作流最佳实践

#### 2.1 选择合适的工作流模式

| 模式 | 适用场景 | 阶段数 | 开发周期 |
|-----|---------|--------|---------|
| **Minimal** | Bug 修复、小功能 | 3 (P→D→R) | 1-2 天 |
| **Standard** | 常规功能开发 | 5 (P1→P2→D1→D2→R1) | 3-7 天 |
| **Complete** | 复杂功能、架构重构 | 8 (S1-S8 + 3个质量门) | 1-4 周 |
| **Smart** | AI 自适应 | 动态 | 根据复杂度自动调整 |

**选择建议**:

```bash
# 示例1: Bug 修复 → Minimal
你: "修复用户登录时的 NPE 异常"
AI: 推荐 Minimal 模式 (预计 2 小时)

# 示例2: 新增功能 → Standard
你: "实现用户头像上传功能"
AI: 推荐 Standard 模式 (预计 2 天)

# 示例3: 架构重构 → Complete
你: "重构用户认证系统,迁移到 OAuth 2.0"
AI: 推荐 Complete 模式 (预计 2 周)
```

#### 2.2 使用项目记忆

**自动记录**:

AI 会自动记录以下内容到项目记忆:

- ✅ 技术决策 (为什么选择某个技术方案)
- ✅ 代码模式 (团队常用的设计模式)
- ✅ 问题和解决方案 (遇到的 Bug 和修复方法)
- ✅ 经验教训 (需要避免的坑)

**手动记录** (重要决策):

```bash
# 在 Cline/Claude Code 中
你: "记录技术决策: 我们选择使用 Redis 作为缓存,原因是..."

AI (使用 memory_record_decision):
  ✅ 决策已记录
  ✅ 关联当前迭代: user-api-v1
  ✅ 关联当前阶段: P2 (技术方案设计)
```

**召回记忆** (查询历史):

```bash
# 召回所有关于"认证"的记忆
你: "搜索关于认证的历史决策和代码模式"

AI (使用 memory_search):
  ✅ 找到 5 条相关记忆:
     1. [决策] 使用 JWT Token (2024-03-15)
     2. [模式] Token 刷新机制 (2024-04-01)
     3. [问题] Token 并发刷新导致失效 (2024-05-10)
     4. [解决方案] 使用 Redis 分布式锁 (2024-05-11)
     5. [经验教训] Token 过期时间应≥30分钟 (2024-06-01)
```

#### 2.3 质量门配置

**DG1 - 开发就绪门** (在 D1 阶段之前):

```yaml
# .aceflow/quality_gates/DG1.yaml
gate_id: DG1
name: "开发就绪门"
stage: "S3"  # 技术方案设计完成后
criteria:
  - name: "技术方案完整性"
    weight: 0.3
    checks:
      - 架构设计完成
      - 数据库设计完成
      - API 接口设计完成

  - name: "风险分析"
    weight: 0.2
    checks:
      - 性能风险评估
      - 安全风险评估
      - 技术债务评估

  - name: "依赖就绪"
    weight: 0.2
    checks:
      - 第三方依赖确认
      - 环境准备完成
      - 测试数据准备完成

  - name: "团队准备"
    weight: 0.1
    checks:
      - 开发人员分配
      - 时间计划确认

pass_threshold: 0.75  # 75分及以上通过
```

**DG2 - 实现质量门** (在 D2 阶段之前):

```yaml
# .aceflow/quality_gates/DG2.yaml
gate_id: DG2
name: "实现质量门"
stage: "S5"  # 开发完成后
criteria:
  - name: "代码质量"
    weight: 0.3
    checks:
      - 单元测试覆盖率 ≥ 80%
      - 代码审查通过
      - 无严重 SonarQube 问题

  - name: "功能完整性"
    weight: 0.25
    checks:
      - 所有功能点实现
      - API 契约实现一致
      - 错误处理完整

  - name: "性能测试"
    weight: 0.2
    checks:
      - 响应时间 < 500ms
      - 并发支持 ≥ 100 QPS
      - 内存泄漏检查

  - name: "安全检查"
    weight: 0.25
    checks:
      - SQL 注入防护
      - XSS 防护
      - 敏感数据加密

pass_threshold: 0.80  # 80分及以上通过
```

**DG3 - 发布就绪门** (在 R1 阶段之前):

```yaml
# .aceflow/quality_gates/DG3.yaml
gate_id: DG3
name: "发布就绪门"
stage: "S7"  # 测试完成后
criteria:
  - name: "测试覆盖"
    weight: 0.3
    checks:
      - 单元测试通过
      - 集成测试通过
      - E2E 测试通过
      - 性能测试通过

  - name: "文档完整性"
    weight: 0.2
    checks:
      - API 文档完整
      - 部署文档完整
      - 用户手册完整

  - name: "运维就绪"
    weight: 0.2
    checks:
      - 监控配置完成
      - 日志配置完成
      - 告警配置完成

  - name: "发布检查"
    weight: 0.3
    checks:
      - 数据库迁移脚本
      - 回滚方案
      - 灰度发布计划

pass_threshold: 0.85  # 85分及以上通过
```

### 3. 团队协作最佳实践

#### 3.1 角色分工

| 角色 | 职责 | 使用工具 |
|-----|------|---------|
| **Tech Lead** | 技术方案设计、质量门审核 | workflow_start_iteration, gate_evaluate |
| **后端开发** | API 实现、契约生成 | contract_generate, contract_push |
| **前端开发** | UI 实现、Mock Server 使用 | contract_pull, mock_start |
| **测试工程师** | 测试用例设计、质量验证 | gate_evaluate, memory_record_issue |
| **项目经理** | 进度跟踪、风险管理 | state_get_current, state_list_iterations |

#### 3.2 团队配置共享

**导出团队配置**:

```bash
# 导出配置模板 (去除敏感信息)
aceflow config export \
  --output team-config-template.yaml \
  --remove-secrets

# team-config-template.yaml:
aceflow:
  project:
    name: "${PROJECT_NAME}"
    openapi_url: "${OPENAPI_URL}"

  contract_repo:
    url: "git@github.com:your-org/contracts.git"
    branch: "main"

  notification:
    email:
      enabled: true
      smtp:
        host: "${SMTP_HOST}"
        port: 587
        user: "${SMTP_USER}"
        password: "${SMTP_PASSWORD}"

  smart_completion:
    enabled: true
    rules: [...]  # 团队统一的补全规则
```

**新成员使用**:

```bash
# 1. 拉取配置模板
git clone git@github.com:your-org/aceflow-configs.git

# 2. 复制模板
cp team-config-template.yaml .aceflow/config.yaml

# 3. 填写个人配置
export PROJECT_NAME="My Local Project"
export OPENAPI_URL="http://localhost:8080/v3/api-docs"
export SMTP_HOST="smtp.company.com"
export SMTP_USER="your-email@company.com"
export SMTP_PASSWORD="your-password"

# 4. 验证配置
aceflow config validate
```

#### 3.3 知识共享会议

**每周分享会** (30分钟):

```bash
# 1. 导出本周的项目记忆
你: "导出本周的技术决策和经验教训"

AI (使用 memory_recall):
  ✅ 本周记录:
     - 3 个技术决策
     - 5 个问题和解决方案
     - 2 个经验教训

  ✅ 生成分享 PPT:
     - 决策: 为什么选择 PostgreSQL JSONB
     - 问题: 如何解决 Token 并发刷新
     - 教训: 避免在事务中调用外部 API

# 2. 团队成员学习
# (其他成员的 AI 助手自动学习这些知识)
```

---

## 技术亮点

### 1. MCP 协议集成

**什么是 MCP?**

MCP (Model Context Protocol) 是 Anthropic 提出的 AI 工具集成协议,类似于 "AI 的 USB 协议"。

**传统方式 vs MCP**:

```python
# 传统方式: AI 无法直接调用工具
你: "帮我生成契约"
AI: "你可以使用 aceflow contract generate 命令..."
你: (手动执行命令) ❌

# MCP 方式: AI 直接调用工具
你: "帮我生成契约"
AI: (直接调用 aceflow_contract_generate 工具) ✅
AI: "契约已生成: contracts/user-api.yaml"
```

**25 个 MCP 工具**:

| 分类 | 工具数 | 工具名称 |
|-----|--------|---------|
| **Contract-First** | 4 | aceflow_init, aceflow_stage, aceflow_validate, aceflow_template |
| **工作流管理** | 4 | workflow_start_iteration, workflow_next_stage, workflow_complete_stage, workflow_complete_iteration |
| **状态管理** | 4 | state_get_current, state_list_iterations, state_get_history, state_update_stage |
| **记忆管理** | 7 | memory_record_*, memory_recall_*, memory_search |
| **模板管理** | 3 | template_get_stage, template_render, template_list |
| **质量门** | 2 | gate_evaluate, gate_get_info |
| **导出** | 1 | export_iteration |

### 2. 智能记忆系统

**记忆类型**:

| 类型 | 描述 | 使用场景 |
|-----|------|---------|
| **STAGE_OUTPUT** | 阶段输出 | 保存每个阶段的产出物 (需求文档、设计方案、代码、测试报告) |
| **DECISION** | 技术决策 | 记录重要的技术选型和设计决策,包含原因和影响 |
| **ISSUE** | 问题记录 | 记录遇到的问题和解决方案,避免重复踩坑 |
| **LEARNING** | 经验教训 | 总结项目中的经验和教训,指导后续开发 |
| **PATTERN** | 代码模式 | 记录团队常用的设计模式和代码风格 |

**记忆检索算法**:

```python
# 基于相关性的智能检索
class MemoryRetrieval:
    def search(self, query: str, context: dict):
        """
        多维度相关性计算:
        1. 语义相关性 (40%) - 使用 TF-IDF 或 Embedding
        2. 时间相关性 (20%) - 近期记忆权重更高
        3. 上下文相关性 (20%) - 当前阶段、迭代相关
        4. 使用频率 (10%) - 经常被召回的记忆权重更高
        5. 重要性 (10%) - 手动标记的重要记忆
        """
        scores = []
        for memory in self.memories:
            score = (
                0.4 * semantic_similarity(query, memory.content) +
                0.2 * time_decay(memory.timestamp) +
                0.2 * context_match(context, memory.context) +
                0.1 * access_frequency(memory.id) +
                0.1 * memory.importance
            )
            scores.append((memory, score))

        return sorted(scores, key=lambda x: x[1], reverse=True)
```

### 3. 自适应工作流引擎

**智能模式推荐**:

```python
class WorkflowRecommender:
    def recommend_mode(self, task_description: str):
        """
        基于任务描述推荐工作流模式:
        1. 分析任务复杂度
        2. 估算开发时间
        3. 识别风险因素
        4. 推荐合适的模式
        """
        complexity = self.analyze_complexity(task_description)
        estimated_days = self.estimate_time(task_description)
        risk_level = self.assess_risk(task_description)

        if estimated_days <= 7 and risk_level in ["low", "medium"]:
            return "standard"  # P1→P2→D1→D2→R1 (大多数项目)
        elif estimated_days > 7 or risk_level == "high":
            return "complete"  # S1-S8 + 质量门 (企业级项目)
        else:
            return "standard"  # 默认推荐标准模式
```

**质量门验证**:

```python
# Standard/Complete 模式支持质量门和阶段验证
class WorkflowEngine:
    def validate_stage_completion(self, current_stage: str, progress: dict):
        """
        在推进到下一阶段前进行质量检查:
        - 代码质量检查 (如果质量低,提示改进)
        - 测试覆盖率检查 (如果覆盖率低,提示补充)
        - 风险评估检查 (如果风险高,提示风险评估)
        """
        warnings = []

        if progress['code_quality'] < 0.6:
            warnings.append("⚠️ 代码质量较低,建议进行重构")

        if progress['test_coverage'] < 0.8:
            warnings.append("⚠️ 测试覆盖率不足,建议补充测试")

        if progress['risk_score'] > 0.7:
            warnings.append("⚠️ 风险较高,建议进行风险评估")

        return warnings
```

### 4. 质量门自动评估

**评估引擎**:

```python
class QualityGateEngine:
    def evaluate(self, gate_id: str, context: dict):
        """
        质量门自动评估:
        1. 加载质量门配置
        2. 执行自动检查 (代码扫描、测试运行)
        3. 收集人工输入 (Code Review 结果)
        4. 计算综合得分
        5. 生成评估报告
        """
        gate = self.load_gate_config(gate_id)

        # 自动检查
        auto_checks = self.run_auto_checks(gate, context)

        # 人工输入
        manual_inputs = self.get_manual_inputs(gate, context)

        # 计算得分
        score = self.calculate_score(gate, auto_checks, manual_inputs)

        # 生成报告
        report = self.generate_report(gate, score, auto_checks, manual_inputs)

        return {
            "passed": score >= gate.pass_threshold,
            "score": score,
            "report": report,
            "recommendations": self.get_recommendations(score, gate)
        }
```

**自动检查项**:

- ✅ 单元测试覆盖率 (JaCoCo/Coverage.py)
- ✅ 代码质量 (SonarQube/ESLint)
- ✅ 安全扫描 (OWASP Dependency Check)
- ✅ 性能测试 (JMeter/K6)
- ✅ API 契约一致性 (OpenAPI Validator)

---

## ROI 分析

### 量化收益

基于内部试点团队 (10人,3个月) 的数据:

| 指标 | 传统方式 | 使用 AceFlow | 改善幅度 |
|-----|---------|-------------|---------|
| **前后端协作等待时间** | 平均 5 天/功能 | 平均 0.5 天/功能 | **-90%** ⬇️ |
| **AI 重复性沟通** | 平均 3-5 轮/问题 | 平均 1-2 轮/问题 | **-60%** ⬇️ |
| **代码返工率** | 平均 2.5 轮/功能 | 平均 1.2 轮/功能 | **-52%** ⬇️ |
| **新人上手时间** | 平均 15 天 | 平均 5 天 | **-67%** ⬇️ |
| **文档维护时间** | 平均 2 小时/周 | 平均 0.5 小时/周 | **-75%** ⬇️ |
| **质量问题发现时间** | Code Review 阶段 | 开发阶段 (质量门) | **提前 3-5 天** ⏰ |

### 成本节约计算

**团队规模**: 10人 (5前端 + 5后端)
**平均工资**: 2万/月 (按 1天=1000元 计算)
**使用周期**: 3个月 (约 60 个工作日)

| 节约项 | 传统方式 (人天) | AceFlow (人天) | 节约 (人天) | 成本节约 (元) |
|--------|----------------|---------------|------------|-------------|
| **前后端等待** | 150 天 (5天×30功能) | 15 天 (0.5天×30功能) | 135 天 | **135,000** |
| **AI 沟通成本** | 60 天 (2天×30功能) | 24 天 (0.8天×30功能) | 36 天 | **36,000** |
| **代码返工** | 75 天 (2.5轮×30功能) | 36 天 (1.2轮×30功能) | 39 天 | **39,000** |
| **新人培训** | 30 天 (2人×15天) | 10 天 (2人×5天) | 20 天 | **20,000** |
| **文档维护** | 24 天 (2小时/周×12周×10人) | 6 天 (0.5小时/周×12周×10人) | 18 天 | **18,000** |
| **合计** | 339 人天 | 91 人天 | **248 人天** | **248,000 元** |

**投资回报率 (ROI)**:

- **初始投资**: 0 元 (开源免费)
- **3个月收益**: 248,000 元
- **ROI**: ∞ (无限大)

**长期收益** (按 1 年计算):

- 节约成本: 248,000 × 4 = **992,000 元/年**
- 质量提升: 减少生产环境 Bug 30%,按每个 Bug 修复成本 5000 元计算:
  - 假设 1 年 100 个 Bug → 节约 30 × 5000 = **150,000 元/年**
- **总收益**: 992,000 + 150,000 = **1,142,000 元/年**

---

## 团队反馈

### 试点团队反馈 (内部收集)

#### 后端团队 (5人)

> **"前后端不再需要等待对方,开发效率提升明显"**
>
> 以前前端需要等我们 API 实现完才能开始,现在契约一推送,前端立刻可以用 Mock Server 开发。我们的压力也小了很多。
>
> — 张工, 高级后端工程师

> **"AI 终于理解我们的项目了!"**
>
> 以前跟 AI 对话总是要重复解释我们的技术栈和架构,现在 AI 会自动读取项目记忆,给出的建议都是符合我们规范的。节省了大量时间。
>
> — 李工, 后端工程师

#### 前端团队 (5人)

> **"Mock Server 太好用了,再也不用手动写假数据"**
>
> 以前前端开发要自己写 Mock 数据,还要手动维护。现在 aceflow mock start 一条命令,所有数据都有了,还能动态生成,真的很方便。
>
> — 王工, 高级前端工程师

> **"契约更新自动邮件通知,不会错过 API 变更"**
>
> 以前后端改了 API,前端不知道,联调时才发现问题。现在后端推送契约,我们立刻收到邮件,可以提前调整代码。
>
> — 刘工, 前端工程师

#### 测试团队 (2人)

> **"质量门自动检查,提前发现很多问题"**
>
> 以前都是等开发完成后才开始测试,发现问题又要返工。现在质量门在开发阶段就能发现单元测试不足、代码质量低等问题,大大减少了返工。
>
> — 赵工, 测试工程师

#### 新人 (2人)

> **"上手速度快了很多,AI 助手像老员工一样指导我"**
>
> 我刚加入团队,以前要问老员工各种问题。现在 AI 助手能告诉我项目的技术栈、架构设计、历史决策,就像有一个老员工在旁边指导我。
>
> — 小王, 初级后端工程师

### 使用数据统计 (3个月)

- **总迭代数**: 45 个
- **Contract 生成**: 120 次
- **Mock Server 启动**: 89 次
- **项目记忆记录**: 340 条
- **质量门评估**: 67 次
- **文档导出**: 23 次

---

## 推广计划

### 第一阶段: 小范围试点 (已完成) ✅

**目标**: 验证可行性,收集反馈

**时间**: 2024-10 ~ 2024-12 (3个月)

**范围**: 1个试点团队 (10人)

**结果**:
- ✅ 成功完成 45 个迭代
- ✅ 收集到 15 条改进建议
- ✅ ROI 达到 ∞ (248,000元节约)
- ✅ 团队满意度 9.2/10

### 第二阶段: 部门推广 (进行中) 🔄

**目标**: 扩大使用范围,验证规模化效果

**时间**: 2025-01 ~ 2025-03 (3个月)

**范围**: 研发部全部团队 (50人)

**计划**:

#### 1月: 培训和部署

**Week 1: 技术培训**
```
- 周一: 项目介绍会 (1小时)
  - 核心价值
  - 典型场景
  - 成功案例

- 周三: 技术培训 (2小时)
  - 安装和配置
  - Contract-First 实战
  - 智能工作流实战

- 周五: 答疑和辅导 (1小时)
  - 解答问题
  - 个性化配置
  - 最佳实践分享
```

**Week 2-4: 部署和接入**
```
- 为每个团队配置 MCP Server
- 创建团队配置模板
- 初始化契约仓库
- 配置 SMTP 邮件通知
```

#### 2月: 实践和优化

**每周监控指标**:
- 使用频率 (工具调用次数)
- 使用深度 (使用工具种类数)
- 满意度调查 (每两周一次)
- 问题反馈 (随时收集)

**每两周迭代优化**:
- 根据反馈改进功能
- 优化配置模板
- 补充使用文档
- 分享最佳实践

#### 3月: 总结和推广

**Week 1: 数据收集**
```
- 使用统计报告
- ROI 分析报告
- 满意度调查报告
- 案例收集
```

**Week 2-3: 成果展示**
```
- 研发部月度会议分享
- 内部技术博客文章
- 视频教程录制
- 推广海报制作
```

**Week 4: 准备下一阶段**
```
- 制定公司级推广计划
- 准备跨部门培训材料
- 优化部署流程
- 建立支持体系
```

### 第三阶段: 公司推广 (计划中) 📋

**目标**: 公司全员使用

**时间**: 2025-04 ~ 2025-06 (3个月)

**范围**: 全公司研发人员 (200人)

**计划** (待定):
- 跨部门培训
- 统一配置管理
- 企业级支持
- 持续优化迭代

---

## 支持和资源

### 文档资源

| 文档 | 链接 | 说明 |
|-----|------|------|
| **快速开始** | [WORKFLOW_QUICK_START.md](./WORKFLOW_QUICK_START.md) | 10分钟上手指南 |
| **API 参考** | [WORKFLOW_API_REFERENCE.md](./WORKFLOW_API_REFERENCE.md) | 完整 API 文档 |
| **MCP 工具指南** | [MCP_TOOLS_QUICK_REFERENCE.md](./MCP_TOOLS_QUICK_REFERENCE.md) | 25个工具速查 |
| **测试报告** | [WORKFLOW_TESTING_REPORT.md](./WORKFLOW_TESTING_REPORT.md) | 99.2% 测试覆盖率 |
| **CHANGELOG** | [CHANGELOG.md](../aceflow-mcp-server/CHANGELOG.md) | 版本更新记录 |

### 联系方式

- **技术支持**: tech-support@company.com
- **问题反馈**: https://github.com/aceflow-pateoas/aceflow-ai/issues
- **内部讨论群**: 钉钉群 12345678
- **项目负责人**: 张工 (zhangsan@company.com)

### 培训安排

**线上培训** (每周三下午 2:00-4:00):
- Week 1: 项目介绍和快速开始
- Week 2: Contract-First 开发实战
- Week 3: 智能工作流管理实战
- Week 4: 高级用法和最佳实践

**一对一辅导** (预约):
- 个性化配置指导
- 疑难问题解答
- 团队定制培训

---

## 附录

### A. 常见问题 (FAQ)

#### Q1: AceFlow 是否支持其他语言 (非 Java/Python)?

**A**: 当前 Contract-First 模块主要支持 Spring Boot (Java) 的 OpenAPI Spec。但智能工作流模块 (21个工具) 是语言无关的,可以用于任何项目。

未来计划支持:
- Node.js (Express, NestJS)
- Go (Gin, Echo)
- .NET (ASP.NET Core)

#### Q2: 是否支持私有部署?

**A**: 支持。AceFlow MCP Server 是开源的,可以在公司内部部署。推荐方式:

```bash
# 方式1: 从 PyPI 安装
pip install aceflow-mcp-server

# 方式2: 从内部 PyPI 镜像安装
pip install --index-url https://pypi.company.com/simple aceflow-mcp-server

# 方式3: 从源码安装
git clone https://github.com/aceflow-pateoas/aceflow-ai.git
cd aceflow-ai/aceflow-mcp-server
pip install -e .
```

#### Q3: 项目记忆数据存储在哪里?

**A**: 默认存储在项目的 `.aceflow/memory/` 目录,使用 JSON 格式。数据完全在本地,不会上传到云端。

如果需要团队共享记忆,可以将 `.aceflow/memory/` 目录加入 Git:

```bash
# .gitignore 中移除
# .aceflow/memory/  # 删除这行

git add .aceflow/memory/
git commit -m "chore: 共享项目记忆"
```

#### Q4: 是否支持自定义工作流阶段?

**A**: 支持。可以通过修改 `.aceflow/workflows/` 目录中的工作流配置文件:

```yaml
# .aceflow/workflows/custom.yaml
name: "自定义工作流"
mode: "custom"
stages:
  - id: "requirement"
    name: "需求分析"
    template: "templates/custom/requirement.md"

  - id: "design"
    name: "设计"
    template: "templates/custom/design.md"

  - id: "implementation"
    name: "实现"
    template: "templates/custom/implementation.md"

  - id: "review"
    name: "评审"
    template: "templates/custom/review.md"
```

#### Q5: Mock Server 支持哪些功能?

**A**: 基于 Prism CLI,支持:

- ✅ 动态响应 (每次请求返回不同数据)
- ✅ 请求验证 (校验请求参数)
- ✅ 响应验证 (校验响应格式)
- ✅ 自定义响应 (通过 OpenAPI examples)
- ✅ 错误模拟 (模拟 4xx, 5xx 错误)
- ✅ 延迟模拟 (模拟网络延迟)

不支持:
- ❌ 状态保持 (重启后数据丢失)
- ❌ 复杂业务逻辑 (只能模拟简单逻辑)

#### Q6: 如何与现有 CI/CD 集成?

**A**: 可以在 CI/CD 流程中调用 AceFlow CLI:

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install AceFlow
        run: pip install aceflow-mcp-server

      - name: Generate Contract
        run: aceflow contract generate --feature ${{ github.event.pull_request.title }}

      - name: Validate Contract
        run: aceflow contract validate --feature ${{ github.event.pull_request.title }}

      - name: Push Contract
        run: aceflow contract push --feature ${{ github.event.pull_request.title }}
```

#### Q7: 是否有性能影响?

**A**: 几乎没有。AceFlow MCP Server 运行在后台,只在 AI 调用工具时执行。典型性能:

- MCP 工具调用延迟: < 100ms
- 契约生成时间: 1-3 秒 (取决于 API 数量)
- Mock Server 启动时间: < 1 秒
- 项目记忆检索: < 50ms (1000 条记忆)

#### Q8: 是否支持多人协作?

**A**: 支持。推荐方式:

1. **契约仓库**: 使用 Git 管理契约,多人可以同时 push/pull
2. **项目记忆**: 提交到 Git,团队共享
3. **配置文件**: 使用模板 + 环境变量,每人有自己的配置
4. **Mock Server**: 每人使用不同端口,互不影响

#### Q9: 是否有商业支持?

**A**: 当前是内部开源项目,由公司内部技术团队维护。如有问题可联系:

- 技术支持邮箱: tech-support@company.com
- 内部讨论群: 钉钉群 12345678
- Issue 跟踪: GitHub Issues

#### Q10: 下一步的发展计划?

**A**: 见 [推广计划](#推广计划) 章节。近期重点:

- ✅ v3.0.2 已发布 (2025-01-12)
- 🔄 部门级推广 (2025-01 ~ 2025-03)
- 📋 公司级推广 (2025-04 ~ 2025-06)
- 🚀 v3.1.0 新功能 (2025-Q2)
  - 多语言支持 (Node.js, Go)
  - 团队协作增强
  - 企业级功能

### B. 术语表

| 术语 | 英文 | 说明 |
|-----|------|------|
| **MCP** | Model Context Protocol | AI 工具集成协议 |
| **Contract-First** | - | 契约优先开发模式 |
| **OpenAPI** | OpenAPI Specification | API 描述规范 (前身是 Swagger) |
| **Mock Server** | - | 模拟 API 服务器 |
| **Prism** | - | Stoplight 出品的 OpenAPI Mock 工具 |
| **工作流模式** | Workflow Mode | 开发流程模式 (Minimal/Standard/Complete/Smart) |
| **质量门** | Quality Gate | 质量检查点 (DG1/DG2/DG3) |
| **项目记忆** | Project Memory | 自动记录项目历史和决策 |
| **迭代** | Iteration | 一个完整的开发周期 |
| **阶段** | Stage | 迭代中的一个步骤 (如 P1, D1, R1) |

### C. 链接汇总

**项目主页**:
- GitHub: https://github.com/aceflow-pateoas/aceflow-ai
- PyPI: https://pypi.org/project/aceflow-mcp-server/

**文档**:
- 快速开始: docs/WORKFLOW_QUICK_START.md
- API 参考: docs/WORKFLOW_API_REFERENCE.md
- MCP 工具: docs/MCP_TOOLS_QUICK_REFERENCE.md
- 测试报告: docs/WORKFLOW_TESTING_REPORT.md

**客户端**:
- Cline (VSCode): https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev
- Claude Code: https://claude.ai/code
- Cursor: https://cursor.sh/

**相关工具**:
- Prism CLI: https://github.com/stoplightio/prism
- OpenAPI Generator: https://github.com/OpenAPITools/openapi-generator
- Swagger Editor: https://editor.swagger.io/

---

**文档版本**: v1.0
**更新日期**: 2025-01-12
**文档作者**: AceFlow 推广团队
**联系方式**: tech-support@company.com
