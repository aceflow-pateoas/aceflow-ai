# 📁 AceFlow-AI 目录结构完整指南

> **AceFlow-AI v3.0 安装后的完整目录结构说明**  
> **更新时间**: 2025-07-28

## 🎯 概览

AceFlow-AI 采用**分层安装架构**，包含：
- 🏠 **全局安装目录** (`$HOME/.aceflow`) - 核心引擎和共享资源
- 🎯 **项目配置目录** (`.aceflow/`) - 每个项目的专用配置
- 🔗 **IDE集成文件** (`.clinerules/`, `.vscode/`) - 开发环境集成

---

## 🏠 一、全局安装目录结构

安装后在用户主目录创建 `$HOME/.aceflow/`：

```
$HOME/.aceflow/                           # AceFlow全局安装根目录
├── aceflow/                              # 🎯 AceFlow核心源码
│   ├── enhanced_cli.py                   # 主CLI入口 - v3.0增强版本
│   ├── config.yaml                       # 🔧 全局主配置文件
│   ├── current_state.json                # 📊 当前系统状态快照
│   │
│   ├── pateoas/                          # 🧠 PATEOAS增强引擎
│   │   ├── __init__.py                   # Python包初始化
│   │   ├── enhanced_engine.py            # 🚀 核心增强引擎
│   │   ├── memory_system.py              # 📚 智能记忆系统
│   │   ├── optimized_memory_retrieval.py # ⚡ 优化记忆检索
│   │   ├── state_manager.py              # 📈 状态管理器
│   │   ├── optimized_state_manager.py    # ⚡ 优化状态管理
│   │   ├── flow_controller.py            # 🎮 流程控制器
│   │   ├── decision_gates.py             # 🚦 智能决策门
│   │   ├── decision_gates_clean.py       # 🚦 优化决策门
│   │   ├── performance_monitor.py        # 📊 性能监控
│   │   ├── quality_assessment.py         # ✅ 质量评估
│   │   ├── smart_recall.py               # 🧠 智能召回引擎
│   │   ├── workflow_optimizer.py         # 🔄 工作流优化器
│   │   ├── adaptive_recovery.py          # 🛠️ 自适应恢复
│   │   ├── memory_categories.py          # 📂 记忆分类管理
│   │   └── utils.py                      # 🛠️ 通用工具函数
│   │
│   ├── config/                           # ⚙️ 配置文件目录
│   │   ├── project.yaml                  # 📋 项目配置模板
│   │   ├── agile_config.yaml             # 🏃 敏捷开发配置
│   │   ├── agile_integration.yaml        # 🔗 敏捷集成配置
│   │   ├── flow_modes.yaml               # 🎯 流程模式配置
│   │   ├── workflow_rules.json           # 📜 工作流规则定义
│   │   └── dynamic_thresholds.json       # 📊 动态质量阈值
│   │
│   ├── state/                            # 📊 状态管理目录
│   │   └── project_state.json            # 🗂️ 全局项目状态
│   │
│   ├── templates/                        # 📄 模板文件库
│   │   ├── s1_user_story.md              # 📖 S1阶段-用户故事模板
│   │   ├── s2_tasks_group.md             # 📋 S2阶段-任务分组模板
│   │   ├── s2_tasks_main.md              # 📋 S2阶段-主任务模板
│   │   ├── s3_testcases.md               # 🧪 S3阶段-测试用例模板
│   │   ├── s3_testcases_main.md          # 🧪 S3阶段-主测试模板
│   │   ├── s4_implementation.md          # 💻 S4阶段-实现模板
│   │   ├── s4_implementation_report.md   # 📊 S4阶段-实现报告模板
│   │   ├── s5_test_report.md             # 📋 S5阶段-测试报告模板
│   │   ├── s6_codereview.md              # 👁️ S6阶段-代码评审模板
│   │   ├── s7_demo_script.md             # 🎬 S7阶段-演示脚本模板
│   │   ├── s8_learning_summary.md        # 📚 S8阶段-学习总结模板
│   │   ├── s8_summary_report.md          # 📊 S8阶段-总结报告模板
│   │   ├── task-status-table.md          # 📈 任务状态表模板
│   │   │
│   │   ├── minimal/                      # 🎯 轻量模式模板
│   │   │   ├── README.md                 # 项目说明模板
│   │   │   ├── requirements.md           # 需求文档模板
│   │   │   ├── tasks.md                  # 任务列表模板
│   │   │   ├── review.md                 # 评审记录模板
│   │   │   ├── summary.md                # 总结报告模板
│   │   │   ├── template.yaml             # 轻量模式配置
│   │   │   └── workflows/                # 轻量工作流
│   │   │       ├── bug_fix.md            # Bug修复流程
│   │   │       ├── feature_quick.md      # 快速功能开发
│   │   │       └── prototype.md          # 原型开发流程
│   │   │
│   │   ├── standard/                     # 📋 标准模式模板
│   │   │   └── template.yaml             # 标准模式配置
│   │   │
│   │   └── document_templates/           # 📚 文档模板集合
│   │       ├── config_guide.md           # 配置指南模板
│   │       └── process_spec.md           # 流程规范模板
│   │
│   ├── scripts/                          # 🔧 脚本工具目录
│   │   ├── __init__.py                   # Python包初始化
│   │   ├── enhanced_cli.py               # CLI增强版本
│   │   ├── init_wizard.py                # 初始化向导
│   │   ├── wizard.py                     # 配置向导
│   │   ├── acceptance_test.py            # 验收测试脚本
│   │   ├── analyze.py                    # 分析工具
│   │   │
│   │   ├── cli/                          # CLI相关脚本
│   │   │   ├── __init__.py               
│   │   │   ├── main.py                   # CLI主入口
│   │   │   ├── aceflow_cli_enhanced.py   # 增强CLI
│   │   │   ├── aceflow_cli_v2.py         # CLI v2版本
│   │   │   └── init.py                   # CLI初始化
│   │   │
│   │   ├── core/                         # 核心功能脚本
│   │   │   ├── __init__.py
│   │   │   ├── state_engine.py           # 状态引擎
│   │   │   ├── state_engine_enhanced.py  # 增强状态引擎
│   │   │   ├── multi_mode_state_engine.py # 多模式状态引擎
│   │   │   ├── workflow_navigator.py     # 工作流导航
│   │   │   ├── workflow_navigator_enhanced.py # 增强工作流导航
│   │   │   └── memory_pool.py            # 记忆池管理
│   │   │
│   │   ├── utils/                        # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── check_env.py              # 环境检查
│   │   │   ├── config_loader.py          # 配置加载器
│   │   │   └── logger.py                 # 日志工具
│   │   │
│   │   └── migrations/                   # 数据迁移脚本
│   │       └── memory_migrator.py        # 记忆数据迁移
│   │
│   ├── ai/                               # 🤖 AI功能模块
│   │   ├── aceflow-tool-spec.yaml        # AI工具规范
│   │   ├── cli/
│   │   │   └── agent_cli.py              # AI代理CLI
│   │   ├── data/
│   │   │   └── training_data.py          # 训练数据管理
│   │   └── engines/
│   │       ├── decision_engine.py        # 决策引擎
│   │       └── rule_based_engine.py      # 规则引擎
│   │
│   ├── reports/                          # 📊 报告输出目录
│   │   ├── acceptance_test_YYYYMMDD_HHMMSS.json # 验收测试报告
│   │   └── pateoas_integration_report.json     # PATEOAS集成报告
│   │
│   ├── .clinerules/                      # 🔗 Cline集成规则
│   │   └── pateoas_integration.md        # PATEOAS-Cline集成规则文件
│   │
│   ├── .vscode/                          # 🎨 VSCode全局配置
│   │   ├── settings.json                 # VSCode设置
│   │   └── tasks.json                    # VSCode任务配置
│   │
│   ├── aceflow-pateoas-workspace.code-workspace # 🏢 VSCode工作区文件
│   ├── start_pateoas_dev.sh              # 🚀 快速启动脚本
│   ├── quick_install.sh                  # ⚡ 快速安装脚本
│   ├── quick_verify.sh                   # ✅ 安装验证脚本
│   ├── debug_pateoas_integration.py      # 🐛 PATEOAS集成调试
│   ├── validate_memory_commands.py       # ✅ 记忆命令验证
│   ├── pateoas_integration.py            # 🔗 PATEOAS集成主文件
│   ├── memory_commands_validation.json   # 📋 记忆命令验证配置
│   ├── requirements.txt                  # 📦 Python依赖文件
│   ├── venv/                             # 🐍 Python虚拟环境（可选）
│   │   ├── bin/
│   │   │   ├── python3
│   │   │   ├── pip
│   │   │   └── activate
│   │   └── lib/python3.x/site-packages/
│   └── web/                              # 🌐 Web界面（可选）
│       └── index.html                    # Web主页
│
└── .aceflow/                             # 🗂️ 全局用户配置目录
    ├── config.yaml                       # 用户主配置文件
    ├── state.json                        # 全局状态文件
    └── memory/                           # 📚 全局记忆存储
        ├── context/                      # 上下文记忆
        ├── decision/                     # 决策记忆
        ├── pattern/                      # 模式记忆
        ├── issue/                        # 问题记忆
        └── learning/                     # 学习记忆
```

### 🔧 全局命令

安装过程在 `$HOME/.local/bin/` 创建全局命令：

```
$HOME/.local/bin/
├── aceflow                               # 🎯 主CLI命令 → enhanced_cli.py
└── aceflow-start                         # 🚀 快速启动命令 → VSCode+Cline
```

并在 `$HOME/.bashrc` 中添加：
```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## 🎯 二、项目目录结构

在任何项目中运行 `aceflow init` 后创建：

```
your-project/                             # 👤 您的项目根目录
├── .aceflow/                             # 🎯 AceFlow项目专用配置
│   ├── config/                           # ⚙️ 项目配置目录
│   │   └── project.yaml                  # 📋 项目专用配置文件
│   ├── state/                            # 📊 项目状态目录
│   │   └── project_state.json            # 🗂️ 项目状态数据
│   ├── memory/                           # 🧠 项目记忆存储
│   │   ├── context/                      # 📖 上下文记忆
│   │   │   ├── CTX-001-project-overview.md
│   │   │   └── CTX-002-team-preferences.md
│   │   ├── decision/                     # 🤔 决策记忆
│   │   │   ├── DEC-001-architecture-choice.md
│   │   │   └── DEC-002-framework-selection.md
│   │   ├── pattern/                      # 🎨 模式记忆
│   │   │   ├── PAT-001-error-handling.md
│   │   │   └── PAT-002-api-design.md
│   │   ├── issue/                        # 🐛 问题记忆
│   │   │   ├── ISS-001-login-bug-fix.md
│   │   │   └── ISS-002-performance-issue.md
│   │   └── learning/                     # 📚 学习记忆
│   │       ├── LEA-001-new-technique.md
│   │       └── LEA-002-best-practice.md
│   ├── templates/                        # 📄 项目模板（从全局复制）
│   └── scripts/                          # 🔧 项目脚本目录
├── .clinerules/                          # 🔗 Cline集成规则
│   └── pateoas_integration.md            # 项目专用Cline规则
├── .vscode/                              # 🎨 VSCode项目配置
│   ├── settings.json                     # 项目VSCode设置
│   ├── tasks.json                        # 项目任务配置
│   └── launch.json                       # 调试启动配置
├── aceflow-workspace.code-workspace      # 🏢 项目VSCode工作区
├── aceflow_result/                       # 📁 AceFlow执行结果目录
│   └── iter_YYYYMMDD_HHMM/              # 🔄 迭代结果目录
│       ├── S1_user_story/               # 📖 S1阶段输出
│       │   ├── user_story.md
│       │   └── requirements.md
│       ├── S2_tasks/                    # 📋 S2阶段输出
│       │   ├── tasks_breakdown.md
│       │   └── task_priorities.md
│       ├── S3_testcases/                # 🧪 S3阶段输出
│       │   ├── test_cases.md
│       │   └── test_plan.md
│       ├── S4_implementation/           # 💻 S4阶段输出
│       │   ├── implementation_plan.md
│       │   └── code_structure.md
│       ├── S5_test_report/              # 📋 S5阶段输出
│       │   ├── test_results.md
│       │   └── coverage_report.md
│       ├── S6_codereview/               # 👁️ S6阶段输出
│       │   ├── review_comments.md
│       │   └── quality_assessment.md
│       ├── S7_demo/                     # 🎬 S7阶段输出
│       │   ├── demo_script.md
│       │   └── showcase_plan.md
│       └── S8_summary/                  # 📊 S8阶段输出
│           ├── project_summary.md
│           └── lessons_learned.md
├── requirements.txt                      # 📦 项目Python依赖
└── .gitignore                           # 🙈 Git忽略文件配置
```

---

## 🔧 三、核心文件详细说明

### 🎯 CLI核心文件

| 文件名 | 作用 | 说明 |
|--------|------|------|
| `enhanced_cli.py` | 🚀 主CLI入口 | AceFlow v3.0增强版CLI，整合PATEOAS功能 |
| `aceflow` | 🔗 全局命令 | 调用enhanced_cli.py，提供全局aceflow命令 |
| `aceflow-start` | ⚡ 快速启动 | 自动打开VSCode工作区和Cline扩展 |

### 🧠 PATEOAS增强引擎

| 文件名 | 作用 | 主要功能 |
|--------|------|----------|
| `enhanced_engine.py` | 🎯 核心引擎 | 状态感知、智能决策、上下文理解 |
| `memory_system.py` | 📚 记忆系统 | 知识存储、智能检索、模式学习 |
| `optimized_memory_retrieval.py` | ⚡ 优化检索 | 高效记忆查询、相关性评分 |
| `state_manager.py` | 📊 状态管理 | 项目状态追踪、阶段管理 |
| `flow_controller.py` | 🎮 流程控制 | 工作流调度、模式切换 |
| `decision_gates.py` | 🚦 决策门 | 质量检查点、智能决策支持 |
| `smart_recall.py` | 🧠 智能召回 | 上下文相关的记忆召回 |
| `workflow_optimizer.py` | 🔄 工作流优化 | 流程分析、效率优化建议 |

### ⚙️ 配置文件系统

| 文件名 | 层级 | 作用 |
|--------|------|------|
| `config.yaml` | 全局 | 系统主配置、默认参数 |
| `project.yaml` | 项目 | 项目专用配置、覆盖全局设置 |
| `flow_modes.yaml` | 全局 | 定义4种工作流模式配置 |
| `workflow_rules.json` | 全局 | 工作流规则、阶段流转逻辑 |
| `dynamic_thresholds.json` | 全局 | 质量阈值、性能指标 |

### 📄 模板系统

#### Complete模式模板 (S1-S8)
- `s1_user_story.md` - 用户故事和需求分析
- `s2_tasks_main.md` - 任务分解和优先级
- `s3_testcases.md` - 测试用例设计
- `s4_implementation.md` - 实现计划和架构
- `s5_test_report.md` - 测试执行和报告
- `s6_codereview.md` - 代码评审检查表
- `s7_demo_script.md` - 演示脚本和展示
- `s8_summary_report.md` - 项目总结和学习

#### Minimal模式模板
- `README.md` - 项目说明
- `requirements.md` - 需求文档
- `tasks.md` - 任务列表
- `review.md` - 评审记录
- `summary.md` - 总结报告

### 🔗 IDE集成文件

| 文件名 | 作用 | 说明 |
|--------|------|------|
| `.clinerules/pateoas_integration.md` | Cline集成 | 定义AI助手行为、触发词、响应模板 |
| `.vscode/settings.json` | VSCode设置 | Python环境、扩展配置、文件关联 |
| `.vscode/tasks.json` | VSCode任务 | PATEOAS命令快捷方式、构建任务 |
| `aceflow-pateoas-workspace.code-workspace` | 工作区 | VSCode工作区配置、文件夹结构 |

### 💾 数据存储文件

| 文件名 | 类型 | 内容 |
|--------|------|------|
| `project_state.json` | 状态 | 当前阶段、进度、迭代信息、统计数据 |
| `memory/*.md` | 记忆 | 分类存储的项目知识和经验 |
| `aceflow_result/` | 输出 | 每次执行的结果文件、报告、分析 |

---

## 🚀 四、主要命令功能

### 🌐 全局命令

```bash
# 🎯 状态查看
aceflow status                    # 基础状态信息
aceflow status --performance      # 性能指标
aceflow status --memory-stats     # 记忆统计

# 🧠 记忆管理
aceflow memory add "内容"         # 添加记忆
aceflow memory find "关键词"      # 基础搜索
aceflow memory recall "查询"      # 智能召回
aceflow memory smart-recall "查询" --detailed  # 高级智能召回
aceflow memory list --recent      # 最近记忆
aceflow memory clean --days 30    # 清理旧记忆

# 🎯 项目管理
aceflow init                      # 初始化项目
aceflow analyze "任务描述"        # AI任务分析

# 🚀 快速启动
aceflow-start                     # 启动开发环境
```

### 🔧 PATEOAS增强命令

```bash
# 🧠 PATEOAS核心功能
aceflow pateoas status            # PATEOAS状态
aceflow pateoas analyze "任务"    # 智能任务分析
aceflow pateoas gates evaluate   # 决策门评估
aceflow pateoas optimize          # 工作流优化
aceflow pateoas diagnose          # 系统诊断

# 🔄 工作流管理
aceflow pateoas flow set minimal  # 设置工作流模式
aceflow pateoas flow switch       # 智能模式切换
aceflow pateoas flow optimize     # 流程优化建议

# 🧪 测试和调试
aceflow pateoas test --all-components  # 全面测试
aceflow pateoas test --quick           # 快速测试
aceflow pateoas debug --verbose        # 详细调试信息
```

---

## 📊 五、磁盘使用分析

### 💾 安装大小

| 组件 | 大小 | 说明 |
|------|------|------|
| **完整安装** | ~50MB | 包含所有功能和模板 |
| 核心功能 | ~35MB | PATEOAS引擎 + CLI |
| Python虚拟环境 | ~30MB | 可选，隔离依赖 |
| 模板系统 | ~5MB | 各种工作流模板 |
| 配置文件 | ~2MB | 配置和规则文件 |

### 📁 项目占用

| 类型 | 大小 | 说明 |
|------|------|------|
| 项目配置 | 1-2MB | `.aceflow/` 目录 |
| 记忆存储 | 根据使用量 | 每条记忆约1-5KB |
| 执行结果 | 根据项目规模 | 每次迭代约5-20MB |

---

## 🎯 六、工作流模式详解

AceFlow v3.0支持4种智能工作流模式：

### 1. 🎯 Minimal模式
- **适用场景**: 快速原型、Bug修复、小功能
- **流程**: P(计划) → D(开发) → R(评审)
- **特点**: 轻量快速，最少文档
- **模板**: `templates/minimal/`

### 2. 📋 Standard模式  
- **适用场景**: 标准功能开发、中等复杂度项目
- **流程**: P1 → P2 → D1 → D2 → R1
- **特点**: 平衡效率和质量
- **模板**: `templates/standard/`

### 3. 🏢 Complete模式
- **适用场景**: 复杂项目、企业级开发、高质量要求
- **流程**: S1→S2→S3→S4→S5→S6→S7→S8 (8阶段完整流程)
- **特点**: 全面完整，高质量保证
- **模板**: `templates/s1_*` - `templates/s8_*`

### 4. 🧠 Smart模式
- **适用场景**: 让AI智能选择最优模式
- **流程**: AI根据任务复杂度自动选择
- **特点**: 自适应，持续优化
- **模板**: 动态选择

---

## 🔍 七、故障排除

### 🐛 常见问题诊断

```bash
# 🔧 系统诊断
aceflow pateoas diagnose --generate-report

# ✅ 安装验证
./quick_verify.sh                 # 全局安装验证
python3 debug_pateoas_integration.py  # PATEOAS集成验证

# 🧠 记忆系统检查
python3 validate_memory_commands.py   # 记忆命令验证

# 📊 性能检查
aceflow status --performance --detailed
```

### 🔧 手动修复

```bash
# 重新初始化配置
aceflow init --force

# 清理并重建记忆索引
aceflow memory rebuild-index

# 重置工作流状态
aceflow pateoas reset --confirm
```

---

## 📈 八、使用建议

### 🎯 新用户建议
1. **首次使用**: 运行 `aceflow-start` 启动完整环境
2. **项目初始化**: 在项目目录运行 `aceflow init`
3. **体验智能功能**: 对Cline说"检查项目状态"
4. **逐步深入**: 从minimal模式开始，逐步使用更复杂的功能

### 🏢 团队使用建议
1. **统一配置**: 使用项目专用的 `project.yaml` 配置
2. **共享记忆**: 定期导出/导入团队记忆库
3. **工作流标准化**: 选择适合团队的工作流模式
4. **持续优化**: 利用性能监控和优化建议

### 🔄 维护建议
1. **定期清理**: 使用 `aceflow memory clean` 清理过期记忆
2. **性能监控**: 定期检查 `aceflow status --performance`
3. **备份重要数据**: 备份 `.aceflow/memory/` 目录
4. **更新升级**: 关注AceFlow版本更新

---

这套目录结构设计既保持了功能的完整性，又确保了使用的便利性。通过PATEOAS增强引擎，AceFlow-AI提供了真正的智能化开发工作流管理能力，让AI助手不仅能编程，更能理解和记忆您的项目。🚀