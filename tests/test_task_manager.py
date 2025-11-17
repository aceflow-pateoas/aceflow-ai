"""
测试 TaskManager (任务管理器)
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from aceflow.workflow.task_manager import TaskManager, TaskSuggestion
from aceflow.workflow.core.state import StateManager
from aceflow.workflow.models import WorkflowType, Task, TaskStatus


class TestTaskSuggestion:
    """测试TaskSuggestion数据类"""

    def test_task_suggestion_creation(self):
        """测试创建任务建议"""
        suggestion = TaskSuggestion(
            task_id="task_1",
            title="实现登录API",
            description="创建POST /api/login端点",
            dependencies=[],
            estimated_hours="2-4小时",
            priority="high"
        )

        assert suggestion.task_id == "task_1"
        assert suggestion.title == "实现登录API"
        assert suggestion.priority == "high"

    def test_task_suggestion_serialization(self):
        """测试任务建议序列化"""
        suggestion = TaskSuggestion(
            task_id="task_1",
            title="Test task",
            description="Test description",
            dependencies=["task_0"],
            metadata={"key": "value"}
        )

        data = suggestion.to_dict()
        assert data['task_id'] == "task_1"
        assert data['dependencies'] == ["task_0"]
        assert data['metadata'] == {"key": "value"}

        # 反序列化
        restored = TaskSuggestion.from_dict(data)
        assert restored.task_id == suggestion.task_id
        assert restored.dependencies == suggestion.dependencies


class TestTaskManagerInitialization:
    """测试TaskManager初始化"""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = StateManager(project_id="test_task_mgr")
        self.task_manager = TaskManager(self.state_manager)

    def teardown_method(self):
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        aceflow_dir = Path.cwd() / ".aceflow" / "state" / "test_task_mgr"
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_task_manager_initialization(self):
        """测试TaskManager初始化"""
        assert self.task_manager.state_manager == self.state_manager


class TestSuggestTasks:
    """测试任务建议功能"""

    def setup_method(self):
        self.state_manager = StateManager(project_id="test_suggest")
        self.task_manager = TaskManager(self.state_manager)

    def teardown_method(self):
        aceflow_dir = Path.cwd() / ".aceflow" / "state" / "test_suggest"
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_suggest_tasks_for_feature(self):
        """测试为功能开发工作项建议任务"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="用户登录API",
            description="实现JWT身份验证的登录接口"
        )

        suggestions = self.task_manager.suggest_tasks(
            work_item=work_item,
            requirement="需要实现POST /api/login接口，支持JWT token"
        )

        # 应该有建议（至少包含测试任务）
        assert len(suggestions) > 0

        # 检查API相关任务
        api_tasks = [s for s in suggestions if "API" in s.title or "接口" in s.title]
        assert len(api_tasks) > 0

        # 应该包含测试任务
        test_tasks = [s for s in suggestions if "测试" in s.title]
        assert len(test_tasks) > 0

    def test_suggest_tasks_for_bugfix_returns_empty(self):
        """测试Bug修复工作项不支持任务建议"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.BUGFIX,
            title="修复登录Bug"
        )

        suggestions = self.task_manager.suggest_tasks(
            work_item=work_item,
            requirement="修复登录超时问题"
        )

        # Bugfix不支持子任务，应该返回空列表
        assert len(suggestions) == 0

    def test_suggest_tasks_with_database(self):
        """测试包含数据库的任务建议"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="用户管理功能",
            description="需要设计用户表并实现CRUD操作"
        )

        suggestions = self.task_manager.suggest_tasks(
            work_item=work_item,
            requirement="需要数据库表存储用户信息"
        )

        # 应该包含数据库相关任务
        db_tasks = [s for s in suggestions if "数据库" in s.title or "表" in s.title]
        assert len(db_tasks) > 0

    def test_suggest_tasks_with_max_limit(self):
        """测试任务建议数量限制"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="完整的用户系统",
            description="包含API、数据库、前端页面"
        )

        suggestions = self.task_manager.suggest_tasks(
            work_item=work_item,
            requirement="完整用户系统",
            max_tasks=3
        )

        # 不应超过限制
        assert len(suggestions) <= 3


class TestCreateTasks:
    """测试批量创建任务"""

    def setup_method(self):
        self.state_manager = StateManager(project_id="test_create")
        self.task_manager = TaskManager(self.state_manager)

    def teardown_method(self):
        aceflow_dir = Path.cwd() / ".aceflow" / "state" / "test_create"
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_create_tasks_for_feature(self):
        """测试为功能开发工作项创建任务"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="Test feature"
        )

        tasks_data = [
            {
                'task_id': 'task_1',
                'title': '任务1',
                'description': '描述1',
                'dependencies': []
            },
            {
                'task_id': 'task_2',
                'title': '任务2',
                'description': '描述2',
                'dependencies': ['task_1']
            }
        ]

        success = self.task_manager.create_tasks(work_item.work_item_id, tasks_data)
        assert success is True

        # 验证任务已创建
        updated_work_item = self.state_manager.get_work_item(work_item.work_item_id)
        assert len(updated_work_item.tasks) == 2
        assert updated_work_item.tasks[0].task_id == 'task_1'
        assert updated_work_item.tasks[1].dependencies == ['task_1']

    def test_create_tasks_for_bugfix_fails(self):
        """测试Bug修复工作项不能创建任务"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.BUGFIX,
            title="Test bugfix"
        )

        tasks_data = [{'task_id': 'task_1', 'title': '任务1'}]

        success = self.task_manager.create_tasks(work_item.work_item_id, tasks_data)
        assert success is False


class TestGetTaskContext:
    """测试获取任务上下文"""

    def setup_method(self):
        self.state_manager = StateManager(project_id="test_context")
        self.task_manager = TaskManager(self.state_manager)

        # 创建工作项和任务
        self.work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="Test feature"
        )

        # 创建任务链：task_1 -> task_2 -> task_3
        self.task_manager.create_tasks(self.work_item.work_item_id, [
            {'task_id': 'task_1', 'title': '任务1', 'description': '第一个任务'},
            {'task_id': 'task_2', 'title': '任务2', 'description': '第二个任务', 'dependencies': ['task_1']},
            {'task_id': 'task_3', 'title': '任务3', 'description': '第三个任务', 'dependencies': ['task_2']}
        ])

    def teardown_method(self):
        aceflow_dir = Path.cwd() / ".aceflow" / "state" / "test_context"
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_get_task_context(self):
        """测试获取任务上下文"""
        context = self.task_manager.get_task_context(
            self.work_item.work_item_id,
            'task_2'
        )

        assert 'task' in context
        assert context['task']['task_id'] == 'task_2'

        # 应该包含工作项信息
        assert context['work_item']['work_item_id'] == self.work_item.work_item_id

        # 应该包含相关任务
        assert 'related_tasks' in context
        related_tasks = context['related_tasks']

        # task_2 依赖 task_1
        dependency_tasks = [rt for rt in related_tasks if rt['relation'] == 'dependency']
        assert len(dependency_tasks) == 1
        assert dependency_tasks[0]['task']['task_id'] == 'task_1'

        # task_3 依赖 task_2
        dependent_tasks = [rt for rt in related_tasks if rt['relation'] == 'dependent']
        assert len(dependent_tasks) == 1
        assert dependent_tasks[0]['task']['task_id'] == 'task_3'

    def test_get_task_context_not_found(self):
        """测试获取不存在的任务上下文"""
        context = self.task_manager.get_task_context(
            self.work_item.work_item_id,
            'task_999'
        )

        assert 'error' in context
        assert context['error'] == 'Task not found'


class TestGetPendingTasks:
    """测试获取待处理任务"""

    def setup_method(self):
        self.state_manager = StateManager(project_id="test_pending")
        self.task_manager = TaskManager(self.state_manager)

        self.work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="Test feature"
        )

        # 创建任务：task_1 -> task_2 -> task_3
        self.task_manager.create_tasks(self.work_item.work_item_id, [
            {'task_id': 'task_1', 'title': '任务1'},
            {'task_id': 'task_2', 'title': '任务2', 'dependencies': ['task_1']},
            {'task_id': 'task_3', 'title': '任务3', 'dependencies': ['task_2']},
            {'task_id': 'task_4', 'title': '任务4'}  # 无依赖
        ])

    def teardown_method(self):
        aceflow_dir = Path.cwd() / ".aceflow" / "state" / "test_pending"
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_get_pending_tasks_initial(self):
        """测试初始状态的待处理任务"""
        pending = self.task_manager.get_pending_tasks(self.work_item.work_item_id)

        # 只有 task_1 和 task_4 没有依赖，可以开始
        assert len(pending) == 2
        task_ids = {t.task_id for t in pending}
        assert task_ids == {'task_1', 'task_4'}

    def test_get_pending_tasks_after_completion(self):
        """测试完成任务后的待处理任务"""
        # 完成 task_1
        self.task_manager.update_task_status(
            self.work_item.work_item_id,
            'task_1',
            'completed'
        )

        pending = self.task_manager.get_pending_tasks(self.work_item.work_item_id)

        # 现在 task_2 和 task_4 可以开始了
        assert len(pending) == 2
        task_ids = {t.task_id for t in pending}
        assert task_ids == {'task_2', 'task_4'}

    def test_get_next_task(self):
        """测试获取下一个任务"""
        next_task = self.task_manager.get_next_task(self.work_item.work_item_id)

        assert next_task is not None
        # 应该是 task_1 或 task_4 之一（都没有依赖）
        assert next_task.task_id in ['task_1', 'task_4']

    def test_get_next_task_with_priority(self):
        """测试基于优先级获取下一个任务"""
        # 设置优先级
        work_item = self.state_manager.get_work_item(self.work_item.work_item_id)
        work_item.tasks[0].metadata['priority'] = 'low'  # task_1
        work_item.tasks[3].metadata['priority'] = 'high'  # task_4
        self.state_manager._save_work_item(work_item)

        next_task = self.task_manager.get_next_task(self.work_item.work_item_id)

        # 应该返回高优先级的 task_4
        assert next_task.task_id == 'task_4'
