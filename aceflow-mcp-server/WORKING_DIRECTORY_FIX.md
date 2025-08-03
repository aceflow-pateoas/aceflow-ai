# AceFlow MCP Server - 工作目录问题修复

## 问题描述

用户报告在使用CodeBuddy AI Agent调用AceFlow MCP Server初始化项目时，文件被创建在错误的位置：

**错误行为**:
- 预期：在用户当前项目目录创建AceFlow文件
- 实际：在CodeBuddy安装目录 `D:\Program Files\CodeBuddy` 创建文件

**返回结果**:
```json
{
  "success": true,
  "message": "Project 'taskmaster' initialized successfully in standard mode",
  "project_info": {
    "name": "taskmaster",
    "mode": "standard",
    "directory": "D:\\Program Files\\CodeBuddy",  // ❌ 错误位置
    "created_files": [...]
  }
}
```

## 问题根因

1. **工作目录检测失败**: MCP服务器使用 `os.getcwd()` 获取工作目录，但这返回的是MCP服务器进程的工作目录，而不是AI客户端的工作目录
2. **缺少客户端上下文**: MCP协议中没有直接传递客户端工作目录的标准方式
3. **环境变量缺失**: 客户端没有设置适当的环境变量来指示真实的工作目录

## 解决方案

### 1. 智能工作目录检测 (已实现)

**多层次检测策略**:
```python
client_working_dir = (
    os.environ.get('CLIENT_CWD') or      # 客户端设置的工作目录
    os.environ.get('PWD') or             # POSIX标准工作目录
    os.environ.get('INIT_CWD') or        # npm/npx原始目录
    os.environ.get('PROJECT_ROOT') or    # 项目根目录
    self._detect_client_directory() or   # 父进程检测
    os.getcwd()                          # 最后fallback
)
```

**父进程检测**:
```python
def _detect_client_directory(self) -> Optional[str]:
    try:
        import psutil
        parent_process = psutil.Process().parent()
        if parent_process:
            parent_name = parent_process.name().lower()
            if any(editor in parent_name for editor in ['code', 'cursor', 'vscode', 'codebuddy']):
                return parent_process.cwd()
    except:
        pass
    return None
```

### 2. 增强调试信息 (已实现)

**详细的调试日志**:
```python
print(f"[DEBUG] Working directory detection:", file=sys.stderr)
print(f"[DEBUG] Instance working_directory: {self.working_directory}", file=sys.stderr)
print(f"[DEBUG] PWD: {os.environ.get('PWD')}", file=sys.stderr)
print(f"[DEBUG] CLIENT_CWD: {os.environ.get('CLIENT_CWD')}", file=sys.stderr)
print(f"[DEBUG] Selected target_dir: {target_dir}", file=sys.stderr)
```

**返回调试信息**:
```json
{
  "debug_info": {
    "detected_working_dir": "实际检测到的目录",
    "original_cwd": "MCP服务器的工作目录",
    "pwd_env": "PWD环境变量值",
    "cwd_env": "CWD环境变量值"
  }
}
```

### 3. 客户端配置建议

**CodeBuddy配置**:
```json
{
  "mcpServers": {
    "aceflow": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@1.0.5"],
      "env": {
        "CLIENT_CWD": "{currentWorkingDirectory}",
        "PWD": "{currentWorkingDirectory}",
        "ACEFLOW_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**其他客户端配置**:
```json
{
  "mcpServers": {
    "aceflow": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@1.0.5"],
      "env": {
        "CLIENT_CWD": "$PWD",
        "PROJECT_ROOT": "$PWD"
      }
    }
  }
}
```

## 修复内容

### 文件变更
1. **tools.py**: 增强工作目录检测逻辑
2. **mcp_stdio_server.py**: 智能父进程检测
3. **pyproject.toml**: 版本升级到v1.0.5，添加psutil依赖

### 新增功能
1. ✅ 多层次工作目录检测策略
2. ✅ 父进程检测支持
3. ✅ 详细调试信息输出
4. ✅ 环境变量fallback机制
5. ✅ 错误处理和容错机制

## 测试验证

### 1. 本地测试
```bash
# 设置环境变量测试
export CLIENT_CWD="/path/to/project"
uvx aceflow-mcp-server@1.0.5

# 在项目目录测试
cd /path/to/my-project
echo '{"method":"tools/call","params":{"name":"aceflow_init","arguments":{"mode":"minimal"}}}' | uvx aceflow-mcp-server@1.0.5
```

### 2. 客户端测试
- 在CodeBuddy中测试初始化
- 检查返回的debug_info
- 验证文件创建位置

## 部署

### 1. 发布新版本
```bash
cd aceflow-mcp-server
python -m build
twine upload dist/*
```

### 2. 用户升级
```bash
# 自动升级到最新版本
uvx aceflow-mcp-server@latest

# 或指定版本
uvx aceflow-mcp-server@1.0.5
```

## 预期效果

**修复后的预期返回**:
```json
{
  "success": true,
  "message": "Project 'taskmaster' initialized successfully in standard mode",
  "project_info": {
    "name": "taskmaster",
    "mode": "standard",
    "directory": "C:\\Users\\User\\Projects\\taskmaster",  // ✅ 正确位置
    "created_files": [...],
    "debug_info": {
      "detected_working_dir": "C:\\Users\\User\\Projects\\taskmaster",
      "original_cwd": "D:\\Program Files\\CodeBuddy",
      "pwd_env": "C:\\Users\\User\\Projects\\taskmaster"
    }
  }
}
```

这个修复确保AceFlow文件始终创建在用户的项目目录中，而不是AI客户端的安装目录。