# AceFlow - OpenAPI Contract Management CLI

> 轻量级的前后端协作契约管理工具，基于 OpenAPI 规范的 Contract-First 开发流程

[![Test Coverage](https://img.shields.io/badge/tests-57%2F57%20passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 🎯 核心特性

- **📄 契约生成** - 从 Spring Boot OpenAPI Spec 生成过滤后的契约文件
- **🔄 Git 集成** - 自动推送/拉取契约到 Git 仓库
- **🤖 智能补全** - 基于规则自动添加 OpenAPI 示例值
- **🎭 Mock Server** - 基于 Prism 的 Mock API 服务器管理
- **📧 邮件通知** - 契约更新自动通知开发团队
- **⚙️ 配置管理** - 简单的 YAML 配置文件管理

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/aceflow-pateoas/aceflow-ai.git
cd aceflow-ai/aceflow-mcp-server

# 安装依赖
pip install -e .

# 安装 Prism CLI (用于 Mock Server)
npm install -g @stoplight/prism-cli
```

### 初始化项目

```bash
# 交互式初始化配置
aceflow init

# 非交互式初始化
aceflow init \
  --project-name "My API Project" \
  --openapi-url "http://localhost:8080/v3/api-docs" \
  --repo-url "git@github.com:your-org/contracts.git" \
  --non-interactive
```

### 基本工作流

#### 1. 后端开发者：生成并推送契约

```bash
# 添加功能配置
aceflow feature add \
  --name user-management \
  --api-filter "/api/user/" \
  --filter-type prefix \
  --description "User management APIs" \
  --dev-team "frontend@example.com,backend@example.com" \
  --non-interactive

# 生成契约
aceflow contract generate --feature user-management

# 推送到 Git 仓库（自动发送邮件通知）
aceflow contract push --feature user-management
```

#### 2. 前端开发者：拉取契约并启动 Mock

```bash
# 拉取最新契约
aceflow contract pull --feature user-management

# 启动 Mock Server
aceflow mock start --feature user-management --port 4010

# 前端开发使用 Mock API
curl http://localhost:4010/api/user/login

# 停止 Mock Server
aceflow mock stop --port 4010
```

## 📚 命令参考

### 项目初始化

```bash
# 初始化配置文件
aceflow init [--non-interactive]

# 查看版本
aceflow --version
```

### Feature 管理

```bash
# 添加功能
aceflow feature add \
  --name <feature-name> \
  --api-filter <pattern> \
  --filter-type <exact|prefix|regex> \
  --description <desc> \
  --dev-team <emails>

# 列出所有功能
aceflow feature list

# 删除功能
aceflow feature remove --name <feature-name>
```

### 契约管理

```bash
# 生成契约
aceflow contract generate \
  --feature <name> \
  [--output <path>] \
  [--format json|yaml] \
  [--no-smart-completion]

# 推送契约到 Git
aceflow contract push \
  --feature <name> \
  [--message <msg>] \
  [--branch <branch>]

# 从 Git 拉取契约
aceflow contract pull \
  --feature <name> \
  [--branch <branch>] \
  [--output <dir>]

# 列出所有契约
aceflow contract list

# 查看契约详情
aceflow contract show <feature-name>
```

### Mock Server 管理

```bash
# 启动 Mock Server
aceflow mock start \
  --feature <name> \
  [--port 4010] \
  [--no-dynamic] \
  [--no-validate]

# 停止 Mock Server
aceflow mock stop --port <port>
# 或停止所有
aceflow mock stop --all

# 列出运行中的 Mock Server
aceflow mock list
```

## 🏗️ 架构设计

### 工作流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│              │     │              │     │              │
│  Spring Boot │────▶│   AceFlow    │────▶│     Git      │
│   OpenAPI    │     │   Contract   │     │  Repository  │
│              │     │  Generator   │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            │ Email Notify
                            ▼
                     ┌──────────────┐
                     │              │
                     │   Dev Team   │
                     │              │
                     └──────────────┘
                            │
                            │ Pull & Mock
                            ▼
                     ┌──────────────┐
                     │              │
                     │ Prism Mock   │
                     │   Server     │
                     │              │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │              │
                     │  Frontend    │
                     │  Development │
                     │              │
                     └──────────────┘
```

### 核心模块

```
aceflow_mcp_server/
├── cli/                    # CLI 命令
│   ├── main.py            # 主入口
│   ├── contract.py        # 契约管理命令
│   ├── feature.py         # Feature 管理命令
│   ├── init.py            # 初始化命令
│   └── mock.py            # Mock Server 命令
├── contract/              # 契约管理
│   ├── config.py          # 配置管理
│   ├── generator.py       # 契约生成
│   ├── filter.py          # 路径过滤
│   ├── completion.py      # 智能补全
│   └── repo.py            # Git 仓库操作
├── mock/                  # Mock Server
│   └── server.py          # Prism 管理
└── notification/          # 通知
    └── email.py           # 邮件通知
```

## 🔧 配置文件

### `.aceflow/config.yaml`

```yaml
aceflow:
  project:
    name: "My API Project"
    openapi_url: "http://localhost:8080/v3/api-docs"

  features:
    user-management:
      description: "User management APIs"
      api_filter:
        type: prefix
        pattern: "/api/user/"
      dev_team:
        - "frontend@example.com"
        - "backend@example.com"
      enabled: true

  contract_repo:
    url: "git@github.com:your-org/contracts.git"
    branch: "main"
    base_path: "contracts/active"

  notification:
    email:
      enabled: true
      smtp:
        host: "smtp.example.com"
        port: 587
        user: "noreply@example.com"
        password: "${SMTP_PASSWORD}"
        from: "AceFlow <aceflow@example.com>"

  smart_completion:
    enabled: true
    rules:
      - pattern: ".*[Uu]uid$"
        example: "550e8400-e29b-41d4-a716-446655440000"
      - pattern: ".*[Ee]mail$"
        example: "user@example.com"
      - pattern: ".*[Pp]hone$"
        example: "13800138000"
      - pattern: ".*[Dd]ate$"
        example: "2025-01-01"
      - pattern: ".*[IiDd][Dd]$"
        example: 12345
```

### 环境变量

```bash
# SMTP 密码（推荐使用环境变量）
export SMTP_PASSWORD="your-smtp-password"
```

## 🎨 使用场景

### 场景 1: 新功能开发

**后端开发者**:
```bash
# 1. 添加新功能
aceflow feature add --name payment --api-filter "/api/payment/" --filter-type prefix

# 2. 实现 Spring Boot API（添加 @Operation 注解）
# ... 编写代码 ...

# 3. 生成并推送契约
aceflow contract generate --feature payment
aceflow contract push --feature payment
```

**前端开发者**:
```bash
# 1. 拉取契约
aceflow contract pull --feature payment

# 2. 启动 Mock Server
aceflow mock start --feature payment --port 4020

# 3. 前端开发
# 使用 http://localhost:4020/api/payment/* 进行开发
```

### 场景 2: API 更新

**后端开发者**:
```bash
# 1. 修改 API
# ... 更新代码 ...

# 2. 重新生成并推送
aceflow contract generate --feature user-management
aceflow contract push --feature user-management --message "feat: add user avatar upload API"

# 前端团队会自动收到邮件通知
```

**前端开发者**:
```bash
# 1. 收到邮件通知后，拉取最新契约
aceflow contract pull --feature user-management

# 2. 重启 Mock Server
aceflow mock stop --port 4010
aceflow mock start --feature user-management --port 4010

# 3. 更新前端代码
```

## 📊 API 过滤器

### Exact (精确匹配)

```yaml
api_filter:
  type: exact
  pattern: "/api/user/login"
```

只匹配 `/api/user/login` 路径。

### Prefix (前缀匹配)

```yaml
api_filter:
  type: prefix
  pattern: "/api/user/"
```

匹配所有以 `/api/user/` 开头的路径，如：
- `/api/user/login`
- `/api/user/logout`
- `/api/user/{userId}`

### Regex (正则匹配)

```yaml
api_filter:
  type: regex
  pattern: "^/api/user/.*"
```

使用正则表达式匹配路径，支持复杂的匹配规则。

## 🤖 智能补全规则

智能补全会根据字段名自动添加示例值：

| 规则模式 | 匹配字段 | 示例值 |
|---------|---------|--------|
| `.*[Uu]uid$` | userId, orderUuid | `550e8400-e29b-41d4-a716-446655440000` |
| `.*[Ee]mail$` | email, userEmail | `user@example.com` |
| `.*[Pp]hone$` | phone, mobile | `13800138000` |
| `.*[Dd]ate$` | createDate, updateDate | `2025-01-01` |
| `.*[IiDd][Dd]$` | id, userId, ID | `12345` |

### 自定义规则

在配置文件中添加自己的规则：

```yaml
smart_completion:
  rules:
    - pattern: ".*[Aa]ddress$"
      example: "123 Main Street"
    - pattern: ".*[Cc]ity$"
      example: "New York"
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 带覆盖率
pytest tests/ --cov=aceflow_mcp_server --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 测试结果

- ✅ 单元测试: 51/51 (100%)
- ✅ 集成测试: 6/6 (100%)
- ✅ 总计: 57/57 (100%)

## 🛠️ 开发

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/aceflow-pateoas/aceflow-ai.git
cd aceflow-ai/aceflow-mcp-server

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"

# 安装 Prism CLI
npm install -g @stoplight/prism-cli
```

### 代码质量

```bash
# 代码格式化
black aceflow_mcp_server/

# Import 排序
isort aceflow_mcp_server/

# 代码风格检查
flake8 aceflow_mcp_server/

# 类型检查
mypy aceflow_mcp_server/
```

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feat/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feat/amazing-feature`)
5. 创建 Pull Request

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` 新功能
- `fix:` 错误修复
- `docs:` 文档更新
- `test:` 测试相关
- `refactor:` 代码重构
- `chore:` 其他更改

## 📝 待办事项

- [ ] 添加钉钉通知支持
- [ ] 实现契约 Diff 功能
- [ ] 支持 Mock Server 日志查看
- [ ] 添加配置文件模板
- [ ] Docker 镜像支持
- [ ] CI/CD 集成示例

## 🐛 问题反馈

如果遇到问题，请提交 [Issue](https://github.com/aceflow-pateoas/aceflow-ai/issues)。

提交 Issue 时请包含：
- 操作系统和 Python 版本
- 完整的错误消息
- 复现步骤
- 配置文件（去除敏感信息）

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Prism](https://github.com/stoplightio/prism) - Mock Server 引擎
- [Click](https://click.palletsprojects.com/) - CLI 框架
- [Rich](https://github.com/Textualize/rich) - 终端美化
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP 协议实现

---

**Made with ❤️ by AceFlow Team**
