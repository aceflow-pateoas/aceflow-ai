"""
Workflow Data Models

Defines core data structures for workflow management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
import uuid


class WorkflowMode(Enum):
    """Workflow execution modes (v3.0 - will be deprecated)"""
    MINIMAL = "minimal"      # P→D→R (Fast prototyping)
    STANDARD = "standard"    # P1→P2→D1→D2→R1 (Balanced)
    COMPLETE = "complete"    # S1-S8 (Comprehensive)
    SMART = "smart"          # AI-driven adaptive mode


class WorkflowType(Enum):
    """Workflow types for different scenarios (v4.0)"""
    FEATURE = "feature"              # 功能开发
    BUGFIX = "bugfix"                # Bug修复
    REFACTOR = "refactor"            # 重构优化
    REVIEW = "review"                # 代码审查
    DOCUMENTATION = "documentation"  # 文档编写
    PERFORMANCE = "performance"      # 性能排查


class WorkItemStatus(Enum):
    """Work item status (v4.0)"""
    PENDING = "pending"              # 待开始
    IN_PROGRESS = "in_progress"      # 进行中
    COMPLETED = "completed"          # 已完成
    CANCELLED = "cancelled"          # 已取消
    BLOCKED = "blocked"              # 被阻塞


class TaskStatus(Enum):
    """Task status for subtasks (v4.0)"""
    PENDING = "pending"              # 待开始
    IN_PROGRESS = "in_progress"      # 进行中
    COMPLETED = "completed"          # 已完成
    SKIPPED = "skipped"              # 已跳过


class StageStatus(Enum):
    """Stage execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class IterationStatus(Enum):
    """Iteration execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Stage:
    """Represents a workflow stage"""
    stage_id: str
    name: str
    description: str
    status: StageStatus = StageStatus.PENDING
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tasks: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'stage_id': self.stage_id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'progress': self.progress,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'tasks': self.tasks,
            'deliverables': self.deliverables,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stage':
        """Create from dictionary"""
        return cls(
            stage_id=data['stage_id'],
            name=data['name'],
            description=data['description'],
            status=StageStatus(data.get('status', 'pending')),
            progress=data.get('progress', 0.0),
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            tasks=data.get('tasks', []),
            deliverables=data.get('deliverables', []),
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.now()
        )


@dataclass
class Iteration:
    """Represents a workflow iteration"""
    iteration_id: str = field(default_factory=lambda: f"iter_{uuid.uuid4().hex[:8]}")
    mode: WorkflowMode = WorkflowMode.SMART
    status: IterationStatus = IterationStatus.IN_PROGRESS
    stages: List[Stage] = field(default_factory=list)
    current_stage_index: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def current_stage(self) -> Optional[Stage]:
        """Get current stage"""
        if 0 <= self.current_stage_index < len(self.stages):
            return self.stages[self.current_stage_index]
        return None

    @property
    def overall_progress(self) -> float:
        """Calculate overall progress"""
        if not self.stages:
            return 0.0
        completed = sum(1 for stage in self.stages if stage.status == StageStatus.COMPLETED)
        return completed / len(self.stages)

    def get_stage_by_id(self, stage_id: str) -> Optional['Stage']:
        """根据stage_id获取阶段"""
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'iteration_id': self.iteration_id,
            'mode': self.mode.value,
            'status': self.status.value,
            'stages': [stage.to_dict() for stage in self.stages],
            'current_stage_index': self.current_stage_index,
            'current_stage_id': self.current_stage.stage_id if self.current_stage else None,
            'overall_progress': self.overall_progress,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Iteration':
        """Create from dictionary"""
        iteration = cls(
            iteration_id=data.get('iteration_id'),
            mode=WorkflowMode(data.get('mode', 'smart')),
            status=IterationStatus(data.get('status', 'in_progress')),
            current_stage_index=data.get('current_stage_index', 0),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.now(),
            metadata=data.get('metadata', {})
        )

        # Reconstruct stages
        for stage_data in data.get('stages', []):
            stage = Stage(
                stage_id=stage_data['stage_id'],
                name=stage_data['name'],
                description=stage_data['description'],
                status=StageStatus(stage_data.get('status', 'pending')),
                progress=stage_data.get('progress', 0.0),
                start_time=datetime.fromisoformat(stage_data['start_time']) if stage_data.get('start_time') else None,
                end_time=datetime.fromisoformat(stage_data['end_time']) if stage_data.get('end_time') else None,
                tasks=stage_data.get('tasks', []),
                deliverables=stage_data.get('deliverables', []),
                metadata=stage_data.get('metadata', {})
            )
            iteration.stages.append(stage)

        return iteration


@dataclass
class StateTransition:
    """Represents a state transition"""
    from_stage: str
    to_stage: str
    timestamp: datetime = field(default_factory=datetime.now)
    trigger: str = "manual"
    success: bool = True
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'from_stage': self.from_stage,
            'to_stage': self.to_stage,
            'timestamp': self.timestamp.isoformat(),
            'trigger': self.trigger,
            'success': self.success,
            'reasoning': self.reasoning,
            'metadata': self.metadata
        }


# ==================== v4.0 New Models ====================

@dataclass
class Task:
    """Represents a subtask (v4.0 - only for feature development)"""
    task_id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)  # List of task_ids
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'dependencies': self.dependencies,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create from dictionary"""
        return cls(
            task_id=data['task_id'],
            title=data['title'],
            description=data['description'],
            status=TaskStatus(data.get('status', 'pending')),
            dependencies=data.get('dependencies', []),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            metadata=data.get('metadata', {})
        )


@dataclass
class ChecklistItem:
    """Represents a checklist item (v4.0)"""
    item_id: str
    content: str
    checked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'item_id': self.item_id,
            'content': self.content,
            'checked': self.checked,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChecklistItem':
        """Create from dictionary"""
        return cls(
            item_id=data['item_id'],
            content=data['content'],
            checked=data.get('checked', False),
            metadata=data.get('metadata', {})
        )


@dataclass
class WorkItem:
    """Represents a work item (v4.0 - top-level tracking)"""
    work_item_id: str = field(default_factory=lambda: f"work_{uuid.uuid4().hex[:8]}")
    type: WorkflowType = WorkflowType.FEATURE
    title: str = ""
    description: str = ""
    status: WorkItemStatus = WorkItemStatus.PENDING
    current_stage_id: Optional[str] = None
    stages: List[Stage] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)  # Only for FEATURE type
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def current_stage(self) -> Optional[Stage]:
        """Get current stage by stage_id"""
        if self.current_stage_id:
            for stage in self.stages:
                if stage.stage_id == self.current_stage_id:
                    return stage
        return None

    @property
    def overall_progress(self) -> float:
        """Calculate overall progress"""
        if not self.stages:
            return 0.0
        completed = sum(1 for stage in self.stages if stage.status == StageStatus.COMPLETED)
        return completed / len(self.stages)

    @property
    def task_progress(self) -> float:
        """Calculate task progress (for feature development)"""
        if not self.tasks:
            return 0.0
        completed = sum(1 for task in self.tasks if task.status == TaskStatus.COMPLETED)
        return completed / len(self.tasks)

    def supports_subtasks(self) -> bool:
        """Check if this work item type supports subtasks"""
        return self.type == WorkflowType.FEATURE

    def get_stage_by_id(self, stage_id: str) -> Optional[Stage]:
        """Get stage by ID"""
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        return None

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'work_item_id': self.work_item_id,
            'type': self.type.value,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'current_stage_id': self.current_stage_id,
            'stages': [stage.to_dict() for stage in self.stages],
            'tasks': [task.to_dict() for task in self.tasks],
            'overall_progress': self.overall_progress,
            'task_progress': self.task_progress,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkItem':
        """Create from dictionary"""
        work_item = cls(
            work_item_id=data.get('work_item_id'),
            type=WorkflowType(data.get('type', 'feature')),
            title=data.get('title', ''),
            description=data.get('description', ''),
            status=WorkItemStatus(data.get('status', 'pending')),
            current_stage_id=data.get('current_stage_id'),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.now(),
            metadata=data.get('metadata', {})
        )

        # Reconstruct stages
        for stage_data in data.get('stages', []):
            stage = Stage.from_dict(stage_data)
            work_item.stages.append(stage)

        # Reconstruct tasks
        for task_data in data.get('tasks', []):
            task = Task.from_dict(task_data)
            work_item.tasks.append(task)

        return work_item
