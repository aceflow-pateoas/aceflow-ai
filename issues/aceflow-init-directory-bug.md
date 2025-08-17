# AceFlow Init 目录路径错误 Bug 报告

## 🐛 问题描述

`aceflow_init` 工具在初始化项目时，返回的 `directory` 路径指向了错误的位置（VS Code安装目录），而不是用户当前的项目目录。

## 📊 问题详情

### 实际行为
- **输入**: `{"mode": "complete", "project_name": "taskmaster"}`
- **输出目录**: `"D:\\Program Files\\Microsoft VS Code"`
- **创建的文件**: 在VS Code安装目录下创建了项目文件

### 预期行为
- **预期目录**: 当前项目工作目录（如 `D:\\AI\\aceflow-ai`）
- **预期文件位置**: 在用户项目目录下创建 `.aceflow/`、`aceflow_result/` 等文件

## 🔍 问题分析

### 可能原因
1. **工作目录获取错误**: MCP服务器可能使用了错误的方法获取当前工作目录
2. **MCP协议上下文问题**: 在IDE环境中运行时继承了IDE的工作目录
3. **路径解析逻辑错误**: `directory` 参数处理不当
4. **环境变量问题**: 依赖了错误的环境变量

### 影响范围
- **文件创建位置错误**: 所有项目文件创建在错误位置
- **后续操作失败**: 其他工具可能无法找到项目文件
- **用户体验问题**: 用户无法在项目目录中找到生成的文件

## 🎯 复现步骤

1. 在Cursor/VS Code中打开项目目录
2. 使用MCP调用 `aceflow_init` 工具
3. 传入参数: `{"mode": "complete", "project_name": "taskmaster"}`
4. 观察返回的 `directory` 字段值
5. 检查文件实际创建位置

## 📋 完整的测试数据

### 输入
```json
{
  "mode": "complete",
  "project_name": "taskmaster"
}
```

### 实际输出
```json
{
  "success": true,
  "message": "Project 'taskmaster' initialized successfully in complete mode",
  "project_info": {
    "name": "taskmaster",
    "mode": "complete",
    "directory": "D:\\Program Files\\Microsoft VS Code",
    "created_files": [
      ".aceflow/",
      "aceflow_result/",
      ".aceflow/current_state.json",
      ".aceflow/config/",
      ".aceflow/templates/",
      ".aceflow/core/",
      ".clinerules/",
      ".aceflow/templates/",
      ".clinerules/system_prompt.md",
      ".clinerules/aceflow_integration.md",
      ".clinerules/spec_summary.md",
      ".clinerules/spec_query_helper.md",
      ".clinerules/quality_standards.md",
      ".aceflow/template.yaml",
      "README_ACEFLOW.md"
    ]
  }
}
```

### 预期输出
```json
{
  "success": true,
  "message": "Project 'taskmaster' initialized successfully in complete mode",
  "project_info": {
    "name": "taskmaster",
    "mode": "complete",
    "directory": "D:\\AI\\aceflow-ai",  // 应该是当前项目目录
    "created_files": [
      // 同样的文件列表，但创建在正确位置
    ]
  }
}
```

## 🔧 可能的解决方案

### 方案1: 改进目录获取逻辑
```python
def get_project_directory(directory_param=None):
    """获取正确的项目目录"""
    if directory_param:
        return directory_param
    
    # 优先级顺序
    candidates = [
        os.environ.get('ACEFLOW_WORKSPACE'),
        os.environ.get('WORKSPACE_FOLDER'),
        os.environ.get('PWD'),
        os.getcwd()
    ]
    
    for candidate in candidates:
        if candidate and is_valid_project_directory(candidate):
            return candidate
    
    # 如果都不合适，使用当前目录但给出警告
    return os.getcwd()

def is_valid_project_directory(path):
    """检查是否是合理的项目目录"""
    ide_paths = [
        "Microsoft VS Code",
        "Visual Studio Code", 
        "Cursor",
        "Program Files"
    ]
    
    return not any(ide_path in path for ide_path in ide_paths)
```

### 方案2: MCP客户端传递工作目录
```python
# 在MCP工具定义中添加工作目录参数
@mcp.tool
def aceflow_init(
    mode: str,
    project_name: Optional[str] = None,
    directory: Optional[str] = None,
    workspace_folder: Optional[str] = None  # 新增参数
) -> Dict[str, Any]:
    # 使用workspace_folder作为优先选择
    target_dir = workspace_folder or directory or get_project_directory()
```

### 方案3: 环境变量配置
```python
# 支持通过环境变量配置工作目录
def load_workspace_from_env():
    """从环境变量加载工作空间配置"""
    return (
        os.environ.get('ACEFLOW_WORKSPACE') or
        os.environ.get('WORKSPACE_ROOT') or
        os.environ.get('PROJECT_ROOT')
    )
```

## 🚨 紧急程度

**高优先级** - 这个bug会导致：
1. 用户无法找到生成的项目文件
2. 后续工作流操作可能失败
3. 需要手动清理错误位置的文件
4. 严重影响用户体验

## 📝 修复建议

### 立即修复
1. **检查** `aceflow_mcp_server/tools.py` 中的 `aceflow_init` 实现
2. **修复** 目录获取逻辑，添加IDE目录检测
3. **测试** 在不同环境下的行为

### 后续改进
1. **添加** 目录验证和警告机制
2. **支持** 环境变量配置
3. **改进** MCP客户端集成
4. **添加** 配置文件支持

## 🧪 测试计划

### 测试环境
- [ ] Windows + VS Code
- [ ] Windows + Cursor  
- [ ] 命令行环境
- [ ] 不同的项目目录结构

### 测试用例
- [ ] 默认参数调用
- [ ] 指定directory参数
- [ ] 设置环境变量
- [ ] 在IDE中调用
- [ ] 在命令行中调用

## 📅 时间线

- **发现时间**: 2024-01-XX
- **报告时间**: 2024-01-XX  
- **预期修复**: 高优先级，需要尽快修复
- **验证时间**: 修复后需要全面测试

## 🔗 相关文件

- `aceflow-mcp-server/aceflow_mcp_server/tools.py` - 主要修复位置
- `aceflow-mcp-server/aceflow_mcp_server/server.py` - 可能需要调整
- `aceflow-mcp-server/aceflow_mcp_server/core/project_manager.py` - 项目管理逻辑

## 📞 联系信息

- **报告人**: 用户测试反馈
- **负责人**: 待分配
- **状态**: 待修复

---

*此问题记录创建于: 2024-01-XX*
*最后更新: 2024-01-XX*