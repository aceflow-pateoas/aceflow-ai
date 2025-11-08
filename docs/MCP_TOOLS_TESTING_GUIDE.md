# AceFlow MCP Tools 测试指南

> 如何测试和验证 AceFlow MCP Tools 的完整功能

**日期**: 2025-01-04
**适用版本**: AceFlow MCP Server v1.0.0

---

## 📋 目录

1. [测试方法概览](#测试方法概览)
2. [方法 1: MCP Inspector（推荐）](#方法-1-mcp-inspector推荐)
3. [方法 2: Python 直接调用](#方法-2-python-直接调用)
4. [方法 3: Claude Desktop 集成测试](#方法-3-claude-desktop-集成测试)
5. [方法 4: HTTP 模式测试](#方法-4-http-模式测试)
6. [完整测试场景](#完整测试场景)

---

## 测试方法概览

| 方法 | 适用场景 | 优点 | 缺点 |
|-----|---------|------|------|
| **MCP Inspector** | 开发调试 | 官方工具，UI友好，实时测试 | 需要 Node.js |
| **Python 直接调用** | 单元测试 | 快速，可自动化 | 不测试 MCP 协议层 |
| **Claude Desktop** | 真实环境 | 完全真实的使用场景 | 需要配置，调试困难 |
| **HTTP 模式** | 远程测试 | 跨平台，Postman/curl 可用 | 需要启动 HTTP 服务器 |

---

## 方法 1: MCP Inspector（推荐）

### 1.1 安装 MCP Inspector

```bash
# 全局安装（推荐）
npm install -g @modelcontextprotocol/inspector

# 或者使用 npx（无需安装）
npx @modelcontextprotocol/inspector
```

### 1.2 启动 Inspector 连接到 AceFlow

```bash
# 进入 AceFlow 目录
cd /home/chenjing/AI/aceflow-ai/aceflow-mcp-server

# 启动 Inspector（stdio 模式）
npx @modelcontextprotocol/inspector \
  python3 -m aceflow_mcp_server.server --transport stdio
```

### 1.3 使用 Inspector 界面

启动后会打开浏览器（默认 http://localhost:6789）：

**界面功能**:
1. **Tools 标签页** - 查看所有可用的 MCP Tools
2. **Resources 标签页** - 查看可用的资源
3. **Prompts 标签页** - 查看可用的提示模板

**测试 Tool**:
1. 在 Tools 列表中选择一个工具（如 `aceflow_workflow_status`）
2. 填写参数（如果需要）
3. 点击 "Execute" 按钮
4. 查看返回结果

**示例测试**:

```json
// 测试 aceflow_init_project
{
  "project_name": "test-project",
  "workflow_mode": "contract_first",
  "openapi_url": "http://localhost:8080/v3/api-docs"
}

// 查看结果
{
  "success": true,
  "project_name": "test-project",
  "config_file": "/path/to/.aceflow/config.yaml",
  "workflow_file": "/path/to/.aceflow/workflow.json"
}
```

---

## 方法 2: Python 直接调用

### 2.1 创建测试脚本

```python
#!/usr/bin/env python3
"""
AceFlow MCP Tools 直接测试脚本
"""

import sys
from pathlib import Path

# 添加 AceFlow 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "aceflow-mcp-server"))

from aceflow_mcp_server.contract_tools import AceFlowContractTools

def test_workflow_status():
    """测试工作流状态查询"""
    print("\n" + "="*60)
    print("测试: aceflow_workflow_status")
    print("="*60)

    tools = AceFlowContractTools()
    result = tools.aceflow_workflow_status()

    print(f"Success: {result.get('success')}")
    print(f"Current Stage: {result.get('current_stage')}")
    print(f"Progress: {result.get('overall_progress')}%")
    print(f"Message: {result.get('message')}")

    return result

def test_init_project():
    """测试项目初始化"""
    print("\n" + "="*60)
    print("测试: aceflow_init_project")
    print("="*60)

    tools = AceFlowContractTools(working_directory="/tmp/test-aceflow-project")
    result = tools.aceflow_init_project(
        project_name="test-project",
        workflow_mode="contract_first",
        openapi_url="http://localhost:8080/v3/api-docs",
        contract_repo_url="git@github.com:test/contracts.git",
        contract_repo_base_path="contracts"
    )

    print(f"Success: {result.get('success')}")
    print(f"Config File: {result.get('config_file')}")
    print(f"Workflow File: {result.get('workflow_file')}")

    return result

def test_define_feature():
    """测试功能定义"""
    print("\n" + "="*60)
    print("测试: aceflow_define_feature")
    print("="*60)

    tools = AceFlowContractTools(working_directory="/tmp/test-aceflow-project")
    result = tools.aceflow_define_feature(
        feature_name="user-authentication",
        description="User login and registration",
        api_scope_type="prefix",
        api_scope_pattern="/api/auth/"
    )

    print(f"Success: {result.get('success')}")
    print(f"Feature: {result.get('feature')}")
    print(f"Message: {result.get('message')}")

    return result

def test_workflow_advance():
    """测试阶段推进"""
    print("\n" + "="*60)
    print("测试: aceflow_workflow_advance")
    print("="*60)

    tools = AceFlowContractTools(working_directory="/tmp/test-aceflow-project")
    result = tools.aceflow_workflow_advance(
        next_stage="define",
        feature_name="user-authentication"
    )

    print(f"Success: {result.get('success')}")
    print(f"Previous Stage: {result.get('previous_stage')}")
    print(f"Current Stage: {result.get('current_stage')}")
    print(f"Message: {result.get('message')}")

    return result

def test_complete_workflow():
    """完整工作流测试"""
    print("\n" + "="*80)
    print("完整工作流测试")
    print("="*80)

    # 1. 初始化项目
    result1 = test_init_project()
    assert result1["success"], "Init failed"

    # 2. 查看初始状态
    result2 = test_workflow_status()
    assert result2["success"], "Status check failed"
    assert result2["current_stage"] == "setup", "Wrong initial stage"

    # 3. 定义功能
    result3 = test_define_feature()
    assert result3["success"], "Define feature failed"

    # 4. 推进到 Define 阶段
    result4 = test_workflow_advance()
    assert result4["success"], "Advance failed"
    assert result4["current_stage"] == "define", "Wrong stage after advance"

    # 5. 查看最终状态
    result5 = test_workflow_status()
    print(f"\n最终状态: {result5['current_stage']} ({result5['overall_progress']}%)")

    print("\n✅ 完整工作流测试成功！")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test AceFlow MCP Tools")
    parser.add_argument("--test", choices=["status", "init", "define", "advance", "all"],
                       default="all", help="Test to run")

    args = parser.parse_args()

    if args.test == "status":
        test_workflow_status()
    elif args.test == "init":
        test_init_project()
    elif args.test == "define":
        test_define_feature()
    elif args.test == "advance":
        test_workflow_advance()
    elif args.test == "all":
        test_complete_workflow()
```

### 2.2 运行测试

```bash
# 单个测试
python3 test_mcp_tools.py --test status

# 完整工作流测试
python3 test_mcp_tools.py --test all
```

---

## 方法 3: Claude Desktop 集成测试

### 3.1 配置 Claude Desktop

**macOS/Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aceflow": {
      "command": "python3",
      "args": [
        "-m",
        "aceflow_mcp_server.server",
        "--transport",
        "stdio"
      ],
      "env": {
        "PYTHONPATH": "/home/chenjing/AI/aceflow-ai/aceflow-mcp-server"
      }
    }
  }
}
```

### 3.2 在 Claude Desktop 中测试

重启 Claude Desktop 后，在对话中：

```
User: 请帮我初始化一个 AceFlow 项目

Claude: 好的，我将使用 aceflow_init_project 工具初始化项目...
[调用 aceflow_init_project MCP Tool]

User: 查看当前工作流状态

Claude: 我将使用 aceflow_workflow_status 查看状态...
[调用 aceflow_workflow_status MCP Tool]
```

### 3.3 查看 MCP 日志

**macOS**:
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

**Linux**:
```bash
tail -f ~/.config/Claude/logs/mcp*.log
```

---

## 方法 4: HTTP 模式测试

### 4.1 启动 HTTP 服务器

```bash
cd /home/chenjing/AI/aceflow-ai/aceflow-mcp-server

# 启动 HTTP 模式
python3 -m aceflow_mcp_server.mcp_http_server --port 18000
```

### 4.2 使用 curl 测试

```bash
# 测试健康检查
curl http://localhost:18000/health

# 列出所有工具
curl http://localhost:18000/mcp/list_tools

# 调用工具 - 初始化项目
curl -X POST http://localhost:18000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_init_project",
    "arguments": {
      "project_name": "test-project",
      "workflow_mode": "contract_first",
      "openapi_url": "http://localhost:8080/v3/api-docs"
    }
  }'

# 调用工具 - 查看状态
curl -X POST http://localhost:18000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_workflow_status",
    "arguments": {}
  }'
```

### 4.3 使用 Postman 测试

**Collection 示例**:

```json
{
  "info": {
    "name": "AceFlow MCP Tools",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "List Tools",
      "request": {
        "method": "GET",
        "url": "http://localhost:18000/mcp/list_tools"
      }
    },
    {
      "name": "Init Project",
      "request": {
        "method": "POST",
        "url": "http://localhost:18000/mcp/call_tool",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"tool\": \"aceflow_init_project\",\n  \"arguments\": {\n    \"project_name\": \"test-project\",\n    \"workflow_mode\": \"contract_first\"\n  }\n}"
        }
      }
    },
    {
      "name": "Workflow Status",
      "request": {
        "method": "POST",
        "url": "http://localhost:18000/mcp/call_tool",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"tool\": \"aceflow_workflow_status\",\n  \"arguments\": {}\n}"
        }
      }
    }
  ]
}
```

---

## 完整测试场景

### 场景 1: Contract-First 工作流完整测试

```bash
#!/bin/bash
# test_contract_first_workflow.sh

export MCP_SERVER="http://localhost:18000"

echo "=== AceFlow Contract-First 工作流完整测试 ==="

# 1. 初始化项目
echo -e "\n[1/10] 初始化项目..."
curl -s -X POST $MCP_SERVER/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_init_project",
    "arguments": {
      "project_name": "datasource-management-system",
      "workflow_mode": "contract_first",
      "openapi_url": "http://localhost:8080/v3/api-docs",
      "contract_repo_url": "git@gitlab:contracts/datasource.git"
    }
  }' | jq .

# 2. 查看初始状态
echo -e "\n[2/10] 查看初始状态..."
curl -s -X POST $MCP_SERVER/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_workflow_status",
    "arguments": {}
  }' | jq '.result | {current_stage, overall_progress}'

# 3. 定义功能
echo -e "\n[3/10] 定义功能: datasource-management..."
curl -s -X POST $MCP_SERVER/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_define_feature",
    "arguments": {
      "feature_name": "datasource-management",
      "description": "数据源管理系统 - 统一管理 FTP/SFTP 数据源",
      "api_scope_type": "prefix",
      "api_scope_pattern": "/api/datasources"
    }
  }' | jq .

# 4. 更新 Define 阶段检查点
echo -e "\n[4/10] 更新 Define 阶段检查点..."
curl -s -X POST $MCP_SERVER/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_workflow_checkpoint",
    "arguments": {
      "stage": "define",
      "checkpoint": "feature_config_exists",
      "value": true
    }
  }' | jq .

curl -s -X POST $MCP_SERVER/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_workflow_checkpoint",
    "arguments": {
      "stage": "define",
      "checkpoint": "api_scope_defined",
      "value": true
    }
  }' | jq .

curl -s -X POST $MCP_SERVER/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_workflow_checkpoint",
    "arguments": {
      "stage": "define",
      "checkpoint": "requirements_documented",
      "value": true
    }
  }' | jq .

# 5. 推进到 Design 阶段
echo -e "\n[5/10] 推进到 Design 阶段..."
curl -s -X POST $MCP_SERVER/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_workflow_advance",
    "arguments": {
      "next_stage": "design",
      "feature_name": "datasource-management"
    }
  }' | jq .

# 6. 生成契约（假设已有 OpenAPI）
echo -e "\n[6/10] 生成契约..."
curl -s -X POST $MCP_SERVER/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_contract_generate",
    "arguments": {
      "feature_name": "datasource-management",
      "output_format": "json"
    }
  }' | jq .

# 7. 更新 Design 阶段检查点
echo -e "\n[7/10] 更新 Design 阶段检查点..."
curl -s -X POST $MCP_SERVER/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_workflow_checkpoint",
    "arguments": {
      "stage": "design",
      "checkpoint": "contract_file_exists",
      "value": true
    }
  }' | jq .

# 8. 推进到 Contract Push 阶段
echo -e "\n[8/10] 推进到 Contract Push 阶段..."
curl -s -X POST $MCP_SERVER/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_workflow_advance",
    "arguments": {
      "next_stage": "contract_push",
      "feature_name": "datasource-management"
    }
  }' | jq .

# 9. 推送契约到 Git
echo -e "\n[9/10] 推送契约到 Git..."
curl -s -X POST $MCP_SERVER/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_contract_push",
    "arguments": {
      "feature_name": "datasource-management",
      "commit_message": "feat: add datasource management API contract",
      "branch": "main"
    }
  }' | jq .

# 10. 查看最终状态
echo -e "\n[10/10] 查看最终状态..."
curl -s -X POST $MCP_SERVER/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "aceflow_workflow_status",
    "arguments": {}
  }' | jq '.result | {
    current_stage,
    overall_progress,
    completed_stages,
    total_stages,
    features,
    recommendations
  }'

echo -e "\n=== 测试完成 ==="
```

### 运行完整测试

```bash
# 1. 启动 HTTP 服务器
cd /home/chenjing/AI/aceflow-ai/aceflow-mcp-server
python3 -m aceflow_mcp_server.mcp_http_server --port 18000 &

# 2. 运行测试脚本
chmod +x test_contract_first_workflow.sh
./test_contract_first_workflow.sh
```

---

## 测试检查清单

### ✅ 基础功能测试

- [ ] MCP Server 启动成功
- [ ] 列出所有 Tools（17个）
- [ ] 每个 Tool 都有正确的 schema
- [ ] Tools 可以正常调用

### ✅ 工作流状态管理测试

- [ ] `aceflow_init_project` - 初始化成功
- [ ] `aceflow_workflow_status` - 返回正确状态
- [ ] `aceflow_workflow_advance` - 阶段转换成功
- [ ] `aceflow_workflow_checkpoint` - 检查点更新成功

### ✅ Contract-First 功能测试

- [ ] `aceflow_define_feature` - 功能定义成功
- [ ] `aceflow_contract_generate` - 契约生成成功
- [ ] `aceflow_contract_push` - 推送到 Git 成功
- [ ] `aceflow_contract_pull` - 从 Git 拉取成功
- [ ] `aceflow_contract_validate` - 契约验证成功

### ✅ Mock Server 测试

- [ ] `aceflow_mock_start` - Mock Server 启动成功
- [ ] `aceflow_mock_stop` - Mock Server 停止成功
- [ ] `aceflow_mock_list` - 列出运行中的 Mock Server

### ✅ 异常处理测试

- [ ] 缺少必需参数 - 返回错误
- [ ] 无效参数值 - 返回错误
- [ ] 工作流未初始化 - 返回友好错误
- [ ] 阶段转换不合法 - 返回错误

---

## 调试技巧

### 1. 查看详细日志

```bash
# 启动时开启调试模式
export ACEFLOW_DEBUG=true
python3 -m aceflow_mcp_server.server --transport stdio
```

### 2. 使用 MCP Inspector 的 Console

打开浏览器控制台（F12），可以看到：
- WebSocket 通信内容
- 工具调用请求/响应
- 错误堆栈信息

### 3. 检查状态文件

```bash
# 查看工作流状态
cat .aceflow/workflow.json | jq .

# 查看配置
cat .aceflow/config.yaml
```

### 4. 测试特定工具

```python
# test_specific_tool.py
from aceflow_mcp_server.contract_tools import AceFlowContractTools

tools = AceFlowContractTools(working_directory="/tmp/test")

# 添加详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

result = tools.aceflow_workflow_status()
print(json.dumps(result, indent=2))
```

---

## 常见问题

### Q1: MCP Inspector 连接失败

**问题**: Inspector 无法连接到 MCP Server

**解决**:
```bash
# 检查 Python 路径
which python3

# 检查模块是否可用
python3 -c "import aceflow_mcp_server"

# 使用绝对路径
npx @modelcontextprotocol/inspector \
  /usr/bin/python3 -m aceflow_mcp_server.server --transport stdio
```

### Q2: Tools 返回空列表

**问题**: Inspector 中看不到任何 Tools

**解决**:
```bash
# 检查 server.py 是否正确注册 Tools
grep "@mcp.tool" aceflow_mcp_server/server.py

# 确保所有装饰器正确
```

### Q3: 工作流状态丢失

**问题**: `workflow.json` 不存在或为空

**解决**:
```bash
# 确保先初始化
curl -X POST http://localhost:18000/mcp/call_tool \
  -d '{"tool": "aceflow_init_project", "arguments": {...}}'

# 检查文件权限
ls -la .aceflow/workflow.json
```

---

## 推荐测试流程

### 1. 开发阶段

```bash
# 使用 MCP Inspector 快速迭代
npx @modelcontextprotocol/inspector python3 -m aceflow_mcp_server.server
```

### 2. 集成测试

```bash
# 使用 HTTP 模式 + curl/Postman
python3 -m aceflow_mcp_server.mcp_http_server --port 18000
./test_contract_first_workflow.sh
```

### 3. 真实环境测试

```bash
# 配置 Claude Desktop / Cline
# 进行真实对话测试
```

---

## 总结

推荐的测试组合：
1. **开发**: MCP Inspector（快速反馈）
2. **CI/CD**: Python 直接调用 + pytest（自动化）
3. **集成**: HTTP 模式 + 脚本（端到端）
4. **验收**: Claude Desktop（真实场景）

---

**创建时间**: 2025-01-04
**下次更新**: 添加更多测试用例和场景
