# AceFlow MCP Server HTTP支持开发计划

## 📋 项目概述

**目标**: 为AceFlow MCP Server添加HTTP传输支持，实现基于Docker的云原生部署能力

**版本**: v2.1.0 (HTTP支持版本)

**时间线**: 2025-01-14 开始实施

## 🎯 核心需求

### 功能需求
- ✅ 支持MCP 2025 Streamable HTTP传输协议
- ✅ 保持与现有stdio模式的完全兼容
- ✅ 多客户端并发连接支持
- ✅ Docker容器化部署
- ✅ 云原生架构友好

### 非功能需求
- 🔒 安全性: HTTPS支持，认证机制
- ⚡ 性能: 异步处理，流式传输
- 📈 可扩展性: 水平扩展能力
- 🔍 可观测性: 日志、监控、追踪

## 🏗️ 技术架构

### 传输层架构
```
┌─────────────────┐    ┌──────────────────┐
│   MCP Client    │────│  HTTP Gateway    │
│  (Cline/Cursor) │    │   (Port 8000)    │
└─────────────────┘    └──────────────────┘
                                │
                       ┌────────┴────────┐
                       │ AceFlow Server  │
                       │  FastMCP Core   │
                       └─────────────────┘
                                │
                       ┌────────┴────────┐
                       │  AceFlow Tools  │
                       │   (Shared)      │
                       └─────────────────┘
```

### 代码结构
```
aceflow-mcp-server/
├── aceflow_mcp_server/
│   ├── mcp_stdio_server.py      # 现有stdio实现
│   ├── mcp_http_server.py       # 新增HTTP实现 ⭐
│   ├── server.py               # FastMCP基础(增强) ⭐
│   ├── unified_server.py       # 统一启动入口 ⭐
│   ├── tools.py               # 共享工具逻辑
│   └── config.py              # 配置管理 ⭐
├── docker/
│   ├── Dockerfile             # 容器镜像 ⭐
│   ├── docker-compose.yml     # 编排配置 ⭐
│   └── docker-entrypoint.sh   # 启动脚本 ⭐
├── scripts/
│   ├── build-docker.sh        # 构建脚本 ⭐
│   └── deploy.sh             # 部署脚本 ⭐
└── docs/
    └── HTTP_DEPLOYMENT.md     # 部署文档 ⭐
```

## 📝 开发阶段

### Phase 1: 核心HTTP服务器实现 (高优先级)

**文件**: `aceflow_mcp_server/mcp_http_server.py`

**功能特性**:
- MCP 2025 Streamable HTTP协议实现
- 基于FastAPI/Starlette的异步HTTP服务器
- Server-Sent Events流式响应
- 断线重连和会话恢复
- 多客户端并发处理

**技术栈**:
- FastAPI/Starlette (HTTP框架)
- asyncio (异步处理)
- Server-Sent Events (流式传输)

**关键实现点**:
```python
# HTTP端点设计
POST /mcp  # 客户端到服务器消息
GET  /mcp  # 服务器到客户端流 (SSE)

# 响应格式
HTTP 202 Accepted (成功接收)
HTTP 400/500 (错误处理)
text/event-stream (SSE流)
```

### Phase 2: 配置和启动统一 (高优先级)

**文件**: 
- `aceflow_mcp_server/config.py` 
- `aceflow_mcp_server/unified_server.py`

**功能特性**:
- 统一配置管理 (环境变量、配置文件)
- 多传输模式启动 (stdio/http/auto)
- 优雅关闭和信号处理
- 运行时模式检测

**配置参数**:
```yaml
# 传输配置
transport: "auto"  # stdio, http, streamable-http
host: "0.0.0.0"   # HTTP监听地址
port: 8000        # HTTP监听端口

# 安全配置
enable_https: false
cert_file: null
key_file: null

# 性能配置
max_connections: 100
request_timeout: 30
keepalive_timeout: 60
```

### Phase 3: Docker容器化 (高优先级)

**文件**: 
- `docker/Dockerfile`
- `docker/docker-compose.yml`
- `docker/docker-entrypoint.sh`

**功能特性**:
- 多阶段构建优化镜像大小
- 健康检查和优雅启动
- 环境变量配置支持
- 持久化存储挂载

**Docker特性**:
```dockerfile
# 基础镜像: python:3.11-slim
# 暴露端口: 8000
# 健康检查: /health 端点
# 用户权限: 非root用户运行
```

### Phase 4: 功能测试验证 (中优先级)

**测试范围**:
- HTTP传输协议合规性测试
- 多客户端并发连接测试  
- 断线重连和会话恢复测试
- Docker容器部署测试
- 与Cline/Cursor集成测试

**测试工具**:
- pytest (单元测试)
- httpx (HTTP客户端测试)
- Docker Compose (集成测试)

### Phase 5: 文档和使用指南 (中优先级)

**文档内容**:
- HTTP模式部署指南
- Docker运行手册
- 客户端配置说明
- 故障排除指南
- 性能调优建议

## 🔧 技术实现细节

### MCP 2025 Streamable HTTP协议要点

1. **端点要求**: 
   - 单一MCP端点支持POST和GET
   - POST用于客户端消息发送
   - GET用于服务器流式响应

2. **消息格式**:
   - JSON-RPC 2.0消息格式
   - Content-Type: application/json
   - Accept: application/json, text/event-stream

3. **流式传输**:
   - Server-Sent Events (SSE)
   - 支持消息分块传输
   - 断线重连: Last-Event-ID头

### 现有代码复用策略

**完全复用**:
- `tools.py`: 核心工具逻辑
- `mcp_output_adapter.py`: 输出格式化
- `tool_prompts.py`: 工具定义

**增强复用**:
- `server.py`: 扩展FastMCP HTTP支持
- `pyproject.toml`: 新增HTTP相关依赖

**新增开发**:
- HTTP服务器实现
- Docker配置文件
- 统一启动入口

## 📊 质量保证

### 代码质量
- 类型注解覆盖率 >95%
- 单元测试覆盖率 >90%  
- 代码规范检查通过
- 安全扫描无高危风险

### 性能指标
- 单实例并发连接: >100
- 平均响应延迟: <100ms
- 内存占用: <256MB
- Docker镜像大小: <200MB

## 🚀 部署策略

### 本地开发
```bash
# stdio模式 (现有)
aceflow-mcp-server --transport stdio

# HTTP模式 (新增)
aceflow-mcp-server --transport streamable-http --port 8000
```

### Docker部署
```bash
# 单容器运行
docker run -p 8000:8000 aceflow/mcp-server:v2.1.0

# Compose编排
docker-compose up -d
```

### 云原生部署
- Kubernetes Deployment + Service
- 水平Pod自动扩展 (HPA)
- ConfigMap配置管理
- Secret密钥管理

## 🎯 成功指标

### 功能指标
- ✅ HTTP传输完全合规MCP 2025规范
- ✅ 与stdio模式功能等价
- ✅ Docker容器正常运行
- ✅ 多客户端并发无冲突

### 性能指标  
- ✅ 并发连接数 >100
- ✅ 响应延迟 <100ms
- ✅ 内存使用 <256MB
- ✅ CPU使用率 <50%

### 用户体验指标
- ✅ 部署流程 <5分钟
- ✅ 配置复杂度低
- ✅ 错误信息清晰
- ✅ 文档完整易懂

## 📅 里程碑时间线

| 阶段 | 预计完成时间 | 交付物 |
|------|-------------|--------|
| Phase 1 | 2025-01-14 | HTTP服务器核心实现 |
| Phase 2 | 2025-01-14 | 配置和启动统一 |
| Phase 3 | 2025-01-14 | Docker容器化 |
| Phase 4 | 2025-01-15 | 功能测试验证 |
| Phase 5 | 2025-01-15 | 文档和发布 |

**总体目标**: 2025-01-15完成v2.1.0版本发布

---

## 📋 待办事项检查清单

- [ ] Phase 1: 实现HTTP MCP Server (`mcp_http_server.py`)
- [ ] Phase 1: 增强FastMCP配置 (`server.py`)  
- [ ] Phase 2: 创建统一配置管理 (`config.py`)
- [ ] Phase 2: 实现统一启动入口 (`unified_server.py`)
- [ ] Phase 3: 编写Dockerfile
- [ ] Phase 3: 创建docker-compose配置
- [ ] Phase 3: 制作Docker构建脚本
- [ ] Phase 4: HTTP功能测试
- [ ] Phase 4: Docker部署测试
- [ ] Phase 5: 编写HTTP部署文档
- [ ] Phase 5: 更新pyproject.toml版本

**开发负责人**: Claude Code  
**项目状态**: 设计完成，准备实施  
**最后更新**: 2025-01-14