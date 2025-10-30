# AceFlow MCP Server - 私有部署快速开始

## 🎯 5分钟快速部署

本指南帮助您在5分钟内完成 AceFlow MCP Server 的私有部署。

## 📦 三种部署方式

### 方式1: Docker 一键部署（推荐）

**适用场景：** 有Docker环境，需要快速部署

```bash
# 1. 构建镜像
./deploy.sh docker --build

# 2. 导出镜像（用于内网传输）
./deploy.sh docker --export

# 3. 在内网服务器导入并运行
docker load -i aceflow-mcp-server-2.2.0.tar
docker run -d -p 8000:8000 --name aceflow-mcp aceflow-mcp-server:2.2.0

# 4. 验证部署
curl http://localhost:8000/health
```

### 方式2: Docker Compose 部署

**适用场景：** 需要完整的服务编排

```bash
# 1. 启动所有服务
./deploy.sh compose --build

# 2. 查看状态
docker-compose ps

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

### 方式3: 可执行文件部署

**适用场景：** 无Docker环境，需要单文件分发

```bash
# 1. 打包为可执行文件
./deploy.sh pyinstaller

# 2. 分发文件
# dist/aceflow-mcp-server

# 3. 在目标机器运行
./aceflow-mcp-server
```

## 🔗 对接私有大模型

### 场景1: 大模型支持 MCP 协议

直接配置大模型连接到 MCP Server：

```json
{
  "mcp_servers": {
    "aceflow": {
      "url": "http://192.168.1.100:8000/mcp",
      "transport": "http"
    }
  }
}
```

### 场景2: 大模型不支持 MCP（需要适配器）

使用我们提供的适配器桥接：

```bash
# 1. 启动 MCP Server
docker run -d -p 8000:8000 aceflow-mcp-server:2.2.0

# 2. 使用适配器连接
python docs/private_llm_adapter.py

# 或启动适配器 API 服务
docker-compose --profile with-adapter up -d
```

**适配器使用示例：**

```python
from private_llm_adapter import PrivateLLMAdapter

# 初始化
adapter = PrivateLLMAdapter(mcp_server_url="http://192.168.1.100:8000")

# 获取工具列表
tools = adapter.get_available_tools()
# 发送给您的私有大模型...

# 执行工具调用
result = adapter.call_tool(
    tool_name="aceflow_init",
    arguments={
        "mode": "standard",
        "project_name": "my-project",
        "directory": "/workspace/my-project"
    }
)
```

## 🧪 验证部署

```bash
# 1. 健康检查
curl http://localhost:8000/health

# 2. 获取工具列表
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/list",
    "params": {}
  }'

# 3. 运行完整测试
./deploy.sh test
```

**预期结果：**
```
✅ 所有测试通过 (12/12, 100%)
```

## 📊 服务端点

| 端点 | 用途 | 示例 |
|------|------|------|
| `/health` | 健康检查 | `GET http://localhost:8000/health` |
| `/mcp` | MCP 协议端点 | `POST http://localhost:8000/mcp` |

## ⚙️ 环境配置

通过环境变量自定义配置：

```bash
# 基础配置
export ACEFLOW_HOST=0.0.0.0
export ACEFLOW_PORT=8000

# 日志配置
export ACEFLOW_LOG_LEVEL=INFO

# 性能配置
export ACEFLOW_MAX_CONNECTIONS=100
```

## 🔧 常用命令

```bash
# 启动服务
./deploy.sh docker --build

# 查看日志
docker logs -f aceflow-mcp

# 重启服务
docker restart aceflow-mcp

# 停止服务
docker stop aceflow-mcp

# 清理环境
./deploy.sh clean
```

## 📝 可用工具

AceFlow MCP Server 提供4个核心工具：

1. **aceflow_init** - 初始化项目工作流
2. **aceflow_stage** - 管理项目阶段
3. **aceflow_validate** - 验证项目质量
4. **aceflow_template** - 管理工作流模板

## 🔐 安全建议

1. **网络隔离**：仅允许内网访问
   ```bash
   docker run -p 127.0.0.1:8000:8000 aceflow-mcp-server:2.2.0
   ```

2. **防火墙配置**：限制访问来源
   ```bash
   iptables -A INPUT -s 192.168.1.0/24 -p tcp --dport 8000 -j ACCEPT
   ```

3. **日志审计**：启用详细日志
   ```bash
   export ACEFLOW_LOG_LEVEL=DEBUG
   ```

## 📚 完整文档

- [私有部署指南](docs/PRIVATE_DEPLOYMENT_GUIDE.md) - 详细部署说明
- [适配器开发](docs/private_llm_adapter.py) - 大模型适配器示例
- [HTTP部署指南](HTTP_DEPLOYMENT_GUIDE.md) - HTTP协议详解

## ❓ 常见问题

### Q: 如何在内网环境使用？

A: 使用 `--export` 导出镜像，传输到内网后导入：
```bash
./deploy.sh docker --build --export
# 将 .tar 文件传输到内网
docker load -i aceflow-mcp-server-2.2.0.tar
```

### Q: 如何对接私有大模型？

A: 参考 `docs/private_llm_adapter.py` 适配器示例，或查看完整文档。

### Q: 如何验证服务正常？

A: 运行健康检查和完整测试：
```bash
curl http://localhost:8000/health
./deploy.sh test
```

## 🆘 获取帮助

```bash
# 显示帮助信息
./deploy.sh help

# 查看版本信息
docker run aceflow-mcp-server:2.2.0 --version
```

## 📞 技术支持

- GitHub: https://github.com/aceflow-pateoas/aceflow-ai
- 文档: https://docs.aceflow.dev/mcp
- Issues: https://github.com/aceflow-pateoas/aceflow-ai/issues
