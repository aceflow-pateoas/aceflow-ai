# AceFlow v3.0 - .clinerules 集成规范
# AI Agent 工作流增强配置标准

## 📋 规范概述

本文档定义了AceFlow v3.0中.clinerules文件的标准格式和集成规则，确保AI Agent能够正确理解和执行AceFlow工作流。

## 🎯 核心原则

### 1. 增强而非替代
- AceFlow是AI Agent的增强层，不是替代工具
- 通过标准化配置引导AI Agent按照既定流程工作
- 保持AI Agent的灵活性和创造性

### 2. 状态驱动工作
- 所有工作都基于项目状态文件进行
- 跨对话保持工作记忆和上下文连续性
- 实时更新和同步项目进度

### 3. 标准化输出
- 统一的文件命名和目录结构
- 符合aceflow-spec_v3.0.md的输出格式
- 可验证和可追溯的工作产出

## 📁 .clinerules 标准模板

### 基础模板结构

```plaintext
# AceFlow v3.0 - AI Agent 集成配置
# 模式: {MODE}

## 工作模式配置
AceFlow模式: {MODE}
输出目录: aceflow_result/
配置目录: .aceflow/
模板文件: .aceflow/template.yaml

## 核心工作原则
1. 所有项目文档和代码必须输出到 aceflow_result/ 目录
2. 严格按照 .aceflow/template.yaml 中定义的流程执行
3. 每个阶段完成后更新项目状态文件
4. 保持跨对话的工作记忆和上下文连续性
5. 遵循AceFlow v3.0规范进行标准化输出

## 工作流程控制
当前阶段: {CURRENT_STAGE}
完成阶段: {COMPLETED_STAGES}
下一阶段: {NEXT_STAGE}
进度百分比: {PROGRESS}%

## 状态管理
- 工作状态文件: aceflow_result/current_state.json
- 阶段进度跟踪: aceflow_result/stage_progress.json
- 记忆持久化: aceflow_result/memory_state.json
- 质量检查点: aceflow_result/quality_gates.json

## 输出规范
### 文件命名规范
- 文档文件: 使用模式前缀 + 描述性名称 + .md
- 配置文件: 使用 .json 或 .yaml 扩展名
- 代码文件: 遵循项目技术栈的标准约定
- 报告文件: report_ + 类型 + 时间戳格式

### 目录结构规范
aceflow_result/
├── current_state.json          # 项目状态
├── stage_progress.json         # 阶段进度
├── memory_state.json          # 记忆状态
├── quality_gates.json         # 质量门控
├── {stage_files}              # 阶段产出文件
├── reports/                   # 报告目录
├── artifacts/                 # 工件目录
└── logs/                      # 日志目录

## 质量标准
### 代码质量
- 代码覆盖率: 根据模式要求（minimal≥60%, standard≥75%, complete≥85%）
- 编码规范: 严格遵循项目定义的代码风格指南
- 注释完整性: 关键函数和复杂逻辑必须有清晰注释
- 安全检查: 进行基本的安全漏洞扫描

### 文档质量
- 结构清晰: 使用标准的Markdown格式和层级结构
- 内容完整: 包含必要的说明、示例和参考信息
- 格式统一: 遵循统一的文档模板和风格指南
- 可维护性: 文档应该易于更新和维护

### 交付质量
- 符合规范: 严格按照aceflow-spec_v3.0.md执行
- 可验证性: 所有产出都可以通过aceflow-validate.sh验证
- 完整性检查: 确保所有必需的交付物都已完成
- 质量门控: 通过相应模式的质量检查点

## AI Agent 工作指导

### 会话开始时
1. 读取 aceflow_result/current_state.json 了解项目状态
2. 检查 aceflow_result/stage_progress.json 确定当前阶段
3. 根据模板配置 .aceflow/template.yaml 准备工作计划
4. 如果是首次运行，执行项目初始化流程

### 工作执行中
1. 严格按照当前阶段的要求执行任务
2. 实时更新项目状态和进度信息
3. 所有输出必须保存到指定的aceflow_result目录
4. 遇到问题时参考模板中的troubleshooting指导

### 阶段完成时
1. 更新 aceflow_result/stage_progress.json 标记阶段完成
2. 更新 aceflow_result/current_state.json 切换到下一阶段
3. 执行当前阶段的质量检查要求
4. 生成阶段完成报告和总结

### 会话结束时
1. 保存当前工作状态到memory_state.json
2. 更新last_session时间戳
3. 确保所有工作产出都已正确保存
4. 为下次会话准备上下文信息

## 错误处理机制

### 状态恢复
如果发现状态文件损坏或丢失：
1. 尝试从backup目录恢复
2. 使用aceflow-validate.sh --fix进行自动修复
3. 如果无法恢复，提示用户重新初始化项目

### 流程中断恢复
如果工作流程被中断：
1. 读取memory_state.json恢复上下文
2. 检查last_session时间确定中断点
3. 从最近的检查点继续执行
4. 必要时重新执行当前阶段的部分工作

### 质量检查失败
如果质量检查不通过：
1. 记录具体的失败原因和位置
2. 提供修复建议和参考文档
3. 暂停进入下一阶段直到问题解决
4. 更新质量门控状态

## 工具集成命令

### 验证和检查
- aceflow-validate.sh: 验证项目配置和输出合规性
- aceflow-validate.sh --mode=complete --report: 生成详细验证报告
- aceflow-validate.sh --fix: 自动修复发现的问题

### 阶段管理
- aceflow-stage.sh status: 查看当前阶段状态
- aceflow-stage.sh next: 推进到下一阶段
- aceflow-stage.sh rollback: 回滚到上一阶段
- aceflow-stage.sh reset STAGE: 重置到指定阶段

### 模板管理
- aceflow-templates.sh list: 列出可用模板
- aceflow-templates.sh switch MODE: 切换流程模式
- aceflow-templates.sh customize: 自定义模板配置

## 记忆系统集成

### PATEOAS记忆池
启用PATEOAS记忆系统以实现：
- 跨项目经验积累
- 智能决策支持
- 个性化工作流优化
- 团队知识共享

### 记忆数据格式
```json
{
  "session_id": "唯一会话标识",
  "timestamp": "ISO格式时间戳",
  "project_context": {
    "name": "项目名称",
    "mode": "流程模式",
    "stage": "当前阶段"
  },
  "work_summary": "工作总结",
  "decisions_made": ["决策记录"],
  "learned_patterns": ["学习到的模式"],
  "next_actions": ["下一步行动"]
}
```

## 最佳实践建议

### 1. 项目启动
- 使用aceflow-init.sh --mode=smart进行智能初始化
- 充分利用AI访谈功能获得最佳配置建议
- 确保团队成员理解选定的流程模式

### 2. 日常工作
- 每次开始工作前检查项目状态
- 严格按照阶段要求执行任务
- 及时更新进度状态和工作记录

### 3. 质量保证
- 定期运行aceflow-validate.sh进行合规检查
- 重视质量门控，不要跳过检查步骤
- 建立代码审查和文档评审机制

### 4. 团队协作
- 使用统一的.clinerules配置
- 定期同步项目状态和记忆数据
- 建立团队知识库和最佳实践分享

## 故障排除

### 常见问题
1. **状态文件不存在**: 运行aceflow-validate.sh --fix
2. **模式不一致**: 检查.clinerules、状态文件和模板配置
3. **输出目录混乱**: 使用标准目录结构重新组织
4. **质量检查失败**: 参考模板中的质量标准进行修复

### 调试技巧
1. 启用详细日志记录
2. 使用aceflow-validate.sh --mode=complete进行全面检查
3. 检查aceflow_result/logs/目录中的错误日志
4. 参考aceflow-spec_v3.0.md确认规范要求

---

**重要提醒**: 
- AceFlow的核心价值在于通过标准化和状态管理实现AI Agent工作的连续性和可追溯性
- 所有AI Agent都应该严格遵循这些规则，确保输出质量和流程一致性
- 记住：AceFlow是增强工具，不是限制工具，在遵循规范的基础上保持创造性和灵活性