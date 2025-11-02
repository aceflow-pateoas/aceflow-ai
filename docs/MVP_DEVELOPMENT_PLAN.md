# AceFlow 前后端协作 MVP 开发计划

**文档版本**: 1.0
**创建日期**: 2025-01-02
**状态**: ✅ 已确认，待开发
**优先级**: P0 (最高优先级)

---

## 🎯 MVP 目标

**核心目标**: 完整跑通一个需求的前后端协作流程

**成功标准**:
- ✅ 后端能从 Spring Boot 应用生成 OpenAPI 契约
- ✅ 后端能推送契约到 Git 仓库
- ✅ 前端能拉取契约
- ✅ 前端能启动 Mock Server 进行开发
- ✅ 能发送邮件通知前端
- ✅ 完成一个真实需求的验证

**不包含** (后续阶段):
- ❌ 契约变更检测
- ❌ 版本管理
- ❌ 钉钉通知
- ❌ 契约测试
- ❌ TypeScript 类型生成

---

## 🛠️ 技术选型（已确认）

### 1. Mock Server
**方案**: 基于开源成熟方案实现

**推荐**: [Prism](https://github.com/stoplightio/prism)
- ✅ 成熟稳定，Star 4k+
- ✅ 完整支持 OpenAPI 3.0
- ✅ 自动基于 example 生成 Mock 数据
- ✅ 命令行工具，易于集成

**安装**:
```bash
npm install -g @stoplight/prism-cli
# 或
yarn global add @stoplight/prism-cli
```

**使用**:
```bash
prism mock openapi.yaml
# 启动在 http://localhost:4010
```

**集成到 AceFlow**:
```bash
# AceFlow 封装 Prism
$ aceflow mock start --contract user-export
  → 内部调用: prism mock .aceflow/contracts/user-export.yaml -p 4010
```

---

### 2. OpenAPI 解析
**方案**: 直接调用 `/v3/api-docs`

**实现**:
```python
import requests
import yaml

def fetch_openapi(url):
    """从 Spring Boot 应用获取 OpenAPI"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 使用
openapi_json = fetch_openapi("http://localhost:8080/v3/api-docs")

# 转换为 YAML
with open("openapi.yaml", "w") as f:
    yaml.dump(openapi_json, f, allow_unicode=True)
```

**接口过滤**:
```python
def filter_paths(openapi_spec, path_filters):
    """根据配置过滤接口"""
    filtered_paths = {}

    for path, methods in openapi_spec.get("paths", {}).items():
        # 精确匹配
        if path in path_filters.get("exact", []):
            filtered_paths[path] = methods

        # 前缀匹配
        for prefix in path_filters.get("prefix", []):
            if path.startswith(prefix):
                filtered_paths[path] = methods
                break

    openapi_spec["paths"] = filtered_paths
    return openapi_spec
```

---

### 3. Git 操作
**方案**: 直接基于本地环境的 git 命令

**实现**:
```python
import subprocess

def git_clone(repo_url, target_dir):
    """克隆仓库"""
    subprocess.run(["git", "clone", repo_url, target_dir], check=True)

def git_commit_and_push(repo_dir, file_path, message):
    """提交并推送"""
    subprocess.run(["git", "-C", repo_dir, "add", file_path], check=True)
    subprocess.run(["git", "-C", repo_dir, "commit", "-m", message], check=True)
    subprocess.run(["git", "-C", repo_dir, "push"], check=True)

def git_pull(repo_dir):
    """拉取最新"""
    subprocess.run(["git", "-C", repo_dir, "pull"], check=True)
```

**契约仓库管理**:
```python
import os
from pathlib import Path

class ContractRepo:
    def __init__(self, config):
        self.repo_url = config["contract_repo"]["url"]
        self.local_path = Path.home() / ".aceflow" / "contract-repo"

    def ensure_cloned(self):
        """确保仓库已克隆"""
        if not self.local_path.exists():
            git_clone(self.repo_url, str(self.local_path))
        else:
            git_pull(str(self.local_path))

    def push_contract(self, feature_name, openapi_yaml, message):
        """推送契约"""
        self.ensure_cloned()

        # 写入文件
        contract_path = self.local_path / "contracts/active" / feature_name / "openapi.yaml"
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract_path.write_text(openapi_yaml)

        # 提交推送
        git_commit_and_push(
            str(self.local_path),
            str(contract_path.relative_to(self.local_path)),
            message
        )

        return str(contract_path)
```

---

### 4. 通知机制
**方案**: 邮件 SMTP（优先），保留钉钉设计（后续）

**邮件实现**:
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailNotifier:
    def __init__(self, smtp_config):
        self.smtp_host = smtp_config["host"]
        self.smtp_port = smtp_config["port"]
        self.smtp_user = smtp_config["user"]
        self.smtp_password = smtp_config["password"]
        self.from_email = smtp_config["from"]

    def send_contract_notification(self, to_email, feature_info, contract_url):
        """发送契约通知"""
        subject = f"【接口契约】{feature_info['name']} - 已更新 v{feature_info['version']}"

        body = self._build_email_body(feature_info, contract_url)

        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)

    def _build_email_body(self, feature_info, contract_url):
        """构建邮件正文"""
        return f"""
{feature_info['frontend_name']}，你好！

后端已完成接口设计，请查看并确认：

需求信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  需求名称：{feature_info['name']}
  需求编号：{feature_info.get('jira', 'N/A')}
  后端负责人：{feature_info['backend_name']} ({feature_info['backend_email']})
  前端负责人：{feature_info['frontend_name']} ({feature_info['frontend_email']})
  契约版本：v{feature_info['version']}

接口摘要：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{feature_info['summary']}

快速开始：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  $ cd frontend-repo/
  $ aceflow contract pull --feature {feature_info['feature_id']}
  $ aceflow mock start --contract {feature_info['feature_id']}

查看详情：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  完整契约文件：{contract_url}

如何反馈：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. 如无问题，请在群里回复 "✅"
  2. 如有建议，请联系后端或在 Git 上留言

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
此邮件由 AceFlow 自动发送
"""
```

**配置示例**:
```yaml
# .aceflow/config.yaml
notification:
  email:
    enabled: true
    smtp:
      host: "smtp.company.com"
      port: 587
      user: "aceflow@company.com"
      password: "${SMTP_PASSWORD}"  # 从环境变量读取
      from: "aceflow@company.com"

  dingtalk:
    enabled: false  # MVP 阶段不实现
    webhook: ""
```

---

## 📦 MVP 功能清单

### 后端功能

#### 1. 初始化配置
```bash
$ aceflow init

交互式问题：
  项目名称: 用户管理系统后端
  OpenAPI 地址: http://localhost:8080/v3/api-docs
  契约仓库地址: git@company.com:api-contracts.git
  SMTP 配置:
    - Host: smtp.company.com
    - Port: 587
    - User: aceflow@company.com
    - Password: ******

生成配置文件：.aceflow/config.yaml
```

**实现要点**:
- 交互式问答（使用 Click 或 Inquirer）
- 生成 YAML 配置文件
- 密码等敏感信息提示使用环境变量

---

#### 2. 添加需求配置
```bash
$ aceflow feature add

交互式问题：
  需求名称: 用户数据导出
  需求编号（可选）: PROJ-1234
  前端负责人邮箱: li@company.com

  接口识别方式:
    1. 精确路径
    2. 路径前缀
    3. 手动输入多个
  选择: 2

  路径前缀: /api/reports/

更新配置文件：.aceflow/config.yaml
```

**实现要点**:
- 更新 YAML 配置
- 支持多种过滤方式
- 验证输入格式

---

#### 3. 生成契约
```bash
$ aceflow contract generate --feature user-export

执行流程：
1. 读取配置：.aceflow/config.yaml
2. 获取 OpenAPI：http://localhost:8080/v3/api-docs
3. 过滤接口：根据配置的路径前缀
4. 简单补全：日期、UUID（MVP 阶段简单实现）
5. 保存契约：.aceflow/contracts/user-export.yaml
6. 显示摘要

输出示例：
  ✅ 契约生成成功: user-export v1.0

  包含接口: 3个
  • POST /api/reports/export - 导出用户数据
  • GET /api/reports/list - 获取报表列表
  • DELETE /api/reports/{id} - 删除报表

  保存位置: .aceflow/contracts/user-export.yaml

  下一步:
  $ aceflow contract push --feature user-export
```

**实现要点**:
- HTTP 请求获取 OpenAPI JSON
- 根据配置过滤 paths
- 简单的智能补全（正则匹配字段名）
- YAML 格式保存
- 彩色输出（使用 Rich 库）

---

#### 4. 推送契约
```bash
$ aceflow contract push --feature user-export --notify li@company.com

执行流程：
1. 读取契约：.aceflow/contracts/user-export.yaml
2. 克隆/更新契约仓库
3. 写入文件到：contracts/active/user-export/openapi.yaml
4. Git commit + push
5. 发送邮件通知
6. 显示结果

输出示例：
  ✅ 契约已推送

  Git Commit: https://git.company.com/.../commit/abc123
  查看契约: https://git.company.com/.../openapi.yaml

  ✅ 邮件通知已发送给: li@company.com
```

**实现要点**:
- 契约仓库管理（克隆、拉取、推送）
- Git 操作（subprocess）
- 邮件发送（SMTP）
- 错误处理

---

### 前端功能

#### 5. 拉取契约
```bash
$ aceflow contract pull --feature user-export

执行流程：
1. 读取配置（如果有本地配置）
2. 克隆/更新契约仓库
3. 复制契约文件到本地：.aceflow/contracts/user-export.yaml
4. 显示契约摘要

输出示例：
  ✅ 契约已下载: user-export v1.0

  📋 接口摘要:
  POST /api/reports/export - 导出用户数据
  GET /api/reports/list - 获取报表列表
  DELETE /api/reports/{id} - 删除报表

  保存位置: .aceflow/contracts/user-export.yaml

  下一步:
  $ aceflow mock start --contract user-export
```

**实现要点**:
- 契约仓库管理（复用后端的逻辑）
- 解析 OpenAPI，提取接口摘要
- 本地存储契约文件

---

#### 6. 启动 Mock Server
```bash
$ aceflow mock start --contract user-export

执行流程：
1. 检查 Prism 是否安装
2. 读取契约文件：.aceflow/contracts/user-export.yaml
3. 启动 Prism: prism mock openapi.yaml -p 4010
4. 后台运行并保存 PID
5. 显示启动信息

输出示例：
  ✅ Mock Server 已启动

  契约: user-export v1.0
  地址: http://localhost:4010
  进程: PID 12345

  接口列表:
  • POST http://localhost:4010/api/reports/export
  • GET http://localhost:4010/api/reports/list
  • DELETE http://localhost:4010/api/reports/{id}

  测试命令:
  curl http://localhost:4010/api/reports/export

  停止 Mock Server:
  $ aceflow mock stop --contract user-export
```

**实现要点**:
- 检查 Prism 安装（npm list -g @stoplight/prism-cli）
- 后台启动 Prism（subprocess）
- 保存 PID 到 .aceflow/mock-servers.json
- 端口管理（默认 4010，支持 --port）

---

#### 7. 停止 Mock Server
```bash
$ aceflow mock stop --contract user-export

执行流程：
1. 读取 PID：.aceflow/mock-servers.json
2. 杀死进程：kill PID
3. 清理记录

输出示例：
  ✅ Mock Server 已停止 (PID 12345)
```

**实现要点**:
- 读取 PID 文件
- 杀死进程（subprocess kill 或 psutil）
- 清理状态文件

---

#### 8. 查看运行的 Mock Server
```bash
$ aceflow mock list

输出示例：
  运行中的 Mock Server:

  user-export v1.0
    地址: http://localhost:4010
    进程: PID 12345
    启动时间: 2025-01-02 10:30:00

  report-dashboard v2.0
    地址: http://localhost:4011
    进程: PID 12346
    启动时间: 2025-01-02 11:00:00
```

**实现要点**:
- 读取状态文件：.aceflow/mock-servers.json
- 检查进程是否存活
- 格式化输出

---

## 📁 项目结构

```
aceflow-ai/
├── aceflow-mcp-server/
│   └── aceflow_mcp_server/
│       ├── contract/              # 新增：契约管理模块
│       │   ├── __init__.py
│       │   ├── generator.py       # 契约生成
│       │   ├── repo.py            # Git 仓库管理
│       │   ├── filter.py          # 接口过滤
│       │   └── completion.py      # 智能补全
│       │
│       ├── mock/                  # 新增：Mock Server 管理
│       │   ├── __init__.py
│       │   ├── prism.py           # Prism 集成
│       │   └── manager.py         # Mock Server 管理
│       │
│       ├── notification/          # 新增：通知模块
│       │   ├── __init__.py
│       │   ├── email.py           # 邮件通知
│       │   └── template.py        # 通知模板
│       │
│       ├── cli/                   # CLI 命令
│       │   ├── __init__.py
│       │   ├── init.py            # aceflow init
│       │   ├── feature.py         # aceflow feature
│       │   ├── contract.py        # aceflow contract
│       │   └── mock.py            # aceflow mock
│       │
│       └── config.py              # 配置管理
│
├── .aceflow/                      # 本地工作空间
│   ├── config.yaml                # 项目配置
│   ├── contracts/                 # 本地契约文件
│   │   └── user-export.yaml
│   ├── contract-repo/             # 克隆的契约仓库
│   └── mock-servers.json          # Mock Server 状态
│
└── docs/
    ├── FRONTEND_BACKEND_COLLABORATION_DISCUSSION.md
    ├── FRONTEND_BACKEND_COLLABORATION_FINAL_DESIGN.md
    └── MVP_DEVELOPMENT_PLAN.md    # 本文档
```

---

## 🔧 技术实现细节

### 1. 配置文件格式

```yaml
# .aceflow/config.yaml

aceflow:
  project:
    name: "用户管理系统后端"
    openapi_url: "http://localhost:8080/v3/api-docs"

  features:
    user-export:
      name: "用户数据导出"
      jira: "PROJ-1234"
      frontend: "li@company.com"
      include:
        - path: "/api/reports/export"
        - path_prefix: "/api/reports/"

  contract_repo:
    url: "git@company.com:api-contracts.git"
    branch: "main"
    base_path: "contracts/active"

  notification:
    email:
      enabled: true
      smtp:
        host: "smtp.company.com"
        port: 587
        user: "aceflow@company.com"
        password: "${SMTP_PASSWORD}"
        from: "aceflow@company.com"

  # MVP 阶段的简单智能补全
  smart_completion:
    enabled: true
    rules:
      # 日期格式
      - pattern: ".*[Dd]ate$"
        example: "2025-01-01"

      # UUID
      - pattern: ".*[Uu]uid$"
        example: "550e8400-e29b-41d4-a716-446655440000"

      # ID
      - pattern: ".*[Ii]d$"
        example: 12345
```

---

### 2. Mock Server 状态文件

```json
// .aceflow/mock-servers.json
{
  "servers": [
    {
      "contract": "user-export",
      "version": "1.0",
      "port": 4010,
      "pid": 12345,
      "started_at": "2025-01-02T10:30:00Z",
      "contract_file": ".aceflow/contracts/user-export.yaml"
    },
    {
      "contract": "report-dashboard",
      "version": "2.0",
      "port": 4011,
      "pid": 12346,
      "started_at": "2025-01-02T11:00:00Z",
      "contract_file": ".aceflow/contracts/report-dashboard.yaml"
    }
  ]
}
```

---

### 3. 简单智能补全实现

```python
import re

class SimpleCompletion:
    """MVP 阶段的简单智能补全"""

    RULES = {
        r'.*[Dd]ate$': "2025-01-01",
        r'.*[Tt]ime$': 1735689600,
        r'.*[Uu]uid$': "550e8400-e29b-41d4-a716-446655440000",
        r'.*[Ii]d$': 12345,
        r'.*[Ee]mail$': "user@example.com",
        r'.*[Pp]hone$': "13800138000",
    }

    def complete_example(self, field_name, field_type, current_example):
        """补全示例值"""
        if current_example is not None:
            return current_example

        # 根据字段名匹配规则
        for pattern, example in self.RULES.items():
            if re.match(pattern, field_name):
                return example

        # 根据类型返回默认值
        if field_type == "integer":
            return 1
        elif field_type == "string":
            return "示例文本"
        elif field_type == "boolean":
            return True

        return None
```

---

## 🧪 测试计划

### 单元测试

```python
# tests/test_contract_generator.py

def test_fetch_openapi():
    """测试获取 OpenAPI"""
    generator = ContractGenerator("http://localhost:8080/v3/api-docs")
    openapi = generator.fetch()
    assert "openapi" in openapi
    assert "paths" in openapi

def test_filter_paths():
    """测试接口过滤"""
    openapi = {...}
    filters = {
        "exact": ["/api/reports/export"],
        "prefix": ["/api/reports/"]
    }
    filtered = filter_paths(openapi, filters)
    assert "/api/reports/export" in filtered["paths"]
    assert "/api/users/list" not in filtered["paths"]

def test_simple_completion():
    """测试简单补全"""
    completion = SimpleCompletion()
    result = completion.complete_example("startDate", "string", None)
    assert result == "2025-01-01"
```

---

### 集成测试

准备测试环境：
1. 启动一个简单的 Spring Boot 应用（提供 OpenAPI）
2. 创建临时的契约仓库
3. 配置测试用的 SMTP（或使用 Mock SMTP 服务器）

测试完整流程：
```bash
# 1. 初始化
$ aceflow init --test-mode

# 2. 添加需求
$ aceflow feature add --name test-feature --frontend test@example.com

# 3. 生成契约
$ aceflow contract generate --feature test-feature

# 4. 推送契约
$ aceflow contract push --feature test-feature --notify test@example.com

# 5. 拉取契约
$ aceflow contract pull --feature test-feature

# 6. 启动 Mock
$ aceflow mock start --contract test-feature

# 7. 测试 Mock
$ curl http://localhost:4010/api/test

# 8. 停止 Mock
$ aceflow mock stop --contract test-feature
```

---

## 📅 开发计划

### Week 1: 基础设施

**Day 1-2**: 项目搭建
- ✅ 创建模块结构
- ✅ 配置管理模块
- ✅ CLI 框架搭建（Click）

**Day 3-4**: 契约生成
- ✅ OpenAPI 获取
- ✅ 接口过滤
- ✅ 简单智能补全

**Day 5**: Git 操作
- ✅ 契约仓库管理
- ✅ 克隆/拉取/推送

---

### Week 2: 核心功能

**Day 1-2**: 后端命令
- ✅ aceflow init
- ✅ aceflow feature add
- ✅ aceflow contract generate
- ✅ aceflow contract push

**Day 3-4**: 前端命令
- ✅ aceflow contract pull
- ✅ aceflow mock start/stop/list

**Day 5**: 通知功能
- ✅ 邮件通知
- ✅ 通知模板

---

### Week 3: 测试与优化

**Day 1-2**: 单元测试
- ✅ 测试覆盖率 > 80%

**Day 3-4**: 集成测试
- ✅ 完整流程测试
- ✅ 边界情况测试

**Day 5**: 文档与优化
- ✅ 使用文档
- ✅ 错误处理优化
- ✅ 日志输出优化

---

### Week 4: 试点验证

**Day 1-2**: 内部试点
- ✅ 选择一个真实需求
- ✅ 后端使用 AceFlow
- ✅ 收集反馈

**Day 3-4**: 迭代优化
- ✅ 根据反馈调整
- ✅ 修复 Bug
- ✅ 改进用户体验

**Day 5**: 准备推广
- ✅ 编写使用指南
- ✅ 录制演示视频
- ✅ 准备培训材料

---

## 📊 成功指标

### MVP 验证标准

1. **功能完整性**
   - ✅ 所有 8 个核心命令都能正常工作
   - ✅ 能完成完整的工作流程

2. **易用性**
   - ✅ 新用户 < 5 分钟完成初始化
   - ✅ 命令输出清晰易懂
   - ✅ 错误提示有帮助

3. **稳定性**
   - ✅ 单元测试覆盖率 > 80%
   - ✅ 集成测试通过
   - ✅ 试点期间无重大 Bug

4. **实用性**
   - ✅ 至少 1 个真实需求成功使用
   - ✅ 后端和前端都认为有价值
   - ✅ 解决了实际痛点

---

## 📝 依赖清单

### Python 依赖

```toml
# pyproject.toml

[project]
dependencies = [
    "click>=8.0",           # CLI 框架
    "rich>=13.0",           # 终端输出美化
    "pyyaml>=6.0",          # YAML 解析
    "requests>=2.28",       # HTTP 请求
    "pydantic>=2.0",        # 数据验证
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "isort>=5.0",
    "mypy>=1.0",
]
```

---

### 外部工具依赖

1. **Prism** (Mock Server)
   ```bash
   npm install -g @stoplight/prism-cli
   ```

2. **Git** (已有)
   ```bash
   git --version  # 需要 >= 2.0
   ```

---

## 🚨 风险与应对

### 风险 1: Prism 安装问题

**风险**: 前端开发者可能没有 Node.js 环境

**应对**:
- 在 `aceflow mock start` 时检测 Prism 是否安装
- 如果未安装，提供清晰的安装指引
- 考虑提供备选方案（如 Python 实现的简单 Mock Server）

---

### 风险 2: Git 权限问题

**风险**: 开发者可能没有契约仓库的写权限

**应对**:
- 在 `aceflow init` 时测试 Git 权限
- 提供清晰的权限申请指引
- 支持通过 SSH Key 或 Personal Access Token

---

### 风险 3: SMTP 配置复杂

**风险**: 公司 SMTP 服务器可能有复杂的认证要求

**应对**:
- 提供详细的 SMTP 配置文档
- 支持常见的 SMTP 服务（Gmail, QQ Mail, 公司邮箱）
- 提供测试命令验证 SMTP 配置

---

### 风险 4: Spring Boot 版本兼容性

**风险**: 不同版本的 Spring Boot 可能 OpenAPI 端点不同

**应对**:
- 支持配置 OpenAPI 端点 URL
- 文档中说明不同版本的配置方式
- 自动检测 `/v3/api-docs` 或 `/v2/api-docs`

---

## 📖 使用文档框架

### 快速开始

```markdown
# AceFlow 快速开始

## 安装

```bash
pip install aceflow-mcp-server
```

## 初始化（后端）

```bash
cd your-backend-project/
aceflow init
```

## 生成并推送契约（后端）

```bash
# 添加需求配置
aceflow feature add

# 启动 Spring Boot 应用
mvn spring-boot:run

# 生成契约
aceflow contract generate --feature your-feature

# 推送契约
aceflow contract push --feature your-feature --notify frontend@example.com
```

## 使用 Mock Server（前端）

```bash
cd your-frontend-project/

# 拉取契约
aceflow contract pull --feature your-feature

# 启动 Mock Server
aceflow mock start --contract your-feature

# 前端开发...

# 停止 Mock Server
aceflow mock stop --contract your-feature
```
```

---

## ✅ MVP 完成标准

MVP 开发完成的标准：

- ✅ 所有 8 个核心命令实现并测试通过
- ✅ 单元测试覆盖率 > 80%
- ✅ 集成测试通过
- ✅ 至少 1 个真实需求验证成功
- ✅ 基础使用文档完成
- ✅ 后端和前端开发者都能独立使用

---

**文档结束**

*MVP 开发计划已制定，可以开始实施。优先级 P0，建议 4 周内完成。*
