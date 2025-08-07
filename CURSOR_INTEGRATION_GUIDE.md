# 🚀 Cursor用户快速集成AceFlow MCP Server指南

## 📋 概述

AceFlow MCP Server为Cursor用户提供AI-人协同工作流功能，让你的AI助手能够：
- 🧠 智能识别开发意图
- 🤝 主动推进工作流程
- 📋 任务级协作执行
- 🔍 多级质量验证
- 📊 智能状态管理

## ⚡ 快速开始 (5分钟集成)

### 步骤1: 安装AceFlow MCP Server

```bash
# 克隆项目
git clone https://github.com/your-repo/aceflow-ai.git
cd aceflow-ai

# 安装MCP服务器
pip install -e aceflow-mcp-server/

# 验证安装
aceflow-enhanced-server --help
```

### 步骤2: 配置Cursor MCP设置

在Cursor中打开设置，找到MCP配置文件，通常位于：
- **Windows**: `%APPDATA%\Cursor\User\globalStorage\mcp.json`
- **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`
- **Linux**: `~/.config/Cursor/User/globalStorage/mcp.json`

添加以下配置：

```json
{
  "mcpServers": {
    "aceflow-enhanced": {
      "command": "aceflow-enhanced-server",
      "args": ["--host", "localhost", "--port", "8000"],
      "env": {
        "ACEFLOW_LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": [
        "aceflow_stage_collaborative",
        "aceflow_task_execute",
        "aceflow_validate_quality"
      ]
    }
  }
}
```

### 步骤3: 重启Cursor

重启Cursor以加载新的MCP配置。

### 步骤4: 验证集成

在Cursor中与AI助手对话，尝试以下命令：

```
@aceflow-enhanced 这是我的PRD文档，开始完整的开发流程
```

如果看到AI助手能够识别意图并提供协作建议，说明集成成功！

## 🎯 核心功能使用指南

### 1. 智能项目启动

**用户输入**:
```
这是我们的用户管理系统PRD文档，需要开始企业级开发流程
```

**AI响应**:
- 🧠 自动识别为启动工作流意图
- 🤝 询问确认启动Complete模式
- 📋 初始化项目结构和配置

### 2. 协作式阶段管理

**用户输入**:
```
@aceflow-enhanced 执行当前阶段
```

**AI响应**:
- 📊 检查当前阶段状态
- 🔍 验证输入条件
- 🤝 征求执行确认
- ✅ 执行完成后询问下一步

### 3. 任务级协作开发

**用户输入**:
```
@aceflow-enhanced 开始实现功能
```

**AI响应**:
- 📋 解析任务分解文档
- 🎯 选择下一个可执行任务
- 🤝 征求任务执行确认
- 📊 实时更新进度状态

### 4. 质量验证检查

**用户输入**:
```
@aceflow-enhanced 验证项目质量
```

**AI响应**:
- 🔍 执行多级质量检查
- 📊 生成量化质量评分
- 💡 提供具体改进建议
- 📈 生成质量趋势报告

## 🔧 高级配置选项

### 自定义工作流模式

```json
{
  "mcpServers": {
    "aceflow-enhanced": {
      "command": "aceflow-enhanced-server",
      "args": ["--host", "localhost", "--port", "8000"],
      "env": {
        "ACEFLOW_LOG_LEVEL": "DEBUG",
        "ACEFLOW_DEFAULT_MODE": "complete",
        "ACEFLOW_AUTO_ADVANCE": "false"
      },
      "disabled": false,
      "autoApprove": [
        "aceflow_stage_collaborative",
        "aceflow_task_execute",
        "aceflow_respond",
        "aceflow_collaboration_status",
        "aceflow_validate_quality"
      ]
    }
  }
}
```

### 协作超时设置

```json
{
  "mcpServers": {
    "aceflow-enhanced": {
      "command": "aceflow-enhanced-server",
      "args": ["--host", "localhost", "--port", "8000"],
      "env": {
        "ACEFLOW_COLLABORATION_TIMEOUT": "600",
        "ACEFLOW_TASK_TIMEOUT": "1800"
      }
    }
  }
}
```

## 📋 常用命令参考

### 项目管理命令

| 用户输入 | 功能描述 |
|---------|---------|
| `这是PRD文档，开始开发` | 智能启动工作流 |
| `查看项目状态` | 获取当前项目状态 |
| `继续下一阶段` | 推进到下一个阶段 |
| `暂停工作流` | 暂停当前工作流 |

### 任务执行命令

| 用户输入 | 功能描述 |
|---------|---------|
| `开始编码实现` | 启动任务级协作执行 |
| `执行下一个任务` | 执行队列中的下一个任务 |
| `查看任务进度` | 显示任务完成情况 |
| `跳过当前任务` | 跳过当前任务到下一个 |

### 质量控制命令

| 用户输入 | 功能描述 |
|---------|---------|
| `验证代码质量` | 执行质量验证检查 |
| `生成质量报告` | 生成详细质量报告 |
| `检查阶段输出` | 验证当前阶段输出 |
| `修复质量问题` | 获取质量改进建议 |

## 🎯 实际使用场景

### 场景1: 新项目启动

```
用户: @aceflow-enhanced 我有一个电商系统的PRD文档，包含用户管理、商品管理、订单处理等模块，需要启动完整的企业级开发流程

AI: 🧠 检测到复杂项目需求，建议启动Complete模式工作流
    📋 项目特征分析：
    - 多模块系统 (用户、商品、订单)
    - 企业级要求
    - 完整开发流程需求
    
    🤝 确认启动Complete模式工作流？这将包含12个阶段的完整开发流程。

用户: 是的，开始

AI: ✅ 项目初始化完成
    📊 当前状态：S1_user_stories (0% 完成)
    🎯 下一步：开始用户故事分析
    
    🤝 是否立即开始S1阶段的用户故事分析？
```

### 场景2: 协作式开发

```
用户: @aceflow-enhanced 继续开发

AI: 📊 当前状态检查：
    - 当前阶段：S5_implementation
    - 任务队列：15个任务，3个已完成
    - 下一个任务：实现用户认证模块
    
    🎯 准备执行任务：实现用户认证模块
    📋 任务详情：
    - 预估时间：6小时
    - 依赖：数据库连接模块 (已完成)
    - 输出：auth.py, test_auth.py
    
    🤝 是否开始执行此任务？

用户: 开始

AI: ✅ 任务执行完成
    📊 进度更新：4/15 任务完成 (26.7%)
    📁 生成文件：auth.py, test_auth.py
    🧪 单元测试：5个测试用例通过
    
    🤝 任务已完成，是否继续下一个任务：实现用户权限管理？
```

### 场景3: 质量验证

```
用户: @aceflow-enhanced 验证当前代码质量

AI: 🔍 执行Standard级别质量验证...
    
    📊 质量验证报告：
    ✅ 总体评分：85.2/100 (良好)
    📋 检查项目：
    - 代码规范：92/100 ✅
    - 测试覆盖：78/100 ⚠️
    - 文档完整：88/100 ✅
    - 安全检查：90/100 ✅
    
    ⚠️ 发现问题：
    1. 测试覆盖率不足 (78% < 80%)
    2. 缺少3个模块的API文档
    
    💡 改进建议：
    1. 为auth.py模块添加边界测试用例
    2. 补充用户管理API文档
    3. 添加异常处理测试
    
    🤝 是否立即修复这些质量问题？
```

## 🛠️ 故障排除

### 常见问题及解决方案

#### 1. MCP服务器无法启动

**问题**: `aceflow-enhanced-server: command not found`

**解决方案**:
```bash
# 重新安装
pip uninstall aceflow-mcp-server
pip install -e aceflow-mcp-server/

# 验证安装
which aceflow-enhanced-server
```

#### 2. Cursor无法连接MCP服务器

**问题**: Cursor显示MCP连接错误

**解决方案**:
1. 检查MCP配置文件路径是否正确
2. 验证JSON格式是否有效
3. 重启Cursor
4. 检查防火墙设置

#### 3. 工具调用失败

**问题**: AI助手无法调用AceFlow工具

**解决方案**:
```bash
# 测试服务器功能
python test_mcp_server_simple.py

# 检查日志
aceflow-enhanced-server --log-level DEBUG
```

#### 4. 协作请求超时

**问题**: 协作请求经常超时

**解决方案**:
在MCP配置中增加超时时间：
```json
{
  "env": {
    "ACEFLOW_COLLABORATION_TIMEOUT": "1200"
  }
}
```

## 📚 进阶使用技巧

### 1. 自定义工作流模式

创建自定义模式配置：
```json
{
  "env": {
    "ACEFLOW_CUSTOM_MODE": "rapid-prototype",
    "ACEFLOW_STAGES": "analysis,implementation,testing"
  }
}
```

### 2. 批量任务执行

```
用户: @aceflow-enhanced 批量执行所有前端任务

AI: 📋 识别到5个前端相关任务
    🎯 批量执行模式启动
    ⏱️ 预估总时间：18小时
    
    🤝 确认批量执行？执行过程中将定期报告进度。
```

### 3. 智能代码审查

```
用户: @aceflow-enhanced 审查最近的代码变更

AI: 🔍 代码审查分析：
    📊 变更统计：15个文件，342行新增，89行删除
    🎯 重点关注：
    - 新增的认证模块
    - 数据库查询优化
    - API接口变更
    
    💡 审查建议：
    1. 认证模块建议添加速率限制
    2. 数据库查询可以进一步优化索引
    3. API版本控制需要完善
```

## 🎉 开始使用

现在你已经了解了如何在Cursor中集成和使用AceFlow MCP Server！

**立即开始**:
1. 按照快速开始步骤完成安装和配置
2. 在Cursor中尝试第一个协作命令
3. 体验AI-人协同开发的强大功能

**获取帮助**:
- 查看详细文档：`aceflow-mcp-server/README.md`
- 运行测试验证：`python test_mcp_server_simple.py`
- 查看示例配置：本文档中的配置示例

**享受AI-人协同开发的全新体验！** 🚀