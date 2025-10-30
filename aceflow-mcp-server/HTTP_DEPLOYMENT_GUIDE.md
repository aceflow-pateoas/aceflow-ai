# AceFlow MCP Server HTTP部署指南

## 📋 概览

AceFlow MCP Server v2.2.0 现在完全支持MCP 2025 HTTP协议（支持同步和流式两种模式），可以通过HTTP方式部署和访问，同时保持对传统stdio模式的完全兼容。

## 🚀 快速开始

### 方式1: 使用PyPI安装

```bash
# 安装最新版本
pip install aceflow-mcp-server==2.2.0

# HTTP模式启动
aceflow-mcp-unified --transport streamable-http --host 0.0.0.0 --port 8000

# 自动检测模式启动
aceflow-mcp-unified --transport auto
```

### 方式2: 使用Docker部署

```bash
# 拉取镜像并运行
docker run -d -p 8000:8000 --name aceflow-mcp aceflow/mcp-server:2.2.0

# 使用docker-compose部署
git clone https://github.com/aceflow-pateoas/aceflow-ai.git
cd aceflow-ai/aceflow-mcp-server
docker-compose -f docker/docker-compose.yml up -d
```

### 方式3: 从源码构建

```bash
# 克隆仓库
git clone https://github.com/aceflow-pateoas/aceflow-ai.git
cd aceflow-ai/aceflow-mcp-server

# 构建Docker镜像
./scripts/build-docker.sh

# 部署服务
./scripts/deploy.sh start --build
```

## 🌐 HTTP模式特性

### MCP 2025 HTTP协议支持

**v2.2.0新增：同步响应模式**
- ✅ **同步响应**: POST请求直接返回完整JSON-RPC响应（推荐）
- ✅ **单一端点**: `/mcp` 支持POST和GET请求
- ✅ **Server-Sent Events**: 可选的流式传输支持（GET端点）
- ✅ **会话管理**: 智能会话隔离和清理（X-Session-ID）
- ✅ **多客户端**: 并发连接支持
- ✅ **断线重连**: 支持Last-Event-ID恢复机制（流式模式）

### 核心端点

| 端点 | 方法 | 描述 | 用途 |
|------|------|------|------|
| `/health` | GET | 健康检查 | 监控和负载均衡 |
| `/mcp` | POST | 发送MCP消息并获取同步响应 | 标准MCP通信（推荐） |
| `/mcp` | GET | 接收SSE流 | 可选的流式通信 |

## ⚙️ 配置选项

### 环境变量配置

```bash
# 传输配置
export ACEFLOW_TRANSPORT=streamable-http    # 传输模式
export ACEFLOW_HOST=0.0.0.0                # 监听地址
export ACEFLOW_PORT=8000                   # 监听端口

# 性能配置
export ACEFLOW_MAX_CONNECTIONS=100         # 最大连接数
export ACEFLOW_REQUEST_TIMEOUT=30          # 请求超时
export ACEFLOW_KEEPALIVE_TIMEOUT=60        # 保持活跃超时

# 安全配置
export ACEFLOW_ALLOWED_ORIGINS="*"         # 允许的源
export ACEFLOW_ENABLE_HTTPS=false          # 启用HTTPS
export ACEFLOW_CERT_FILE=""                # 证书文件
export ACEFLOW_KEY_FILE=""                 # 密钥文件

# 工作目录
export ACEFLOW_WORKING_DIRECTORY="/app/workspace"

# 日志配置
export ACEFLOW_LOG_LEVEL=INFO              # 日志级别
export ACEFLOW_DEBUG=false                 # 调试模式
```

### 命令行参数

```bash
aceflow-mcp-unified [选项]

选项:
  -t, --transport MODE        传输模式 (auto, stdio, streamable-http)
  -h, --host HOST            HTTP监听主机 (默认: localhost)
  -p, --port PORT            HTTP监听端口 (默认: 8000)
  -l, --log-level LEVEL      日志级别 (DEBUG, INFO, WARNING, ERROR)
  -w, --working-directory DIR 工作目录
  -c, --config FILE          配置文件路径
  --debug                    启用调试模式
  --help                     显示帮助信息
```

## 🐳 Docker部署

### 基础部署

```bash
# 运行单个容器
docker run -d \
  --name aceflow-mcp \
  -p 8000:8000 \
  -e ACEFLOW_TRANSPORT=streamable-http \
  -e ACEFLOW_HOST=0.0.0.0 \
  -e ACEFLOW_PORT=8000 \
  aceflow/mcp-server:2.1.0
```

### Docker Compose部署

```yaml
version: '3.8'

services:
  aceflow-mcp-server:
    image: aceflow/mcp-server:2.1.0
    ports:
      - "8000:8000"
    environment:
      - ACEFLOW_TRANSPORT=streamable-http
      - ACEFLOW_HOST=0.0.0.0
      - ACEFLOW_PORT=8000
      - ACEFLOW_LOG_LEVEL=INFO
    volumes:
      - workspace:/app/workspace
      - logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  workspace:
  logs:
```

### 高级部署 (包含Nginx + Redis + 监控)

```bash
# 包含所有服务的完整部署
docker-compose --profile with-nginx --profile with-redis --profile with-monitoring up -d
```

## 🔧 客户端集成

### MCP客户端配置

在MCP客户端（如Cline、Cursor等）中配置HTTP传输：

```json
{
  "mcpServers": {
    "aceflow": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-H", "Accept: application/json, text/event-stream",
        "http://localhost:8000/mcp"
      ],
      "transport": "http"
    }
  }
}
```

### 直接HTTP请求示例

```bash
# 健康检查
curl -f http://localhost:8000/health

# 获取工具列表
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/list",
    "params": {}
  }'

# 建立SSE连接
curl -N -H "Accept: text/event-stream" http://localhost:8000/mcp
```

## 📊 监控和维护

### 健康检查

```bash
# 基本健康检查
curl -f http://localhost:8000/health

# 详细状态检查  
./scripts/deploy.sh health
```

### 日志查看

```bash
# Docker Compose日志
docker-compose -f docker/docker-compose.yml logs -f

# 单独容器日志
docker logs -f aceflow-mcp

# 部署脚本日志
./scripts/deploy.sh logs -f
```

### 性能监控

服务器提供以下监控指标：

- **并发连接数**: 实时活跃连接统计
- **请求处理时间**: 平均和P95延迟
- **内存使用**: 服务器内存占用
- **会话统计**: 活跃会话数和清理统计

## 🚨 故障排除

### 常见问题

**1. 端口冲突**
```bash
# 检查端口占用
netstat -tlnp | grep 8000
# 更改端口
export ACEFLOW_PORT=8080
```

**2. 权限问题**
```bash
# 以非root用户运行
docker run --user 1000:1000 aceflow/mcp-server:2.1.0
```

**3. 工作目录问题**
```bash
# 明确指定工作目录
export ACEFLOW_WORKING_DIRECTORY=/path/to/workspace
```

**4. 连接超时**
```bash
# 增加超时时间
export ACEFLOW_REQUEST_TIMEOUT=60
export ACEFLOW_KEEPALIVE_TIMEOUT=120
```

### 调试模式

```bash
# 启用详细日志
export ACEFLOW_DEBUG=true
export ACEFLOW_LOG_LEVEL=DEBUG

# 重启服务
docker-compose restart aceflow-mcp-server
```

## 🔄 升级指南

### 从v2.0.x升级到v2.1.0

1. **保存数据** (如果有重要工作空间数据)
```bash
./scripts/deploy.sh backup
```

2. **停止旧版本**
```bash
./scripts/deploy.sh stop
```

3. **拉取新镜像**
```bash
docker pull aceflow/mcp-server:2.1.0
```

4. **更新配置** (如需要)
```bash
# 新增HTTP相关环境变量
export ACEFLOW_TRANSPORT=auto  # 新的自动检测模式
```

5. **启动新版本**
```bash
./scripts/deploy.sh start --pull
```

6. **验证功能**
```bash
python test_http_functionality.py --test all
```

## 🌍 生产部署建议

### 负载均衡配置 (Nginx)

```nginx
upstream aceflow_backend {
    server aceflow-mcp-1:8000;
    server aceflow-mcp-2:8000;
    server aceflow-mcp-3:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location /mcp {
        proxy_pass http://aceflow_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # SSE支持
        proxy_buffering off;
        proxy_cache off;
    }

    location /health {
        proxy_pass http://aceflow_backend;
    }
}
```

### Kubernetes部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aceflow-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aceflow-mcp-server
  template:
    metadata:
      labels:
        app: aceflow-mcp-server
    spec:
      containers:
      - name: aceflow-mcp-server
        image: aceflow/mcp-server:2.1.0
        ports:
        - containerPort: 8000
        env:
        - name: ACEFLOW_TRANSPORT
          value: "streamable-http"
        - name: ACEFLOW_HOST
          value: "0.0.0.0"
        - name: ACEFLOW_PORT
          value: "8000"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          limits:
            memory: "512Mi"
            cpu: "1000m"
          requests:
            memory: "256Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: aceflow-mcp-service
spec:
  selector:
    app: aceflow-mcp-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 📚 更多资源

- **GitHub仓库**: https://github.com/aceflow-pateoas/aceflow-ai
- **PyPI页面**: https://pypi.org/project/aceflow-mcp-server/
- **Docker Hub**: https://hub.docker.com/r/aceflow/mcp-server
- **文档站点**: https://docs.aceflow.dev/mcp
- **问题反馈**: https://github.com/aceflow-pateoas/aceflow-ai/issues

## 🎯 下一步

现在您已经成功部署了AceFlow MCP Server的HTTP模式，可以：

1. 在您的MCP客户端中配置HTTP连接
2. 通过HTTP API集成到您的应用程序
3. 探索高级功能如会话管理和流式传输
4. 设置生产环境的监控和日志
5. 参与社区贡献和反馈

享受AI增强的开发工作流体验！ 🚀