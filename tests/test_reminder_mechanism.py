"""
测试 AceFlow v4.0 MCP 状态更新提示机制 (Task 2.3)
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


def get_unique_project_id():
    """Generate a unique project ID for test isolation."""
    return f"test_{uuid.uuid4().hex[:8]}"


class TestReminderMechanism:
    """测试状态更新提示机制"""

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

    def test_start_work_item_has_reminder(self):
        """测试启动工作项包含提示信息"""
        result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test Feature"
        )

        assert result['success'] is True
        assert 'reminder' in result
        assert '⚠️ NEXT STEP' in result['reminder']
        assert 'complete_stage' in result['reminder'].lower()
        # Should include the actual stage_id and work_item_id
        assert result['work_item_id'] in result['reminder']
        assert result['current_stage']['stage_id'] in result['reminder']

    def test_complete_stage_has_next_stage_reminder(self):
        """测试完成阶段包含下一阶段提示"""
        # Start a work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test Feature"
        )
        work_item_id = start_result['work_item_id']
        first_stage_id = start_result['stages'][0]['stage_id']

        # Complete first stage
        result = self.tools.aceflow_v4_complete_stage(
            work_item_id=work_item_id,
            stage_id=first_stage_id
        )

        assert result['success'] is True
        assert 'reminder' in result
        assert '⚠️ NEXT STEP' in result['reminder']
        assert 'next_stage_name' in result
        # Reminder should mention the next stage
        assert result['next_stage_name'] in result['reminder']
        # Reminder should include the call to complete_stage
        assert 'complete_stage' in result['reminder'].lower()
        assert work_item_id in result['reminder']

    def test_complete_final_stage_has_completion_reminder(self):
        """测试完成最后阶段包含完成提示"""
        # Start a bugfix work item (only 5 stages)
        start_result = self.tools.aceflow_v4_start_work_item(
            type="bugfix",
            title="Test Bugfix"
        )
        work_item_id = start_result['work_item_id']
        stages = start_result['stages']

        # Complete all stages
        for stage in stages:
            result = self.tools.aceflow_v4_complete_stage(
                work_item_id=work_item_id,
                stage_id=stage['stage_id']
            )

        # Last result should indicate completion
        assert result['success'] is True
        assert 'reminder' in result
        assert '🎉' in result['reminder']  # Celebration emoji
        assert 'completed' in result['reminder'].lower()

    def test_update_task_status_no_reminder_when_incomplete(self):
        """测试任务未全部完成时没有提示"""
        # Start a feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test Feature"
        )
        work_item_id = start_result['work_item_id']

        # Create tasks
        tasks_data = [
            {'task_id': 'task_1', 'title': '任务1'},
            {'task_id': 'task_2', 'title': '任务2'}
        ]
        self.tools.aceflow_v4_create_tasks(work_item_id, tasks_data)

        # Complete only first task
        result = self.tools.aceflow_v4_update_task_status(
            work_item_id=work_item_id,
            task_id='task_1',
            status='completed'
        )

        assert result['success'] is True
        # Should NOT have reminder since not all tasks completed
        assert 'reminder' not in result or result.get('reminder') is None

    def test_update_task_status_has_reminder_when_all_completed(self):
        """测试所有任务完成时包含提示"""
        # Start a feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test Feature"
        )
        work_item_id = start_result['work_item_id']

        # Create tasks
        tasks_data = [
            {'task_id': 'task_1', 'title': '任务1'},
            {'task_id': 'task_2', 'title': '任务2'}
        ]
        self.tools.aceflow_v4_create_tasks(work_item_id, tasks_data)

        # Complete all tasks
        self.tools.aceflow_v4_update_task_status(work_item_id, 'task_1', 'completed')
        result = self.tools.aceflow_v4_update_task_status(
            work_item_id=work_item_id,
            task_id='task_2',
            status='completed'
        )

        assert result['success'] is True
        assert result['task_progress'] == 1.0  # 100% completed
        # Should have reminder to complete stage
        assert 'reminder' in result
        assert '🎉' in result['reminder']
        assert 'complete_stage' in result['reminder'].lower()
        assert work_item_id in result['reminder']

    def test_docstring_has_warning(self):
        """测试工具文档字符串包含警告"""
        # Check complete_stage docstring
        complete_stage_doc = self.tools.aceflow_v4_complete_stage.__doc__
        assert '⚠️ IMPORTANT' in complete_stage_doc
        assert 'MUST call this tool' in complete_stage_doc

        # Check start_work_item docstring
        start_work_item_doc = self.tools.aceflow_v4_start_work_item.__doc__
        assert '⚠️ IMPORTANT' in start_work_item_doc
        assert 'complete_stage' in start_work_item_doc

        # Check update_task_status docstring
        update_task_status_doc = self.tools.aceflow_v4_update_task_status.__doc__
        assert '⚠️ IMPORTANT' in update_task_status_doc
        assert 'complete_stage' in update_task_status_doc


class TestReminderIntegration:
    """集成测试：完整工作流中的提示"""

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

    def test_complete_workflow_with_reminders(self):
        """测试完整工作流中的提示信息"""
        # 1. Start work item - should have reminder
        start_result = self.tools.aceflow_v4_start_work_item(
            type="bugfix",
            title="Fix Login Bug"
        )
        assert 'reminder' in start_result
        work_item_id = start_result['work_item_id']

        # 2. Complete first stage - should have next stage reminder
        first_stage_id = start_result['stages'][0]['stage_id']
        complete_result1 = self.tools.aceflow_v4_complete_stage(
            work_item_id=work_item_id,
            stage_id=first_stage_id
        )
        assert 'reminder' in complete_result1
        assert complete_result1['next_stage_name'] is not None

        # 3. Complete second stage - should still have reminder
        second_stage_id = start_result['stages'][1]['stage_id']
        complete_result2 = self.tools.aceflow_v4_complete_stage(
            work_item_id=work_item_id,
            stage_id=second_stage_id
        )
        assert 'reminder' in complete_result2

        # 4. Complete all remaining stages
        for i in range(2, len(start_result['stages'])):
            stage_id = start_result['stages'][i]['stage_id']
            result = self.tools.aceflow_v4_complete_stage(
                work_item_id=work_item_id,
                stage_id=stage_id
            )
            assert 'reminder' in result

        # Final reminder should indicate completion
        assert '🎉' in result['reminder']

    def test_feature_workflow_with_tasks_reminders(self):
        """测试功能开发工作流（含任务）的提示信息"""
        # 1. Start feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="User Login API"
        )
        assert 'reminder' in start_result
        work_item_id = start_result['work_item_id']

        # 2. Create tasks
        tasks_data = [
            {'task_id': 'task_1', 'title': 'API设计'},
            {'task_id': 'task_2', 'title': 'API实现', 'dependencies': ['task_1']},
            {'task_id': 'task_3', 'title': '测试', 'dependencies': ['task_2']}
        ]
        self.tools.aceflow_v4_create_tasks(work_item_id, tasks_data)

        # 3. Complete tasks one by one
        update_result1 = self.tools.aceflow_v4_update_task_status(
            work_item_id, 'task_1', 'completed'
        )
        # Not all tasks done, no reminder
        assert 'reminder' not in update_result1 or update_result1.get('reminder') is None

        update_result2 = self.tools.aceflow_v4_update_task_status(
            work_item_id, 'task_2', 'completed'
        )
        # Still not all done
        assert 'reminder' not in update_result2 or update_result2.get('reminder') is None

        update_result3 = self.tools.aceflow_v4_update_task_status(
            work_item_id, 'task_3', 'completed'
        )
        # All tasks done, should have reminder
        assert 'reminder' in update_result3
        assert '🎉' in update_result3['reminder']
        assert 'complete_stage' in update_result3['reminder'].lower()
