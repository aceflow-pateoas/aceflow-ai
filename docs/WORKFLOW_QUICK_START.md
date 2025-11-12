# AceFlow Workflow 快速入门指南

> **版本**: v3.0
> **适用对象**: 开发者、项目经理
> **预计阅读时间**: 10 分钟

---

## 🎯 什么是 AceFlow Workflow?

AceFlow Workflow 是一个 AI 驱动的敏捷开发工作流框架，提供:

- ✅ **4种工作流模式** - 从快速原型到企业级开发
- ✅ **智能状态管理** - 自动追踪项目进度
- ✅ **项目记忆系统** - 记住你的决策和经验教训
- ✅ **21个 MCP 工具** - 无缝集成到 AI 助手
- ✅ **灵活的模板系统** - 快速生成项目文档

---

## 🚀 5分钟快速开始

### 1. 基础设置

```python
from pathlib import Path
from aceflow.workflow.core.engine import WorkflowEngine
from aceflow.workflow.core.state import StateManager
from aceflow.workflow.models import WorkflowMode
from aceflow.workflow.modes import MinimalWorkflow

# 初始化状态管理器
state_manager = StateManager(
    project_id="my_project",
    state_dir=Path(".aceflow/state")
)

# 创建工作流引擎
engine = WorkflowEngine(project_id="my_project")
engine.state_manager = state_manager

# 注册工作流模式
engine.register_mode_implementation(
    WorkflowMode.MINIMAL,
    MinimalWorkflow()
)
```

### 2. 开始第一个迭代

```python
# 开始新迭代
result = engine.initialize(
    mode="minimal",              # 选择 minimal 模式
    metadata={
        "goal": "实现用户登录功能",
        "team": "前端团队"
    }
)

print(f"✅ 迭代已创建: {result['iteration_id']}")
print(f"📊 总阶段数: {result['total_stages']}")
print(f"🎯 当前阶段: {result['current_stage']['name']}")
```

**输出**:
```
✅ 迭代已创建: iter_a1b2c3d4
📊 总阶段数: 3
🎯 当前阶段: Planning
```

### 3. 查看当前状态

```python
# 获取当前迭代
iteration = state_manager.get_current_iteration()

print(f"模式: {iteration.mode.value}")
print(f"状态: {iteration.status.value}")
print(f"进度: {iteration.overall_progress * 100:.1f}%")

# 获取当前阶段
stage = state_manager.get_current_stage()
print(f"当前阶段: {stage.name} ({stage.stage_id})")
print(f"阶段状态: {stage.status.value}")
```

### 4. 推进到下一阶段

```python
# 完成当前阶段的工作...
# 然后推进到下一阶段
success = state_manager.advance_stage(metadata={
    "completed_tasks": [
        "用户需求分析",
        "技术方案设计"
    ],
    "notes": "选择 JWT 认证方案"
})

if success:
    print("✅ 已进入下一阶段")
    new_stage = state_manager.get_current_stage()
    print(f"📍 新阶段: {new_stage.name}")
else:
    print("✅ 所有阶段已完成!")
```

---

## 📚 四种工作流模式

### 1. Minimal 模式 (P→D→R)

**适用场景**: 快速原型、小型功能

```
Planning (规划) → Development (开发) → Review (评审)
```

**特点**:
- ⚡ 最快速，3个阶段
- 🎯 专注核心功能
- ⏱️ 1-7天完成

**使用**:
```python
engine.initialize(mode="minimal")
```

### 2. Standard 模式 (P1→P2→D1→D2→R1)

**适用场景**: 常规功能开发

```
Requirements → Planning → Implementation → Testing → Review
```

**特点**:
- ⚖️ 平衡的流程
- 📋 需求到测试全覆盖
- ⏱️ 1-2周完成

**使用**:
```python
engine.initialize(mode="standard")
```

### 3. Complete 模式 (S1-S8)

**适用场景**: 企业级项目、关键系统

```
用户故事 → 任务拆分 → 测试用例 → 功能实现 →
测试执行 → 代码评审 → 演示反馈 → 总结归档
```

**特点**:
- 🏢 完整的 SDLC
- 📝 严格的文档要求
- ⏱️ 2-4周完成

**使用**:
```python
engine.initialize(mode="complete")
```

### 4. Smart 模式 (AI驱动)

**适用场景**: 复杂项目、需要灵活调整

**特点**:
- 🤖 AI 自动选择最优流程
- 🔄 根据项目进展动态调整
- 📊 基于历史数据优化

**使用**:
```python
engine.initialize(mode="smart")
```

---

## 🧠 使用记忆系统

### 记录技术决策

```python
from aceflow.workflow.memory import MemoryManager

mm = MemoryManager()

# 记录决策
mm.record_decision(
    "选择 React 作为前端框架",
    context={
        "alternatives": ["Vue", "Angular"],
        "reason": "团队熟悉度高，生态完善"
    },
    iteration_id=iteration.iteration_id
)
```

### 记录问题和解决方案

```python
# 记录遇到的问题
mm.record_issue(
    "API 响应时间超过 2 秒",
    severity="high",
    iteration_id=iteration.iteration_id,
    solution="添加 Redis 缓存层"
)
```

### 记录经验教训

```python
# 记录学到的经验
mm.record_learning(
    "JWT token 过期时间设置为 30 分钟效果最佳",
    category="security",
    iteration_id=iteration.iteration_id
)
```

### 召回相关记忆

```python
# 查找当前阶段的相关记忆
memories = mm.recall_for_stage(
    iteration_id=iteration.iteration_id,
    stage_id=stage.stage_id,
    limit=5
)

for memory in memories:
    print(f"{memory.type.value}: {memory.content}")
```

---

## 📄 使用模板系统

### 获取阶段模板

```python
from aceflow.workflow.templates import TemplateManager

tm = TemplateManager()

# 获取当前阶段的模板
template = tm.get_template_for_stage(
    mode="minimal",
    stage_id="P"
)

if template:
    # 渲染模板
    content = template.render({
        "iteration_id": iteration.iteration_id,
        "project_name": "用户认证系统",
        "owner": "张三"
    })

    print(content)
```

### 保存渲染后的模板

```python
# 渲染并保存到文件
output_path = tm.write_stage_template(
    mode="minimal",
    stage_id="P",
    variables={
        "iteration_id": iteration.iteration_id,
        "project_name": "用户认证系统"
    },
    output_root=Path(".aceflow/output")
)

print(f"模板已保存: {output_path}")
```

---

## 📤 导出项目文档

### 导出为 Markdown

```python
from aceflow.workflow.exporter import (
    DocumentExporter,
    ExportOptions,
    ExportFormat
)

exporter = DocumentExporter()

# 配置导出选项
options = ExportOptions(
    format=ExportFormat.MARKDOWN,
    single_file=True,
    include_metadata=True,
    include_memories=True,
    add_toc=True
)

# 执行导出
result = exporter.export_iteration(
    iteration.iteration_id,
    options
)

if result.success:
    print(f"✅ 文档已导出: {result.output_path}")
```

### 导出为 HTML

```python
options = ExportOptions(
    format=ExportFormat.HTML,
    single_file=True
)

result = exporter.export_iteration(iteration.iteration_id, options)
```

### 导出为 JSON

```python
options = ExportOptions(
    format=ExportFormat.JSON
)

result = exporter.export_iteration(iteration.iteration_id, options)
```

---

## 🛠️ 使用 MCP 工具

MCP 工具允许 AI 助手直接调用 Workflow 功能。

### 基础使用

```python
from aceflow.workflow.mcp import WorkflowMCPTools

mcp = WorkflowMCPTools()

# 开始新迭代
result = mcp.execute_tool(
    "workflow_start_iteration",
    {
        "mode": "minimal",
        "metadata": {"goal": "实现登录功能"}
    }
)

if result.success:
    print(result.data)
```

### 可用的 MCP 工具

**工作流管理** (4个):
- `workflow_start_iteration` - 开始新迭代
- `workflow_next_stage` - 进入下一阶段
- `workflow_complete_stage` - 完成阶段
- `workflow_complete_iteration` - 完成迭代

**状态管理** (4个):
- `state_get_current` - 获取当前状态
- `state_list_iterations` - 列出迭代
- `state_get_history` - 查看历史
- `state_update_stage` - 更新阶段

**记忆工具** (7个):
- `memory_record_stage_output` - 记录阶段输出
- `memory_record_decision` - 记录决策
- `memory_record_issue` - 记录问题
- `memory_record_learning` - 记录经验
- `memory_recall` - 召回记忆
- `memory_search` - 搜索记忆
- `memory_recall_for_stage` - 召回阶段记忆

**其他工具** (6个):
- 模板工具 (3个)
- 质量门工具 (2个)
- 导出工具 (1个)

详细文档: [MCP Tools Complete Catalog](./MCP_TOOLS_COMPLETE_CATALOG.md)

---

## 📊 完整工作流示例

```python
from pathlib import Path
from aceflow.workflow.core.engine import WorkflowEngine
from aceflow.workflow.core.state import StateManager
from aceflow.workflow.templates import TemplateManager
from aceflow.workflow.memory import MemoryManager
from aceflow.workflow.models import WorkflowMode
from aceflow.workflow.modes import MinimalWorkflow

# === 1. 初始化 ===
project_id = "user_auth_system"
state_manager = StateManager(
    project_id=project_id,
    state_dir=Path(".aceflow/state")
)

engine = WorkflowEngine(project_id=project_id)
engine.state_manager = state_manager
engine.register_mode_implementation(WorkflowMode.MINIMAL, MinimalWorkflow())

tm = TemplateManager()
mm = MemoryManager()

# === 2. 开始迭代 ===
result = engine.initialize(
    mode="minimal",
    metadata={"goal": "实现 JWT 用户认证"}
)

iteration_id = result['iteration_id']
print(f"📝 开始迭代: {iteration_id}")

# === 3. 第一阶段: Planning ===
iteration = state_manager.get_current_iteration()
stage = iteration.current_stage

# 获取并渲染模板
template = tm.get_template_for_stage(iteration.mode.value, stage.stage_id)
if template:
    doc = template.render({
        "iteration_id": iteration_id,
        "project_name": "用户认证系统",
        "owner": "开发团队"
    })
    print(f"\n📄 {stage.name} 阶段模板:")
    print(doc[:200] + "...")

# 记录决策
mm.record_decision(
    "使用 JWT 进行用户认证",
    {"reason": "无状态、易扩展"},
    iteration_id=iteration_id
)

# 记录阶段输出
mm.record_stage_output(
    iteration_id,
    stage,
    "完成需求分析和技术选型",
    iteration.mode.value
)

# === 4. 推进到 Development 阶段 ===
state_manager.advance_stage(metadata={
    "completed": ["需求文档", "技术方案"]
})

stage = state_manager.get_current_stage()
print(f"\n🚀 进入 {stage.name} 阶段")

# 记录问题
mm.record_issue(
    "Token 刷新机制需要设计",
    "medium",
    iteration_id=iteration_id,
    solution="实现 Refresh Token 机制"
)

# === 5. 推进到 Review 阶段 ===
state_manager.advance_stage()

# === 6. 导出文档 ===
from aceflow.workflow.exporter import DocumentExporter, ExportOptions, ExportFormat

exporter = DocumentExporter(state_manager, mm)
options = ExportOptions(
    format=ExportFormat.MARKDOWN,
    single_file=True,
    include_memories=True
)

export_result = exporter.export_iteration(iteration_id, options)
if export_result.success:
    print(f"\n✅ 文档已导出: {export_result.output_path}")

# === 7. 查看记忆摘要 ===
summary = mm.get_iteration_summary(iteration_id)
print(f"\n📊 记忆摘要:")
print(f"  - 总记忆数: {summary['total_memories']}")
print(f"  - 决策数: {summary['decisions_made']}")
print(f"  - 问题数: {summary['issues_encountered']}")
```

---

## 🔧 常见操作

### 查看项目状态

```python
# 获取状态摘要
summary = state_manager.get_state_summary()

print(f"迭代ID: {summary['iteration_id']}")
print(f"模式: {summary['mode']}")
print(f"当前阶段: {summary['current_stage']}")
print(f"完成度: {summary['completed_stages']}/{summary['total_stages']}")
print(f"进度: {summary['progress'] * 100:.1f}%")
```

### 更新阶段进度

```python
# 更新当前阶段进度为 50%
state_manager.update_stage_progress(stage.stage_id, 0.5)
```

### 查看状态转换历史

```python
# 获取最近 5 次状态转换
history = state_manager.get_transition_history(limit=5)

for transition in history:
    print(f"{transition['timestamp']}: {transition['from_stage']} → {transition['to_stage']}")
```

---

## 📖 下一步

- **详细 API 文档**: [Workflow API Reference](./WORKFLOW_API_REFERENCE.md)
- **MCP 工具目录**: [MCP Tools Complete Catalog](./MCP_TOOLS_COMPLETE_CATALOG.md)
- **测试报告**: [Workflow Testing Report](./WORKFLOW_TESTING_REPORT.md)
- **状态机设计**: [Workflow State Machine Design](./WORKFLOW_STATE_MACHINE_DESIGN.md)

---

## 💡 最佳实践

1. **选择合适的模式**
   - 小功能/原型 → Minimal
   - 常规功能 → Standard
   - 企业项目 → Complete
   - 复杂项目 → Smart

2. **充分利用记忆系统**
   - 记录所有技术决策
   - 记录问题和解决方案
   - 定期总结经验教训

3. **使用模板系统**
   - 保持文档一致性
   - 加速项目启动

4. **定期导出文档**
   - 作为项目归档
   - 便于团队分享

---

**文档版本**: v3.0
**最后更新**: 2025-11-09
**维护者**: AceFlow Team
