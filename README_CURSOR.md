# 🚀 AceFlow for Cursor - AI-人协同工作流

> 为Cursor用户提供智能的AI-人协同开发体验

## ⚡ 30秒快速开始

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/aceflow-ai.git
cd aceflow-ai

# 2. 一键安装配置
python install-for-cursor.py

# 3. 重启Cursor，开始使用！
```

## 🎯 核心功能

### 🧠 智能意图识别
```
你: "这是我的电商系统PRD文档，开始完整开发流程"
AI: 🧠 检测到复杂项目需求，建议启动Complete模式工作流
    🤝 确认启动包含12个阶段的完整开发流程？
```

### 🤝 主动协作推进
```
AI: ✅ S1用户故事分析完成 (识别了8个用户故事)
    📊 当前进度: 12.5% (1/8阶段)
    🤝 是否继续S2任务分解阶段？
```

### 📋 任务级协作执行
```
AI: 🎯 下一个任务: 实现用户认证模块
    ⏱️ 预估时间: 6小时
    📋 依赖: 数据库连接模块 (已完成)
    🤝 是否开始执行此任务？
```

### 🔍 智能质量验证
```
AI: 📊 质量验证完成: 85.2/100 (良好)
    ✅ 代码规范: 92/100
    ⚠️ 测试覆盖: 78/100 (建议提升至80%+)
    💡 发现3个可优化点，是否查看详细建议？
```

## 🎮 使用方式

### 基础命令

| 说什么 | AI做什么 |
|--------|----------|
| `这是PRD文档，开始开发` | 🧠 智能识别需求，启动相应工作流 |
| `继续下一阶段` | 🤝 推进到下一个开发阶段 |
| `开始编码实现` | 📋 启动任务级协作开发 |
| `验证代码质量` | 🔍 执行多级质量检查 |
| `查看项目状态` | 📊 显示当前进度和状态 |

### 高级功能

```bash
# 批量任务执行
"批量执行所有前端任务"

# 智能代码审查
"审查最近的代码变更"

# 自定义工作流
"使用快速原型模式开始开发"

# 协作历史分析
"分析我们的协作效果"
```

## 🛠️ 配置选项

### 基础配置 (推荐)
```json
{
  "mcpServers": {
    "aceflow-enhanced": {
      "command": "aceflow-enhanced-server",
      "disabled": false,
      "autoApprove": ["aceflow_stage_collaborative", "aceflow_task_execute"]
    }
  }
}
```

### 高级配置
```json
{
  "mcpServers": {
    "aceflow-enhanced": {
      "command": "aceflow-enhanced-server",
      "args": ["--host", "localhost", "--port", "8000"],
      "env": {
        "ACEFLOW_LOG_LEVEL": "INFO",
        "ACEFLOW_DEFAULT_MODE": "standard",
        "ACEFLOW_COLLABORATION_TIMEOUT": "600"
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

## 🎯 实际使用场景

### 场景1: 新项目启动
```
你: @aceflow-enhanced 我要开发一个任务管理系统，包含用户管理、任务创建、团队协作功能

AI: 🧠 项目分析完成
    📋 识别核心模块: 用户管理、任务管理、团队协作
    🎯 推荐: Standard模式 (8阶段开发流程)
    
    🤝 确认启动Standard模式工作流？
    
你: 确认

AI: ✅ 项目初始化完成
    📊 当前: S1_user_stories (0% 完成)
    🎯 下一步: 开始用户故事分析
    
    🤝 立即开始用户故事分析？
```

### 场景2: 协作开发
```
你: @aceflow-enhanced 继续开发

AI: 📊 状态检查:
    - 当前阶段: S5_implementation
    - 任务进度: 5/12 完成 (41.7%)
    - 下一任务: 实现任务分配功能
    
    🎯 任务详情:
    - 预估: 4小时
    - 依赖: 用户权限模块 ✅
    - 输出: task_assignment.py, tests/
    
    🤝 开始执行？

你: 开始

AI: ⚡ 执行中...
    ✅ 任务完成! 
    📊 进度: 6/12 (50%)
    🧪 测试: 8个用例全部通过
    
    🤝 继续下一个任务: 实现任务状态管理？
```

### 场景3: 质量控制
```
你: @aceflow-enhanced 检查代码质量

AI: 🔍 执行Standard级别验证...
    
    📊 质量报告:
    ✅ 总评: 88.5/100 (优秀)
    
    详细评分:
    - 代码规范: 95/100 ✅
    - 测试覆盖: 82/100 ✅  
    - 文档完整: 85/100 ✅
    - 安全检查: 92/100 ✅
    
    💡 优化建议:
    1. 为task_assignment.py添加异常处理测试
    2. 补充API文档的错误码说明
    
    🤝 是否立即应用这些优化？
```

## 🚨 故障排除

### 常见问题

**Q: Cursor找不到aceflow-enhanced服务器**
```bash
# 解决方案
pip install -e aceflow-mcp-server/
aceflow-enhanced-server --help  # 验证安装
```

**Q: MCP配置不生效**
```bash
# 检查配置文件位置
# Windows: %APPDATA%\Cursor\User\globalStorage\mcp.json
# macOS: ~/Library/Application Support/Cursor/User/globalStorage/mcp.json
# Linux: ~/.config/Cursor/User/globalStorage/mcp.json

# 重启Cursor
```

**Q: 工具调用失败**
```bash
# 测试服务器功能
python test_mcp_server_simple.py

# 检查autoApprove配置
```

### 获取帮助

1. **运行诊断**: `python test_mcp_server_simple.py`
2. **查看日志**: 在MCP配置中设置 `"ACEFLOW_LOG_LEVEL": "DEBUG"`
3. **重置配置**: 删除MCP配置文件，重新运行安装脚本
4. **查看详细文档**: `CURSOR_INTEGRATION_GUIDE.md`

## 🎉 开始体验

1. **安装**: `python install-for-cursor.py`
2. **重启**: 重启Cursor
3. **测试**: `@aceflow-enhanced 这是测试，开始协作开发`
4. **享受**: AI-人协同开发的全新体验！

---

**🚀 让AI成为你的最佳开发伙伴！**