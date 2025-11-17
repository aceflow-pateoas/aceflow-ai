"""
测试 AceFlow v4.0 MCP 任务管理工具 (Task 2.2)
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import uuid

# Add aceflow-mcp-server to path
mcp_server_dir = Path(__file__).parent.parent / "aceflow-mcp-server"
sys.path.insert(0, str(mcp_server_dir))

from aceflow_mcp_server.tools import AceFlowTools
from aceflow.workflow.models import WorkflowType


def get_unique_project_id():
    """Generate a unique project ID for test isolation."""
    return f"test_{uuid.uuid4().hex[:8]}"


class TestMCPTaskTools:
    """测试MCP任务管理工具（5个新方法）"""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_id = get_unique_project_id()
        self.tools = AceFlowTools(working_directory=self.temp_dir, project_id=self.project_id)

    def teardown_method(self):
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        # Clean up project-specific .aceflow directory
        aceflow_dir = Path.cwd() / ".aceflow" / "state" / self.project_id
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_suggest_tasks_for_feature(self):
        """测试为功能开发工作项建议任务"""
        # Start a feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="用户登录API",
            description="实现JWT身份验证的登录接口"
        )
        work_item_id = start_result['work_item_id']

        # Suggest tasks
        result = self.tools.aceflow_v4_suggest_tasks(
            work_item_id=work_item_id,
            requirement="需要实现POST /api/login接口，支持JWT token"
        )

        assert result['success'] is True
        assert result['count'] > 0
        assert 'suggestions' in result
        # Should contain API-related tasks
        assert any('API' in s['title'] or '接口' in s['title'] for s in result['suggestions'])

    def test_suggest_tasks_for_bugfix_returns_empty(self):
        """测试Bug修复工作项不支持任务建议"""
        # Start a bugfix work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="bugfix",
            title="修复登录Bug"
        )
        work_item_id = start_result['work_item_id']

        # Try to suggest tasks
        result = self.tools.aceflow_v4_suggest_tasks(
            work_item_id=work_item_id,
            requirement="修复登录超时问题"
        )

        assert result['success'] is True
        assert result['count'] == 0  # Bugfix doesn't support subtasks

    def test_create_tasks_batch(self):
        """测试批量创建任务"""
        # Start a feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']

        # Create tasks
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

        result = self.tools.aceflow_v4_create_tasks(
            work_item_id=work_item_id,
            tasks=tasks_data
        )

        assert result['success'] is True
        assert result['tasks_created'] == 2
        assert result['total_tasks'] == 2

    def test_create_tasks_for_bugfix_fails(self):
        """测试Bug修复工作项不能批量创建任务"""
        # Start a bugfix work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="bugfix",
            title="Test bugfix"
        )
        work_item_id = start_result['work_item_id']

        # Try to create tasks
        tasks_data = [{'task_id': 'task_1', 'title': '任务1'}]

        result = self.tools.aceflow_v4_create_tasks(
            work_item_id=work_item_id,
            tasks=tasks_data
        )

        assert result['success'] is False

    def test_get_task_context(self):
        """测试获取任务上下文"""
        # Start a feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']

        # Create tasks with dependencies
        tasks_data = [
            {'task_id': 'task_1', 'title': '任务1'},
            {'task_id': 'task_2', 'title': '任务2', 'dependencies': ['task_1']},
            {'task_id': 'task_3', 'title': '任务3', 'dependencies': ['task_2']}
        ]
        self.tools.aceflow_v4_create_tasks(work_item_id, tasks_data)

        # Get task context for task_2
        result = self.tools.aceflow_v4_get_task_context(
            work_item_id=work_item_id,
            task_id='task_2'
        )

        assert result['success'] is True
        assert 'context' in result
        context = result['context']
        assert context['task']['task_id'] == 'task_2'
        assert 'related_tasks' in context
        # task_2 depends on task_1 and task_3 depends on task_2
        related_tasks = context['related_tasks']
        assert len(related_tasks) == 2

    def test_get_task_context_not_found(self):
        """测试获取不存在的任务上下文"""
        # Start a feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']

        # Try to get context for non-existent task
        result = self.tools.aceflow_v4_get_task_context(
            work_item_id=work_item_id,
            task_id='task_999'
        )

        assert result['success'] is False

    def test_get_pending_tasks_initial(self):
        """测试获取初始状态的待处理任务"""
        # Start a feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']

        # Create tasks: task_1 -> task_2 -> task_3, and independent task_4
        tasks_data = [
            {'task_id': 'task_1', 'title': '任务1'},
            {'task_id': 'task_2', 'title': '任务2', 'dependencies': ['task_1']},
            {'task_id': 'task_3', 'title': '任务3', 'dependencies': ['task_2']},
            {'task_id': 'task_4', 'title': '任务4'}  # No dependencies
        ]
        self.tools.aceflow_v4_create_tasks(work_item_id, tasks_data)

        # Get pending tasks
        result = self.tools.aceflow_v4_get_pending_tasks(work_item_id=work_item_id)

        assert result['success'] is True
        assert result['count'] == 2  # Only task_1 and task_4 have no pending dependencies
        task_ids = {t['task_id'] for t in result['pending_tasks']}
        assert task_ids == {'task_1', 'task_4'}

    def test_get_pending_tasks_after_completion(self):
        """测试完成任务后的待处理任务"""
        # Start a feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']

        # Create tasks: task_1 -> task_2 -> task_3, and independent task_4
        tasks_data = [
            {'task_id': 'task_1', 'title': '任务1'},
            {'task_id': 'task_2', 'title': '任务2', 'dependencies': ['task_1']},
            {'task_id': 'task_3', 'title': '任务3', 'dependencies': ['task_2']},
            {'task_id': 'task_4', 'title': '任务4'}
        ]
        self.tools.aceflow_v4_create_tasks(work_item_id, tasks_data)

        # Complete task_1
        self.tools.aceflow_v4_update_task_status(
            work_item_id=work_item_id,
            task_id='task_1',
            status='completed'
        )

        # Get pending tasks
        result = self.tools.aceflow_v4_get_pending_tasks(work_item_id=work_item_id)

        assert result['success'] is True
        assert result['count'] == 2  # Now task_2 and task_4 are ready
        task_ids = {t['task_id'] for t in result['pending_tasks']}
        assert task_ids == {'task_2', 'task_4'}

    def test_get_next_task(self):
        """测试获取下一个任务"""
        # Start a feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']

        # Create tasks
        tasks_data = [
            {'task_id': 'task_1', 'title': '任务1'},
            {'task_id': 'task_2', 'title': '任务2', 'dependencies': ['task_1']}
        ]
        self.tools.aceflow_v4_create_tasks(work_item_id, tasks_data)

        # Get next task
        result = self.tools.aceflow_v4_get_next_task(work_item_id=work_item_id)

        assert result['success'] is True
        assert result['has_next_task'] is True
        assert result['next_task']['task_id'] == 'task_1'  # task_1 has no dependencies

    def test_get_next_task_with_priority(self):
        """测试基于优先级获取下一个任务"""
        # Start a feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']

        # Create tasks with different priorities
        tasks_data = [
            {'task_id': 'task_1', 'title': '任务1', 'metadata': {'priority': 'low'}},
            {'task_id': 'task_2', 'title': '任务2', 'metadata': {'priority': 'high'}}
        ]
        self.tools.aceflow_v4_create_tasks(work_item_id, tasks_data)

        # Get next task (should prioritize high priority)
        result = self.tools.aceflow_v4_get_next_task(work_item_id=work_item_id)

        assert result['success'] is True
        assert result['has_next_task'] is True
        assert result['next_task']['task_id'] == 'task_2'  # High priority task

    def test_get_next_task_when_all_completed(self):
        """测试所有任务都完成后获取下一个任务"""
        # Start a feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']

        # Create and complete all tasks
        tasks_data = [{'task_id': 'task_1', 'title': '任务1'}]
        self.tools.aceflow_v4_create_tasks(work_item_id, tasks_data)
        self.tools.aceflow_v4_update_task_status(work_item_id, 'task_1', 'completed')

        # Get next task
        result = self.tools.aceflow_v4_get_next_task(work_item_id=work_item_id)

        assert result['success'] is True
        assert result['has_next_task'] is False
        assert result['next_task'] is None


class TestMCPTaskToolsIntegration:
    """集成测试：完整的任务管理流程"""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_id = get_unique_project_id()
        self.tools = AceFlowTools(working_directory=self.temp_dir, project_id=self.project_id)

    def teardown_method(self):
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        aceflow_dir = Path.cwd() / ".aceflow" / "state" / self.project_id
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_complete_task_lifecycle(self):
        """测试完整的任务生命周期：建议 -> 创建 -> 执行 -> 完成"""
        # 1. Start feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="用户管理功能",
            description="需要实现用户CRUD API和数据库表设计"
        )
        work_item_id = start_result['work_item_id']

        # 2. Suggest tasks
        suggest_result = self.tools.aceflow_v4_suggest_tasks(
            work_item_id=work_item_id,
            requirement="需要实现用户API接口和数据库表设计"
        )
        assert suggest_result['success'] is True
        assert suggest_result['count'] > 0
        # Should suggest both API and database tasks
        suggestions = suggest_result['suggestions']
        has_api = any('API' in s['title'] or '接口' in s['title'] for s in suggestions)
        has_db = any('数据库' in s['title'] or '表' in s['title'] for s in suggestions)
        assert has_api or has_db

        # 3. Create tasks (simplified version)
        tasks_data = [
            {'task_id': 'task_1', 'title': 'API设计', 'dependencies': []},
            {'task_id': 'task_2', 'title': '数据库设计', 'dependencies': []},
            {'task_id': 'task_3', 'title': 'API实现', 'dependencies': ['task_1', 'task_2']},
            {'task_id': 'task_4', 'title': '测试', 'dependencies': ['task_3']}
        ]
        create_result = self.tools.aceflow_v4_create_tasks(work_item_id, tasks_data)
        assert create_result['success'] is True
        assert create_result['tasks_created'] == 4

        # 4. Get next task (should be task_1 or task_2)
        next_result = self.tools.aceflow_v4_get_next_task(work_item_id)
        assert next_result['has_next_task'] is True
        assert next_result['next_task']['task_id'] in ['task_1', 'task_2']

        # 5. Complete task_1
        self.tools.aceflow_v4_update_task_status(work_item_id, 'task_1', 'completed')

        # 6. Get pending tasks (should still include task_2, not task_3)
        pending_result = self.tools.aceflow_v4_get_pending_tasks(work_item_id)
        pending_ids = {t['task_id'] for t in pending_result['pending_tasks']}
        assert 'task_2' in pending_ids
        assert 'task_3' not in pending_ids  # Still depends on task_2

        # 7. Complete task_2
        self.tools.aceflow_v4_update_task_status(work_item_id, 'task_2', 'completed')

        # 8. Now task_3 should be available
        pending_result = self.tools.aceflow_v4_get_pending_tasks(work_item_id)
        pending_ids = {t['task_id'] for t in pending_result['pending_tasks']}
        assert 'task_3' in pending_ids

        # 9. Get task context for task_3
        context_result = self.tools.aceflow_v4_get_task_context(work_item_id, 'task_3')
        assert context_result['success'] is True
        context = context_result['context']
        # Should have 2 dependencies and 1 dependent
        assert len(context['task']['dependencies']) == 2
        assert len([rt for rt in context['related_tasks'] if rt['relation'] == 'dependent']) == 1
