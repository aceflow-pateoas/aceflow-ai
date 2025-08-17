# AceFlow MCP Unified Server

> 🚀 **统一架构，无缝体验** - 将原有的双服务器架构整合为单一、可配置、模块化的MCP服务器

[![PyPI version](https://badge.fury.io/py/aceflow-mcp-server.svg)](https://badge.fury.io/py/aceflow-mcp-server)
[![Python Support](https://img.shields.io/pypi/pyversions/aceflow-mcp-server.svg)](https://pypi.org/project/aceflow-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/aceflow/mcp-server/workflows/Tests/badge.svg)](https://github.com/aceflow/mcp-server/actions)

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
# 使用 pip 安装
pip install aceflow-mcp-server

# 使用 uvx 安装（推荐）
uvx aceflow-mcp-server
```

### 基础使用

```bash
# 启动服务器 - 基础模式
aceflow-unified serve --mode basic

# 启动服务器 - 增强模式
aceflow-unified serve --mode enhanced

# 查看帮助
aceflow-unified --help
```

### MCP 配置

在你的 MCP 客户端配置中添加：

```json
{
  "mcpServers": {
    "aceflow-unified": {
      "command": "aceflow-unified",
      "args": ["serve", "--mode", "enhanced"],
      "env": {
        "ACEFLOW_LOG_LEVEL": "INFO"
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

```python
result = await aceflow_init(
    mode="standard",
    project_name="my-project",
    directory="./my-project"
)
```

#### `aceflow_stage`
管理项目阶段

```python
result = await aceflow_stage(
    action="next",
    current_stage="planning"
)
```

#### `aceflow_validate`
验证项目状态

```python
result = await aceflow_validate(
    mode="basic",
    target="project"
)
```

### 协作工具 (增强模式)

#### `aceflow_respond`
响应协作请求

```python
result = await aceflow_respond(
    request_id="req-123",
    response="Approved",
    user_id="user-456"
)
```

### 智能工具 (增强模式)

#### `aceflow_intent_analyze`
分析用户意图

```python
result = await aceflow_intent_analyze(
    user_input="Create a new web project",
    context={"type": "project_creation"}
)
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
  }
}
```

## 🔄 迁移指南

### 从 aceflow-server 迁移

```bash
# 自动迁移配置
aceflow-unified config --migrate

# 验证迁移结果
aceflow-unified config --validate
```

### 从 aceflow-enhanced-server 迁移

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
      "command": "aceflow-unified",
      "args": ["serve", "--mode", "enhanced"]
    }
  }
}
```

## 🧪 开发

### 安装开发依赖

```bash
# 克隆仓库
git clone https://github.com/aceflow/mcp-server.git
cd mcp-server

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行类型检查
mypy aceflow_mcp_server

# 格式化代码
black aceflow_mcp_server
isort aceflow_mcp_server
```

### 运行测试

```bash
# 运行所有测试
aceflow-unified test

# 运行单元测试
aceflow-unified test --mode unit

# 运行集成测试
aceflow-unified test --mode integration

# 运行兼容性测试
aceflow-unified test --mode compatibility
```

## 🐛 故障排除

### 常见问题

#### 服务器启动失败

```bash
# 检查系统状态
aceflow-unified doctor

# 验证配置
aceflow-unified config --validate

# 查看详细日志
aceflow-unified serve --mode enhanced --log-level DEBUG
```

#### 功能模块未加载

```bash
# 检查模式设置
echo $ACEFLOW_MODE

# 强制启用功能
export ACEFLOW_COLLABORATION_ENABLED=true
export ACEFLOW_INTELLIGENCE_ENABLED=true
```

更多故障排除信息，请查看 [故障排除指南](https://docs.aceflow.dev/troubleshooting)。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [文档](https://docs.aceflow.dev)
- [问题反馈](https://github.com/aceflow/mcp-server/issues)
- [讨论区](https://github.com/aceflow/mcp-server/discussions)
- [更新日志](https://github.com/aceflow/mcp-server/blob/main/CHANGELOG.md)

## 🤝 贡献

我们欢迎社区贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详情。

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