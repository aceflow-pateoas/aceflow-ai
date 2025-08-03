# VSCode Cline MCP 故障排除指南

## 问题描述
在 VSCode Cline 中使用 AceFlow MCP Server 时出现大量 DEBUG 日志输出。

## 解决方案

### 1. 调整日志级别
将 MCP 配置中的日志级别从 `DEBUG` 改为 `WARNING` 或 `ERROR`：

```json
{
  "mcpServers": {
    "aceflow": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@1.0.3"],
      "env": {
        "ACEFLOW_LOG_LEVEL": "WARNING"
      }
    }
  }
}
```

### 2. VSCode Cline 专用配置
在项目根目录创建 `.cline_mcp_settings.json`：

```json
{
  "mcpServers": {
    "aceflow": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@1.0.3"],
      "env": {
        "ACEFLOW_LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

### 3. 验证安装
确保 AceFlow MCP Server 正确安装：

```bash
# 检查版本
uvx aceflow-mcp-server@1.0.3 --version

# 测试运行
uvx aceflow-mcp-server@1.0.3 --transport stdio --log-level ERROR
```

### 4. 常见问题

#### 问题：大量 DEBUG 日志
**原因**: 日志级别设置过低
**解决**: 将日志级别设置为 `WARNING` 或 `ERROR`

#### 问题：连接超时
**原因**: 网络问题或包版本不匹配
**解决**: 
- 检查网络连接
- 使用最新版本 `@1.0.3`
- 尝试本地安装：`pip install aceflow-mcp-server==1.0.3`

#### 问题：工具调用失败
**原因**: 权限或配置问题
**解决**:
- 确保 `autoApprove` 列表包含所需工具
- 检查环境变量设置

### 5. 测试配置
使用以下命令测试 MCP 连接：

```python
# 在 Python 中测试
import subprocess
result = subprocess.run(['uvx', 'aceflow-mcp-server@1.0.3', '--version'], 
                       capture_output=True, text=True)
print(result.stdout)
```

### 6. 联系支持
如果问题仍然存在，请提供：
- VSCode Cline 版本
- 操作系统信息
- 完整的错误日志
- MCP 配置文件内容

## 最佳实践

1. **生产环境**: 使用 `WARNING` 或 `ERROR` 日志级别
2. **开发调试**: 临时使用 `DEBUG` 级别
3. **定期更新**: 保持 AceFlow MCP Server 为最新版本
4. **配置备份**: 保存工作的配置文件