"""
Unit tests for StateManager v4.0 features

Tests the new work item and task management functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from aceflow.workflow.core.state import StateManager
from aceflow.workflow.models import (
    WorkflowType, WorkItemStatus, TaskStatus,
    WorkItem, Task, Stage, StageStatus
)


class TestWorkItemManagement:
    """Test work item management methods"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.state_manager = StateManager(
            project_id="test_project_v4",
            state_dir=self.temp_dir
        )

    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_create_work_item(self):
        """Test creating a work item"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="用户登录功能",
            description="实现账号密码登录",
            metadata={"priority": "high"}
        )

        assert work_item.work_item_id.startswith("work_")
        assert work_item.type == WorkflowType.FEATURE
        assert work_item.title == "用户登录功能"
        assert work_item.description == "实现账号密码登录"
        assert work_item.status == WorkItemStatus.PENDING
        assert work_item.metadata["priority"] == "high"

    def test_get_work_item(self):
        """Test getting a work item by ID"""
        # Create work item
        created = self.state_manager.create_work_item(
            type=WorkflowType.BUGFIX,
            title="修复登录超时"
        )

        # Retrieve work item
        retrieved = self.state_manager.get_work_item(created.work_item_id)

        assert retrieved is not None
        assert retrieved.work_item_id == created.work_item_id
        assert retrieved.type == WorkflowType.BUGFIX
        assert retrieved.title == "修复登录超时"

    def test_get_nonexistent_work_item(self):
        """Test getting a nonexistent work item"""
        result = self.state_manager.get_work_item("work_nonexistent")
        assert result is None

    def test_list_work_items(self):
        """Test listing all work items"""
        # Create multiple work items
        work_item1 = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="功能1"
        )
        work_item2 = self.state_manager.create_work_item(
            type=WorkflowType.BUGFIX,
            title="Bug修复"
        )

        # List all
        all_items = self.state_manager.list_work_items()
        assert len(all_items) == 2
        # Should be sorted by created_at descending (newest first)
        assert all_items[0].work_item_id == work_item2.work_item_id
        assert all_items[1].work_item_id == work_item1.work_item_id

    def test_list_work_items_filtered_by_status(self):
        """Test listing work items filtered by status"""
        # Create work items with different statuses
        work_item1 = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="功能1"
        )
        work_item2 = self.state_manager.create_work_item(
            type=WorkflowType.BUGFIX,
            title="Bug修复"
        )

        # Update status of second item
        self.state_manager.update_work_item_status(
            work_item2.work_item_id,
            "in_progress"
        )

        # Filter by pending
        pending_items = self.state_manager.list_work_items(status="pending")
        assert len(pending_items) == 1
        assert pending_items[0].work_item_id == work_item1.work_item_id

        # Filter by in_progress
        in_progress_items = self.state_manager.list_work_items(status="in_progress")
        assert len(in_progress_items) == 1
        assert in_progress_items[0].work_item_id == work_item2.work_item_id

    def test_update_work_item_status(self):
        """Test updating work item status"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="测试功能"
        )

        # Update to in_progress
        result = self.state_manager.update_work_item_status(
            work_item.work_item_id,
            "in_progress"
        )
        assert result is True

        # Verify update
        updated = self.state_manager.get_work_item(work_item.work_item_id)
        assert updated.status == WorkItemStatus.IN_PROGRESS

        # Update to completed
        result = self.state_manager.update_work_item_status(
            work_item.work_item_id,
            "completed"
        )
        assert result is True

        updated = self.state_manager.get_work_item(work_item.work_item_id)
        assert updated.status == WorkItemStatus.COMPLETED

    def test_update_work_item_status_invalid(self):
        """Test updating work item with invalid status"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="测试功能"
        )

        result = self.state_manager.update_work_item_status(
            work_item.work_item_id,
            "invalid_status"
        )
        assert result is False

    def test_get_active_work_item(self):
        """Test getting active work item"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="活跃工作项"
        )

        active = self.state_manager.get_active_work_item()
        assert active is not None
        assert active.work_item_id == work_item.work_item_id


class TestTaskManagement:
    """Test task management methods"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.state_manager = StateManager(
            project_id="test_project_v4",
            state_dir=self.temp_dir
        )

    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_add_task_to_feature(self):
        """Test adding task to feature work item"""
        # Create feature work item
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="用户登录"
        )

        # Add task
        task = Task(
            task_id="task_001",
            title="实现登录API",
            description="POST /api/login"
        )
        result = self.state_manager.add_task(work_item.work_item_id, task)
        assert result is True

        # Verify task was added
        tasks = self.state_manager.get_tasks(work_item.work_item_id)
        assert len(tasks) == 1
        assert tasks[0].task_id == "task_001"
        assert tasks[0].title == "实现登录API"

    def test_add_task_to_bugfix_fails(self):
        """Test that adding task to bugfix work item fails"""
        # Create bugfix work item (doesn't support subtasks)
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.BUGFIX,
            title="修复登录Bug"
        )

        # Try to add task
        task = Task(
            task_id="task_001",
            title="修复逻辑",
            description="修复验证逻辑"
        )
        result = self.state_manager.add_task(work_item.work_item_id, task)
        assert result is False

    def test_add_task_with_position(self):
        """Test adding task with position hint"""
        # Create work item
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="用户登录"
        )

        # Add first task
        task1 = Task(task_id="task_001", title="任务1", description="")
        self.state_manager.add_task(work_item.work_item_id, task1)

        # Add second task
        task2 = Task(task_id="task_002", title="任务2", description="")
        self.state_manager.add_task(work_item.work_item_id, task2)

        # Add third task after task_001
        task3 = Task(task_id="task_003", title="任务3", description="")
        self.state_manager.add_task(
            work_item.work_item_id,
            task3,
            position="after:task_001"
        )

        # Verify order: task_001, task_003, task_002
        tasks = self.state_manager.get_tasks(work_item.work_item_id)
        assert len(tasks) == 3
        assert tasks[0].task_id == "task_001"
        assert tasks[1].task_id == "task_003"
        assert tasks[2].task_id == "task_002"

    def test_update_task_status(self):
        """Test updating task status"""
        # Create work item with task
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="测试功能"
        )
        task = Task(task_id="task_001", title="测试任务", description="")
        self.state_manager.add_task(work_item.work_item_id, task)

        # Update to in_progress
        result = self.state_manager.update_task_status(
            work_item.work_item_id,
            "task_001",
            "in_progress"
        )
        assert result is True

        # Verify update
        tasks = self.state_manager.get_tasks(work_item.work_item_id)
        assert tasks[0].status == TaskStatus.IN_PROGRESS

        # Update to completed
        result = self.state_manager.update_task_status(
            work_item.work_item_id,
            "task_001",
            "completed"
        )
        assert result is True

        tasks = self.state_manager.get_tasks(work_item.work_item_id)
        assert tasks[0].status == TaskStatus.COMPLETED
        assert tasks[0].completed_at is not None

    def test_update_task_status_invalid(self):
        """Test updating task with invalid status"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="测试"
        )
        task = Task(task_id="task_001", title="任务", description="")
        self.state_manager.add_task(work_item.work_item_id, task)

        result = self.state_manager.update_task_status(
            work_item.work_item_id,
            "task_001",
            "invalid_status"
        )
        assert result is False

    def test_get_tasks_empty(self):
        """Test getting tasks from work item with no tasks"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="空任务列表"
        )

        tasks = self.state_manager.get_tasks(work_item.work_item_id)
        assert tasks == []


class TestStageManagement:
    """Test enhanced stage management methods"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.state_manager = StateManager(
            project_id="test_project_v4",
            state_dir=self.temp_dir
        )

    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_complete_stage(self):
        """Test completing a stage"""
        # Create work item with stages
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="测试功能"
        )

        # Add stages
        stage1 = Stage(
            stage_id="requirement",
            name="需求梳理",
            description="梳理需求",
            status=StageStatus.IN_PROGRESS
        )
        stage2 = Stage(
            stage_id="design",
            name="设计方案",
            description="设计方案"
        )
        work_item.stages = [stage1, stage2]
        work_item.current_stage_id = "requirement"
        self.state_manager._save_work_item(work_item)

        # Complete first stage
        checklist_results = {
            "接口定义": True,
            "核心逻辑": True
        }
        result = self.state_manager.complete_stage(
            work_item.work_item_id,
            "requirement",
            checklist_results
        )
        assert result is True

        # Verify stage completed and next stage started
        updated = self.state_manager.get_work_item(work_item.work_item_id)
        assert updated.stages[0].status == StageStatus.COMPLETED
        assert updated.stages[0].progress == 1.0
        assert updated.stages[0].end_time is not None
        assert updated.stages[0].metadata.get('checklist_results') == checklist_results

        assert updated.stages[1].status == StageStatus.IN_PROGRESS
        assert updated.stages[1].start_time is not None
        assert updated.current_stage_id == "design"

    def test_complete_last_stage(self):
        """Test completing the last stage"""
        work_item = self.state_manager.create_work_item(
            type=WorkflowType.FEATURE,
            title="测试功能"
        )

        stage = Stage(
            stage_id="final",
            name="最终阶段",
            description="最后阶段",
            status=StageStatus.IN_PROGRESS
        )
        work_item.stages = [stage]
        work_item.current_stage_id = "final"
        self.state_manager._save_work_item(work_item)

        # Complete last stage
        result = self.state_manager.complete_stage(
            work_item.work_item_id,
            "final"
        )
        assert result is True

        # Verify stage completed but current_stage_id unchanged (no next stage)
        updated = self.state_manager.get_work_item(work_item.work_item_id)
        assert updated.stages[0].status == StageStatus.COMPLETED
        assert updated.current_stage_id == "final"  # Remains the same


class TestPersistence:
    """Test data persistence across StateManager instances"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_work_item_persistence(self):
        """Test work item persists across instances"""
        # Create work item with first instance
        sm1 = StateManager(project_id="test_persist", state_dir=self.temp_dir)
        work_item = sm1.create_work_item(
            type=WorkflowType.FEATURE,
            title="持久化测试"
        )
        work_item_id = work_item.work_item_id

        # Create new instance and verify data persists
        sm2 = StateManager(project_id="test_persist", state_dir=self.temp_dir)
        retrieved = sm2.get_work_item(work_item_id)

        assert retrieved is not None
        assert retrieved.work_item_id == work_item_id
        assert retrieved.title == "持久化测试"

    def test_task_persistence(self):
        """Test tasks persist across instances"""
        # Create work item and add task
        sm1 = StateManager(project_id="test_persist", state_dir=self.temp_dir)
        work_item = sm1.create_work_item(
            type=WorkflowType.FEATURE,
            title="任务持久化"
        )
        task = Task(task_id="task_001", title="测试任务", description="")
        sm1.add_task(work_item.work_item_id, task)

        # Create new instance and verify task persists
        sm2 = StateManager(project_id="test_persist", state_dir=self.temp_dir)
        tasks = sm2.get_tasks(work_item.work_item_id)

        assert len(tasks) == 1
        assert tasks[0].task_id == "task_001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
