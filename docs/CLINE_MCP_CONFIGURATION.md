# Cline MCP Configuration Examples

> VSCode + Cline + AceFlow MCP Server 配置示例

**版本**: v1.0.0
**适用**: Cline v2.0+, VSCode 1.85+

---

## 📁 配置文件位置

### Linux/macOS
```
~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

### Windows
```
%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

---

## 🔧 配置示例

### 1. 标准配置（stdio 模式）

**推荐公网环境使用**

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

### 2. 完整路径配置（推荐）

**适用于 Python 路径不明确的情况**

```json
{
  "mcpServers": {
    "aceflow": {
      "command": "/usr/bin/python3",
      "args": [
        "-m",
        "aceflow_mcp_server.server",
        "--transport",
        "stdio"
      ],
      "env": {
        "PYTHONPATH": "/home/developer/aceflow-ai/aceflow-mcp-server",
        "PATH": "/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

### 3. HTTP/SSE 模式配置

**推荐内网环境使用**

先启动 HTTP Server:
```bash
python -m aceflow_mcp_server.server \
    --transport sse \
    --host 127.0.0.1 \
    --port 8000
```

Cline 配置:
```json
{
  "mcpServers": {
    "aceflow": {
      "url": "http://127.0.0.1:8000/sse",
      "transport": "sse"
    }
  }
}
```

### 4. 远程 MCP Server 配置

**适用于团队共享 MCP Server**

```json
{
  "mcpServers": {
    "aceflow": {
      "url": "http://aceflow-mcp.company.internal:8000/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer your-team-token"
      }
    }
  }
}
```

### 5. 多环境配置

**开发/测试/生产环境分离**

```json
{
  "mcpServers": {
    "aceflow-dev": {
      "command": "/usr/bin/python3",
      "args": ["-m", "aceflow_mcp_server.server", "--transport", "stdio"],
      "env": {
        "PYTHONPATH": "/home/dev/aceflow-ai/aceflow-mcp-server",
        "ACEFLOW_ENV": "development"
      }
    },
    "aceflow-prod": {
      "url": "http://aceflow-mcp-prod.company.internal:8000/sse",
      "transport": "sse"
    }
  }
}
```

### 6. 调试模式配置

**启用详细日志**

```json
{
  "mcpServers": {
    "aceflow": {
      "command": "/usr/bin/python3",
      "args": [
        "-m",
        "aceflow_mcp_server.server",
        "--transport",
        "stdio",
        "--log-level",
        "DEBUG"
      ],
      "env": {
        "PYTHONPATH": "/path/to/aceflow-ai/aceflow-mcp-server",
        "ACEFLOW_DEBUG": "1"
      }
    }
  }
}
```

---

## 🚀 Qwen Code3 集成配置

### 方式 1: OpenAI-Compatible API

**Qwen Code3 作为 OpenAI API 使用**

Cline 设置:
```json
{
  "apiProvider": "openai-compatible",
  "apiKey": "your-qwen-api-key",
  "baseURL": "http://qwen.company.internal:8000/v1",
  "modelId": "qwen-coder-plus-latest"
}
```

### 方式 2: Ollama 本地部署

**使用 Ollama 运行 Qwen Code3**

启动 Ollama:
```bash
# 拉取 Qwen Code3 模型
ollama pull qwen2.5-coder:32b

# 启动 Ollama 服务
ollama serve
```

Cline 设置:
```json
{
  "apiProvider": "ollama",
  "baseURL": "http://localhost:11434",
  "modelId": "qwen2.5-coder:32b"
}
```

### 方式 3: vLLM 部署

**使用 vLLM 高性能推理**

启动 vLLM:
```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-Coder-32B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --served-model-name qwen-coder
```

Cline 设置:
```json
{
  "apiProvider": "openai-compatible",
  "apiKey": "token-abc123",
  "baseURL": "http://qwen-vllm.company.internal:8000/v1",
  "modelId": "qwen-coder"
}
```

---

## 🛠️ 快速配置脚本

### Linux/macOS 自动配置

保存为 `setup-cline-aceflow.sh`:

```bash
#!/bin/bash

# AceFlow + Cline 自动配置脚本

set -e

echo "🚀 AceFlow MCP Server - Cline 配置向导"
echo ""

# 1. 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_DIR="$HOME/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings"
else
    CONFIG_DIR="$HOME/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings"
fi

CONFIG_FILE="$CONFIG_DIR/cline_mcp_settings.json"

# 2. 检查 AceFlow 安装
echo "检查 AceFlow 安装..."
if ! command -v aceflow &> /dev/null; then
    echo "❌ AceFlow 未安装"
    echo "请先运行: pip install aceflow-mcp-server"
    exit 1
fi
echo "✅ AceFlow 已安装: $(aceflow --version)"

# 3. 检测 Python 路径
PYTHON_PATH=$(which python3)
echo "✅ Python 路径: $PYTHON_PATH"

# 4. 检测 AceFlow 模块路径
ACEFLOW_PATH=$(python3 -c "import aceflow_mcp_server; import os; print(os.path.dirname(os.path.dirname(aceflow_mcp_server.__file__)))")
echo "✅ AceFlow 路径: $ACEFLOW_PATH"

# 5. 选择配置模式
echo ""
echo "请选择配置模式:"
echo "1) stdio 模式 (推荐)"
echo "2) HTTP/SSE 模式"
read -p "选择 (1/2): " MODE_CHOICE

# 6. 创建配置目录
mkdir -p "$CONFIG_DIR"

# 7. 生成配置文件
if [ "$MODE_CHOICE" == "1" ]; then
    # stdio 模式
    cat > "$CONFIG_FILE" <<EOF
{
  "mcpServers": {
    "aceflow": {
      "command": "$PYTHON_PATH",
      "args": [
        "-m",
        "aceflow_mcp_server.server",
        "--transport",
        "stdio"
      ],
      "env": {
        "PYTHONPATH": "$ACEFLOW_PATH"
      }
    }
  }
}
EOF
    echo "✅ 配置已生成 (stdio 模式)"
else
    # HTTP 模式
    echo ""
    read -p "HTTP Server 端口 (默认 8000): " HTTP_PORT
    HTTP_PORT=${HTTP_PORT:-8000}

    cat > "$CONFIG_FILE" <<EOF
{
  "mcpServers": {
    "aceflow": {
      "url": "http://127.0.0.1:$HTTP_PORT/sse",
      "transport": "sse"
    }
  }
}
EOF

    echo "✅ 配置已生成 (HTTP 模式)"
    echo ""
    echo "请在新终端中启动 HTTP Server:"
    echo "  python -m aceflow_mcp_server.server --transport sse --host 127.0.0.1 --port $HTTP_PORT"
fi

# 8. 显示配置文件内容
echo ""
echo "📄 配置文件内容:"
cat "$CONFIG_FILE"

# 9. 完成
echo ""
echo "✅ 配置完成!"
echo "请重启 VSCode 使配置生效"
echo ""
echo "测试命令:"
echo "  在 VSCode 中打开 Cline"
echo "  输入: 帮我初始化一个新项目"
```

使用方法:
```bash
chmod +x setup-cline-aceflow.sh
./setup-cline-aceflow.sh
```

### Windows PowerShell 自动配置

保存为 `setup-cline-aceflow.ps1`:

```powershell
# AceFlow + Cline 自动配置脚本 (Windows)

Write-Host "🚀 AceFlow MCP Server - Cline 配置向导" -ForegroundColor Green
Write-Host ""

# 1. 配置路径
$ConfigDir = "$env:APPDATA\Code\User\globalStorage\saoudrizwan.claude-dev\settings"
$ConfigFile = "$ConfigDir\cline_mcp_settings.json"

# 2. 检查 AceFlow 安装
Write-Host "检查 AceFlow 安装..." -ForegroundColor Yellow
try {
    $Version = & aceflow --version
    Write-Host "✅ AceFlow 已安装: $Version" -ForegroundColor Green
} catch {
    Write-Host "❌ AceFlow 未安装" -ForegroundColor Red
    Write-Host "请先运行: pip install aceflow-mcp-server"
    exit 1
}

# 3. 检测 Python 路径
$PythonPath = (Get-Command python).Source
Write-Host "✅ Python 路径: $PythonPath" -ForegroundColor Green

# 4. 检测 AceFlow 模块路径
$AceflowPath = & python -c "import aceflow_mcp_server; import os; print(os.path.dirname(os.path.dirname(aceflow_mcp_server.__file__)))"
Write-Host "✅ AceFlow 路径: $AceflowPath" -ForegroundColor Green

# 5. 选择配置模式
Write-Host ""
Write-Host "请选择配置模式:"
Write-Host "1) stdio 模式 (推荐)"
Write-Host "2) HTTP/SSE 模式"
$ModeChoice = Read-Host "选择 (1/2)"

# 6. 创建配置目录
New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null

# 7. 生成配置文件
if ($ModeChoice -eq "1") {
    # stdio 模式
    $Config = @{
        mcpServers = @{
            aceflow = @{
                command = $PythonPath
                args = @(
                    "-m",
                    "aceflow_mcp_server.server",
                    "--transport",
                    "stdio"
                )
                env = @{
                    PYTHONPATH = $AceflowPath
                }
            }
        }
    }

    $Config | ConvertTo-Json -Depth 10 | Set-Content -Path $ConfigFile
    Write-Host "✅ 配置已生成 (stdio 模式)" -ForegroundColor Green
} else {
    # HTTP 模式
    $HttpPort = Read-Host "HTTP Server 端口 (默认 8000)"
    if ([string]::IsNullOrEmpty($HttpPort)) {
        $HttpPort = "8000"
    }

    $Config = @{
        mcpServers = @{
            aceflow = @{
                url = "http://127.0.0.1:$HttpPort/sse"
                transport = "sse"
            }
        }
    }

    $Config | ConvertTo-Json -Depth 10 | Set-Content -Path $ConfigFile
    Write-Host "✅ 配置已生成 (HTTP 模式)" -ForegroundColor Green
    Write-Host ""
    Write-Host "请在新终端中启动 HTTP Server:"
    Write-Host "  python -m aceflow_mcp_server.server --transport sse --host 127.0.0.1 --port $HttpPort"
}

# 8. 显示配置文件内容
Write-Host ""
Write-Host "📄 配置文件内容:" -ForegroundColor Yellow
Get-Content $ConfigFile

# 9. 完成
Write-Host ""
Write-Host "✅ 配置完成!" -ForegroundColor Green
Write-Host "请重启 VSCode 使配置生效"
```

使用方法:
```powershell
powershell -ExecutionPolicy Bypass -File setup-cline-aceflow.ps1
```

---

## 🔍 验证配置

### 1. 检查配置文件

```bash
# Linux/macOS
cat ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Windows
type %APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

### 2. 测试 MCP Server

**stdio 模式**:
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
  python -m aceflow_mcp_server.server --transport stdio
```

**HTTP 模式**:
```bash
# 启动 Server
python -m aceflow_mcp_server.server --transport sse --host 127.0.0.1 --port 8000

# 测试连接
curl http://127.0.0.1:8000/health
```

### 3. 在 Cline 中测试

在 VSCode 中:
1. 打开 Cline 面板
2. 输入: "列出所有可用的 AceFlow 工具"
3. Cline 应该返回 17 个 MCP 工具

---

## 📚 相关文档

- [Internal Network Deployment Guide](INTERNAL_NETWORK_DEPLOYMENT_GUIDE.md) - 内网部署指南
- [Quick Start Guide](QUICK_START_GUIDE.md) - 快速开始
- [MCP Contract Tools Guide](MCP_CONTRACT_TOOLS_GUIDE.md) - 工具参考

---

**Created by**: AceFlow Team
**Last Updated**: 2025-01-04
**Version**: 1.0.0
