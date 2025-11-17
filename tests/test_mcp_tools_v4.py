"""
测试 AceFlow v4.0 MCP Tools
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


class TestMCPToolsV4Initialization:
    """测试v4.0 MCP工具初始化"""

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

    def test_v4_engine_initialized(self):
        """验证v4.0引擎已初始化"""
        assert self.tools.v4_engine is not None

    def test_workflows_registered(self):
        """验证所有6个工作流已注册"""
        assert self.tools.v4_engine._workflow_registry is not None
        assert len(self.tools.v4_engine._workflow_registry) == 6

        # Verify all workflow types are registered
        assert WorkflowType.FEATURE in self.tools.v4_engine._workflow_registry
        assert WorkflowType.BUGFIX in self.tools.v4_engine._workflow_registry
        assert WorkflowType.REFACTOR in self.tools.v4_engine._workflow_registry
        assert WorkflowType.REVIEW in self.tools.v4_engine._workflow_registry
        assert WorkflowType.DOCUMENTATION in self.tools.v4_engine._workflow_registry
        assert WorkflowType.PERFORMANCE in self.tools.v4_engine._workflow_registry


class TestMCPToolsV4StartWorkItem:
    """测试启动工作项"""

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

    def test_start_feature_work_item(self):
        """测试启动功能开发工作项"""
        result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="添加用户登录功能",
            description="实现JWT身份验证"
        )

        assert result['success'] is True
        assert result['type'] == 'feature'
        assert result['title'] == "添加用户登录功能"
        assert result['total_stages'] == 5
        assert result['supports_subtasks'] is True
        assert 'work_item_id' in result

    def test_start_bugfix_work_item(self):
        """测试启动Bug修复工作项"""
        result = self.tools.aceflow_v4_start_work_item(
            type="bugfix",
            title="修复登录超时问题"
        )

        assert result['success'] is True
        assert result['type'] == 'bugfix'
        assert result['total_stages'] == 5
        assert result['supports_subtasks'] is False

    def test_start_all_workflow_types(self):
        """测试启动所有6种工作流类型"""
        workflow_types = [
            ("feature", 5, True),
            ("bugfix", 5, False),
            ("refactor", 5, False),
            ("review", 4, False),
            ("documentation", 4, False),
            ("performance", 4, False)
        ]

        for wf_type, expected_stages, supports_subtasks in workflow_types:
            result = self.tools.aceflow_v4_start_work_item(
                type=wf_type,
                title=f"Test {wf_type} work item"
            )

            assert result['success'] is True, f"{wf_type} failed"
            assert result['type'] == wf_type
            assert result['total_stages'] == expected_stages
            assert result['supports_subtasks'] == supports_subtasks

    def test_invalid_workflow_type(self):
        """测试无效的工作流类型"""
        result = self.tools.aceflow_v4_start_work_item(
            type="invalid_type",
            title="Test"
        )

        assert result['success'] is False
        assert 'error' in result


class TestMCPToolsV4GetCurrentWorkItem:
    """测试获取当前工作项"""

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

    def test_get_current_work_item_when_active(self):
        """测试获取活跃的工作项"""
        # Start a work item first
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']

        # Get current work item
        result = self.tools.aceflow_v4_get_current_work_item()

        assert result['success'] is True
        assert result['active'] is True
        assert result['work_item']['work_item_id'] == work_item_id

    def test_get_current_work_item_when_none(self):
        """测试没有活跃工作项时获取"""
        result = self.tools.aceflow_v4_get_current_work_item()

        assert result['success'] is True
        assert result['active'] is False


class TestMCPToolsV4ListWorkItems:
    """测试列出工作项"""

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

    def test_list_work_items_empty(self):
        """测试列出空的工作项列表"""
        result = self.tools.aceflow_v4_list_work_items()

        assert result['success'] is True
        assert result['count'] == 0
        assert result['work_items'] == []

    def test_list_work_items_multiple(self):
        """测试列出多个工作项"""
        # Create 3 work items
        self.tools.aceflow_v4_start_work_item(type="feature", title="Feature 1")
        self.tools.aceflow_v4_start_work_item(type="bugfix", title="Bugfix 1")
        self.tools.aceflow_v4_start_work_item(type="refactor", title="Refactor 1")

        result = self.tools.aceflow_v4_list_work_items()

        assert result['success'] is True
        assert result['count'] == 3

    def test_list_work_items_with_status_filter(self):
        """测试按状态过滤工作项"""
        # Start a work item (will be in_progress)
        self.tools.aceflow_v4_start_work_item(type="feature", title="Feature 1")

        result = self.tools.aceflow_v4_list_work_items(status="in_progress")

        assert result['success'] is True
        assert result['count'] == 1
        assert result['filter'] == "in_progress"


class TestMCPToolsV4CompleteStage:
    """测试完成阶段"""

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

    def test_complete_first_stage(self):
        """测试完成第一个阶段"""
        # Start a work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']
        first_stage_id = start_result['stages'][0]['stage_id']

        # Complete first stage
        result = self.tools.aceflow_v4_complete_stage(
            work_item_id=work_item_id,
            stage_id=first_stage_id,
            checklist_results={"checked": True}
        )

        assert result['success'] is True
        assert 'current_stage' in result
        # Should now be on second stage
        assert result['current_stage']['stage_id'] != first_stage_id


class TestMCPToolsV4TaskManagement:
    """测试任务管理（仅FEATURE类型）"""

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

    def test_add_task_to_feature_work_item(self):
        """测试为功能开发工作项添加任务"""
        # Start feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']

        # Add task
        result = self.tools.aceflow_v4_add_task(
            work_item_id=work_item_id,
            task_id="task_1",
            title="实现登录API",
            description="创建POST /api/login端点"
        )

        assert result['success'] is True
        assert result['task']['task_id'] == "task_1"
        assert result['task']['status'] == "pending"

    def test_add_task_to_bugfix_fails(self):
        """测试为Bug修复工作项添加任务（应该失败）"""
        # Start bugfix work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="bugfix",
            title="Test bugfix"
        )
        work_item_id = start_result['work_item_id']

        # Try to add task (should fail)
        result = self.tools.aceflow_v4_add_task(
            work_item_id=work_item_id,
            task_id="task_1",
            title="Test task"
        )

        assert result['success'] is False

    def test_update_task_status(self):
        """测试更新任务状态"""
        # Start feature work item and add task
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']

        self.tools.aceflow_v4_add_task(
            work_item_id=work_item_id,
            task_id="task_1",
            title="Test task"
        )

        # Update task status
        result = self.tools.aceflow_v4_update_task_status(
            work_item_id=work_item_id,
            task_id="task_1",
            status="in_progress"
        )

        assert result['success'] is True

    def test_add_task_with_dependencies(self):
        """测试添加带依赖关系的任务"""
        # Start feature work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test feature"
        )
        work_item_id = start_result['work_item_id']

        # Add first task
        self.tools.aceflow_v4_add_task(
            work_item_id=work_item_id,
            task_id="task_1",
            title="Task 1"
        )

        # Add second task with dependency on first
        result = self.tools.aceflow_v4_add_task(
            work_item_id=work_item_id,
            task_id="task_2",
            title="Task 2",
            dependencies=["task_1"]
        )

        assert result['success'] is True


class TestMCPToolsV4Integration:
    """v4.0 MCP工具集成测试"""

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

    def test_complete_workflow_lifecycle(self):
        """测试完整的工作流生命周期"""
        # 1. Start work item
        start_result = self.tools.aceflow_v4_start_work_item(
            type="bugfix",
            title="修复登录Bug",
            description="用户登录时出现超时错误"
        )
        assert start_result['success'] is True
        work_item_id = start_result['work_item_id']

        # 2. Get current work item
        current = self.tools.aceflow_v4_get_current_work_item()
        assert current['active'] is True

        # 3. Complete first stage
        first_stage = start_result['stages'][0]['stage_id']
        complete_result = self.tools.aceflow_v4_complete_stage(
            work_item_id=work_item_id,
            stage_id=first_stage
        )
        assert complete_result['success'] is True

        # 4. List work items
        list_result = self.tools.aceflow_v4_list_work_items()
        assert list_result['count'] == 1
