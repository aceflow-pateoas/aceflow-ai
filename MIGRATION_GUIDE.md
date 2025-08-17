# AceFlow MCP 服务器迁移指南

> 🔄 **无缝升级** - 从旧版本平滑迁移到统一架构

## 📋 概述

本指南帮助你从现有的 `aceflow-server` 或 `aceflow-enhanced-server` 迁移到新的统一架构。迁移过程设计为**零停机时间**和**100%向后兼容**。

## 🎯 迁移优势

### 为什么要迁移？

- **🔄 统一架构**: 单一服务器替代双服务器架构
- **⚡ 性能提升**: 优化的模块化设计
- **🔧 灵活配置**: 支持多种运行模式
- **📊 增强监控**: 内置使用统计和性能监控
- **🧪 更好测试**: 100%单元测试覆盖率
- **🔮 未来保障**: 持续维护和新功能支持

### 迁移时间线

| 版本 | 状态 | 支持期限 | 建议行动 |
|------|------|----------|----------|
| aceflow-server v1.x | 🟡 维护模式 | 2025年6月 | 尽快迁移 |
| aceflow-enhanced-server v1.x | 🟡 维护模式 | 2025年6月 | 尽快迁移 |
| aceflow-mcp-server v2.x | 🟢 活跃开发 | 长期支持 | 推荐使用 |

## 🚀 快速迁移

### 自动迁移（推荐）

统一服务器支持自动检测和迁移现有配置：

```bash
# 1. 安装统一服务器
uvx aceflow-mcp-server@latest

# 2. 自动迁移（首次运行时自动执行）
aceflow-unified --auto-migrate

# 3. 验证迁移结果
aceflow-unified --migration-status
```

### 手动迁移

如果需要更多控制，可以手动执行迁移：

```bash
# 1. 备份现有配置
aceflow-unified --backup-existing-config

# 2. 执行迁移
aceflow-unified --migrate-config --source-type auto

# 3. 验证配置
aceflow-unified --validate-config

# 4. 测试功能
aceflow-unified --test-migration
```

## 📊 迁移场景

### 场景1: 从 aceflow-server 迁移

#### 当前配置
```json
{
  "mcpServers": {
    "aceflow-server": {
      "command": "uvx",
      "args": ["aceflow-server@latest"],
      "env": {
        "ACEFLOW_PROJECT_ROOT": "/path/to/project"
      }
    }
  }
}
```

#### 迁移后配置
```json
{
  "mcpServers": {
    "aceflow-unified": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@latest"],
      "env": {
        "ACEFLOW_MODE": "basic",
        "ACEFLOW_PROJECT_ROOT": "/path/to/project"
      }
    }
  }
}
```

#### 迁移步骤

1. **保持现有配置不变**（向后兼容）
2. **或者更新为推荐配置**：

```bash
# 方法1: 保持现有配置（自动兼容）
# 无需任何更改，统一服务器会自动识别

# 方法2: 更新为新配置（推荐）
# 更新 MCP 配置文件
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

3. **验证功能**：

```bash
# 测试核心工具
aceflow_init --mode standard --project-name test-migration
aceflow_stage --action status
aceflow_validate --mode basic
```

### 场景2: 从 aceflow-enhanced-server 迁移

#### 当前配置
```json
{
  "mcpServers": {
    "aceflow-enhanced-server": {
      "command": "uvx",
      "args": ["aceflow-enhanced-server@latest"],
      "env": {
        "ENABLE_COLLABORATION": "true",
        "ENABLE_INTELLIGENCE": "true"
      }
    }
  }
}
```

#### 迁移后配置
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

#### 迁移步骤

1. **自动迁移环境变量**：

```bash
# 旧环境变量会自动映射到新格式
ENABLE_COLLABORATION=true → ACEFLOW_COLLABORATION_ENABLED=true
ENABLE_INTELLIGENCE=true → ACEFLOW_INTELLIGENCE_ENABLED=true
```

2. **更新配置**：

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

3. **验证增强功能**：

```bash
# 测试协作工具
aceflow_respond --request-id test --response "Migration test"
aceflow_collaboration_status
aceflow_task_execute --task-id test-task

# 测试智能工具
aceflow_intent_analyze --user-input "Create a new project"
aceflow_recommend --context '{"type": "project_setup"}'
```

### 场景3: 双服务器环境迁移

如果你同时使用两个服务器：

#### 当前配置
```json
{
  "mcpServers": {
    "aceflow-server": {
      "command": "uvx",
      "args": ["aceflow-server@latest"]
    },
    "aceflow-enhanced-server": {
      "command": "uvx",
      "args": ["aceflow-enhanced-server@latest"]
    }
  }
}
```

#### 迁移后配置
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

#### 迁移步骤

1. **分阶段迁移**：

```bash
# 阶段1: 添加统一服务器（并行运行）
{
  "mcpServers": {
    "aceflow-server": { /* 现有配置 */ },
    "aceflow-enhanced-server": { /* 现有配置 */ },
    "aceflow-unified": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@latest"],
      "env": { "ACEFLOW_MODE": "enhanced" }
    }
  }
}

# 阶段2: 测试统一服务器功能
# 阶段3: 移除旧服务器配置
```

2. **功能验证**：

```bash
# 验证所有功能都可用
aceflow-unified --test-all-tools
aceflow-unified --compare-with-legacy
```

## 🔧 详细迁移步骤

### 步骤1: 环境准备

```bash
# 1. 备份现有配置
cp ~/.config/mcp/config.json ~/.config/mcp/config.json.backup

# 2. 检查当前版本
aceflow-server --version  # 如果存在
aceflow-enhanced-server --version  # 如果存在

# 3. 安装统一服务器
uvx aceflow-mcp-server@latest

# 4. 验证安装
aceflow-unified --version
```

### 步骤2: 配置迁移

```bash
# 1. 自动检测现有配置
aceflow-unified --detect-existing-config

# 2. 生成迁移计划
aceflow-unified --generate-migration-plan

# 3. 执行迁移
aceflow-unified --execute-migration

# 4. 验证迁移结果
aceflow-unified --validate-migration
```

### 步骤3: 功能测试

```bash
# 1. 基础功能测试
aceflow-unified --test-core-tools

# 2. 协作功能测试（如果启用）
aceflow-unified --test-collaboration-tools

# 3. 智能功能测试（如果启用）
aceflow-unified --test-intelligence-tools

# 4. 性能基准测试
aceflow-unified --benchmark
```

### 步骤4: 生产部署

```bash
# 1. 在测试环境验证
aceflow-unified --test-environment staging

# 2. 生产环境部署
aceflow-unified --deploy-production

# 3. 监控部署状态
aceflow-unified --monitor-deployment

# 4. 回滚计划（如需要）
aceflow-unified --prepare-rollback
```

## 🔍 配置映射

### 环境变量映射

| 旧变量 | 新变量 | 说明 |
|--------|--------|------|
| `ENABLE_COLLABORATION` | `ACEFLOW_COLLABORATION_ENABLED` | 协作功能开关 |
| `ENABLE_INTELLIGENCE` | `ACEFLOW_INTELLIGENCE_ENABLED` | 智能功能开关 |
| `ENABLE_MONITORING` | `ACEFLOW_MONITORING_ENABLED` | 监控功能开关 |
| `DEBUG_MODE` | `ACEFLOW_LOG_LEVEL=DEBUG` | 调试模式 |
| `PROJECT_ROOT` | `ACEFLOW_PROJECT_ROOT` | 项目根目录 |

### 配置文件映射

#### aceflow-server 配置
```json
// 旧配置
{
  "mode": "standard",
  "auto_advance": false,
  "quality_threshold": 0.8
}

// 新配置
{
  "mode": "basic",
  "core": {
    "default_mode": "standard",
    "auto_advance": false,
    "quality_threshold": 0.8
  }
}
```

#### aceflow-enhanced-server 配置
```json
// 旧配置
{
  "collaboration": {
    "timeout": 30,
    "auto_confirm": false
  },
  "intelligence": {
    "intent_recognition": true,
    "adaptive_guidance": true
  }
}

// 新配置
{
  "mode": "enhanced",
  "collaboration": {
    "enabled": true,
    "confirmation_timeout": 30,
    "auto_confirm": false
  },
  "intelligence": {
    "enabled": true,
    "intent_recognition": true,
    "adaptive_guidance": true
  }
}
```

## ⚠️ 迁移注意事项

### 兼容性保证

- **API兼容**: 所有现有工具调用保持不变
- **参数兼容**: 工具参数格式完全兼容
- **响应兼容**: 返回数据格式保持一致
- **配置兼容**: 旧配置自动识别和转换

### 已知差异

#### 1. 日志格式变化
```bash
# 旧格式
[INFO] aceflow-server: Project initialized

# 新格式
[INFO] aceflow-unified[core]: Project initialized
```

#### 2. 错误消息改进
```bash
# 旧错误消息
Error: Invalid mode

# 新错误消息
Error: Invalid mode 'invalid_mode'. Valid modes are: basic, standard, enhanced, auto
```

#### 3. 性能指标
```bash
# 新增性能监控
aceflow-unified --stats
# 显示详细的性能统计
```

### 潜在问题

#### 1. 端口冲突
如果同时运行多个服务器：

```bash
# 检查端口使用
aceflow-unified --check-ports

# 指定端口
aceflow-unified --port 8080
```

#### 2. 配置冲突
多个配置文件存在时：

```bash
# 查看配置优先级
aceflow-unified --show-config-sources

# 指定配置文件
aceflow-unified --config-path ./my-config.json
```

#### 3. 权限问题
文件权限可能需要调整：

```bash
# 检查权限
aceflow-unified --check-permissions

# 修复权限
aceflow-unified --fix-permissions
```

## 🧪 测试和验证

### 自动化测试

```bash
# 运行完整测试套件
aceflow-unified --run-tests

# 运行迁移验证测试
aceflow-unified --test-migration

# 运行性能回归测试
aceflow-unified --test-performance
```

### 手动验证清单

#### ✅ 基础功能验证
- [ ] `aceflow_init` 工具正常工作
- [ ] `aceflow_stage` 工具正常工作
- [ ] `aceflow_validate` 工具正常工作
- [ ] 所有资源可正常访问

#### ✅ 协作功能验证（如果启用）
- [ ] `aceflow_respond` 工具正常工作
- [ ] `aceflow_collaboration_status` 工具正常工作
- [ ] `aceflow_task_execute` 工具正常工作
- [ ] 协作流程完整可用

#### ✅ 智能功能验证（如果启用）
- [ ] `aceflow_intent_analyze` 工具正常工作
- [ ] `aceflow_recommend` 工具正常工作
- [ ] 智能推荐准确有效

#### ✅ 配置验证
- [ ] 配置文件格式正确
- [ ] 环境变量正确应用
- [ ] 模式切换正常工作
- [ ] 性能配置生效

## 🔄 回滚计划

如果迁移遇到问题，可以快速回滚：

### 自动回滚

```bash
# 回滚到迁移前状态
aceflow-unified --rollback

# 恢复备份配置
aceflow-unified --restore-backup
```

### 手动回滚

```bash
# 1. 停止统一服务器
aceflow-unified --stop

# 2. 恢复旧配置
cp ~/.config/mcp/config.json.backup ~/.config/mcp/config.json

# 3. 重新安装旧版本
uvx aceflow-server@1.x.x  # 或 aceflow-enhanced-server@1.x.x

# 4. 验证功能
aceflow-server --test  # 或相应的测试命令
```

## 📊 迁移后优化

### 性能优化

```json
{
  "performance_config": {
    "cache_ttl": 600,
    "max_concurrent_requests": 100,
    "request_timeout": 30
  },
  "feature_flags": {
    "caching": true,
    "resource_routing": true
  }
}
```

### 监控设置

```bash
# 启用详细监控
export ACEFLOW_MONITORING_ENABLED=true
export ACEFLOW_USAGE_TRACKING=true
export ACEFLOW_PERFORMANCE_TRACKING=true

# 查看监控数据
aceflow-unified --stats
aceflow-unified --health-check
```

### 安全加固

```json
{
  "collaboration": {
    "auto_confirm": false,
    "interaction_level": "full"
  },
  "intelligence": {
    "learning_enabled": false
  }
}
```

## 🆘 故障排除

### 常见问题

#### 1. 迁移失败
```bash
# 查看迁移日志
aceflow-unified --migration-log

# 重新尝试迁移
aceflow-unified --retry-migration

# 手动修复配置
aceflow-unified --fix-config
```

#### 2. 功能不可用
```bash
# 检查模块状态
aceflow-unified --module-status

# 重新初始化模块
aceflow-unified --reinit-modules

# 验证配置
aceflow-unified --validate-config
```

#### 3. 性能问题
```bash
# 性能诊断
aceflow-unified --diagnose-performance

# 优化建议
aceflow-unified --optimize-config

# 重置缓存
aceflow-unified --clear-cache
```

## 📞 获取帮助

### 支持渠道

- **📧 邮件支持**: migration-support@aceflow.dev
- **💬 社区论坛**: https://community.aceflow.dev
- **🐛 问题报告**: https://github.com/aceflow/mcp-server/issues
- **📚 文档**: https://docs.aceflow.dev

### 迁移支持

我们提供专门的迁移支持：

- **🔧 迁移咨询**: 免费迁移计划评估
- **👨‍💻 技术支持**: 迁移过程中的技术协助
- **📋 定制方案**: 复杂环境的定制迁移方案
- **🎓 培训服务**: 团队培训和最佳实践指导

---

**🚀 准备开始迁移？联系我们获取个性化的迁移支持！**