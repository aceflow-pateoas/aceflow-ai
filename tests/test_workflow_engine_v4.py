"""
Unit tests for WorkflowEngine v4.0 features

Tests the new work item-based workflow API.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

from aceflow.workflow.core.engine import WorkflowEngine
from aceflow.workflow.models import (
    WorkflowType, WorkItemStatus, Stage, StageStatus
)


class MockWorkflowImplementation:
    """Mock workflow implementation for testing"""

    def __init__(self, workflow_type: WorkflowType):
        self.workflow_type = workflow_type

    def get_stages(self):
        """Return mock stages"""
        return [
            Stage(
                stage_id="stage_1",
                name="第一阶段",
                description="第一个阶段",
                tasks=["任务1", "任务2"],
                deliverables=["交付物1"]
            ),
            Stage(
                stage_id="stage_2",
                name="第二阶段",
                description="第二个阶段",
                tasks=["任务3"],
                deliverables=["交付物2"]
            ),
            Stage(
                stage_id="stage_3",
                name="第三阶段",
                description="第三个阶段",
                tasks=["任务4", "任务5"],
                deliverables=["交付物3"]
            )
        ]


class TestWorkflowEngineV4:
    """Test WorkflowEngine v4.0 API"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        # Create engine with temp state dir
        self.engine = WorkflowEngine(project_id="test_engine_v4")
        self.engine.state_manager.state_dir = self.temp_dir
        self.engine.state_manager.project_state_dir = self.temp_dir / "test_engine_v4"
        self.engine.state_manager.project_state_dir.mkdir(parents=True, exist_ok=True)
        self.engine.state_manager.work_items_index_file = (
            self.engine.state_manager.project_state_dir / "work_items.json"
        )
        self.engine.state_manager.active_work_item_file = (
            self.engine.state_manager.project_state_dir / "active_work_item.txt"
        )

        # Register mock workflow implementations
        for wf_type in WorkflowType:
            mock_impl = MockWorkflowImplementation(wf_type)
            self.engine.register_workflow_implementation(wf_type, mock_impl)

    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_start_work_item_feature(self):
        """Test starting a feature work item"""
        result = self.engine.start_work_item(
            type=WorkflowType.FEATURE,
            title="用户登录功能",
            description="实现账号密码登录"
        )

        assert result['success'] is True
        assert result['type'] == "feature"
        assert result['title'] == "用户登录功能"
        assert result['status'] == "in_progress"
        assert result['total_stages'] == 3
        assert result['supports_subtasks'] is True
        assert result['work_item_id'].startswith("work_")
        assert 'current_stage' in result
        assert result['current_stage']['stage_id'] == "stage_1"
        assert result['current_stage']['status'] == "in_progress"

    def test_start_work_item_bugfix(self):
        """Test starting a bugfix work item"""
        result = self.engine.start_work_item(
            type=WorkflowType.BUGFIX,
            title="修复登录超时",
            description="修复登录超时问题"
        )

        assert result['success'] is True
        assert result['type'] == "bugfix"
        assert result['title'] == "修复登录超时"
        assert result['supports_subtasks'] is False

    def test_start_work_item_all_types(self):
        """Test starting work items for all 6 workflow types"""
        for wf_type in WorkflowType:
            result = self.engine.start_work_item(
                type=wf_type,
                title=f"测试{wf_type.value}",
                description=f"{wf_type.value}描述"
            )

            assert result['success'] is True
            assert result['type'] == wf_type.value
            assert result['total_stages'] == 3

    def test_start_work_item_without_implementation(self):
        """Test starting work item without registered implementation"""
        # Create new engine without registrations
        engine = WorkflowEngine(project_id="test_no_impl")
        engine.state_manager.state_dir = self.temp_dir
        engine.state_manager.project_state_dir = self.temp_dir / "test_no_impl"
        engine.state_manager.project_state_dir.mkdir(parents=True, exist_ok=True)

        with pytest.raises(ValueError, match="No workflow implementation found"):
            engine.start_work_item(
                type=WorkflowType.FEATURE,
                title="测试"
            )

    def test_start_work_item_with_metadata(self):
        """Test starting work item with metadata"""
        metadata = {
            "priority": "high",
            "assignee": "developer_1",
            "tags": ["backend", "api"]
        }

        result = self.engine.start_work_item(
            type=WorkflowType.FEATURE,
            title="带元数据的工作项",
            metadata=metadata
        )

        assert result['success'] is True
        # Verify metadata is saved
        work_item = self.engine.state_manager.get_work_item(result['work_item_id'])
        assert work_item.metadata == metadata

    def test_get_current_work_item(self):
        """Test getting current work item"""
        # Start a work item
        start_result = self.engine.start_work_item(
            type=WorkflowType.FEATURE,
            title="当前工作项测试"
        )
        work_item_id = start_result['work_item_id']

        # Get current work item
        current = self.engine.get_current_work_item()

        assert current is not None
        assert current['work_item_id'] == work_item_id
        assert current['type'] == "feature"
        assert current['title'] == "当前工作项测试"
        assert current['status'] == "in_progress"
        assert 'overall_progress' in current
        assert 'task_progress' in current
        assert 'total_stages' in current
        assert 'total_tasks' in current
        assert 'created_at' in current
        assert 'updated_at' in current

    def test_get_current_work_item_none(self):
        """Test getting current work item when none exists"""
        current = self.engine.get_current_work_item()
        assert current is None

    def test_list_all_work_items(self):
        """Test listing all work items"""
        # Create multiple work items
        self.engine.start_work_item(
            type=WorkflowType.FEATURE,
            title="功能1"
        )
        self.engine.start_work_item(
            type=WorkflowType.BUGFIX,
            title="Bug修复"
        )
        self.engine.start_work_item(
            type=WorkflowType.REFACTOR,
            title="重构优化"
        )

        # List all
        all_items = self.engine.list_all_work_items()

        assert len(all_items) == 3
        # Should be sorted by created_at descending (newest first)
        assert all_items[0]['title'] == "重构优化"
        assert all_items[1]['title'] == "Bug修复"
        assert all_items[2]['title'] == "功能1"

        # Check structure
        for item in all_items:
            assert 'work_item_id' in item
            assert 'type' in item
            assert 'title' in item
            assert 'status' in item
            assert 'overall_progress' in item
            assert 'current_stage_id' in item
            assert 'total_stages' in item
            assert 'total_tasks' in item
            assert 'created_at' in item
            assert 'updated_at' in item

    def test_list_work_items_filtered_by_status(self):
        """Test listing work items with status filter"""
        # Create work items
        item1 = self.engine.start_work_item(
            type=WorkflowType.FEATURE,
            title="功能1"
        )
        item2 = self.engine.start_work_item(
            type=WorkflowType.BUGFIX,
            title="Bug修复"
        )

        # Update one to completed
        self.engine.state_manager.update_work_item_status(
            item2['work_item_id'],
            "completed"
        )

        # Filter by in_progress
        in_progress = self.engine.list_all_work_items(status="in_progress")
        assert len(in_progress) == 1
        assert in_progress[0]['work_item_id'] == item1['work_item_id']

        # Filter by completed
        completed = self.engine.list_all_work_items(status="completed")
        assert len(completed) == 1
        assert completed[0]['work_item_id'] == item2['work_item_id']

    def test_list_work_items_empty(self):
        """Test listing work items when none exist"""
        items = self.engine.list_all_work_items()
        assert items == []

    def test_register_workflow_implementation(self):
        """Test registering workflow implementation"""
        mock_impl = MockWorkflowImplementation(WorkflowType.REVIEW)
        self.engine.register_workflow_implementation(WorkflowType.REVIEW, mock_impl)

        # Verify registration
        impl = self.engine._get_workflow_implementation(WorkflowType.REVIEW)
        assert impl is mock_impl

    def test_work_item_stages_initialized(self):
        """Test that work item stages are properly initialized"""
        result = self.engine.start_work_item(
            type=WorkflowType.FEATURE,
            title="阶段测试"
        )

        work_item = self.engine.state_manager.get_work_item(result['work_item_id'])

        assert len(work_item.stages) == 3
        assert work_item.stages[0].status == StageStatus.IN_PROGRESS
        assert work_item.stages[1].status == StageStatus.PENDING
        assert work_item.stages[2].status == StageStatus.PENDING
        assert work_item.current_stage_id == "stage_1"


# TestBackwardCompatibility class removed - v3.0 modes are fully deprecated
# The old modes (MinimalWorkflow, StandardWorkflow, CompleteWorkflow, SmartWorkflow)
# have been removed and raise ImportError when imported.
# See aceflow/workflow/modes/__init__.py for deprecation implementation.


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
