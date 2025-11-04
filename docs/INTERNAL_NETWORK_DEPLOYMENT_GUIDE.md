# AceFlow 内网部署指南

> 在封闭网络环境中部署 AceFlow MCP Server，集成 VSCode + Cline + Qwen Code3

**版本**: v1.0.0
**日期**: 2025-01-04
**适用场景**: 企业内网、离线环境、自建大模型

---

## 📋 目录

1. [架构概览](#架构概览)
2. [前置条件](#前置条件)
3. [依赖准备](#依赖准备)
4. [AceFlow 部署](#aceflow-部署)
5. [Cline 集成配置](#cline-集成配置)
6. [内网 Git 仓库配置](#内网-git-仓库配置)
7. [Mock Server 部署](#mock-server-部署)
8. [测试验证](#测试验证)
9. [常见问题](#常见问题)

---

## 🏗️ 架构概览

### 标准架构（公网）

```
┌─────────────┐     MCP      ┌──────────────┐
│Claude Desktop│◄────────────►│AceFlow Server│
└─────────────┘              └──────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              ┌─────────┐     ┌─────────┐     ┌─────────┐
              │ GitHub  │     │ OpenAPI │     │  SMTP   │
              │Contracts│     │Backend  │     │ Server  │
              └─────────┘     └─────────┘     └─────────┘
```

### 内网架构（您的环境）

```
┌──────────────┐     MCP      ┌──────────────┐
│VSCode + Cline│◄────────────►│AceFlow Server│
│ + Qwen Code3 │              │  (内网部署)   │
└──────────────┘              └──────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              ┌─────────┐     ┌─────────┐     ┌─────────┐
              │  GitLab │     │ Spring  │     │内网SMTP │
              │ (内网)   │     │  Boot   │     │(可选)   │
              └─────────┘     └─────────┘     └─────────┘
```

**关键差异**:
- Claude Desktop → **VSCode + Cline**
- Claude API → **Qwen Code3 (内网大模型)**
- GitHub → **GitLab/Gitea (内网 Git)**
- 公网 SMTP → **内网邮件服务器**
- 公网 NPM → **内网 NPM 镜像**

---

## 🔧 前置条件

### 必需环境

✅ **Python 3.8+**
✅ **Node.js 16+** (用于 Prism Mock Server)
✅ **Git** (内网版本)
✅ **VSCode**
✅ **Qwen Code3 大模型** (已部署)

### 可选环境

- 内网 GitLab/Gitea
- 内网 SMTP 服务器
- 内网 NPM 镜像 (如 Verdaccio/Nexus)
- 内网 PyPI 镜像 (如 devpi)

---

## 📦 依赖准备

### Step 1: 准备 Python 依赖包（离线）

在**有公网的机器**上打包依赖：

```bash
# 1. 下载 AceFlow 及其依赖
mkdir aceflow-offline
cd aceflow-offline

pip download aceflow-mcp-server -d ./packages
pip download fastmcp -d ./packages
pip download click -d ./packages
pip download rich -d ./packages
pip download requests -d ./packages
pip download pyyaml -d ./packages
pip download gitpython -d ./packages
pip download psutil -d ./packages

# 2. 打包传输到内网
tar -czf aceflow-offline.tar.gz packages/
```

在**内网机器**上安装：

```bash
# 解压
tar -xzf aceflow-offline.tar.gz

# 离线安装
pip install --no-index --find-links=./packages aceflow-mcp-server
```

### Step 2: 准备 Node.js 依赖（Prism Mock Server）

在**有公网的机器**上：

```bash
# 1. 下载 Prism CLI
mkdir prism-offline
cd prism-offline

npm pack @stoplight/prism-cli
# 会生成: stoplight-prism-cli-5.x.x.tgz

# 2. 下载所有依赖
npm install --global-style --legacy-peer-deps @stoplight/prism-cli
tar -czf prism-offline.tar.gz node_modules/ stoplight-prism-cli-*.tgz
```

在**内网机器**上：

```bash
# 解压
tar -xzf prism-offline.tar.gz

# 全局安装
npm install -g ./stoplight-prism-cli-*.tgz --offline

# 验证
prism --version
```

### Step 3: 配置内网 NPM 镜像（推荐）

如果公司有内网 NPM 镜像服务器：

```bash
# 配置内网镜像
npm config set registry http://npm.company.internal:4873

# 安装 Prism
npm install -g @stoplight/prism-cli
```

### Step 4: 配置内网 PyPI 镜像（推荐）

如果公司有内网 PyPI 镜像：

```bash
# 配置 pip
cat > ~/.pip/pip.conf <<EOF
[global]
index-url = http://pypi.company.internal:8080/simple
trusted-host = pypi.company.internal
EOF

# 安装 AceFlow
pip install aceflow-mcp-server
```

---

## 🚀 AceFlow 部署

### Step 1: 克隆仓库到内网

```bash
# 方式 1: 如果内网有 Git 仓库
git clone http://gitlab.company.internal/devops/aceflow-ai.git

# 方式 2: 离线传输
# 在外网机器:
git clone https://github.com/your-org/aceflow-ai.git
tar -czf aceflow-ai.tar.gz aceflow-ai/

# 在内网机器:
tar -xzf aceflow-ai.tar.gz
cd aceflow-ai/aceflow-mcp-server
```

### Step 2: 安装 AceFlow

```bash
cd aceflow-ai/aceflow-mcp-server

# 开发模式安装
pip install -e .

# 或生产模式安装
pip install .
```

### Step 3: 验证安装

```bash
# 验证 CLI
aceflow --version

# 验证 MCP Server
python -m aceflow_mcp_server.server --help
```

---

## 🔌 Cline 集成配置

### Step 1: 安装 Cline 插件

在 VSCode 中：

1. 打开扩展商店
2. 搜索 "Cline"
3. 安装 Cline 插件

### Step 2: 配置 Cline 使用 Qwen Code3

在 VSCode 设置中配置 Cline：

**方式 A: 使用 Cline 配置文件**

创建 `.cline/config.json`:

```json
{
  "apiProvider": "openai-compatible",
  "apiKey": "your-qwen-api-key",
  "baseURL": "http://qwen.company.internal:8000/v1",
  "modelId": "qwen-coder-plus-latest"
}
```

**方式 B: 使用环境变量**

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export CLINE_API_PROVIDER="openai-compatible"
export CLINE_API_KEY="your-qwen-api-key"
export CLINE_BASE_URL="http://qwen.company.internal:8000/v1"
export CLINE_MODEL_ID="qwen-coder-plus-latest"
```

### Step 3: 配置 Cline MCP 支持

Cline 配置文件位置：
- **Linux/macOS**: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Windows**: `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

编辑 `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "aceflow": {
      "command": "python",
      "args": [
        "-m",
        "aceflow_mcp_server.server",
        "--transport",
        "stdio"
      ],
      "env": {
        "PYTHONPATH": "/path/to/aceflow-ai/aceflow-mcp-server"
      }
    }
  }
}
```

### Step 4: 配置 HTTP 模式（可选，推荐内网使用）

如果 stdio 模式有问题，可以使用 HTTP 模式：

**启动 AceFlow HTTP Server**:

```bash
# 方式 1: 命令行启动
python -m aceflow_mcp_server.server \
    --transport sse \
    --host 0.0.0.0 \
    --port 8000

# 方式 2: 使用 systemd (Linux)
cat > /etc/systemd/system/aceflow-mcp.service <<EOF
[Unit]
Description=AceFlow MCP Server
After=network.target

[Service]
Type=simple
User=developer
WorkingDirectory=/opt/aceflow
Environment="PYTHONPATH=/opt/aceflow-ai/aceflow-mcp-server"
ExecStart=/usr/bin/python3 -m aceflow_mcp_server.server --transport sse --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable aceflow-mcp
sudo systemctl start aceflow-mcp
```

**配置 Cline 使用 HTTP**:

```json
{
  "mcpServers": {
    "aceflow": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

### Step 5: 重启 VSCode

重启 VSCode 使配置生效。

---

## 🔐 内网 Git 仓库配置

### Step 1: 创建契约仓库

在 GitLab/Gitea 中创建仓库：

```bash
# 在 GitLab 中创建项目
# http://gitlab.company.internal/contracts/api-contracts

# 克隆到本地
git clone http://gitlab.company.internal/contracts/api-contracts.git
cd api-contracts

# 创建目录结构
mkdir -p contracts/{user-service,product-service,order-service}
touch README.md

git add .
git commit -m "Initial commit"
git push origin main
```

### Step 2: 配置 SSH Key（推荐）

```bash
# 生成 SSH Key
ssh-keygen -t ed25519 -C "developer@company.com"

# 添加到 GitLab
cat ~/.ssh/id_ed25519.pub
# 复制内容，添加到 GitLab Settings > SSH Keys

# 测试连接
ssh -T git@gitlab.company.internal
```

### Step 3: 配置 HTTPS 访问（备用）

如果使用 HTTPS + 用户名密码：

```bash
# 配置 Git credential helper
git config --global credential.helper store

# 首次推送时输入用户名密码
git push
# Username: your-username
# Password: your-password

# 后续自动使用保存的凭证
```

### Step 4: 配置 AceFlow 使用内网 Git

初始化项目时使用内网 Git URL：

```python
aceflow_init_project(
    project_name="Internal API",
    workflow_mode="contract_first",
    openapi_url="http://spring-boot.company.internal:8080/v3/api-docs",
    repo_url="http://gitlab.company.internal/contracts/api-contracts.git"
    # 或使用 SSH:
    # repo_url="git@gitlab.company.internal:contracts/api-contracts.git"
)
```

---

## 🎭 Mock Server 部署

### Step 1: 验证 Prism 安装

```bash
prism --version
# 应输出: 5.x.x
```

### Step 2: 启动 Mock Server

使用 AceFlow CLI：

```bash
# 启动 Mock Server
aceflow mock start --feature user-service --port 4010

# 查看运行状态
aceflow mock list

# 测试 Mock Server
curl http://localhost:4010/api/users
```

### Step 3: 配置多个 Mock Server（推荐）

为不同服务使用不同端口：

```bash
# 用户服务
aceflow mock start --feature user-service --port 4010

# 商品服务
aceflow mock start --feature product-service --port 4011

# 订单服务
aceflow mock start --feature order-service --port 4012

# 查看所有运行的 Mock Server
aceflow mock list
```

### Step 4: 配置反向代理（可选）

使用 Nginx 统一入口：

```nginx
# /etc/nginx/conf.d/mock-servers.conf

upstream user_mock {
    server localhost:4010;
}

upstream product_mock {
    server localhost:4011;
}

upstream order_mock {
    server localhost:4012;
}

server {
    listen 80;
    server_name mock.company.internal;

    location /api/users/ {
        proxy_pass http://user_mock;
        proxy_set_header Host $host;
    }

    location /api/products/ {
        proxy_pass http://product_mock;
        proxy_set_header Host $host;
    }

    location /api/orders/ {
        proxy_pass http://order_mock;
        proxy_set_header Host $host;
    }
}
```

前端配置：

```javascript
// 开发环境使用统一 Mock Server
const API_BASE_URL = process.env.NODE_ENV === 'development'
  ? 'http://mock.company.internal'
  : 'http://api.company.internal';
```

---

## ✅ 测试验证

### Step 1: 验证 AceFlow MCP Server

```bash
# 测试 stdio 模式
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
  python -m aceflow_mcp_server.server --transport stdio

# 应返回工具列表
```

### Step 2: 在 Cline 中测试

在 VSCode 中打开 Cline，输入：

```
帮我初始化一个新项目
```

Cline 应该能够调用 `aceflow_init_project` MCP 工具。

### Step 3: 完整工作流测试

在 Cline 中执行完整流程：

```
1. 初始化项目：使用 contract-first 模式
2. 定义一个用户登录功能
3. 设计登录 API
4. 推送契约到内网 Git
5. 启动 Mock Server
```

### Step 4: 验证 Mock Server

```bash
# 检查 Mock Server 是否运行
lsof -i :4010

# 测试 API
curl http://localhost:4010/api/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}'

# 应返回模拟的 JSON 响应
```

---

## 🐛 常见问题

### 问题 1: Cline 无法连接 AceFlow MCP Server

**症状**: Cline 报错 "Failed to connect to MCP server"

**原因**:
- Python 路径不正确
- PYTHONPATH 未设置
- 权限问题

**解决方案**:

```bash
# 1. 验证 Python 路径
which python3

# 2. 更新 Cline 配置使用完整路径
{
  "mcpServers": {
    "aceflow": {
      "command": "/usr/bin/python3",  # 使用完整路径
      "args": ["-m", "aceflow_mcp_server.server", "--transport", "stdio"],
      "env": {
        "PYTHONPATH": "/opt/aceflow-ai/aceflow-mcp-server"
      }
    }
  }
}

# 3. 检查权限
ls -la /opt/aceflow-ai/aceflow-mcp-server

# 4. 使用 HTTP 模式代替 stdio
# 启动 HTTP Server
python -m aceflow_mcp_server.server --transport sse --host 127.0.0.1 --port 8000

# 更新 Cline 配置
{
  "mcpServers": {
    "aceflow": {
      "url": "http://127.0.0.1:8000/sse",
      "transport": "sse"
    }
  }
}
```

### 问题 2: 无法推送契约到内网 Git

**症状**: `aceflow_contract_push` 报错 "Git push failed"

**原因**:
- Git 认证失败
- 网络不通
- 仓库权限问题

**解决方案**:

```bash
# 1. 测试 Git 连接
git ls-remote http://gitlab.company.internal/contracts/api-contracts.git

# 2. 配置 Git 认证
# 使用 SSH
ssh -T git@gitlab.company.internal

# 使用 HTTPS
git config --global credential.helper store
git clone http://gitlab.company.internal/contracts/api-contracts.git /tmp/test

# 3. 检查仓库权限
# 确保用户有 push 权限

# 4. 更新 .aceflow/config.yaml
contract:
  repo_url: "http://username:password@gitlab.company.internal/contracts/api-contracts.git"
  # 或使用 SSH
  # repo_url: "git@gitlab.company.internal:contracts/api-contracts.git"
```

### 问题 3: Qwen Code3 无法调用 MCP 工具

**症状**: Qwen 没有调用 MCP 工具，只是返回文本

**原因**:
- Cline 未正确配置 MCP
- Qwen Code3 需要特定的提示词格式
- MCP Server 未启动

**解决方案**:

```bash
# 1. 验证 MCP Server 状态
# stdio 模式
ps aux | grep aceflow_mcp_server

# HTTP 模式
curl http://localhost:8000/health

# 2. 在 Cline 中明确要求使用工具
"请使用 aceflow_init_project 工具初始化项目"

# 3. 检查 Cline 日志
# VSCode > Output > Cline
# 查看是否有 MCP 相关错误

# 4. 重启 VSCode
# 有时需要完全重启 VSCode 才能加载 MCP 配置
```

### 问题 4: Mock Server 启动失败

**症状**: `aceflow mock start` 报错

**原因**:
- Prism 未安装
- 端口被占用
- 契约文件不存在

**解决方案**:

```bash
# 1. 验证 Prism
prism --version
which prism

# 2. 检查端口
lsof -i :4010
# 如果被占用，杀掉进程或使用其他端口
aceflow mock start --feature user-service --port 4011

# 3. 检查契约文件
ls -la .aceflow/contracts/
# 确保契约文件存在

# 4. 手动启动 Prism 测试
prism mock .aceflow/contracts/user-service.json --port 4010
```

### 问题 5: 内网 SMTP 配置问题

**症状**: 邮件通知发送失败

**原因**:
- SMTP 服务器配置错误
- 认证失败
- 网络不通

**解决方案**:

```bash
# 1. 测试 SMTP 连接
telnet smtp.company.internal 25

# 2. 使用 Python 测试 SMTP
python3 <<EOF
import smtplib
from email.mime.text import MIMEText

msg = MIMEText('Test email')
msg['Subject'] = 'Test'
msg['From'] = 'aceflow@company.com'
msg['To'] = 'developer@company.com'

with smtplib.SMTP('smtp.company.internal', 25) as server:
    server.send_message(msg)
    print('Email sent successfully')
EOF

# 3. 更新 .aceflow/config.yaml
notification:
  email:
    enabled: true
    smtp_host: "smtp.company.internal"
    smtp_port: 25  # 内网通常不需要 TLS
    smtp_user: "aceflow@company.com"
    smtp_password: "password"
    from_address: "aceflow@company.com"

# 4. 如果 SMTP 不可用，禁用邮件通知
notification:
  email:
    enabled: false
```

---

## 📚 下一步

- [Quick Start Guide](QUICK_START_GUIDE.md) - 快速开始指南
- [MCP Contract Tools Guide](MCP_CONTRACT_TOOLS_GUIDE.md) - 工具详细参考
- [Workflow State Management Guide](WORKFLOW_STATE_MANAGEMENT_GUIDE.md) - 工作流管理

---

## 🆘 获取支持

### 内部支持渠道

1. **内部文档**: http://wiki.company.internal/aceflow
2. **问题追踪**: http://gitlab.company.internal/devops/aceflow-ai/issues
3. **内部论坛**: http://forum.company.internal/aceflow
4. **技术支持**: devops@company.com

### 日志收集

如果遇到问题，收集以下信息：

```bash
# 1. AceFlow 版本
aceflow --version

# 2. Python 环境
python --version
pip list | grep aceflow

# 3. Prism 版本
prism --version

# 4. 配置文件
cat .aceflow/config.yaml

# 5. 工作流状态
cat .aceflow/workflow.json

# 6. 日志文件
cat .aceflow/logs/aceflow.log

# 7. 系统信息
uname -a
cat /etc/os-release
```

---

**Created by**: AceFlow Team
**Last Updated**: 2025-01-04
**Version**: 1.0.0
**Environment**: Internal Network / Offline Deployment
