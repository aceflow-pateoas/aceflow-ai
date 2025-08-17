# AceFlow MCP 统一服务器

> 🚀 **统一架构，无缝体验** - 将原有的双服务器架构整合为单一、可配置、模块化的MCP服务器

## 📋 概述

AceFlow MCP 统一服务器是对原有 `aceflow-server` 和 `aceflow-enhanced-server` 的完全重构和统一。它提供了一个单一的入口点，支持多种运行模式，确保向后兼容性的同时提供了更强大的功能。

### 🎯 主要特性

- **🔄 统一架构**: 单一服务器支持所有功能模式
- **⚙️ 灵活配置**: 支持基础、标准、增强三种模式
- **🔌 模块化设计**: 按需加载功能模块
- **🔙 向后兼容**: 100%兼容原有API
- **🧪 全面测试**: 100%单元测试覆盖率
- **📊 智能监控**: 内置使用统计和性能监控

## 🚀 快速开始

### 安装

```bash
# 使用 uvx 安装（推荐）
uvx aceflow-mcp-server@latest

# 或使用 pip 安装
pip install aceflow-mcp-server
```

### 基础使用

```bash
# 基础模式（仅核心功能）
aceflow-unified --mode basic

# 标准模式（核心功能 + 可选功能）
aceflow-unified --mode standard

# 增强模式（所有功能）
aceflow-unified --mode enhanced
```

### MCP 配置

在你的 MCP 客户端配置中添加：

```json
{
  "mcpServers": {
    "aceflow-unified": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@latest"],
      "env": {
        "ACEFLOW_MODE": "enhanced"
      }
    }
  }
}
```

## 🔧 配置模式

### 基础模式 (Basic)
- ✅ 核心工具: `aceflow_init`, `aceflow_stage`, `aceflow_validate`
- ✅ 基础资源: `project_state`, `workflow_config`, `stage_guide`
- 🎯 适用于: 简单项目，快速原型

### 标准模式 (Standard)
- ✅ 包含基础模式所有功能
- ✅ 可选启用协作和智能功能
- 🎯 适用于: 大多数项目，平衡功能和性能

### 增强模式 (Enhanced)
- ✅ 包含标准模式所有功能
- ✅ 协作工具: `aceflow_respond`, `aceflow_collaboration_status`, `aceflow_task_execute`
- ✅ 智能工具: `aceflow_intent_analyze`, `aceflow_recommend`
- ✅ 增强资源: `collaboration_insights`, `usage_stats`
- 🎯 适用于: 复杂项目，团队协作

## 📚 API 参考

### 核心工具

#### `aceflow_init`
初始化 AceFlow 项目

```typescript
interface AceFlowInitParams {
  mode: "minimal" | "standard" | "complete" | "smart";
  project_name?: string;
  directory?: string;
}
```

#### `aceflow_stage`
管理项目阶段

```typescript
interface AceFlowStageParams {
  action: "next" | "previous" | "set" | "status";
  current_stage?: string;
  target_stage?: string;
}
```

#### `aceflow_validate`
验证项目状态

```typescript
interface AceFlowValidateParams {
  mode?: "basic" | "comprehensive" | "smart";
  target?: string;
  fix_issues?: boolean;
}
```

### 协作工具 (增强模式)

#### `aceflow_respond`
响应协作请求

```typescript
interface AceFlowRespondParams {
  request_id: string;
  response: string;
  user_id?: string;
}
```

#### `aceflow_collaboration_status`
获取协作状态

```typescript
interface AceFlowCollaborationStatusParams {
  project_id?: string;
}
```

#### `aceflow_task_execute`
执行协作任务

```typescript
interface AceFlowTaskExecuteParams {
  task_id?: string;
  auto_confirm?: boolean;
}
```

### 智能工具 (增强模式)

#### `aceflow_intent_analyze`
分析用户意图

```typescript
interface AceFlowIntentAnalyzeParams {
  user_input: string;
  context?: Record<string, any>;
}
```

#### `aceflow_recommend`
获取智能推荐

```typescript
interface AceFlowRecommendParams {
  context?: Record<string, any>;
}
```

## 🔧 高级配置

### 环境变量

```bash
# 设置运行模式
export ACEFLOW_MODE=enhanced

# 启用/禁用特定功能
export ACEFLOW_COLLABORATION_ENABLED=true
export ACEFLOW_INTELLIGENCE_ENABLED=true

# 性能配置
export ACEFLOW_CACHE_TTL=300
export ACEFLOW_MAX_CONCURRENT_REQUESTS=100
```

### 配置文件

创建 `aceflow-config.json`:

```json
{
  "version": "2.0",
  "mode": "enhanced",
  "core": {
    "enabled": true,
    "default_mode": "standard",
    "auto_advance": false,
    "quality_threshold": 0.8
  },
  "collaboration": {
    "enabled": true,
    "confirmation_timeout": 30,
    "auto_confirm": false,
    "interaction_level": "standard"
  },
  "intelligence": {
    "enabled": true,
    "intent_recognition": true,
    "adaptive_guidance": true,
    "learning_enabled": false
  },
  "monitoring": {
    "enabled": true,
    "usage_tracking": true,
    "performance_tracking": true,
    "data_retention_days": 30
  }
}
```

## 🔄 迁移指南

### 从 aceflow-server 迁移

如果你当前使用 `aceflow-server`:

1. **无需更改配置** - 统一服务器自动检测并兼容
2. **自动迁移** - 首次运行时自动迁移配置
3. **API 兼容** - 所有现有工具调用保持不变

```json
// 旧配置 (自动兼容)
{
  "mcpServers": {
    "aceflow-server": {
      "command": "uvx",
      "args": ["aceflow-server@latest"]
    }
  }
}

// 新配置 (推荐)
{
  "mcpServers": {
    "aceflow-unified": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@latest"],
      "env": {
        "ACEFLOW_MODE": "basic"
      }
    }
  }
}
```

### 从 aceflow-enhanced-server 迁移

如果你当前使用 `aceflow-enhanced-server`:

1. **设置增强模式** - 使用 `ACEFLOW_MODE=enhanced`
2. **保持所有功能** - 协作和智能工具完全兼容
3. **性能提升** - 统一架构提供更好的性能

```json
// 旧配置
{
  "mcpServers": {
    "aceflow-enhanced-server": {
      "command": "uvx",
      "args": ["aceflow-enhanced-server@latest"]
    }
  }
}

// 新配置
{
  "mcpServers": {
    "aceflow-unified": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@latest"],
      "env": {
        "ACEFLOW_MODE": "enhanced"
      }
    }
  }
}
```

## 🐛 故障排除

### 常见问题

#### 1. 服务器启动失败

**症状**: 服务器无法启动或连接失败

**解决方案**:
```bash
# 检查配置
aceflow-unified --validate-config

# 重置配置
aceflow-unified --reset-config

# 查看详细日志
aceflow-unified --debug
```

#### 2. 功能模块未加载

**症状**: 协作或智能工具不可用

**解决方案**:
```bash
# 检查模式设置
echo $ACEFLOW_MODE

# 强制启用功能
export ACEFLOW_COLLABORATION_ENABLED=true
export ACEFLOW_INTELLIGENCE_ENABLED=true
```

#### 3. 性能问题

**症状**: 响应缓慢或超时

**解决方案**:
```bash
# 启用缓存
export ACEFLOW_CACHE_ENABLED=true

# 调整并发限制
export ACEFLOW_MAX_CONCURRENT_REQUESTS=50

# 减少超时时间
export ACEFLOW_REQUEST_TIMEOUT=15
```

#### 4. 配置迁移问题

**症状**: 旧配置无法识别

**解决方案**:
```bash
# 手动触发迁移
aceflow-unified --migrate-config

# 查看迁移日志
aceflow-unified --migration-status

# 备份并重置
aceflow-unified --backup-config --reset-config
```

### 调试模式

启用详细日志记录:

```bash
export ACEFLOW_LOG_LEVEL=DEBUG
export ACEFLOW_LOG_FILE=aceflow-debug.log
aceflow-unified
```

### 健康检查

```bash
# 检查服务器状态
aceflow-unified --health-check

# 验证所有模块
aceflow-unified --module-status

# 运行诊断
aceflow-unified --diagnose
```

## 📊 监控和统计

### 使用统计

统一服务器自动收集使用统计（可选）:

- 工具调用频率
- 性能指标
- 错误率
- 用户模式偏好

### 访问统计

```bash
# 查看使用统计
aceflow-unified --stats

# 导出统计数据
aceflow-unified --export-stats stats.json

# 清除统计数据
aceflow-unified --clear-stats
```

## 🤝 贡献

我们欢迎社区贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 开发设置

```bash
# 克隆仓库
git clone https://github.com/your-org/aceflow-mcp-server.git
cd aceflow-mcp-server

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
python -m pytest

# 运行单元测试套件
python test_comprehensive_unit_tests.py
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [MCP 协议文档](https://modelcontextprotocol.io/)
- [FastMCP 框架](https://github.com/jlowin/fastmcp)
- [问题反馈](https://github.com/your-org/aceflow-mcp-server/issues)
- [讨论区](https://github.com/your-org/aceflow-mcp-server/discussions)

## 📈 版本历史

### v2.0.0 (统一架构)
- 🎉 统一 aceflow-server 和 aceflow-enhanced-server
- ✨ 新增模块化架构
- 🔧 改进配置系统
- 📊 内置监控和统计
- 🧪 100% 测试覆盖率

### v1.x.x (传统版本)
- aceflow-server: 基础功能
- aceflow-enhanced-server: 增强功能

---

**🚀 开始使用 AceFlow MCP 统一服务器，体验更强大、更灵活的工作流管理！**