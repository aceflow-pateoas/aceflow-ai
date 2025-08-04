# 🔄 AceFlow MCP Server 模板同步系统

## 📋 概述

为了确保 AceFlow MCP Server 与主项目的模板文件保持一致，我们实现了一个自动化的模板同步系统。

## 🏗️ 架构设计

```
aceflow/
├── templates/                    # 主模板目录（源头）
│   ├── s1_user_story.md         # 用户故事模板
│   ├── s2_tasks_main.md         # 任务分解模板
│   └── ...                      # 其他模板文件
└── ...

aceflow-mcp-server/
├── aceflow_mcp_server/
│   ├── templates/               # 同步的模板副本
│   │   ├── s1_user_story.md    # 从主模板同步
│   │   ├── sync_manifest.json  # 同步清单
│   │   └── ...
│   └── config/
│       └── template_config.py   # 模板配置管理
├── scripts/
│   ├── sync_templates.py        # 模板同步脚本
│   ├── build_hook.py           # 构建钩子
│   └── dev_workflow.py         # 开发工作流
└── pyproject.toml              # 包含模板文件配置
```

## 🔧 核心组件

### 1. 模板同步脚本 (`scripts/sync_templates.py`)

**功能**：
- 自动检测主项目模板文件的变化
- 将更新的模板文件同步到 MCP 服务器
- 维护同步清单，避免重复同步
- 提供同步状态检查

**使用方法**：
```bash
# 同步模板文件
python scripts/sync_templates.py --sync

# 检查同步状态
python scripts/sync_templates.py --check

# 强制同步所有文件
python scripts/sync_templates.py --sync --force
```

### 2. 构建钩子 (`scripts/build_hook.py`)

**功能**：
- 在打包前自动执行模板同步
- 确保发布的包包含最新模板

**集成方式**：
```toml
# pyproject.toml
[tool.hatch.build.hooks.custom]
path = "scripts/build_hook.py"
```

### 3. 模板配置管理 (`aceflow_mcp_server/config/template_config.py`)

**功能**：
- 智能查找模板目录（优先使用内置模板）
- 管理阶段到模板文件的映射关系
- 提供模板配置信息查询

### 4. 开发工作流脚本 (`scripts/dev_workflow.py`)

**功能**：
- 简化常见开发任务
- 集成模板同步到开发流程

**使用方法**：
```bash
# 同步模板
python scripts/dev_workflow.py sync

# 检查状态
python scripts/dev_workflow.py check

# 构建包（自动同步模板）
python scripts/dev_workflow.py build

# 完整工作流
python scripts/dev_workflow.py all
```

## 📦 打包集成

### 包含模板文件

```toml
# pyproject.toml
[tool.hatch.build.targets.wheel.shared-data]
"aceflow_mcp_server/templates" = "aceflow_mcp_server/templates"
```

### 自动同步

构建时会自动执行模板同步，确保包含最新模板。

## 🔄 工作流程

### 开发阶段

1. **修改主项目模板**：在 `aceflow/templates/` 中修改模板文件
2. **同步到 MCP 服务器**：运行 `python scripts/sync_templates.py --sync`
3. **测试验证**：确保 MCP 服务器使用新模板正常工作
4. **提交代码**：同时提交主项目和 MCP 服务器的变更

### 发布阶段

1. **自动同步**：构建钩子自动同步最新模板
2. **打包发布**：模板文件被包含在发布包中
3. **用户使用**：用户安装的 MCP 服务器包含最新模板

## 🎯 优势

### ✅ 一致性保证
- 主项目模板是唯一的真实来源
- 自动同步确保版本一致性
- 构建时验证确保发布质量

### ✅ 独立部署
- MCP 服务器包含完整的模板文件
- 不依赖外部文件或网络资源
- 用户安装即可使用

### ✅ 开发友好
- 简化的同步命令
- 清晰的状态检查
- 集成的开发工作流

### ✅ 自动化
- 构建时自动同步
- 避免手动操作错误
- 持续集成友好

## 🔍 监控和维护

### 检查同步状态

```bash
python scripts/sync_templates.py --check
```

输出示例：
```
📁 主模板目录: /path/to/aceflow/templates
📁 MCP模板目录: /path/to/aceflow-mcp-server/aceflow_mcp_server/templates
🕒 上次同步: 2025-08-04T15:17:22.695971
📊 总模板数: 44
✅ 所有模板文件都已同步
```

### 同步清单

系统维护一个 `sync_manifest.json` 文件，记录：
- 上次同步时间
- 每个文件的哈希值
- 同步历史

## 🚨 注意事项

### 开发时
- 始终在主项目中修改模板文件
- 修改后及时同步到 MCP 服务器
- 测试时确保使用同步后的模板

### 发布时
- 构建前检查同步状态
- 确保所有模板变更都已提交
- 验证构建包含正确的模板文件

### 维护时
- 定期检查同步状态
- 清理不再使用的模板文件
- 更新模板映射关系

## 🔧 故障排除

### 同步失败
```bash
# 强制重新同步所有文件
python scripts/sync_templates.py --sync --force
```

### 模板缺失
```bash
# 检查主项目模板目录是否存在
python scripts/sync_templates.py --check
```

### 构建问题
```bash
# 手动执行构建前同步
python scripts/sync_templates.py --sync
python -m build
```

---

通过这个模板同步系统，我们确保了 AceFlow MCP Server 能够：
1. **保持模板一致性** - 与主项目完全同步
2. **独立部署** - 包含完整的模板文件
3. **自动化维护** - 减少手动操作和错误
4. **开发友好** - 简化开发和发布流程