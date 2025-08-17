# AceFlow MCP服务器使用指南

## 🎉 安装成功！

AceFlow MCP服务器已成功安装并配置完成。现在你可以在Cursor中使用AI-人协作工作流功能。

## 🚀 快速开始

### 1. 重启Cursor
首先重启Cursor以加载新的MCP配置。

### 2. 测试连接
在Cursor中输入：
```
@aceflow-enhanced 查看协作状态
```

如果看到协作状态信息，说明连接成功！

## 🛠️ 主要功能

### 智能工作流启动
```
@aceflow-enhanced 我想开发一个用户管理系统，这是PRD文档...
```
AI会自动识别你的意图并启动相应的工作流。

### 协作式阶段管理
```
@aceflow-enhanced 继续下一阶段
@aceflow-enhanced 查看当前阶段状态
@aceflow-enhanced 执行当前阶段
```

### 任务级协作执行
```
@aceflow-enhanced 执行下一个任务
@aceflow-enhanced 查看任务进度
```

### 质量验证
```
@aceflow-enhanced 验证项目质量
@aceflow-enhanced 进行严格质量检查
```

## 🔧 可用工具

1. **aceflow_stage_collaborative** - 智能协作式阶段管理
2. **aceflow_task_execute** - 任务级协作执行
3. **aceflow_respond** - 协作请求响应
4. **aceflow_collaboration_status** - 协作状态查询
5. **aceflow_validate_quality** - 多级质量验证

## 💡 使用技巧

### 自然语言交互
你可以用自然语言描述你的需求：
- "我想开发一个博客系统"
- "继续下一步"
- "检查代码质量"
- "暂停当前工作"

### AI-人协作模式
- AI会在关键决策点主动询问你的确认
- 你可以随时暂停或修改工作流程
- 系统会记录所有协作历史

### 工作流模式
- **Simple模式**: 快速开发流程
- **Standard模式**: 标准开发流程  
- **Complete模式**: 企业级完整流程(S1-S8)

## 🐛 故障排除

### 如果连接失败
1. 确保Cursor已重启
2. 检查MCP配置：`@aceflow-enhanced 查看协作状态`
3. 运行测试脚本：`python test_aceflow_mcp.py`

### 如果工具不响应
1. 检查服务器状态：`aceflow-enhanced-server --help`
2. 重新运行设置脚本：`python complete-mcp-setup.py`

### 查看日志
服务器日志会显示详细的执行信息，帮助诊断问题。

## 📚 更多资源

- 查看 `aceflow-mcp-server/` 目录了解更多技术细节
- 运行 `python test_aceflow_mcp.py` 进行完整测试
- 查看 `cursor-mcp-config.json` 了解配置详情

## 🎯 下一步

现在你可以开始使用AceFlow进行AI-人协作开发了！

尝试这个示例：
```
@aceflow-enhanced 我想开发一个简单的待办事项应用，包含添加、删除、标记完成功能
```

AI会自动识别你的需求并启动相应的开发工作流。

---

**祝你开发愉快！** 🚀