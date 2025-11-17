# AceFlow v4.0 开发计划

> 基于需求文档的完整开发实施计划
>
> **版本**: v1.0
> **创建日期**: 2025-11-16
> **预计开发周期**: 8-10周

---

## 目录

1. [项目概览](#项目概览)
2. [开发原则](#开发原则)
3. [阶段0：基础架构重构](#阶段0基础架构重构)
4. [阶段1：核心工作流系统](#阶段1核心工作流系统)
5. [阶段2：任务追踪系统](#阶段2任务追踪系统)
6. [阶段3：质量检查机制](#阶段3质量检查机制)
7. [阶段4：记忆系统](#阶段4记忆系统)
8. [测试策略](#测试策略)
9. [发布计划](#发布计划)

---

## 项目概览

### 目标

将 AceFlow 从 v3.0 升级到 v4.0，重点解决：
- **P0**: 结构化工作流不实用 → 实现6种场景化工作流
- **P1**: AI 失忆问题 → 实现记忆自动注入机制
- **P2**: 代码质量不稳定 → 实现透明质量检查
- **P3**: 知识无法共享 → 后续版本考虑

### 核心变化

| 模块 | v3.0 | v4.0 |
|------|------|------|
| 工作流模式 | 4种通用模式 | 6种场景化工作流 |
| 任务追踪 | 单层（仅阶段） | 双层（工作项+子任务） |
| 提示词 | 简单描述 | 检查清单式 |
| 质量检查 | 无 | 透明+分类+主动 |
| 记忆系统 | 手动查询 | 自动注入 |

### 技术栈

- **语言**: Python 3.8+
- **MCP协议**: FastMCP
- **数据存储**: JSON文件（.aceflow/）
- **模板引擎**: Jinja2
- **测试**: pytest

---

## 开发原则

### 向后兼容

- ✅ 保留 v3.0 的核心 API
- ✅ 现有状态文件可迁移
- ✅ 逐步废弃旧模式，不强制删除

### 渐进式开发

- ✅ 每个阶段独立可测试
- ✅ 每个阶段完成后可发布 alpha/beta 版本
- ✅ 核心功能优先，高级功能后置

### 质量保证

- ✅ 单元测试覆盖率 > 80%
- ✅ 集成测试覆盖核心流程
- ✅ 每个阶段都有验收标准

---

## 阶段0：基础架构重构

**目标**: 为新功能奠定基础，重构数据模型和核心架构

**工期**: 1-1.5周

### 任务清单

#### Task 0.1: 数据模型扩展

**文件**: `aceflow/workflow/models/__init__.py`

**新增模型**:

```python
# 1. WorkflowType 枚举（6种工作流类型）
class WorkflowType(Enum):
    FEATURE = "feature"           # 功能开发
    BUGFIX = "bugfix"             # Bug修复
    REFACTOR = "refactor"         # 重构优化
    REVIEW = "review"             # 代码审查
    DOCUMENTATION = "documentation" # 文档编写
    PERFORMANCE = "performance"   # 性能排查

# 2. WorkItem 模型（工作项，第一层追踪）
@dataclass
class WorkItem:
    work_item_id: str
    type: WorkflowType
    title: str
    description: str
    status: WorkItemStatus  # pending/in_progress/completed/cancelled
    current_stage: str
    stages: List[Stage]
    tasks: List[Task]  # 仅 feature 类型有
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

# 3. Task 模型（子任务，第二层追踪）
@dataclass
class Task:
    task_id: str
    title: str
    description: str
    status: TaskStatus  # pending/in_progress/completed
    dependencies: List[str]  # 依赖的其他 task_id
    created_at: datetime
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]

# 4. ChecklistItem 模型（检查清单项）
@dataclass
class ChecklistItem:
    item_id: str
    content: str
    checked: bool
    metadata: Dict[str, Any]
```

**验收标准**:
- ✅ 所有新模型可以序列化/反序列化
- ✅ 通过单元测试（test_models.py）

---

#### Task 0.2: 状态管理器升级

**文件**: `aceflow/workflow/core/state.py`

**新增方法**:

```python
class StateManager:
    # 工作项管理
    def create_work_item(self, type: WorkflowType, title: str, ...) -> WorkItem
    def get_work_item(self, work_item_id: str) -> Optional[WorkItem]
    def list_work_items(self, status: Optional[str] = None) -> List[WorkItem]
    def update_work_item_status(self, work_item_id: str, status: str) -> bool

    # 任务管理（仅 feature 类型）
    def add_task(self, work_item_id: str, task: Task) -> bool
    def update_task_status(self, work_item_id: str, task_id: str, status: str) -> bool
    def get_tasks(self, work_item_id: str) -> List[Task]

    # 阶段管理（现有方法升级）
    def advance_stage(self, work_item_id: str) -> bool
    def complete_stage(self, work_item_id: str, stage_id: str) -> bool
```

**数据存储结构变更**:

```
.aceflow/
├── state/
│   └── {project_id}/
│       ├── work_items.json          # 所有工作项列表
│       ├── work_item_{id}.json      # 单个工作项详情
│       └── active_work_item.txt     # 当前活跃工作项ID
```

**验收标准**:
- ✅ 新增方法通过单元测试
- ✅ 向后兼容 v3.0 状态文件
- ✅ 并发安全（线程锁）

---

#### Task 0.3: 工作流引擎重构

**文件**: `aceflow/workflow/core/engine.py`

**重构内容**:

```python
class WorkflowEngine:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.state_manager = StateManager(project_id)
        self._workflow_registry = {}  # 注册6种工作流实现

    # 核心方法重构
    def start_work_item(self, type: WorkflowType, title: str,
                        description: str, metadata: Dict) -> Dict:
        """创建新工作项，替代原 initialize()"""
        pass

    def get_current_work_item(self) -> Optional[WorkItem]:
        """获取当前活跃工作项"""
        pass

    def list_all_work_items(self) -> List[WorkItem]:
        """列出所有工作项"""
        pass
```

**验收标准**:
- ✅ 新 API 通过单元测试
- ✅ 保留旧 API 并标记为 deprecated
- ✅ 文档更新

---

#### Task 0.4: 模板系统准备

**文件**: `aceflow/workflow/templates/manager.py`

**新增功能**:

```python
class TemplateManager:
    def get_workflow_template(self, type: WorkflowType, stage_id: str) -> str:
        """获取工作流阶段模板（检查清单式）"""
        pass

    def render_checklist(self, type: WorkflowType, stage_id: str,
                        context: Dict) -> str:
        """渲染检查清单"""
        pass
```

**模板目录结构**:

```
aceflow/templates/
├── workflows/
│   ├── feature/              # 功能开发
│   │   ├── requirement.md
│   │   ├── design.md
│   │   ├── implementation.md
│   │   ├── testing.md
│   │   └── delivery.md
│   ├── bugfix/               # Bug修复
│   ├── refactor/             # 重构优化
│   ├── review/               # 代码审查
│   ├── documentation/        # 文档编写
│   └── performance/          # 性能排查
```

**验收标准**:
- ✅ 模板目录结构创建完成
- ✅ 至少实现1个工作流的完整模板（feature）
- ✅ 模板渲染测试通过

---

### 阶段0 里程碑

**输出物**:
- ✅ 新数据模型完成并测试
- ✅ StateManager 升级完成
- ✅ WorkflowEngine 重构完成
- ✅ 模板系统基础搭建完成
- ✅ 单元测试通过率 > 90%

**下一阶段前置条件**:
- 所有 Task 0.x 完成
- 集成测试通过
- 代码审查完成

---

## 阶段1：核心工作流系统

**目标**: 实现6种场景化工作流的核心逻辑

**工期**: 2-3周

### Task 1.1: 工作流基类定义

**文件**: `aceflow/workflow/workflows/base.py`

**实现内容**:

```python
class BaseWorkflow(ABC):
    """工作流基类"""

    @property
    @abstractmethod
    def workflow_type(self) -> WorkflowType:
        """工作流类型"""
        pass

    @abstractmethod
    def get_stages(self) -> List[StageDefinition]:
        """返回阶段定义列表"""
        pass

    @abstractmethod
    def supports_subtasks(self) -> bool:
        """是否支持子任务拆分"""
        pass

    def get_stage_template(self, stage_id: str) -> str:
        """获取阶段模板（检查清单）"""
        pass

    def validate_stage_completion(self, stage_id: str,
                                  checklist: Dict) -> ValidationResult:
        """验证阶段是否完成"""
        pass
```

**验收标准**:
- ✅ 基类定义清晰
- ✅ 抽象方法明确
- ✅ 文档完整

---

### Task 1.2: 功能开发工作流

**文件**: `aceflow/workflow/workflows/feature.py`

**实现内容**:

```python
class FeatureWorkflow(BaseWorkflow):
    workflow_type = WorkflowType.FEATURE

    def get_stages(self) -> List[StageDefinition]:
        return [
            StageDefinition(
                stage_id="requirement",
                name="需求梳理",
                description="梳理需求并输出设计方案",
                checklist_template="workflows/feature/requirement.md"
            ),
            StageDefinition(
                stage_id="design",
                name="设计方案",
                description="输出核心逻辑、接口定义、技术方案",
                checklist_template="workflows/feature/design.md"
            ),
            StageDefinition(
                stage_id="implementation",
                name="编码实现",
                description="实现功能代码",
                checklist_template="workflows/feature/implementation.md"
            ),
            StageDefinition(
                stage_id="testing",
                name="功能测试",
                description="测试验证功能正确性",
                checklist_template="workflows/feature/testing.md"
            ),
            StageDefinition(
                stage_id="delivery",
                name="完成交付",
                description="标记完成并记录",
                checklist_template="workflows/feature/delivery.md"
            )
        ]

    def supports_subtasks(self) -> bool:
        return True  # 功能开发支持子任务
```

**模板内容示例** (`workflows/feature/requirement.md`):

```markdown
# 需求梳理阶段

## 检查清单

请确保完成以下所有项目：

### 必须完成
- [ ] 接口定义已输出（API路径、入参、出参、错误码）
- [ ] 核心逻辑已设计（伪代码或流程描述）
- [ ] 技术方案已确认（使用的库、存储方案、架构模式）
- [ ] 潜在问题已识别（性能、安全、并发等）

### 输出物
- API 接口定义文档
- 核心逻辑设计文档
- 技术方案说明

## 完成标准

全部检查项通过后，调用 `complete_stage(stage_id="requirement")` 进入下一阶段。

## 项目上下文

{{ project_memory }}
```

**验收标准**:
- ✅ FeatureWorkflow 实现完整
- ✅ 5个阶段模板编写完成
- ✅ 单元测试通过

---

### Task 1.3: Bug修复工作流

**文件**: `aceflow/workflow/workflows/bugfix.py`

**阶段定义**:
```
问题定位 → 修复方案 → 编码修复 → 回归测试 → 完成交付
```

**特点**:
- ❌ 不支持子任务
- ✅ 快速定位问题
- ✅ 简化流程

**验收标准**:
- ✅ BugfixWorkflow 实现完整
- ✅ 5个阶段模板编写完成
- ✅ 单元测试通过

---

### Task 1.4: 重构优化工作流

**文件**: `aceflow/workflow/workflows/refactor.py`

**阶段定义**:
```
现状分析 → 优化设计 → 编码重构 → 性能验证 → 完成交付
```

**验收标准**:
- ✅ RefactorWorkflow 实现完整
- ✅ 模板完成
- ✅ 测试通过

---

### Task 1.5: 代码审查工作流

**文件**: `aceflow/workflow/workflows/review.py`

**阶段定义**:
```
理解变更 → 检查清单审查 → 输出审查意见
```

**检查清单**:
```markdown
- [ ] 功能正确性：是否实现需求
- [ ] 代码规范：命名、格式、注释
- [ ] 测试覆盖：是否有测试、覆盖是否充分
- [ ] 性能影响：是否有性能问题
- [ ] 安全风险：是否有安全漏洞
- [ ] 可维护性：代码是否清晰、易理解
```

**验收标准**:
- ✅ ReviewWorkflow 实现完整
- ✅ 模板完成
- ✅ 测试通过

---

### Task 1.6: 文档编写工作流

**文件**: `aceflow/workflow/workflows/documentation.py`

**阶段定义**:
```
确定大纲 → 逐章编写 → 补充示例 → 审查发布
```

**验收标准**:
- ✅ DocumentationWorkflow 实现完整
- ✅ 模板完成
- ✅ 测试通过

---

### Task 1.7: 性能排查工作流

**文件**: `aceflow/workflow/workflows/performance.py`

**阶段定义**:
```
问题描述 → 快速定位 → 验证假设 → 给出方案
```

**验收标准**:
- ✅ PerformanceWorkflow 实现完整
- ✅ 模板完成
- ✅ 测试通过

---

### Task 1.8: MCP 工具更新

**文件**: `aceflow-mcp-server/aceflow_mcp_server/tools.py`

**新增工具**:

```python
@mcp.tool()
async def start_work_item(
    type: str,  # feature/bugfix/refactor/review/documentation/performance
    title: str,
    description: str,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    创建新工作项

    Args:
        type: 工作流类型
        title: 工作标题
        description: 详细描述
        metadata: 额外元数据

    Returns:
        {
            "success": true,
            "work_item_id": "work_001",
            "type": "feature",
            "current_stage": {...},
            "checklist": [...]
        }
    """
    pass

@mcp.tool()
async def list_work_items(
    status: Optional[str] = None
) -> Dict:
    """列出所有工作项"""
    pass

@mcp.tool()
async def get_work_item(
    work_item_id: str
) -> Dict:
    """获取工作项详情"""
    pass

@mcp.tool()
async def complete_stage(
    work_item_id: str,
    stage_id: str,
    checklist_results: Optional[Dict] = None
) -> Dict:
    """
    完成阶段

    Args:
        work_item_id: 工作项ID
        stage_id: 阶段ID
        checklist_results: 检查清单结果

    Returns:
        {
            "success": true,
            "next_stage": {...},
            "message": "进入下一阶段"
        }
    """
    pass
```

**验收标准**:
- ✅ 新工具实现完整
- ✅ 工具描述清晰（AI可理解）
- ✅ 集成测试通过

---

### 阶段1 里程碑

**输出物**:
- ✅ 6种工作流全部实现
- ✅ 30个阶段模板（6工作流 × 平均5阶段）
- ✅ MCP工具更新完成
- ✅ 集成测试覆盖所有工作流
- ✅ 用户文档更新

**演示场景**:
```
用户: "开始做用户登录功能"
AI: "这是功能开发任务吗？"
用户: "是"
AI 调用: start_work_item(type="feature", title="用户登录功能", ...)
返回: 需求梳理阶段的检查清单
AI: "让我们开始需求梳理，需要完成以下检查项..."
```

---

## 阶段2：任务追踪系统

**目标**: 实现双层任务追踪（工作项+子任务）

**工期**: 1.5-2周

### Task 2.1: 子任务管理核心

**文件**: `aceflow/workflow/task_manager.py`

**实现内容**:

```python
class TaskManager:
    """任务管理器（仅功能开发使用）"""

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager

    def suggest_tasks(self, work_item: WorkItem,
                     requirement: str) -> List[TaskSuggestion]:
        """
        AI建议任务拆解（不执行，只返回建议）

        这个方法返回任务建议，由AI展示给用户确认
        """
        pass

    def create_tasks(self, work_item_id: str,
                    tasks: List[Dict]) -> bool:
        """创建任务列表（用户确认后）"""
        pass

    def add_task(self, work_item_id: str, task: Task,
                position: Optional[str] = None) -> bool:
        """动态添加任务"""
        pass

    def update_task_status(self, work_item_id: str,
                          task_id: str, status: str) -> bool:
        """更新任务状态"""
        pass

    def get_task_context(self, work_item_id: str,
                        task_id: str) -> Dict:
        """
        获取任务上下文（用于AI补充任务要求）

        Returns:
            {
                "task": {...},
                "related_tasks": [...],
                "project_memory": {...}
            }
        """
        pass
```

**验收标准**:
- ✅ TaskManager 实现完整
- ✅ 单元测试通过
- ✅ 线程安全

---

### Task 2.2: MCP 任务管理工具

**文件**: `aceflow-mcp-server/aceflow_mcp_server/task_tools.py`

**新增工具**:

```python
@mcp.tool()
async def create_tasks(
    work_item_id: str,
    tasks: List[Dict]  # [{"title": "...", "description": "..."}]
) -> Dict:
    """
    创建任务列表（AI建议后，用户确认）

    Returns:
        {
            "success": true,
            "tasks": [...]
        }
    """
    pass

@mcp.tool()
async def add_task(
    work_item_id: str,
    title: str,
    description: str,
    position: Optional[str] = None  # "after:task_2"
) -> Dict:
    """
    动态添加任务

    触发流程：
    1. AI建议添加任务
    2. 系统提示用户确认
    3. 用户确认后调用此工具
    4. AI开始对话式补充任务要求
    """
    pass

@mcp.tool()
async def suggest_task_completion(
    work_item_id: str,
    task_id: str,
    completion_evidence: Optional[str] = None
) -> Dict:
    """
    建议标记任务完成

    Returns:
        {
            "success": true,
            "message": "💡 AI 建议标记 Task 1 为完成，是否确认？",
            "suggestion": {
                "task_id": "task_1",
                "task_title": "...",
                "completion_status": "ready"
            }
        }
    """
    pass

@mcp.tool()
async def confirm_task_completion(
    work_item_id: str,
    task_id: str,
    confirmed: bool
) -> Dict:
    """
    用户确认任务完成

    Args:
        confirmed: true=确认完成, false=需要修改
    """
    pass

@mcp.tool()
async def list_tasks(
    work_item_id: str,
    status: Optional[str] = None
) -> Dict:
    """列出工作项的所有任务"""
    pass
```

**验收标准**:
- ✅ 工具实现完整
- ✅ 工具描述清晰
- ✅ 集成测试通过

---

### Task 2.3: 状态更新提示机制

**问题**: AI 可能忘记调用状态更新工具

**解决方案**:

**方案1（工具返回值提示）- 优先实现**:

```python
# 在 complete_stage 返回值中强调下一步
{
    "success": true,
    "message": "✅ 需求梳理完成",
    "next_stage": {
        "stage_id": "design",
        "name": "设计方案",
        "checklist": [...]
    },
    "reminder": "⚠️ 请在完成设计方案后调用 complete_stage('design')"
}
```

**方案2（工具描述优化）**:

```python
@mcp.tool()
async def complete_stage(...):
    """
    完成当前阶段并进入下一阶段

    ⚠️ 重要：完成阶段所有检查项后，必须调用此工具标记完成！

    Args:
        ...
    """
    pass
```

**验收标准**:
- ✅ 工具返回值包含提示
- ✅ 工具描述强调必要性
- ✅ AI测试中遗忘率<10%

---

### Task 2.4: 工作项列表UI展示

**问题**: 用户需要查看所有工作项

**解决方案**:

创建格式化输出函数：

```python
def format_work_items_list(work_items: List[WorkItem]) -> str:
    """
    格式化工作项列表为Markdown

    Returns:
        ```
        ## 项目工作列表

        ### 进行中 (2)
        - #1 [功能] 用户登录功能 - 编码实现阶段
          进度: [██████░░░░] 60%
        - #5 [审查] Review PR#123 - 检查清单审查
          进度: [███░░░░░░░] 30%

        ### 待开始 (3)
        - #2 [Bug] 修复注册验证码
        - #3 [Bug] 修复密码重置超时
        - #6 [文档] 编写部署文档

        ### 已完成 (1)
        - #4 [优化] 登录性能优化 ✅
        ```
    """
    pass
```

**MCP工具**:

```python
@mcp.tool()
async def show_work_items_dashboard() -> Dict:
    """
    显示工作项仪表板

    Returns:
        {
            "success": true,
            "dashboard": "格式化的Markdown文本"
        }
    """
    pass
```

**验收标准**:
- ✅ 格式化输出清晰易读
- ✅ 包含进度条
- ✅ 分类展示（进行中/待开始/已完成）

---

### 阶段2 里程碑

**输出物**:
- ✅ 双层任务追踪完成
- ✅ 任务管理工具完成
- ✅ 状态更新提示机制完成
- ✅ 工作项仪表板完成
- ✅ 端到端测试通过

**演示场景**:
```
# 场景1：任务拆解
用户: "实现用户登录功能：账号密码登录、返回JWT、3次锁定"
AI: "我建议拆分为5个任务：
1. 实现登录API endpoint
2. 实现Token生成逻辑
..."
用户: "确认"
AI 调用: create_tasks(work_item_id="work_001", tasks=[...])

# 场景2：动态添加任务
用户: "需要加个验证码"
AI: "建议添加任务：实现验证码校验，插入在Task2之后"
AI 调用: add_task(...)
AI: "关于验证码，用图形还是短信？其他参数我按惯例设置..."

# 场景3：任务完成
AI: "登录API已实现完成"
AI 调用: suggest_task_completion(task_id="task_1")
返回: "💡 建议标记Task1完成，是否确认？"
用户: "确认"
AI 调用: confirm_task_completion(task_id="task_1", confirmed=true)
```

---

## 阶段3：质量检查机制

**目标**: 实现透明、分类、主动的质量检查

**工期**: 1-1.5周

### Task 3.1: 测试结果汇报格式

**文件**: `aceflow/workflow/quality/test_reporter.py`

**实现内容**:

```python
class TestReporter:
    """测试结果汇报器"""

    def format_test_results(self, results: TestResults) -> str:
        """
        格式化测试结果

        场景A：全部通过
        ✅ 所有测试通过（3/3）
        详细结果：
        1. ✅ test_login_success - 认证成功场景
        2. ✅ test_login_wrong_password - 密码错误处理
        3. ✅ test_login_user_not_found - 用户不存在处理
        执行时间：1.2s

        场景B：部分失败
        测试结果：2通过 / 1失败
        ✅ 通过：...
        ❌ 失败：...

        问题分类：
        🔧 可自动修复：无
        ⚠️ 需要决策：密码验证逻辑...

        场景C：发现潜在问题
        ✅ 所有测试通过
        ⚠️ 潜在问题发现：
        - 并发登录场景未测试
        - ...
        """
        pass

    def classify_failures(self, failures: List[TestFailure]) -> Dict:
        """
        分类测试失败

        Returns:
            {
                "auto_fixable": [...],      # AI可自动修复
                "needs_decision": [...],    # 需要人类决策
                "blocked": [...]            # 被阻塞
            }
        """
        pass

    def suggest_fixes(self, failure: TestFailure) -> List[FixSuggestion]:
        """
        建议修复方案（2-3个）

        Returns:
            [
                {
                    "title": "方案1：使用bcrypt",
                    "pros": ["安全、标准"],
                    "cons": ["需要引入库"],
                    "impact": "需要修改密码存储逻辑"
                },
                ...
            ]
        """
        pass
```

**验收标准**:
- ✅ 格式化输出清晰
- ✅ 问题分类准确
- ✅ 修复建议合理
- ✅ 单元测试通过

---

### Task 3.2: 代码生成策略

**文件**: `aceflow/workflow/quality/code_generator.py`

**实现内容**:

```python
class CodeGenerationStrategy:
    """代码生成策略"""

    def suggest_generation_order(self, work_item: WorkItem) -> List[str]:
        """
        建议代码生成顺序

        优先级：D > C > B
        D: 先骨架后实现
        C: 核心优先
        B: 逐文件生成

        Returns:
            [
                "1. 展示代码结构（函数签名、类定义）",
                "2. 生成核心逻辑",
                "3. 生成辅助函数",
                "4. 生成测试代码"
            ]
        """
        pass

    def generate_code_skeleton(self, design: Dict) -> str:
        """
        生成代码骨架

        示例:
        class LoginController {
          async login(req, res) { }
          async validatePassword(password, hash) { }
          async generateToken(user) { }
        }
        """
        pass
```

**MCP工具**:

```python
@mcp.tool()
async def request_code_generation(
    work_item_id: str,
    task_id: str,
    design_doc: str
) -> Dict:
    """
    请求代码生成（返回生成策略）

    Returns:
        {
            "success": true,
            "strategy": {
                "order": ["骨架", "核心", "辅助", "测试"],
                "skeleton": "class LoginController {...}",
                "reminder": "请确认代码结构后再填充实现"
            }
        }
    """
    pass
```

**验收标准**:
- ✅ 生成策略清晰
- ✅ 代码骨架准确
- ✅ AI理解并遵循

---

### Task 3.3: 静态检查集成

**文件**: `aceflow/workflow/quality/static_checker.py`

**实现内容**:

```python
class StaticChecker:
    """静态代码检查"""

    def check_syntax(self, code: str, language: str) -> List[Issue]:
        """语法检查"""
        pass

    def check_style(self, code: str, language: str) -> List[Issue]:
        """代码风格检查（ESLint/Flake8）"""
        pass

    def check_types(self, code: str, language: str) -> List[Issue]:
        """类型检查（TypeScript/mypy）"""
        pass

    def auto_fix(self, code: str, issues: List[Issue]) -> Tuple[str, List[Issue]]:
        """
        自动修复问题

        Returns:
            (修复后的代码, 无法修复的问题列表)
        """
        pass
```

**MCP工具**:

```python
@mcp.tool()
async def run_static_checks(
    work_item_id: str,
    code: str,
    language: str
) -> Dict:
    """
    运行静态检查

    Returns:
        {
            "success": true,
            "issues": {
                "syntax": [...],
                "style": [...],
                "types": [...]
            },
            "auto_fixed": [...],
            "needs_manual_fix": [...]
        }
    """
    pass
```

**验收标准**:
- ✅ 支持主流语言（Python/JavaScript/TypeScript）
- ✅ 自动修复常见问题
- ✅ 报告清晰

---

### Task 3.4: 潜在问题检测

**文件**: `aceflow/workflow/quality/issue_detector.py`

**实现内容**:

```python
class IssueDetector:
    """潜在问题检测器"""

    def detect_missing_tests(self, code: str, tests: str) -> List[MissingTest]:
        """
        检测缺失的测试场景

        Returns:
            [
                {
                    "type": "并发场景",
                    "description": "并发登录场景未测试",
                    "risk": "high",
                    "suggestion": "补充并发测试"
                },
                ...
            ]
        """
        pass

    def detect_security_risks(self, code: str) -> List[SecurityRisk]:
        """检测安全风险"""
        pass

    def detect_performance_issues(self, code: str) -> List[PerformanceIssue]:
        """检测性能问题"""
        pass
```

**MCP工具**:

```python
@mcp.tool()
async def detect_potential_issues(
    work_item_id: str,
    scope: str = "all"  # all/security/performance/testing
) -> Dict:
    """
    检测潜在问题

    Returns:
        {
            "success": true,
            "issues": [
                {
                    "category": "testing",
                    "description": "并发场景未测试",
                    "risk": "high",
                    "suggestion": "补充并发测试"
                },
                ...
            ],
            "question": "是否需要补充以下测试/功能？",
            "options": [
                "并发登录测试",
                "分布式计数器",
                "Token刷新机制"
            ]
        }
    """
    pass
```

**验收标准**:
- ✅ 检测准确率 > 70%
- ✅ 建议合理
- ✅ 主动询问用户

---

### 阶段3 里程碑

**输出物**:
- ✅ 测试汇报机制完成
- ✅ 代码生成策略完成
- ✅ 静态检查集成完成
- ✅ 潜在问题检测完成
- ✅ 质量检查端到端测试通过

**演示场景**:
```
# 场景：测试失败
AI 运行测试后：
"测试结果：2通过 / 1失败

❌ 失败：test_login_wrong_password
  错误：密码验证使用明文比对

问题分类：
⚠️ 需要决策：密码验证逻辑

修复方案建议：
方案1：使用bcrypt（推荐）
  优点：安全、标准
  缺点：需要引入库
  影响：需要修改密码存储逻辑

方案2：使用SHA256
  优点：无需额外库
  缺点：不够安全

请选择方案。"
```

---

## 阶段4：记忆系统

**目标**: 实现类似 Cline Memory Bank 的记忆自动注入

**工期**: 1.5-2周

### Task 4.1: 研究 Cline Memory Bank

**任务**: 深入研究 Cline Memory Bank 机制

**研究内容**:
1. Memory Bank 文件格式
2. 记忆触发时机
3. 记忆筛选策略
4. 记忆注入方式

**输出**:
- 技术调研报告（1-2页）
- 实现方案设计

---

### Task 4.2: 记忆数据模型

**文件**: `aceflow/workflow/memory/models.py`

**数据模型**:

```python
@dataclass
class Memory:
    memory_id: str
    type: MemoryType  # decision/lesson/document_ref
    title: str
    content: str
    tags: List[str]
    related_work_items: List[str]
    created_at: datetime
    importance: float  # 0-1
    metadata: Dict

@dataclass
class TechDecision(Memory):
    """技术决策记忆"""
    decision: str
    reason: str
    alternatives: List[str]
    impact: str

@dataclass
class Lesson(Memory):
    """经验教训记忆"""
    problem: str
    solution: str
    notes: str

@dataclass
class DocumentReference(Memory):
    """文档引用记忆"""
    document_path: str
    summary: str
```

**存储格式** (`.aceflow/memory/{project_id}/memory_bank.json`):

```json
{
  "version": "4.0",
  "memories": [
    {
      "memory_id": "mem_001",
      "type": "decision",
      "title": "JWT认证方案",
      "content": {
        "decision": "使用JWT认证，30分钟过期",
        "reason": "无状态，适合微服务",
        "tech_stack": "JWT + Redis",
        "alternatives": ["Session", "OAuth2"]
      },
      "tags": ["auth", "jwt", "security"],
      "importance": 0.9,
      "created_at": "2025-01-15T10:00:00"
    },
    {
      "memory_id": "mem_002",
      "type": "lesson",
      "title": "bcrypt性能优化",
      "content": {
        "problem": "bcrypt 10轮加密太慢",
        "solution": "改用8轮",
        "notes": "仍然安全，性能提升50%"
      },
      "tags": ["performance", "bcrypt", "auth"],
      "importance": 0.7,
      "created_at": "2025-01-15T14:00:00"
    }
  ]
}
```

**验收标准**:
- ✅ 数据模型定义完整
- ✅ 序列化/反序列化正常
- ✅ 向后兼容（可从v3迁移）

---

### Task 4.3: 记忆管理器

**文件**: `aceflow/workflow/memory/manager.py`

**实现内容**:

```python
class MemoryManager:
    """记忆管理器"""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.memory_file = Path(f".aceflow/memory/{project_id}/memory_bank.json")
        self._load_memories()

    def add_memory(self, memory: Memory) -> bool:
        """添加记忆"""
        pass

    def search_memories(self, query: str,
                       tags: Optional[List[str]] = None,
                       limit: int = 5) -> List[Memory]:
        """搜索记忆（关键词+标签）"""
        pass

    def get_relevant_memories(self, context: str,
                             limit: int = 5) -> List[Memory]:
        """
        获取相关记忆（智能匹配）

        Args:
            context: 当前上下文（如work_item描述）
            limit: 返回数量

        Returns:
            按相关性排序的记忆列表
        """
        pass

    def format_memories_for_injection(self,
                                     memories: List[Memory]) -> str:
        """
        格式化记忆用于注入

        Returns:
            ## 项目记忆

            ### 认证方案
            - 使用JWT认证，30分钟过期（无状态，适合微服务）
            - 注意：bcrypt使用8轮（性能优化）

            ### 相关文档
            - 邮件验证码实现：docs/email-verify.md
        """
        pass
```

**验收标准**:
- ✅ CRUD 操作完整
- ✅ 搜索功能有效
- ✅ 相关性匹配合理
- ✅ 格式化输出清晰

---

### Task 4.4: 记忆提炼机制

**文件**: `aceflow/workflow/memory/extractor.py`

**实现内容**:

```python
class MemoryExtractor:
    """记忆提炼器"""

    def detect_decision(self, text: str) -> Optional[TechDecision]:
        """
        检测技术决策

        判断标准（A+B+C）：
        A. 包含决策关键词（选择、决定、使用、采用）
        B. 影响范围广（多模块、长期维护）
        C. 技术选型类（库、框架、架构）

        满足2个以上 → 返回决策对象
        """
        pass

    def extract_decision_details(self, text: str) -> Dict:
        """
        从对话中提炼决策细节

        Returns:
            {
                "decision": "使用JWT认证",
                "reason": "无状态，适合微服务",
                "alternatives": ["Session", "OAuth2"],
                "tech_stack": ["JWT", "Redis"]
            }
        """
        pass

    def suggest_memory_save(self, text: str) -> Optional[Dict]:
        """
        建议保存记忆

        Returns:
            {
                "type": "decision",
                "title": "JWT认证方案",
                "extracted": {...},
                "confidence": 0.85
            }
        """
        pass
```

**MCP工具**:

```python
@mcp.tool()
async def save_memory(
    type: str,  # decision/lesson/document_ref
    title: str,
    content: Dict,
    tags: List[str]
) -> Dict:
    """
    保存记忆

    触发流程：
    1. AI检测到关键决策
    2. AI调用此工具展示提炼结果
    3. 用户确认/修改
    4. 写入memory bank

    Returns:
        {
            "success": true,
            "memory_id": "mem_003",
            "message": "记忆已保存"
        }
    """
    pass

@mcp.tool()
async def recall_memory(
    query: str,
    tags: Optional[List[str]] = None
) -> Dict:
    """
    手动查询记忆

    用户："之前登录怎么做的？"
    AI 调用：recall_memory(query="登录实现", tags=["auth"])
    """
    pass
```

**验收标准**:
- ✅ 决策检测准确率 > 75%
- ✅ 提炼内容完整
- ✅ 用户可修改
- ✅ 集成测试通过

---

### Task 4.5: 记忆自动注入

**文件**: `aceflow/workflow/memory/injector.py`

**实现内容**:

```python
class MemoryInjector:
    """记忆注入器"""

    def inject_memories_to_stage_prompt(self,
                                       work_item: WorkItem,
                                       stage: Stage) -> str:
        """
        将相关记忆注入到阶段提示词中

        工作流程：
        1. 根据work_item上下文搜索相关记忆
        2. 格式化记忆
        3. 注入到stage模板的 {{project_memory}} 占位符

        Returns:
            完整的阶段提示词（包含记忆）
        """
        pass

    def filter_relevant_memories(self,
                                work_item: WorkItem,
                                stage: Stage) -> List[Memory]:
        """
        筛选相关记忆

        筛选策略：
        1. 关键词匹配（work_item.title/description）
        2. 标签匹配（work_item.metadata.tags）
        3. 阶段相关性（设计阶段→决策类记忆）
        4. 重要性排序（importance字段）

        Returns:
            最多5条相关记忆
        """
        pass
```

**集成到 MCP 工具**:

修改 `start_work_item` 和 `complete_stage` 工具：

```python
@mcp.tool()
async def start_work_item(...) -> Dict:
    # ... 创建work_item ...

    # 注入记忆
    memories = memory_manager.get_relevant_memories(
        context=f"{title} {description}"
    )
    stage_prompt = memory_injector.inject_memories_to_stage_prompt(
        work_item, current_stage
    )

    return {
        "success": true,
        "work_item_id": "...",
        "current_stage": {
            "name": "需求梳理",
            "prompt": stage_prompt,  # ← 已包含项目记忆
            "checklist": [...]
        }
    }
```

**验收标准**:
- ✅ 记忆自动注入到每个阶段
- ✅ 筛选准确（相关性 > 0.7）
- ✅ 格式清晰（Markdown）
- ✅ 端到端测试通过

---

### Task 4.6: 记忆迁移工具

**文件**: `aceflow/workflow/memory/migrator.py`

**实现内容**:

```python
class MemoryMigrator:
    """从v3迁移记忆到v4"""

    def migrate_from_v3(self, v3_memory_dir: Path) -> Dict:
        """
        从v3记忆格式迁移到v4

        v3格式：
        .aceflow/memory/
        ├── decisions.json
        ├── issues.json
        └── learnings.json

        v4格式：
        .aceflow/memory/{project_id}/memory_bank.json
        """
        pass
```

**验收标准**:
- ✅ 迁移脚本完成
- ✅ v3数据完整迁移
- ✅ 测试通过

---

### 阶段4 里程碑

**输出物**:
- ✅ 记忆数据模型完成
- ✅ 记忆管理器完成
- ✅ 记忆提炼机制完成
- ✅ 记忆自动注入完成
- ✅ 迁移工具完成
- ✅ 端到端测试通过

**演示场景**:
```
# 场景1：记忆提炼
用户："我们用JWT认证，30分钟过期，用Redis存储"
AI："💾 检测到技术决策，是否记录到记忆库？

提炼内容：
- 决策：JWT认证，30分钟过期
- 技术栈：JWT + Redis
- 原因：无状态，适合微服务

[记录] [忽略]"

用户点击"记录" → 保存到memory_bank.json

# 场景2：记忆自动注入
用户："开始做密码重置功能"
AI 调用：start_work_item(type="feature", title="密码重置", ...)

返回的stage_prompt包含：
"""
## 项目记忆

### 认证方案
- 项目使用JWT认证，30分钟过期
- Redis存储，配置在 config/redis.ts

### 相关实现
- 邮件验证码已实现（5分钟过期）
  文档：docs/email-verify.md

基于以上记忆，请设计密码重置方案。
"""

AI："基于项目现有的JWT认证和邮件验证码，我建议..."
```

---

## 测试策略

### 单元测试

**覆盖率目标**: > 80%

**测试文件结构**:

```
tests/
├── test_models.py          # 数据模型测试
├── test_state_manager.py   # 状态管理器测试
├── test_workflow_engine.py # 工作流引擎测试
├── test_task_manager.py    # 任务管理器测试
├── test_quality/           # 质量检查测试
│   ├── test_reporter.py
│   ├── test_checker.py
│   └── test_detector.py
└── test_memory/            # 记忆系统测试
    ├── test_manager.py
    ├── test_extractor.py
    └── test_injector.py
```

**测试工具**:
- pytest
- pytest-cov（覆盖率）
- pytest-mock（Mock）
- pytest-asyncio（异步测试）

---

### 集成测试

**测试场景**:

```python
# 端到端：完整功能开发流程
def test_feature_development_workflow():
    """测试完整的功能开发工作流"""

    # 1. 创建工作项
    result = start_work_item(
        type="feature",
        title="用户登录",
        description="账号密码登录，JWT认证"
    )
    work_item_id = result["work_item_id"]

    # 2. 任务拆解
    tasks = create_tasks(work_item_id, [
        {"title": "实现登录API", "description": "..."},
        {"title": "实现Token生成", "description": "..."}
    ])

    # 3. 完成第一个任务
    suggest_task_completion(work_item_id, "task_1")
    confirm_task_completion(work_item_id, "task_1", confirmed=True)

    # 4. 完成阶段
    complete_stage(work_item_id, "requirement")

    # 5. 进入下一阶段
    stage = get_current_stage(work_item_id)
    assert stage["name"] == "设计方案"

    # 6. 保存记忆
    save_memory(
        type="decision",
        title="JWT认证",
        content={...}
    )

    # 7. 新工作项（验证记忆注入）
    result = start_work_item(
        type="feature",
        title="密码重置",
        description="邮件验证码重置"
    )

    # 验证返回的prompt包含之前的记忆
    assert "JWT认证" in result["current_stage"]["prompt"]
```

**测试场景清单**:
- ✅ 完整功能开发流程
- ✅ Bug修复流程
- ✅ 任务动态添加
- ✅ 质量检查流程
- ✅ 记忆提炼和注入
- ✅ 并发工作项处理

---

### AI 测试

**目标**: 验证AI能否正确理解和使用工具

**测试方法**:

1. **工具描述测试**: 确保description清晰
2. **返回值测试**: 确保返回结构AI可理解
3. **提示词测试**: 确保提示词有效引导AI

**测试脚本**:

```python
def test_ai_understands_tool_description():
    """测试AI是否理解工具描述"""

    tool_desc = get_tool_description("start_work_item")

    # 使用简单的NLP检查关键信息
    assert "创建" in tool_desc
    assert "工作项" in tool_desc
    assert "type" in tool_desc
    assert "title" in tool_desc
```

---

### 性能测试

**测试指标**:

| 操作 | 目标响应时间 |
|------|-------------|
| start_work_item | < 100ms |
| create_tasks | < 50ms |
| complete_stage | < 80ms |
| search_memories | < 200ms |
| inject_memories | < 150ms |

**测试工具**: pytest-benchmark

---

## 发布计划

### Alpha 版本（阶段0+1完成）

**时间**: 第3-4周

**功能**:
- ✅ 6种工作流基本实现
- ✅ 工作项列表管理
- ✅ 阶段追踪
- ⏸️ 任务追踪（未完成）
- ⏸️ 质量检查（未完成）
- ⏸️ 记忆系统（未完成）

**发布方式**:
- GitHub release（tag: v4.0.0-alpha.1）
- 文档说明"实验性版本"
- 小范围测试（内部+1-2个外部用户）

---

### Beta 版本（阶段0+1+2+3完成）

**时间**: 第6-7周

**功能**:
- ✅ 6种工作流完整
- ✅ 双层任务追踪
- ✅ 质量检查机制
- ⏸️ 记忆系统（未完成）

**发布方式**:
- GitHub release（tag: v4.0.0-beta.1）
- 扩大测试范围（5-10个用户）
- 收集反馈

---

### RC 版本（所有阶段完成）

**时间**: 第9周

**功能**:
- ✅ 所有功能完成
- ✅ 记忆系统完成
- ✅ 完整测试通过
- ✅ 文档完整

**发布方式**:
- GitHub release（tag: v4.0.0-rc.1）
- 公开测试

---

### 正式版本 v4.0.0

**时间**: 第10周

**发布条件**:
- ✅ 所有验收标准通过
- ✅ 无P0/P1 bug
- ✅ 测试覆盖率 > 80%
- ✅ 文档完整
- ✅ 至少5个用户反馈良好

**发布方式**:
- PyPI 发布（aceflow-ai==4.0.0）
- GitHub release
- 更新文档网站
- 发布公告（博客/社区）

---

## 附录

### 开发规范

**代码风格**:
- Python: Black (line-length=100)
- 类型注解: 必须
- 文档字符串: Google style

**Git 工作流**:
```
main (stable)
  ↑
develop (开发主分支)
  ↑
feature/stage-0-models (功能分支)
feature/stage-1-workflows
feature/stage-2-tasks
...
```

**Commit 规范**:
```
feat: 添加功能开发工作流实现
fix: 修复状态管理器并发问题
docs: 更新工作流API文档
test: 添加任务管理器集成测试
refactor: 重构模板管理器
```

---

### 依赖管理

**新增依赖**:

```toml
[project.dependencies]
# 现有依赖...
"jinja2>=3.1.0",
"pyyaml>=6.0.0",
"aiofiles>=23.0.0",

# 新增
"python-dateutil>=2.8.0",  # 时间处理
"jsonschema>=4.0.0",       # JSON验证
```

---

### 风险评估

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 记忆筛选不准确 | 中 | 中 | 多轮测试+用户反馈调优 |
| AI不遵守工具调用 | 高 | 低 | 强化工具描述+返回值提示 |
| 性能问题 | 中 | 低 | 性能测试+优化 |
| 向后兼容问题 | 高 | 低 | 迁移工具+充分测试 |

---

**文档版本**: v1.0
**最后更新**: 2025-11-16
**下次审核**: 阶段0完成后
