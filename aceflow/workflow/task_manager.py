"""
Task Manager for AceFlow v4.0

Provides advanced task management capabilities including:
- AI-driven task suggestions
- Task creation and organization
- Task context retrieval for AI assistance
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading

from .core.state import StateManager
from .models import WorkItem, Task, TaskStatus, WorkflowType


@dataclass
class TaskSuggestion:
    """任务建议"""
    task_id: str
    title: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    estimated_hours: Optional[str] = None
    priority: str = "medium"  # high/medium/low
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'dependencies': self.dependencies,
            'estimated_hours': self.estimated_hours,
            'priority': self.priority,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskSuggestion':
        """Create from dictionary"""
        return cls(
            task_id=data['task_id'],
            title=data['title'],
            description=data['description'],
            dependencies=data.get('dependencies', []),
            estimated_hours=data.get('estimated_hours'),
            priority=data.get('priority', 'medium'),
            metadata=data.get('metadata', {})
        )


class TaskManager:
    """
    任务管理器 - 提供高级任务管理功能

    主要用于 FeatureWorkflow，支持任务拆解、依赖管理、进度追踪
    """

    def __init__(self, state_manager: StateManager):
        """
        Initialize task manager

        Args:
            state_manager: StateManager instance for persistence
        """
        self.state_manager = state_manager
        self._lock = threading.RLock()

    def suggest_tasks(
        self,
        work_item: WorkItem,
        requirement: str,
        max_tasks: int = 10
    ) -> List[TaskSuggestion]:
        """
        AI建议任务拆解（不执行，只返回建议）

        这个方法基于需求和工作项类型生成任务建议列表，
        由AI展示给用户确认后再调用 create_tasks 创建

        Args:
            work_item: 工作项对象
            requirement: 需求描述
            max_tasks: 最大任务数量

        Returns:
            任务建议列表
        """
        # 只有 FEATURE 类型支持子任务
        if work_item.type != WorkflowType.FEATURE:
            return []

        # 基于工作流类型和需求生成任务建议
        suggestions = []

        # 提取关键信息（简化版，实际可以使用更复杂的逻辑）
        title = work_item.title
        description = work_item.description or requirement

        # 基于阶段生成典型任务
        # 这里提供一个基础实现，实际使用时可以集成AI模型
        # 合并所有文本进行关键词检测
        all_text = f"{title} {description} {requirement}".lower()

        if "api" in all_text or "接口" in all_text:
            suggestions.extend(self._suggest_api_tasks(title, description))

        if "数据库" in all_text or "database" in all_text or "表" in all_text:
            suggestions.extend(self._suggest_database_tasks(title, description))

        if "前端" in all_text or "ui" in all_text or "页面" in all_text:
            suggestions.extend(self._suggest_frontend_tasks(title, description))

        # 总是添加测试任务
        suggestions.append(TaskSuggestion(
            task_id=f"task_{len(suggestions) + 1}",
            title="编写单元测试",
            description=f"为 {title} 编写完整的单元测试",
            dependencies=[s.task_id for s in suggestions],  # 依赖所有前面的任务
            estimated_hours="2-4小时",
            priority="high"
        ))

        return suggestions[:max_tasks]

    def _suggest_api_tasks(self, title: str, description: str) -> List[TaskSuggestion]:
        """建议API相关任务"""
        return [
            TaskSuggestion(
                task_id="task_1",
                title="设计API接口",
                description=f"定义 {title} 的API接口规范（路径、参数、返回值）",
                estimated_hours="2-4小时",
                priority="high"
            ),
            TaskSuggestion(
                task_id="task_2",
                title="实现API逻辑",
                description=f"编写 {title} 的核心业务逻辑",
                dependencies=["task_1"],
                estimated_hours="4-8小时",
                priority="high"
            )
        ]

    def _suggest_database_tasks(self, title: str, description: str) -> List[TaskSuggestion]:
        """建议数据库相关任务"""
        return [
            TaskSuggestion(
                task_id="task_db_1",
                title="设计数据库表结构",
                description=f"设计 {title} 所需的数据库表、字段、索引",
                estimated_hours="2-4小时",
                priority="high"
            ),
            TaskSuggestion(
                task_id="task_db_2",
                title="编写数据库迁移脚本",
                description="创建表结构的迁移脚本",
                dependencies=["task_db_1"],
                estimated_hours="1-2小时",
                priority="medium"
            )
        ]

    def _suggest_frontend_tasks(self, title: str, description: str) -> List[TaskSuggestion]:
        """建议前端相关任务"""
        return [
            TaskSuggestion(
                task_id="task_ui_1",
                title="设计页面布局",
                description=f"设计 {title} 的页面布局和交互流程",
                estimated_hours="2-4小时",
                priority="high"
            ),
            TaskSuggestion(
                task_id="task_ui_2",
                title="实现页面组件",
                description="编写页面组件和样式",
                dependencies=["task_ui_1"],
                estimated_hours="4-8小时",
                priority="high"
            )
        ]

    def create_tasks(
        self,
        work_item_id: str,
        tasks: List[Dict[str, Any]]
    ) -> bool:
        """
        创建任务列表（用户确认后）

        Args:
            work_item_id: 工作项ID
            tasks: 任务列表（字典格式）

        Returns:
            是否成功创建
        """
        with self._lock:
            work_item = self.state_manager.get_work_item(work_item_id)
            if not work_item:
                return False

            # 检查是否支持子任务
            if not work_item.supports_subtasks():
                return False

            # 批量创建任务
            for task_data in tasks:
                task = Task(
                    task_id=task_data['task_id'],
                    title=task_data['title'],
                    description=task_data.get('description', ''),
                    dependencies=task_data.get('dependencies', []),
                    metadata=task_data.get('metadata', {})
                )

                # 添加到工作项
                work_item.tasks.append(task)

            # 保存工作项
            self.state_manager._save_work_item(work_item)
            return True

    def add_task(
        self,
        work_item_id: str,
        task: Task,
        position: Optional[str] = None
    ) -> bool:
        """
        动态添加单个任务

        Args:
            work_item_id: 工作项ID
            task: 任务对象
            position: 可选位置（如 "after:task_2"）

        Returns:
            是否成功添加
        """
        # 直接委托给 StateManager
        return self.state_manager.add_task(work_item_id, task, position)

    def update_task_status(
        self,
        work_item_id: str,
        task_id: str,
        status: str
    ) -> bool:
        """
        更新任务状态

        Args:
            work_item_id: 工作项ID
            task_id: 任务ID
            status: 新状态

        Returns:
            是否成功更新
        """
        # 直接委托给 StateManager
        return self.state_manager.update_task_status(work_item_id, task_id, status)

    def get_task_context(
        self,
        work_item_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        获取任务上下文（用于AI补充任务要求）

        Args:
            work_item_id: 工作项ID
            task_id: 任务ID

        Returns:
            任务上下文信息，包括：
            - task: 当前任务详情
            - related_tasks: 相关任务（依赖和被依赖）
            - work_item: 工作项信息
            - current_stage: 当前阶段
        """
        work_item = self.state_manager.get_work_item(work_item_id)
        if not work_item:
            return {'error': 'Work item not found'}

        task = work_item.get_task_by_id(task_id)
        if not task:
            return {'error': 'Task not found'}

        # 查找相关任务
        related_tasks = []

        # 依赖的任务
        for dep_id in task.dependencies:
            dep_task = work_item.get_task_by_id(dep_id)
            if dep_task:
                related_tasks.append({
                    'relation': 'dependency',
                    'task': dep_task.to_dict()
                })

        # 依赖此任务的任务
        for other_task in work_item.tasks:
            if task_id in other_task.dependencies:
                related_tasks.append({
                    'relation': 'dependent',
                    'task': other_task.to_dict()
                })

        return {
            'task': task.to_dict(),
            'related_tasks': related_tasks,
            'work_item': {
                'work_item_id': work_item.work_item_id,
                'type': work_item.type.value,
                'title': work_item.title,
                'description': work_item.description
            },
            'current_stage': work_item.current_stage.to_dict() if work_item.current_stage else None,
            'task_progress': work_item.task_progress,
            'total_tasks': len(work_item.tasks),
            'completed_tasks': len([t for t in work_item.tasks if t.status == TaskStatus.COMPLETED])
        }

    def get_pending_tasks(self, work_item_id: str) -> List[Task]:
        """
        获取所有待处理的任务（已满足依赖）

        Args:
            work_item_id: 工作项ID

        Returns:
            可以开始的待处理任务列表
        """
        work_item = self.state_manager.get_work_item(work_item_id)
        if not work_item:
            return []

        pending_tasks = []
        completed_task_ids = {t.task_id for t in work_item.tasks if t.status == TaskStatus.COMPLETED}

        for task in work_item.tasks:
            if task.status == TaskStatus.PENDING:
                # 检查依赖是否都已完成
                dependencies_met = all(dep_id in completed_task_ids for dep_id in task.dependencies)
                if dependencies_met:
                    pending_tasks.append(task)

        return pending_tasks

    def get_next_task(self, work_item_id: str) -> Optional[Task]:
        """
        获取下一个应该执行的任务（基于依赖和优先级）

        Args:
            work_item_id: 工作项ID

        Returns:
            下一个任务，如果没有则返回 None
        """
        pending_tasks = self.get_pending_tasks(work_item_id)

        if not pending_tasks:
            return None

        # 优先级排序：high > medium > low
        priority_order = {'high': 0, 'medium': 1, 'low': 2}

        # 按优先级排序
        pending_tasks.sort(
            key=lambda t: priority_order.get(t.metadata.get('priority', 'medium'), 1)
        )

        return pending_tasks[0]
