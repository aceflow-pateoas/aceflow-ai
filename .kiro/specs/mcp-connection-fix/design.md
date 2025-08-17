# MCP 连接修复设计文档

## 概述

基于参考的 MCPOutputAdapter.js 实现和当前问题分析，设计一个稳定可靠的 AceFlow MCP Server 解决方案。主要问题是工具调用 pending 和响应格式不兼容，需要重新设计 MCP 协议适配层。

## 架构设计

### 核心组件

```
┌─────────────────────────────────────────────────────────────┐
│                    Kiro IDE MCP Client                     │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP Protocol (stdio)
┌─────────────────────▼───────────────────────────────────────┐
│                MCP Protocol Adapter                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Input Parser  │  │ Output Adapter  │  │ Error Handler│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ Internal API
┌─────────────────────▼───────────────────────────────────────┐
│                 AceFlow Core Engine                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Tools Module  │  │ Resources Module│  │Prompts Module│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 设计原则

1. **协议兼容性**: 严格遵循 MCP 2024-11-05 协议规范
2. **响应格式标准化**: 参考 MCPOutputAdapter 的输出格式设计
3. **错误处理机制**: 统一的错误处理和恢复机制
4. **异步非阻塞**: 避免 pending 状态的异步处理
5. **日志分离**: 将调试日志与 stdio 通信分离

## 组件设计

### 1. MCP Protocol Adapter

**职责**: 处理 MCP 协议的输入输出转换

**核心功能**:
- 解析 MCP JSON-RPC 请求
- 将内部响应转换为 MCP 标准格式
- 处理协议错误和异常

**实现要点**:
```python
class MCPProtocolAdapter:
    def __init__(self):
        self.version = "2024-11-05"
        self.output_adapter = MCPOutputAdapter()
    
    async def handle_request(self, request):
        """处理 MCP 请求"""
        try:
            # 解析请求
            parsed = self.parse_request(request)
            
            # 路由到对应处理器
            result = await self.route_request(parsed)
            
            # 转换为 MCP 格式
            return self.output_adapter.convert_to_mcp_format(result)
        except Exception as e:
            return self.output_adapter.create_error_response(str(e))
```

### 2. Output Adapter (基于参考代码)

**职责**: 将 AceFlow 工具的输出转换为 MCP 标准格式

**核心功能**:
- 标准化各种类型的输出
- 保留 emoji、中文字符、markdown 格式
- 统一错误处理

**实现要点**:
```python
class MCPOutputAdapter:
    def convert_to_mcp_format(self, input_data):
        """转换为 MCP 标准格式"""
        try:
            text = self.normalize_input(input_data)
            sanitized_text = self.sanitize_text(text)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": sanitized_text
                    }
                ]
            }
        except Exception as e:
            return self.handle_error(e)
    
    def normalize_input(self, input_data):
        """标准化输入数据"""
        if input_data is None:
            return "null"
        if isinstance(input_data, str):
            return input_data
        if isinstance(input_data, dict):
            return json.dumps(input_data, indent=2, ensure_ascii=False)
        return str(input_data)
```

### 3. Async Request Handler

**职责**: 处理异步请求，避免 pending 状态

**核心功能**:
- 异步工具调用
- 超时控制
- 并发请求管理

**实现要点**:
```python
class AsyncRequestHandler:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.active_requests = {}
    
    async def handle_tool_call(self, tool_name, arguments):
        """处理工具调用"""
        try:
            # 设置超时
            result = await asyncio.wait_for(
                self.execute_tool(tool_name, arguments),
                timeout=self.timeout
            )
            return result
        except asyncio.TimeoutError:
            return {"success": False, "error": "Tool call timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

### 4. Connection Manager

**职责**: 管理 MCP 连接的生命周期

**核心功能**:
- 连接初始化
- 心跳检测
- 连接恢复

**实现要点**:
```python
class ConnectionManager:
    def __init__(self):
        self.is_connected = False
        self.last_heartbeat = None
    
    async def initialize_connection(self, capabilities):
        """初始化连接"""
        self.is_connected = True
        self.last_heartbeat = time.time()
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"listChanged": False},
                "prompts": {"listChanged": False}
            },
            "serverInfo": {
                "name": "AceFlow",
                "version": "1.0.3"
            }
        }
```

## 数据模型

### MCP Request Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "aceflow_stage",
    "arguments": {
      "action": "list"
    }
  }
}
```

### MCP Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"success\": true,\n  \"action\": \"list\",\n  \"result\": {\n    \"stages\": [\"user_stories\", \"task_breakdown\", \"test_design\", \"implementation\", \"unit_test\", \"integration_test\", \"code_review\", \"demo\"]\n  }\n}"
      }
    ]
  }
}
```

### Error Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": "Tool execution failed: Invalid action"
  }
}
```

## 错误处理策略

### 1. 分层错误处理

- **协议层**: JSON-RPC 协议错误
- **适配层**: 数据转换错误
- **业务层**: 工具执行错误
- **系统层**: 连接和超时错误

### 2. 错误恢复机制

- **自动重试**: 对于临时性错误进行重试
- **降级处理**: 在部分功能不可用时提供基础功能
- **错误上报**: 详细的错误日志和诊断信息

### 3. 超时处理

- **请求超时**: 10 秒工具调用超时
- **连接超时**: 5 秒连接建立超时
- **心跳超时**: 30 秒心跳检测超时

## 测试策略

### 1. 单元测试
- 输出适配器测试
- 协议解析测试
- 错误处理测试

### 2. 集成测试
- MCP 协议兼容性测试
- 工具调用端到端测试
- 连接稳定性测试

### 3. 性能测试
- 并发请求测试
- 长时间运行测试
- 内存泄漏测试

## 部署配置

### 1. 开发模式
```json
{
  "command": "python",
  "args": ["-m", "aceflow_mcp_server.main", "--mode", "dev"],
  "cwd": "aceflow-mcp-server",
  "env": {
    "ACEFLOW_LOG_LEVEL": "DEBUG",
    "ACEFLOW_LOG_FILE": "mcp_debug.log"
  }
}
```

### 2. 生产模式
```json
{
  "command": "uvx",
  "args": ["aceflow-mcp-server@1.0.4"],
  "env": {
    "ACEFLOW_LOG_LEVEL": "WARNING"
  }
}
```

## 实现计划

### Phase 1: 核心适配器实现
1. 实现 MCPOutputAdapter
2. 实现 AsyncRequestHandler
3. 基础协议处理

### Phase 2: 连接管理
1. 实现 ConnectionManager
2. 心跳和重连机制
3. 错误恢复逻辑

### Phase 3: 测试和优化
1. 完整的测试套件
2. 性能优化
3. 文档和部署指南

### Phase 4: 发布和维护
1. 发布新版本到 PyPI
2. 更新配置文档
3. 持续监控和改进

这个设计基于参考代码的最佳实践，应该能够解决当前的 pending 问题和协议兼容性问题。