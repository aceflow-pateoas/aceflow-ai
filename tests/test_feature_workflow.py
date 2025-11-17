"""
测试 FeatureWorkflow（功能开发工作流）
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from aceflow.workflow.workflows.feature import FeatureWorkflow
from aceflow.workflow.workflows.base import ValidationResult
from aceflow.workflow.models import WorkflowType, Stage
from aceflow.workflow.core.engine import WorkflowEngine


class TestFeatureWorkflowBasics:
    """测试 FeatureWorkflow 的基本属性"""

    def setup_method(self):
        """每个测试前创建 FeatureWorkflow 实例"""
        self.workflow = FeatureWorkflow()

    def test_workflow_type(self):
        """测试工作流类型"""
        assert self.workflow.workflow_type == WorkflowType.FEATURE

    def test_workflow_name(self):
        """测试工作流名称"""
        assert self.workflow.workflow_name == "功能开发工作流"
        assert isinstance(self.workflow.workflow_name, str)

    def test_workflow_description(self):
        """测试工作流描述"""
        assert "功能开发" in self.workflow.description
        assert "5个阶段" in self.workflow.description

    def test_estimated_duration(self):
        """测试预计耗时"""
        assert self.workflow.estimated_duration == "1-2周"

    def test_supports_subtasks(self):
        """测试支持子任务拆分"""
        assert self.workflow.supports_subtasks() is True


class TestFeatureWorkflowStages:
    """测试 FeatureWorkflow 的阶段定义"""

    def setup_method(self):
        """每个测试前创建 FeatureWorkflow 实例"""
        self.workflow = FeatureWorkflow()

    def test_stage_definitions_count(self):
        """测试阶段数量"""
        stage_defs = self.workflow.get_stage_definitions()
        assert len(stage_defs) == 5

    def test_stage_ids_and_order(self):
        """测试阶段ID和顺序"""
        stage_defs = self.workflow.get_stage_definitions()
        expected_ids = ["requirement", "design", "implementation", "testing", "delivery"]
        actual_ids = [s.stage_id for s in stage_defs]
        assert actual_ids == expected_ids

    def test_stage_names(self):
        """测试阶段名称"""
        stage_defs = self.workflow.get_stage_definitions()
        stage_names = [s.name for s in stage_defs]

        assert "需求梳理" in stage_names[0]
        assert "设计方案" in stage_names[1]
        assert "编码实现" in stage_names[2]
        assert "功能测试" in stage_names[3]
        assert "完成交付" in stage_names[4]

    def test_all_stages_have_templates(self):
        """测试所有阶段都有模板路径"""
        stage_defs = self.workflow.get_stage_definitions()
        for stage_def in stage_defs:
            assert stage_def.checklist_template
            assert stage_def.checklist_template.startswith("workflows/feature/")
            assert stage_def.checklist_template.endswith(".md")

    def test_all_stages_have_deliverables(self):
        """测试所有阶段都有交付物"""
        stage_defs = self.workflow.get_stage_definitions()
        for stage_def in stage_defs:
            assert len(stage_def.deliverables) > 0

    def test_all_stages_have_metadata(self):
        """测试所有阶段都有元数据"""
        stage_defs = self.workflow.get_stage_definitions()
        for stage_def in stage_defs:
            assert "stage_type" in stage_def.metadata
            assert "required_completion_rate" in stage_def.metadata
            assert "can_skip" in stage_def.metadata

    def test_stage_estimated_hours(self):
        """测试阶段预估时间"""
        stage_defs = self.workflow.get_stage_definitions()
        for stage_def in stage_defs:
            assert stage_def.estimated_hours
            assert "小时" in stage_def.estimated_hours


class TestFeatureWorkflowStageConversion:
    """测试 FeatureWorkflow 的阶段转换"""

    def setup_method(self):
        """每个测试前创建 FeatureWorkflow 实例"""
        self.workflow = FeatureWorkflow()

    def test_get_stages_returns_stage_objects(self):
        """测试 get_stages() 返回 Stage 对象"""
        stages = self.workflow.get_stages()
        assert len(stages) == 5
        assert all(isinstance(stage, Stage) for stage in stages)

    def test_stages_contain_template_in_metadata(self):
        """测试 Stage 对象的 metadata 包含模板路径"""
        stages = self.workflow.get_stages()
        for stage in stages:
            assert "checklist_template" in stage.metadata

    def test_get_stage_by_id(self):
        """测试按ID获取阶段"""
        stage = self.workflow.get_stage_by_id("requirement")
        assert stage is not None
        assert stage.stage_id == "requirement"

    def test_get_stage_by_id_not_found(self):
        """测试获取不存在的阶段"""
        stage = self.workflow.get_stage_by_id("nonexistent")
        assert stage is None

    def test_get_next_stage(self):
        """测试获取下一阶段"""
        next_stage = self.workflow.get_next_stage("requirement")
        assert next_stage is not None
        assert next_stage.stage_id == "design"

        next_stage = self.workflow.get_next_stage("testing")
        assert next_stage is not None
        assert next_stage.stage_id == "delivery"

    def test_get_next_stage_at_end(self):
        """测试在最后阶段获取下一阶段"""
        next_stage = self.workflow.get_next_stage("delivery")
        assert next_stage is None


class TestFeatureWorkflowValidation:
    """测试 FeatureWorkflow 的阶段验证逻辑"""

    def setup_method(self):
        """每个测试前创建 FeatureWorkflow 实例"""
        self.workflow = FeatureWorkflow()

    def test_validate_requirement_stage_success(self):
        """测试需求阶段验证 - 成功"""
        checklist = {
            "item1": True,
            "item2": True,
            "item3": True,
            "item4": True,
            "item5": True
        }
        result = self.workflow.validate_stage_completion("requirement", checklist)
        assert result.valid is True
        assert len(result.completed_items) == 5
        assert len(result.missing_items) == 0

    def test_validate_requirement_stage_partial(self):
        """测试需求阶段验证 - 部分完成（80%阈值）"""
        checklist = {
            "item1": True,
            "item2": True,
            "item3": True,
            "item4": True,
            "item5": False  # 5个中完成4个 = 80%
        }
        result = self.workflow.validate_stage_completion("requirement", checklist)
        assert result.valid is True  # 刚好达到80%阈值
        assert len(result.completed_items) == 4

    def test_validate_requirement_stage_failure(self):
        """测试需求阶段验证 - 失败（低于80%）"""
        checklist = {
            "item1": True,
            "item2": True,
            "item3": True,
            "item4": False,
            "item5": False  # 5个中完成3个 = 60%
        }
        result = self.workflow.validate_stage_completion("requirement", checklist)
        assert result.valid is False
        assert len(result.completed_items) == 3
        assert len(result.warnings) > 0

    def test_validate_implementation_stage_high_threshold(self):
        """测试实现阶段验证 - 更高的阈值（90%）"""
        # 90%阈值：10个中需要完成9个
        checklist = {f"item{i}": i < 9 for i in range(10)}
        result = self.workflow.validate_stage_completion("implementation", checklist)
        assert result.valid is True

        # 低于90%应该失败
        checklist = {f"item{i}": i < 8 for i in range(10)}
        result = self.workflow.validate_stage_completion("implementation", checklist)
        assert result.valid is False

    def test_validate_empty_checklist(self):
        """测试空检查清单"""
        result = self.workflow.validate_stage_completion("requirement", {})
        assert result.valid is False
        assert "为空" in result.message

    def test_validate_nonexistent_stage(self):
        """测试验证不存在的阶段"""
        result = self.workflow.validate_stage_completion("nonexistent", {"item1": True})
        assert result.valid is False
        assert "未找到" in result.message


class TestFeatureWorkflowSummary:
    """测试 FeatureWorkflow 的摘要信息"""

    def setup_method(self):
        """每个测试前创建 FeatureWorkflow 实例"""
        self.workflow = FeatureWorkflow()

    def test_get_workflow_summary(self):
        """测试获取工作流摘要"""
        summary = self.workflow.get_workflow_summary()

        assert summary['type'] == 'feature'
        assert summary['name'] == "功能开发工作流"
        assert summary['total_stages'] == 5
        assert summary['supports_subtasks'] is True
        assert 'stages' in summary
        assert len(summary['stages']) == 5


class TestFeatureWorkflowEngineIntegration:
    """测试 FeatureWorkflow 与 WorkflowEngine 的集成"""

    def setup_method(self):
        """每个测试前创建临时目录和 WorkflowEngine"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_id = "test_feature_workflow"
        self.engine = WorkflowEngine(project_id=self.project_id)

        # 注册 FeatureWorkflow
        self.engine.register_workflow_implementation(
            WorkflowType.FEATURE,
            FeatureWorkflow()
        )

    def teardown_method(self):
        """每个测试后清理临时目录"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        # 清理 .aceflow 目录
        aceflow_dir = Path.cwd() / ".aceflow"
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_start_feature_work_item(self):
        """测试启动功能开发工作项"""
        result = self.engine.start_work_item(
            type=WorkflowType.FEATURE,
            title="测试功能",
            description="这是一个测试功能"
        )

        assert result['success'] is True
        assert result['type'] == 'feature'
        assert result['title'] == "测试功能"
        assert result['total_stages'] == 5
        assert result['supports_subtasks'] is True

    def test_feature_work_item_has_correct_stages(self):
        """测试功能工作项包含正确的阶段"""
        result = self.engine.start_work_item(
            type=WorkflowType.FEATURE,
            title="测试功能"
        )

        stages = result['stages']
        assert len(stages) == 5

        stage_ids = [s['stage_id'] for s in stages]
        assert stage_ids == ["requirement", "design", "implementation", "testing", "delivery"]

    def test_feature_work_item_first_stage_active(self):
        """测试功能工作项第一阶段自动激活"""
        result = self.engine.start_work_item(
            type=WorkflowType.FEATURE,
            title="测试功能"
        )

        current_stage = result['current_stage']
        assert current_stage is not None
        assert current_stage['stage_id'] == "requirement"
        assert current_stage['status'] == "in_progress"

    def test_get_current_feature_work_item(self):
        """测试获取当前功能工作项"""
        # 创建工作项
        self.engine.start_work_item(
            type=WorkflowType.FEATURE,
            title="测试功能"
        )

        # 获取当前工作项
        current = self.engine.get_current_work_item()
        assert current is not None
        assert current['type'] == 'feature'
        assert current['title'] == "测试功能"
