# AceFlow Workflow API 参考文档

> **版本**: v3.0
> **最后更新**: 2025-11-09
> **模块**: `aceflow.workflow`

---

## 📚 目录

- [核心模块](#核心模块)
  - [WorkflowEngine](#workflowengine)
  - [StateManager](#statemanager)
- [数据模型](#数据模型)
  - [WorkflowMode](#workflowmode)
  - [Iteration](#iteration)
  - [Stage](#stage)
- [模板系统](#模板系统)
  - [TemplateManager](#templatemanager)
- [记忆系统](#记忆系统)
  - [MemoryManager](#memorymanager)
- [MCP 工具](#mcp-工具)
  - [WorkflowMCPTools](#workflowmcptools)
- [导出系统](#导出系统)
  - [DocumentExporter](#documentexporter)

---

## 核心模块

### WorkflowEngine

工作流引擎，负责工作流的初始化和模式管理。

**导入路径**: `aceflow.workflow.core.engine.WorkflowEngine`

#### 构造函数

```python
WorkflowEngine(project_id: str)
```

**参数**:
- `project_id` (str): 项目唯一标识符

**示例**:
```python
from aceflow.workflow.core.engine import WorkflowEngine

engine = WorkflowEngine(project_id="my_project")
```

#### 方法

##### `initialize(mode: str, metadata: dict = None, iteration_id: str = None) -> dict`

初始化一个新的工作流迭代。

**参数**:
- `mode` (str): 工作流模式 ("minimal", "standard", "complete", "smart")
- `metadata` (dict, 可选): 迭代元数据
- `iteration_id` (str, 可选): 自定义迭代ID，不提供则自动生成

**返回**: dict
```python
{
    "iteration_id": str,
    "mode": str,
    "total_stages": int,
    "current_stage": {
        "stage_id": str,
        "name": str,
        "description": str,
        # ...
    },
    "message": str
}
```

**示例**:
```python
result = engine.initialize(
    mode="minimal",
    metadata={"goal": "实现用户认证"},
    iteration_id="auth_feature_001"
)

print(f"Iteration ID: {result['iteration_id']}")
print(f"Total Stages: {result['total_stages']}")
print(f"Current Stage: {result['current_stage']['name']}")
```

##### `register_mode_implementation(mode: WorkflowMode, implementation: object)`

注册工作流模式实现。

**参数**:
- `mode` (WorkflowMode): 工作流模式枚举
- `implementation` (object): 模式实现对象

**示例**:
```python
from aceflow.workflow.models import WorkflowMode
from aceflow.workflow.modes import MinimalWorkflow

engine.register_mode_implementation(
    WorkflowMode.MINIMAL,
    MinimalWorkflow()
)
```

---

### StateManager

状态管理器，负责迭代状态的持久化和查询。

**导入路径**: `aceflow.workflow.core.state.StateManager`

#### 构造函数

```python
StateManager(project_id: str, state_dir: Path = None)
```

**参数**:
- `project_id` (str): 项目唯一标识符
- `state_dir` (Path, 可选): 状态存储目录，默认为 `.aceflow/state`

**示例**:
```python
from aceflow.workflow.core.state import StateManager
from pathlib import Path

state_manager = StateManager(
    project_id="my_project",
    state_dir=Path(".aceflow/state")
)
```

#### 方法

##### `initialize_iteration(iteration: Iteration) -> bool`

初始化并保存新迭代。

**参数**:
- `iteration` (Iteration): 迭代对象

**返回**: bool - 成功返回 True

**示例**:
```python
from aceflow.workflow.models import Iteration, WorkflowMode

iteration = Iteration(
    iteration_id="test_001",
    mode=WorkflowMode.MINIMAL
)

state_manager.initialize_iteration(iteration)
```

##### `get_current_iteration() -> Optional[Iteration]`

获取当前迭代对象。

**返回**: Iteration | None

**示例**:
```python
iteration = state_manager.get_current_iteration()
if iteration:
    print(f"Current stage: {iteration.current_stage.name}")
```

##### `get_current_stage() -> Optional[Stage]`

获取当前阶段对象。

**返回**: Stage | None

**示例**:
```python
stage = state_manager.get_current_stage()
if stage:
    print(f"Stage: {stage.stage_id} - {stage.name}")
    print(f"Status: {stage.status.value}")
```

##### `advance_stage(metadata: dict = None) -> bool`

推进到下一阶段。

**参数**:
- `metadata` (dict, 可选): 要添加到当前阶段的元数据

**返回**: bool - 成功返回 True，无更多阶段返回 False

**示例**:
```python
# 完成当前阶段并进入下一阶段
success = state_manager.advance_stage(
    metadata={"completed_tasks": ["task1", "task2"]}
)

if success:
    print("进入下一阶段")
else:
    print("所有阶段已完成")
```

##### `update_stage_progress(stage_id: str, progress: float) -> bool`

更新阶段进度。

**参数**:
- `stage_id` (str): 阶段ID
- `progress` (float): 进度值 (0.0 - 1.0)

**返回**: bool

**示例**:
```python
state_manager.update_stage_progress("P1", 0.5)  # 50%
```

##### `update_stage_status(iteration_id: str, stage_id: str, status: StageStatus) -> bool`

更新阶段状态。

**参数**:
- `iteration_id` (str): 迭代ID
- `stage_id` (str): 阶段ID
- `status` (StageStatus): 新状态

**返回**: bool

**示例**:
```python
from aceflow.workflow.models import StageStatus

state_manager.update_stage_status(
    "iter_001",
    "P1",
    StageStatus.COMPLETED
)
```

##### `get_state_summary() -> dict`

获取状态摘要。

**返回**: dict
```python
{
    "iteration_id": str,
    "mode": str,
    "current_stage": str,
    "total_stages": int,
    "completed_stages": int,
    "progress": float,
    "status": str
}
```

##### `get_transition_history(limit: int = 10) -> List[dict]`

获取状态转换历史。

**参数**:
- `limit` (int): 返回数量限制

**返回**: List[dict] - 转换记录列表

---

## 数据模型

### WorkflowMode

工作流模式枚举。

**导入路径**: `aceflow.workflow.models.WorkflowMode`

```python
class WorkflowMode(Enum):
    MINIMAL = "minimal"      # P→D→R (快速原型)
    STANDARD = "standard"    # P1→P2→D1→D2→R1 (标准流程)
    COMPLETE = "complete"    # S1-S8 (完整流程)
    SMART = "smart"          # AI驱动自适应模式
```

**使用示例**:
```python
from aceflow.workflow.models import WorkflowMode

mode = WorkflowMode.MINIMAL
print(mode.value)  # "minimal"
```

---

### Iteration

迭代数据模型。

**导入路径**: `aceflow.workflow.models.Iteration`

#### 字段

```python
@dataclass
class Iteration:
    iteration_id: str                          # 迭代ID
    mode: WorkflowMode                         # 工作流模式
    status: IterationStatus                    # 迭代状态
    stages: List[Stage]                        # 阶段列表
    current_stage_index: int                   # 当前阶段索引
    created_at: datetime                       # 创建时间
    updated_at: datetime                       # 更新时间
    metadata: Dict[str, Any]                   # 元数据
```

#### 属性

##### `current_stage -> Optional[Stage]`

获取当前阶段对象。

```python
iteration = state_manager.get_current_iteration()
if iteration.current_stage:
    print(iteration.current_stage.name)
```

##### `overall_progress -> float`

计算整体进度 (0.0 - 1.0)。

```python
progress = iteration.overall_progress
print(f"Progress: {progress * 100:.1f}%")
```

#### 方法

##### `get_stage_by_id(stage_id: str) -> Optional[Stage]`

根据 stage_id 获取阶段。

```python
stage = iteration.get_stage_by_id("P1")
if stage:
    print(f"Stage: {stage.name}")
```

##### `to_dict() -> Dict[str, Any]`

转换为字典。

```python
data = iteration.to_dict()
# 返回包含所有字段的字典
```

##### `from_dict(data: Dict[str, Any]) -> Iteration` (classmethod)

从字典创建迭代对象。

```python
iteration = Iteration.from_dict(data)
```

---

### Stage

阶段数据模型。

**导入路径**: `aceflow.workflow.models.Stage`

#### 字段

```python
@dataclass
class Stage:
    stage_id: str                              # 阶段ID
    name: str                                  # 阶段名称
    description: str                           # 阶段描述
    status: StageStatus                        # 阶段状态
    progress: float                            # 进度 (0.0-1.0)
    start_time: Optional[datetime]             # 开始时间
    end_time: Optional[datetime]               # 结束时间
    tasks: List[str]                           # 任务列表
    deliverables: List[str]                    # 交付物列表
    metadata: Dict[str, Any]                   # 元数据
    created_at: datetime                       # 创建时间
    updated_at: datetime                       # 更新时间
```

#### StageStatus 枚举

```python
class StageStatus(Enum):
    PENDING = "pending"                        # 待处理
    IN_PROGRESS = "in_progress"                # 进行中
    COMPLETED = "completed"                    # 已完成
    SKIPPED = "skipped"                        # 已跳过
    FAILED = "failed"                          # 失败
```

---

## 模板系统

### TemplateManager

模板管理器，负责模板的查询、渲染和输出。

**导入路径**: `aceflow.workflow.templates.TemplateManager`

#### 构造函数

```python
TemplateManager()
```

#### 方法

##### `get_template_for_stage(mode: str, stage_id: str) -> Optional[Template]`

获取指定模式和阶段的模板。

**参数**:
- `mode` (str): 工作流模式
- `stage_id` (str): 阶段ID

**返回**: Template | None

**示例**:
```python
from aceflow.workflow.templates import TemplateManager

tm = TemplateManager()
template = tm.get_template_for_stage("minimal", "P")

if template:
    content = template.read_content()
    print(content)
```

##### `render_template(template_id: str, variables: dict) -> str`

渲染模板。

**参数**:
- `template_id` (str): 模板ID
- `variables` (dict): 变量字典

**返回**: str - 渲染后的内容

**示例**:
```python
rendered = tm.render_template(
    "minimal_P",
    {
        "iteration_id": "iter_001",
        "project_name": "My Project",
        "owner": "John Doe"
    }
)
```

##### `list_templates(mode: str = None, type: TemplateType = None) -> List[Template]`

列出模板。

**参数**:
- `mode` (str, 可选): 按模式过滤
- `type` (TemplateType, 可选): 按类型过滤

**返回**: List[Template]

**示例**:
```python
# 获取所有 minimal 模式的模板
templates = tm.list_templates(mode="minimal")

for t in templates:
    print(f"{t.template_id}: {t.name}")
```

---

## 记忆系统

### MemoryManager

记忆管理器，负责项目记忆的记录、召回和搜索。

**导入路径**: `aceflow.workflow.memory.MemoryManager`

#### 构造函数

```python
MemoryManager(storage_path: Path = None)
```

**参数**:
- `storage_path` (Path, 可选): 存储路径，默认为 `.aceflow/memory.json`

#### 方法

##### `record_stage_output(iteration_id: str, stage: Stage, output: str, mode: str) -> Memory`

记录阶段输出。

**参数**:
- `iteration_id` (str): 迭代ID
- `stage` (Stage): 阶段对象
- `output` (str): 输出内容
- `mode` (str): 工作流模式

**返回**: Memory

**示例**:
```python
from aceflow.workflow.memory import MemoryManager

mm = MemoryManager()
memory = mm.record_stage_output(
    "iter_001",
    stage,
    "完成了用户认证模块的开发",
    "minimal"
)
```

##### `record_decision(decision: str, context: dict, iteration_id: str = None, stage_id: str = None) -> Memory`

记录技术决策。

**参数**:
- `decision` (str): 决策内容
- `context` (dict): 决策上下文
- `iteration_id` (str, 可选): 迭代ID
- `stage_id` (str, 可选): 阶段ID

**返回**: Memory

**示例**:
```python
memory = mm.record_decision(
    "选择 JWT 作为认证方案",
    {
        "alternatives": ["OAuth2", "Session"],
        "reason": "轻量级且易于实现"
    },
    iteration_id="iter_001"
)
```

##### `record_issue(issue: str, severity: str, iteration_id: str = None, stage_id: str = None, solution: str = None) -> Memory`

记录问题。

**参数**:
- `issue` (str): 问题描述
- `severity` (str): 严重程度 ("low", "medium", "high", "critical")
- `iteration_id` (str, 可选): 迭代ID
- `stage_id` (str, 可选): 阶段ID
- `solution` (str, 可选): 解决方案

**返回**: Memory

**示例**:
```python
memory = mm.record_issue(
    "登录接口响应时间过长",
    "high",
    iteration_id="iter_001",
    solution="添加 Redis 缓存"
)
```

##### `record_learning(learning: str, category: str = "general", iteration_id: str = None) -> Memory`

记录经验教训。

**参数**:
- `learning` (str): 经验教训内容
- `category` (str, 可选): 分类
- `iteration_id` (str, 可选): 迭代ID

**返回**: Memory

**示例**:
```python
memory = mm.record_learning(
    "JWT token 过期时间应设置为 30 分钟",
    category="security",
    iteration_id="iter_001"
)
```

##### `recall_for_stage(iteration_id: str, stage_id: str, limit: int = 10) -> List[Memory]`

召回阶段相关记忆。

**参数**:
- `iteration_id` (str): 迭代ID
- `stage_id` (str): 阶段ID
- `limit` (int): 返回数量限制

**返回**: List[Memory]

**示例**:
```python
memories = mm.recall_for_stage("iter_001", "P1", limit=5)

for mem in memories:
    print(f"{mem.type.value}: {mem.content[:50]}...")
```

##### `get_iteration_summary(iteration_id: str) -> dict`

获取迭代记忆摘要。

**返回**: dict
```python
{
    "iteration_id": str,
    "total_memories": int,
    "stages_completed": int,
    "decisions_made": int,
    "issues_encountered": int,
    "learnings_captured": int
}
```

---

## MCP 工具

### WorkflowMCPTools

MCP 工具集合，提供 21 个工作流相关的 MCP 工具。

**导入路径**: `aceflow.workflow.mcp.WorkflowMCPTools`

#### 构造函数

```python
WorkflowMCPTools(working_directory: Path = None)
```

**参数**:
- `working_directory` (Path, 可选): 工作目录，默认为当前目录

#### 方法

##### `execute_tool(tool_name: str, arguments: dict) -> MCPToolResult`

执行 MCP 工具。

**参数**:
- `tool_name` (str): 工具名称
- `arguments` (dict): 工具参数

**返回**: MCPToolResult

**示例**:
```python
from aceflow.workflow.mcp import WorkflowMCPTools

mcp = WorkflowMCPTools()

# 开始新迭代
result = mcp.execute_tool(
    "workflow_start_iteration",
    {
        "mode": "minimal",
        "iteration_id": "test_001",
        "metadata": {"goal": "实现登录功能"}
    }
)

if result.success:
    print(result.data)
```

#### 可用工具列表

**工作流管理** (4个):
1. `workflow_start_iteration` - 开始新迭代
2. `workflow_next_stage` - 进入下一阶段
3. `workflow_complete_stage` - 完成当前阶段
4. `workflow_complete_iteration` - 完成迭代

**状态管理** (4个):
5. `state_get_current` - 获取当前状态
6. `state_list_iterations` - 列出所有迭代
7. `state_get_history` - 获取状态转换历史
8. `state_update_stage` - 更新阶段状态

**模板工具** (3个):
9. `template_get_stage` - 获取阶段模板
10. `template_render` - 渲染模板
11. `template_list` - 列出可用模板

**记忆工具** (7个):
12. `memory_record_stage_output` - 记录阶段输出
13. `memory_recall_for_stage` - 召回阶段记忆
14. `memory_record_issue` - 记录问题
15. `memory_record_decision` - 记录决策
16. `memory_record_learning` - 记录经验教训
17. `memory_recall` - 召回指定记忆
18. `memory_search` - 搜索记忆内容

**质量门工具** (2个):
19. `gate_evaluate` - 评估质量门
20. `gate_get_info` - 获取质量门信息

**导出工具** (1个):
21. `export_iteration` - 导出迭代文档

详细的工具参数和使用方法，请参考 [MCP Tools Complete Catalog](./MCP_TOOLS_COMPLETE_CATALOG.md)。

---

## 导出系统

### DocumentExporter

文档导出器，支持多种格式的迭代文档导出。

**导入路径**: `aceflow.workflow.exporter.DocumentExporter`

#### 构造函数

```python
DocumentExporter(
    state_manager: StateManager = None,
    memory_manager: MemoryManager = None
)
```

**参数**:
- `state_manager` (StateManager, 可选): 状态管理器
- `memory_manager` (MemoryManager, 可选): 记忆管理器

#### 方法

##### `export_iteration(iteration_id: str, options: ExportOptions = None) -> ExportResult`

导出单个迭代。

**参数**:
- `iteration_id` (str): 迭代ID
- `options` (ExportOptions, 可选): 导出选项

**返回**: ExportResult

**示例**:
```python
from aceflow.workflow.exporter import DocumentExporter, ExportOptions, ExportFormat

exporter = DocumentExporter()

# 导出为 Markdown
options = ExportOptions(
    format=ExportFormat.MARKDOWN,
    single_file=True,
    include_metadata=True
)

result = exporter.export_iteration("iter_001", options)

if result.success:
    print(f"Exported to: {result.output_path}")
```

### ExportOptions

导出选项配置。

```python
@dataclass
class ExportOptions:
    # 格式选项
    format: ExportFormat = ExportFormat.MARKDOWN

    # 内容选项
    include_metadata: bool = True
    include_stage_outputs: bool = True
    include_memories: bool = True
    include_gate_results: bool = True
    include_templates: bool = False
    include_transitions: bool = False

    # 输出选项
    output_dir: Optional[Path] = None
    single_file: bool = True
    create_index: bool = True

    # 样式选项
    add_toc: bool = True
    add_timestamps: bool = True
    add_statistics: bool = True

    # 过滤选项
    stage_filter: Optional[List[str]] = None
```

### ExportFormat

导出格式枚举。

```python
class ExportFormat(Enum):
    MARKDOWN = "markdown"   # Markdown 格式
    HTML = "html"          # HTML 格式
    JSON = "json"          # JSON 格式
    ARCHIVE = "archive"    # ZIP 压缩包
```

---

## 使用示例

### 完整的工作流示例

```python
from pathlib import Path
from aceflow.workflow.core.engine import WorkflowEngine
from aceflow.workflow.core.state import StateManager
from aceflow.workflow.templates import TemplateManager
from aceflow.workflow.memory import MemoryManager
from aceflow.workflow.models import WorkflowMode
from aceflow.workflow.modes import MinimalWorkflow

# 1. 初始化组件
project_id = "my_project"
state_manager = StateManager(
    project_id=project_id,
    state_dir=Path(".aceflow/state")
)

engine = WorkflowEngine(project_id=project_id)
engine.state_manager = state_manager
engine.register_mode_implementation(WorkflowMode.MINIMAL, MinimalWorkflow())

template_manager = TemplateManager()
memory_manager = MemoryManager()

# 2. 开始新迭代
result = engine.initialize(
    mode="minimal",
    metadata={"goal": "实现用户认证功能"}
)

iteration_id = result['iteration_id']
print(f"开始迭代: {iteration_id}")

# 3. 获取当前阶段模板
iteration = state_manager.get_current_iteration()
stage = iteration.current_stage

template = template_manager.get_template_for_stage(
    iteration.mode.value,
    stage.stage_id
)

if template:
    content = template.render({
        "iteration_id": iteration_id,
        "project_name": "My Project",
        "owner": "John Doe"
    })
    print(f"Stage: {stage.name}")
    print(content)

# 4. 记录阶段工作
memory_manager.record_stage_output(
    iteration_id,
    stage,
    "完成了需求分析和技术选型",
    iteration.mode.value
)

memory_manager.record_decision(
    "使用 JWT 进行用户认证",
    {"reason": "轻量级且易于实现"},
    iteration_id=iteration_id,
    stage_id=stage.stage_id
)

# 5. 完成阶段并推进
state_manager.advance_stage(metadata={
    "completed_tasks": ["需求分析", "技术选型"]
})

# 6. 导出迭代文档
from aceflow.workflow.exporter import DocumentExporter, ExportOptions, ExportFormat

exporter = DocumentExporter(state_manager, memory_manager)
options = ExportOptions(
    format=ExportFormat.MARKDOWN,
    single_file=True,
    include_metadata=True,
    include_memories=True
)

export_result = exporter.export_iteration(iteration_id, options)
if export_result.success:
    print(f"文档已导出: {export_result.output_path}")
```

---

## 错误处理

所有 API 方法都应该进行适当的错误处理:

```python
try:
    result = engine.initialize(mode="minimal")
except ValueError as e:
    print(f"无效的模式: {e}")
except Exception as e:
    print(f"初始化失败: {e}")
```

---

## 相关文档

- [MCP Tools Complete Catalog](./MCP_TOOLS_COMPLETE_CATALOG.md) - MCP 工具完整目录
- [Workflow Testing Report](./WORKFLOW_TESTING_REPORT.md) - 测试报告
- [Workflow State Machine Design](./WORKFLOW_STATE_MACHINE_DESIGN.md) - 状态机设计

---

**文档维护**: AceFlow Team
**API 版本**: v3.0
**最后更新**: 2025-11-09
