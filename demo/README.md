# AceFlow Demo Project

这是一个展示AceFlow集成的示例项目，演示如何将AceFlow工作流系统集成到你的项目中。

## 📁 目录结构

```
demo/
├── .aceflow/                           # AceFlow配置和模板目录
│   └── templates/                      # 模板库（通过 aceflow export templates 生成）
│       ├── SPEC.md                     # AceFlow v3.1 完整规范文档
│       ├── README.md                   # 模板库说明
│       ├── USAGE.md                    # 使用指南（重要！）
│       ├── complete/                   # Complete模式模板（10个阶段）
│       │   ├── requirement_analysis.md
│       │   ├── architecture_design.md
│       │   ├── user_stories.md
│       │   ├── task_breakdown.md
│       │   ├── test_design.md
│       │   ├── implementation.md
│       │   ├── unit_test.md
│       │   ├── integration_test.md
│       │   ├── performance_test.md
│       │   └── code_review.md
│       └── standard/                   # Standard模式模板（7个阶段）
│           ├── user_stories.md
│           ├── task_breakdown.md
│           ├── test_design.md
│           ├── implementation.md
│           ├── unit_test.md
│           ├── integration_test.md
│           └── code_review.md
│
└── README.md                           # 本文件
```

## 🚀 如何使用这个Demo

### 方式1: 复制到你的项目

```bash
# 将 .aceflow 目录复制到你的项目根目录
cp -r demo/.aceflow your-project/

# 进入你的项目
cd your-project

# 查看使用指南
cat .aceflow/templates/USAGE.md
```

### 方式2: 在新项目中导出

```bash
# 安装AceFlow
pip install aceflow-mcp-server

# 在你的项目根目录执行
cd your-project
aceflow export templates

# 模板将自动导出到 .aceflow/templates/
```

## 📖 三种使用方式

### 1️⃣ 纯提示词驱动（推荐新手）

**适合**: 快速开始，无需安装工具

**步骤**:
1. 复制 `.aceflow/templates/` 到你的项目
2. 手动创建结果目录: `mkdir -p aceflow_result/iter_001/standard`
3. 与AI对话时引用模板

**AI提示词示例**:
```
我要开始一个新功能"用户登录"的开发，使用AceFlow的Standard模式。

请读取 .aceflow/templates/standard/user_stories.md 模板，
为"用户登录"功能生成用户故事，并保存到
aceflow_result/iter_001/standard/user_stories.md
```

### 2️⃣ CLI命令辅助（半自动）

**适合**: 需要命令行工具辅助

**步骤**:
```bash
# 1. 安装
pip install aceflow-mcp-server

# 2. 初始化配置
aceflow init

# 3. 导出模板
aceflow export templates

# 4. 生成合同（Contract-First工作流）
aceflow contract generate --feature user-login

# 5. 启动Mock Server
aceflow mock start --feature user-login
```

### 3️⃣ MCP集成（全自动，推荐）

**适合**: 使用Claude Code或Cline

**步骤**:
1. 安装MCP Server: `pip install aceflow-mcp-server`
2. 配置Claude Code/Cline的MCP设置
3. AI自动调用MCP工具管理工作流

**效果**:
- AI自动调用 `aceflow_init_workflow`
- AI自动调用 `aceflow_generate_stage_document`
- AI自动基于模板生成文档
- AI自动管理工作流状态

## 📚 核心文档说明

### 必读文档

1. **`.aceflow/templates/USAGE.md`** ⭐
   - 完整的使用指南
   - 包含目录结构说明
   - AI提示词示例
   - Git配置建议

2. **`.aceflow/templates/SPEC.md`** ⭐
   - AceFlow v3.1 完整规范
   - 工作流模式详解
   - 阶段定义和质量标准

3. **`.aceflow/templates/README.md`**
   - 模板库概述
   - 各模板文件说明

### 模板文件

每个模板文件都是AI优化设计的：
- ✅ 简洁高效，去除冗余
- ✅ 表格驱动，易于填充
- ✅ 单例示范，由AI扩展
- ✅ 专为AI代理设计

## 🎯 实际使用流程示例

### 开始新功能开发

```
1. AI对话开始
   User: "开始一个新功能开发，使用Standard模式"

2. AI读取模板
   AI: [读取 .aceflow/templates/standard/user_stories.md]

3. AI生成文档
   AI: "我已经基于模板生成了用户故事..."
   [保存到 aceflow_result/iter_001/standard/user_stories.md]

4. 推进到下一阶段
   User: "继续任务分解阶段"
   AI: [读取 task_breakdown.md 模板，生成任务分解文档]

5. 持续推进...
   - 测试设计 → 功能实现 → 单元测试 → 集成测试 → 代码审查
```

## 💡 Tips

### Git配置建议

在项目的 `.gitignore` 中添加：
```gitignore
# AceFlow运行时状态（不提交）
.aceflow/current_state.json

# 保留模板和配置（提交）
!.aceflow/config.yaml
!.aceflow/templates/

# 执行结果（可选提交作为项目文档）
# aceflow_result/
```

### 团队协作

1. 将 `.aceflow/templates/` 提交到Git
2. 团队成员使用统一模板标准
3. 可自定义修改模板适应团队规范

### 自定义模板

模板文件可以编辑：
- 修改 `.aceflow/templates/standard/` 或 `complete/` 下的文件
- 调整格式、字段适应项目需求
- 保存后团队共享

## 🔗 相关资源

- **GitHub**: https://github.com/aceflow/aceflow-ai
- **PyPI**: https://pypi.org/project/aceflow-mcp-server/
- **完整文档**: 查看 `.aceflow/templates/SPEC.md`

## ❓ 常见问题

**Q: 为什么使用隐藏目录 `.aceflow/`？**
A: 保持项目根目录整洁，避免模板文件干扰项目结构。

**Q: 可以不使用MCP吗？**
A: 可以！支持纯提示词驱动，无需安装任何工具。

**Q: 如何更新模板？**
A: 重新执行 `aceflow export templates` 即可覆盖更新。

**Q: aceflow_result/ 目录需要提交到Git吗？**
A: 可选。如果想保留开发过程文档，可以提交；否则加入 `.gitignore`。

---

**开始使用**: 查看 `.aceflow/templates/USAGE.md` 获取详细指南！
