# AceFlow 模板包使用指南

> 导出时间: 2025-11-13 09:16:39
> 导出模式: standard, complete

## 📁 项目目录结构

将AceFlow集成到你的项目后的推荐目录结构：

```
my-project/                              # 你的项目根目录
├── .aceflow/                            # AceFlow配置和模板
│   ├── config.yaml                      # 项目配置（aceflow init生成）
│   ├── current_state.json               # 工作流状态（MCP自动生成）
│   └── templates/                       # 模板库（本次导出的内容）
│       ├── SPEC.md                      # AceFlow v3.1 规范
│       ├── README.md                    # 模板说明
│       ├── USAGE.md                     # 本使用指南
│       ├── standard/                 # Standard模式(7阶段)
│       │   ├── user_stories.md
│       │   ├── task_breakdown.md
│       │   └── ...（7个模板文件）
│       ├── complete/                # Complete模式(10阶段)
│       │   ├── requirement_analysis.md
│       │   ├── architecture_design.md
│       │   └── ...（10个模板文件）
│
├── aceflow_result/                      # 工作流执行结果
│   └── iter_20250113_001/               # 迭代目录
│       └── standard/                  # 使用的模式
│           ├── user_stories.md          # AI填充后的文档
│           ├── task_breakdown.md
│           └── ...
│
├── src/                                 # 项目源码
└── README.md                            # 项目文档
```

## 🚀 快速开始

### 步骤1: 初始化项目配置（可选）

如果需要使用MCP集成，先初始化配置：

```bash
cd my-project
aceflow init
```

### 步骤2: 导出模板到项目

```bash
# 导出到默认位置 .aceflow/templates/
aceflow export templates

# 或指定模式
aceflow export templates --mode standard
```

### 步骤3: 开始使用

**方式A - 纯提示词驱动（推荐新手）**:

1. 手动创建结果目录: `mkdir -p aceflow_result/iter_001/standard`
2. 与AI对话时引用模板文件

示例对话:
```
User: 请根据 .aceflow/templates/standard/user_stories.md 模板，
      为"用户登录"功能编写用户故事

AI: [基于模板生成内容]

User: 保存到 aceflow_result/iter_001/standard/user_stories.md
```

**方式B - MCP集成（推荐熟练用户）**:

配置Claude Code或Cline后，AI会自动：
- 调用MCP工具管理工作流
- 基于 `.aceflow/templates/` 生成文档
- 保存到 `aceflow_result/` 目录
- 追踪工作流状态

## 📋 工作流模式

### Standard模式 (7阶段)
适用于大多数项目的日常开发，周期5-10天

阶段顺序:
1. user_stories - 用户故事
2. task_breakdown - 任务分解
3. test_design - 测试设计
4. implementation - 功能实现
5. unit_test - 单元测试
6. integration_test - 集成测试
7. code_review - 代码审查

### Complete模式 (10阶段)
适用于大型项目、关键系统，周期2-4周

阶段顺序:
1. requirement_analysis - 需求分析
2. architecture_design - 架构设计
3. user_stories - 用户故事
4. task_breakdown - 任务分解
5. test_design - 测试设计
6. implementation - 功能实现
7. unit_test - 单元测试
8. integration_test - 集成测试
9. performance_test - 性能测试
10. code_review - 代码审查

## 💡 使用提示

### 1. 版本控制建议

`.gitignore` 配置:
```
# AceFlow运行时状态（不提交）
.aceflow/current_state.json

# 保留模板和配置（提交到Git）
!.aceflow/config.yaml
!.aceflow/templates/

# 执行结果（可选：提交作为项目文档）
aceflow_result/
```

### 2. 团队协作

- 将 `.aceflow/templates/` 提交到Git，团队共享统一标准
- 可自定义编辑模板适应团队规范
- `aceflow_result/` 可作为项目文档提交

### 3. 模板自定义

模板文件位于 `.aceflow/templates/standard/`，可以：
- 修改模板格式适应项目需求
- 添加团队特定的检查项
- 调整文档结构

### 4. 多迭代管理

每次新功能开发创建新的迭代目录：
```
aceflow_result/
├── iter_001/    # 第一次迭代
├── iter_002/    # 第二次迭代
└── iter_003/    # 第三次迭代
```

## 📖 AI提示词示例

### 开始新的工作流

```
我要开始一个新功能"用户认证"的开发，使用AceFlow的Standard模式。

请从第一个阶段开始，参考 .aceflow/templates/standard/user_stories.md 模板，
生成用户故事文档并保存到 aceflow_result/iter_001/standard/user_stories.md
```

### 推进到下一阶段

```
用户故事阶段已完成，现在进入任务分解阶段。

请参考 .aceflow/templates/standard/task_breakdown.md 模板，
基于已有的用户故事，分解开发任务。
```

## 🔗 相关资源

- **完整规范**: 查看 `.aceflow/templates/SPEC.md`
- **模板说明**: 查看 `.aceflow/templates/README.md`
- **MCP集成**: `pip install aceflow-mcp-server`
- **GitHub**: https://github.com/aceflow/aceflow-ai

---

**提示**: `.aceflow/` 是隐藏目录，保持项目根目录整洁。使用 `ls -la` 查看。
