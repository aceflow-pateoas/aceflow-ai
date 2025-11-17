"""
Unit tests for v4.0 data models

Tests the new WorkflowType, WorkItem, Task, and ChecklistItem models.
"""

import pytest
from datetime import datetime
from aceflow.workflow.models import (
    WorkflowType,
    WorkItemStatus,
    TaskStatus,
    WorkItem,
    Task,
    ChecklistItem,
    Stage,
    StageStatus
)


class TestWorkflowType:
    """Test WorkflowType enum"""

    def test_all_workflow_types(self):
        """Test all 6 workflow types exist"""
        assert WorkflowType.FEATURE.value == "feature"
        assert WorkflowType.BUGFIX.value == "bugfix"
        assert WorkflowType.REFACTOR.value == "refactor"
        assert WorkflowType.REVIEW.value == "review"
        assert WorkflowType.DOCUMENTATION.value == "documentation"
        assert WorkflowType.PERFORMANCE.value == "performance"

    def test_workflow_type_from_string(self):
        """Test creating WorkflowType from string"""
        workflow_type = WorkflowType("feature")
        assert workflow_type == WorkflowType.FEATURE


class TestTask:
    """Test Task model"""

    def test_task_creation(self):
        """Test creating a task"""
        task = Task(
            task_id="task_001",
            title="实现登录API",
            description="实现POST /api/login端点"
        )

        assert task.task_id == "task_001"
        assert task.title == "实现登录API"
        assert task.status == TaskStatus.PENDING
        assert task.dependencies == []
        assert task.completed_at is None

    def test_task_with_dependencies(self):
        """Test task with dependencies"""
        task = Task(
            task_id="task_002",
            title="实现Token生成",
            description="生成JWT Token",
            dependencies=["task_001"]
        )

        assert task.dependencies == ["task_001"]

    def test_task_serialization(self):
        """Test task to_dict and from_dict"""
        task = Task(
            task_id="task_001",
            title="实现登录API",
            description="实现POST /api/login端点",
            status=TaskStatus.IN_PROGRESS
        )

        # Serialize
        task_dict = task.to_dict()
        assert task_dict['task_id'] == "task_001"
        assert task_dict['title'] == "实现登录API"
        assert task_dict['status'] == "in_progress"

        # Deserialize
        task_restored = Task.from_dict(task_dict)
        assert task_restored.task_id == task.task_id
        assert task_restored.title == task.title
        assert task_restored.status == task.status

    def test_task_completion(self):
        """Test marking task as completed"""
        task = Task(
            task_id="task_001",
            title="实现登录API",
            description="实现POST /api/login端点"
        )

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()

        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None


class TestChecklistItem:
    """Test ChecklistItem model"""

    def test_checklist_item_creation(self):
        """Test creating a checklist item"""
        item = ChecklistItem(
            item_id="check_001",
            content="接口定义已输出"
        )

        assert item.item_id == "check_001"
        assert item.content == "接口定义已输出"
        assert item.checked is False

    def test_checklist_item_checked(self):
        """Test checking a checklist item"""
        item = ChecklistItem(
            item_id="check_001",
            content="接口定义已输出",
            checked=True
        )

        assert item.checked is True

    def test_checklist_item_serialization(self):
        """Test checklist item to_dict and from_dict"""
        item = ChecklistItem(
            item_id="check_001",
            content="接口定义已输出",
            checked=True
        )

        # Serialize
        item_dict = item.to_dict()
        assert item_dict['item_id'] == "check_001"
        assert item_dict['content'] == "接口定义已输出"
        assert item_dict['checked'] is True

        # Deserialize
        item_restored = ChecklistItem.from_dict(item_dict)
        assert item_restored.item_id == item.item_id
        assert item_restored.content == item.content
        assert item_restored.checked == item.checked


class TestWorkItem:
    """Test WorkItem model"""

    def test_work_item_creation(self):
        """Test creating a work item"""
        work_item = WorkItem(
            type=WorkflowType.FEATURE,
            title="用户登录功能",
            description="实现账号密码登录"
        )

        assert work_item.type == WorkflowType.FEATURE
        assert work_item.title == "用户登录功能"
        assert work_item.status == WorkItemStatus.PENDING
        assert work_item.work_item_id.startswith("work_")

    def test_work_item_with_stages(self):
        """Test work item with stages"""
        work_item = WorkItem(
            type=WorkflowType.FEATURE,
            title="用户登录功能",
            description="实现账号密码登录"
        )

        # Add stages
        stage1 = Stage(
            stage_id="requirement",
            name="需求梳理",
            description="梳理需求并输出设计方案"
        )
        stage2 = Stage(
            stage_id="design",
            name="设计方案",
            description="输出核心逻辑、接口定义"
        )

        work_item.stages = [stage1, stage2]
        work_item.current_stage_id = "requirement"

        assert len(work_item.stages) == 2
        assert work_item.current_stage.stage_id == "requirement"

    def test_work_item_with_tasks(self):
        """Test work item with tasks (feature type)"""
        work_item = WorkItem(
            type=WorkflowType.FEATURE,
            title="用户登录功能",
            description="实现账号密码登录"
        )

        # Add tasks
        task1 = Task(
            task_id="task_001",
            title="实现登录API",
            description="POST /api/login"
        )
        task2 = Task(
            task_id="task_002",
            title="实现Token生成",
            description="生成JWT Token"
        )

        work_item.tasks = [task1, task2]

        assert len(work_item.tasks) == 2
        assert work_item.supports_subtasks() is True
        assert work_item.task_progress == 0.0

    def test_work_item_bugfix_no_subtasks(self):
        """Test bugfix work item doesn't support subtasks"""
        work_item = WorkItem(
            type=WorkflowType.BUGFIX,
            title="修复登录超时",
            description="修复登录超时问题"
        )

        assert work_item.supports_subtasks() is False

    def test_work_item_progress_calculation(self):
        """Test overall progress calculation"""
        work_item = WorkItem(
            type=WorkflowType.FEATURE,
            title="用户登录功能"
        )

        # Add 5 stages
        for i in range(5):
            stage = Stage(
                stage_id=f"stage_{i}",
                name=f"阶段{i}",
                description=f"阶段{i}描述"
            )
            if i < 2:  # Mark first 2 as completed
                stage.status = StageStatus.COMPLETED
            work_item.stages.append(stage)

        assert work_item.overall_progress == 0.4  # 2/5 = 0.4

    def test_work_item_task_progress_calculation(self):
        """Test task progress calculation"""
        work_item = WorkItem(
            type=WorkflowType.FEATURE,
            title="用户登录功能"
        )

        # Add 5 tasks
        for i in range(5):
            task = Task(
                task_id=f"task_{i}",
                title=f"任务{i}",
                description=f"任务{i}描述"
            )
            if i < 3:  # Mark first 3 as completed
                task.status = TaskStatus.COMPLETED
            work_item.tasks.append(task)

        assert work_item.task_progress == 0.6  # 3/5 = 0.6

    def test_work_item_serialization(self):
        """Test work item to_dict and from_dict"""
        work_item = WorkItem(
            work_item_id="work_test_001",
            type=WorkflowType.FEATURE,
            title="用户登录功能",
            description="实现账号密码登录",
            status=WorkItemStatus.IN_PROGRESS
        )

        # Add a stage
        stage = Stage(
            stage_id="requirement",
            name="需求梳理",
            description="梳理需求"
        )
        work_item.stages.append(stage)
        work_item.current_stage_id = "requirement"

        # Add a task
        task = Task(
            task_id="task_001",
            title="实现登录API",
            description="POST /api/login"
        )
        work_item.tasks.append(task)

        # Serialize
        work_item_dict = work_item.to_dict()
        assert work_item_dict['work_item_id'] == "work_test_001"
        assert work_item_dict['type'] == "feature"
        assert work_item_dict['status'] == "in_progress"
        assert len(work_item_dict['stages']) == 1
        assert len(work_item_dict['tasks']) == 1

        # Deserialize
        work_item_restored = WorkItem.from_dict(work_item_dict)
        assert work_item_restored.work_item_id == work_item.work_item_id
        assert work_item_restored.type == work_item.type
        assert work_item_restored.status == work_item.status
        assert len(work_item_restored.stages) == 1
        assert len(work_item_restored.tasks) == 1

    def test_work_item_get_stage_by_id(self):
        """Test getting stage by ID"""
        work_item = WorkItem(
            type=WorkflowType.FEATURE,
            title="用户登录功能"
        )

        stage1 = Stage(
            stage_id="requirement",
            name="需求梳理",
            description="梳理需求"
        )
        stage2 = Stage(
            stage_id="design",
            name="设计方案",
            description="设计方案"
        )
        work_item.stages = [stage1, stage2]

        found_stage = work_item.get_stage_by_id("design")
        assert found_stage is not None
        assert found_stage.stage_id == "design"

        not_found = work_item.get_stage_by_id("nonexistent")
        assert not_found is None

    def test_work_item_get_task_by_id(self):
        """Test getting task by ID"""
        work_item = WorkItem(
            type=WorkflowType.FEATURE,
            title="用户登录功能"
        )

        task1 = Task(
            task_id="task_001",
            title="实现登录API",
            description="POST /api/login"
        )
        task2 = Task(
            task_id="task_002",
            title="实现Token生成",
            description="生成JWT"
        )
        work_item.tasks = [task1, task2]

        found_task = work_item.get_task_by_id("task_002")
        assert found_task is not None
        assert found_task.task_id == "task_002"

        not_found = work_item.get_task_by_id("nonexistent")
        assert not_found is None


class TestWorkItemStatus:
    """Test WorkItemStatus enum"""

    def test_all_statuses(self):
        """Test all work item statuses exist"""
        assert WorkItemStatus.PENDING.value == "pending"
        assert WorkItemStatus.IN_PROGRESS.value == "in_progress"
        assert WorkItemStatus.COMPLETED.value == "completed"
        assert WorkItemStatus.CANCELLED.value == "cancelled"
        assert WorkItemStatus.BLOCKED.value == "blocked"


class TestTaskStatus:
    """Test TaskStatus enum"""

    def test_all_statuses(self):
        """Test all task statuses exist"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.SKIPPED.value == "skipped"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
