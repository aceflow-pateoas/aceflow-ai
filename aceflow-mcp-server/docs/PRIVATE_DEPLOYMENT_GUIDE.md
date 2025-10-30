# AceFlow MCP Server 私有部署指南

## 📋 概述

本指南介绍如何将 AceFlow MCP Server 打包为可执行程序，部署在内网环境，并对接私有部署的大模型（如 Qwen、ChatGLM、LLaMA、私有GPT等）。

## 🎯 适用场景

- ✅ 企业内网环境，无法访问公网
- ✅ 使用私有部署的大模型（本地/内网LLM）
- ✅ 需要数据隔离和安全控制
- ✅ 需要自定义工具集成
- ✅ 需要离线运行环境

## 🔧 部署方案

### 方案1: Docker 容器部署（推荐）

**优点：** 环境隔离、易于迁移、跨平台一致性

#### 1.1 构建 Docker 镜像

```bash
# 进入项目目录
cd aceflow-mcp-server

# 构建镜像
docker build -t aceflow-mcp-server:2.2.0 -f Dockerfile .

# 导出镜像（用于内网传输）
docker save aceflow-mcp-server:2.2.0 -o aceflow-mcp-server-2.2.0.tar
```

#### 1.2 内网部署

```bash
# 1. 将 tar 文件传输到内网服务器

# 2. 导入镜像
docker load -i aceflow-mcp-server-2.2.0.tar

# 3. 运行容器
docker run -d \
  --name aceflow-mcp \
  -p 8000:8000 \
  -v /path/to/workdir:/workspace \
  -e ACEFLOW_HOST=0.0.0.0 \
  -e ACEFLOW_PORT=8000 \
  aceflow-mcp-server:2.2.0

# 4. 验证部署
curl http://localhost:8000/health
```

#### 1.3 Docker Compose 部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  aceflow-mcp:
    image: aceflow-mcp-server:2.2.0
    container_name: aceflow-mcp
    ports:
      - "8000:8000"
    volumes:
      - ./workspace:/workspace
    environment:
      - ACEFLOW_HOST=0.0.0.0
      - ACEFLOW_PORT=8000
      - ACEFLOW_LOG_LEVEL=INFO
      - ACEFLOW_MAX_CONNECTIONS=100
    restart: unless-stopped
    networks:
      - internal-network

networks:
  internal-network:
    driver: bridge
```

启动：
```bash
docker-compose up -d
```

---

### 方案2: PyInstaller 打包可执行文件

**优点：** 单文件分发、无需安装依赖、启动快速

#### 2.1 准备打包环境

```bash
# 安装打包工具
pip install pyinstaller

# 确保所有依赖都已安装
pip install -e .
```

#### 2.2 创建打包配置

创建 `aceflow-mcp-server.spec` 文件：

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['aceflow_mcp_server/mcp_http_server.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('aceflow_mcp_server', 'aceflow_mcp_server'),
    ],
    hiddenimports=[
        'aceflow_mcp_server.tools',
        'aceflow_mcp_server.config',
        'aceflow_mcp_server.mcp_output_adapter',
        'aceflow_mcp_server.tool_prompts',
        'uvicorn',
        'fastapi',
        'pydantic',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='aceflow-mcp-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

#### 2.3 执行打包

```bash
# 使用配置文件打包
pyinstaller aceflow-mcp-server.spec

# 或直接命令行打包（简单场景）
pyinstaller --onefile \
  --name aceflow-mcp-server \
  --hidden-import aceflow_mcp_server \
  --add-data "aceflow_mcp_server:aceflow_mcp_server" \
  aceflow_mcp_server/mcp_http_server.py

# 生成的可执行文件在 dist/ 目录
```

#### 2.4 内网使用

```bash
# 直接运行
./dist/aceflow-mcp-server

# 或配置环境变量运行
ACEFLOW_HOST=0.0.0.0 ACEFLOW_PORT=8000 ./dist/aceflow-mcp-server
```

---

### 方案3: 虚拟环境打包

**优点：** 灵活性高、易于调试、保留Python环境

#### 3.1 创建独立虚拟环境

```bash
# 创建虚拟环境
python3 -m venv aceflow-venv

# 激活虚拟环境
source aceflow-venv/bin/activate  # Linux/Mac
# 或
aceflow-venv\Scripts\activate.bat  # Windows

# 安装项目
pip install -e .
```

#### 3.2 打包整个环境

```bash
# 打包虚拟环境目录
tar -czf aceflow-mcp-bundle.tar.gz \
  aceflow-venv/ \
  aceflow_mcp_server/ \
  pyproject.toml \
  README.md

# 或使用 zip（Windows友好）
zip -r aceflow-mcp-bundle.zip \
  aceflow-venv/ \
  aceflow_mcp_server/ \
  pyproject.toml \
  README.md
```

#### 3.3 内网部署使用

```bash
# 解压
tar -xzf aceflow-mcp-bundle.tar.gz

# 激活虚拟环境
source aceflow-venv/bin/activate

# 运行服务器
python -m aceflow_mcp_server.mcp_http_server
```

---

## 🤖 对接私有大模型

### 架构说明

```
┌─────────────────┐     MCP 协议      ┌──────────────────┐
│   私有大模型     │ ←─────────────→  │  AceFlow MCP     │
│  (Qwen/GLM等)   │   HTTP/Stdio      │     Server       │
└─────────────────┘                   └──────────────────┘
        │                                       │
        │                                       ↓
        │                              ┌──────────────────┐
        └──────────────────────────────→  项目工作流管理  │
               (通过适配器)              │  (init/stage等) │
                                         └──────────────────┘
```

### 对接方式1: 直接 MCP 协议对接

如果您的私有大模型支持 MCP 协议（或可以配置Function Calling），直接配置：

**配置示例：**

```json
{
  "mcp_servers": {
    "aceflow": {
      "transport": "http",
      "url": "http://192.168.1.100:8000/mcp",
      "method": "POST",
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
```

**API调用示例：**

```bash
# 1. 获取工具列表
curl -X POST http://192.168.1.100:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/list",
    "params": {}
  }'

# 2. 调用工具
curl -X POST http://192.168.1.100:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/call",
    "params": {
      "name": "aceflow_init",
      "arguments": {
        "mode": "standard",
        "project_name": "my-project",
        "directory": "/workspace/my-project"
      }
    }
  }'
```

### 对接方式2: 使用适配器桥接

如果您的私有大模型不支持 MCP，使用我们提供的适配器：

#### 2.1 使用 Python 适配器

参见 `docs/private_llm_adapter.py`，核心代码：

```python
from private_llm_adapter import PrivateLLMAdapter

# 初始化适配器
adapter = PrivateLLMAdapter(mcp_server_url="http://192.168.1.100:8000")

# 获取工具列表（转换为您的大模型格式）
tools = adapter.get_available_tools()

# 发送给您的私有大模型...

# 当大模型决定调用工具时，使用适配器执行
result = adapter.call_tool(
    tool_name="aceflow_init",
    arguments={
        "mode": "standard",
        "project_name": "my-project",
        "directory": "/workspace/my-project"
    }
)

# 将结果返回给大模型继续处理...
```

#### 2.2 部署适配器 API 服务

如果需要独立的适配器服务：

```bash
# 启动适配器 API
uvicorn private_llm_adapter:create_adapter_api --host 0.0.0.0 --port 9000

# 您的私有大模型调用适配器
curl http://192.168.1.100:9000/tools  # 获取工具
curl -X POST http://192.168.1.100:9000/tool-call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "aceflow_init",
    "arguments": {...}
  }'
```

---

## 🔐 安全配置

### 1. 网络隔离

```bash
# 仅允许内网访问
docker run -d \
  -p 127.0.0.1:8000:8000 \  # 仅本机
  aceflow-mcp-server:2.2.0

# 或通过防火墙限制
iptables -A INPUT -p tcp --dport 8000 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j DROP
```

### 2. 认证配置（可选）

如需添加认证，在适配器层实现：

```python
from fastapi import FastAPI, HTTPException, Depends, Header

def verify_token(authorization: str = Header(None)):
    if authorization != "Bearer your-secret-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

@app.post("/mcp")
async def mcp_endpoint(authenticated: bool = Depends(verify_token)):
    # 处理请求...
```

### 3. 日志和审计

```bash
# 启用详细日志
export ACEFLOW_LOG_LEVEL=DEBUG

# 日志持久化
docker run -d \
  -v /var/log/aceflow:/logs \
  -e ACEFLOW_LOG_FILE=/logs/aceflow.log \
  aceflow-mcp-server:2.2.0
```

---

## 🧪 验证部署

### 1. 健康检查

```bash
curl http://192.168.1.100:8000/health
# 预期输出:
# {
#   "status": "healthy",
#   "version": "2.2.0",
#   "transport": "streamable-http",
#   "timestamp": "2025-10-30T03:00:00Z"
# }
```

### 2. 功能测试

```bash
# 运行完整测试套件
cd aceflow-mcp-server
export ACEFLOW_PORT=8000
python run_tests.py

# 预期结果: 12/12 tests passing (100%)
```

### 3. 性能测试

```bash
# 使用 Apache Bench
ab -n 1000 -c 10 http://192.168.1.100:8000/health

# 或使用 wrk
wrk -t4 -c100 -d30s http://192.168.1.100:8000/health
```

---

## 📊 性能优化

### 1. 并发配置

```bash
# 增加 uvicorn workers
uvicorn aceflow_mcp_server.mcp_http_server:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4

# Docker 环境
docker run -d \
  -e UVICORN_WORKERS=4 \
  aceflow-mcp-server:2.2.0
```

### 2. 资源限制

```yaml
# docker-compose.yml
services:
  aceflow-mcp:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
```

---

## 🛠️ 常见问题

### Q1: 如何更新服务？

```bash
# Docker 方式
docker stop aceflow-mcp
docker rm aceflow-mcp
docker load -i aceflow-mcp-server-2.2.1.tar
docker run -d ...

# 可执行文件方式
# 直接替换可执行文件并重启
```

### Q2: 如何备份数据？

```bash
# 备份工作目录
tar -czf workspace-backup-$(date +%Y%m%d).tar.gz /path/to/workspace

# Docker volume 备份
docker run --rm \
  -v aceflow-workspace:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/workspace-backup.tar.gz /data
```

### Q3: 如何监控服务状态？

```bash
# 使用健康检查端点
watch -n 5 'curl -s http://localhost:8000/health | jq'

# 或集成到监控系统（Prometheus、Zabbix等）
curl http://localhost:8000/health
```

---

## 📞 支持联系

如有问题，请联系：
- GitHub Issues: https://github.com/aceflow-pateoas/aceflow-ai/issues
- 文档: https://docs.aceflow.dev/mcp
- Email: team@aceflow.dev

---

## 📝 更新日志

- **v2.2.0** (2025-10-30): 同步响应模式，完整测试套件
- **v2.1.5** (2025-09-17): PyPI安装支持
- **v2.1.4** (2025-09-14): HTTP MCP Server 支持
