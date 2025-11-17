"""
测试 ReviewWorkflow（代码审查工作流）
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from aceflow.workflow.workflows.review import ReviewWorkflow
from aceflow.workflow.workflows.base import ValidationResult
from aceflow.workflow.models import WorkflowType, Stage
from aceflow.workflow.core.engine import WorkflowEngine


class TestReviewWorkflowBasics:
    """测试 ReviewWorkflow 的基本属性"""

    def setup_method(self):
        self.workflow = ReviewWorkflow()

    def test_workflow_type(self):
        assert self.workflow.workflow_type == WorkflowType.REVIEW

    def test_workflow_name(self):
        assert self.workflow.workflow_name == "代码审查工作流"

    def test_workflow_description(self):
        assert "代码审查" in self.workflow.description
        assert "4个阶段" in self.workflow.description

    def test_estimated_duration(self):
        assert self.workflow.estimated_duration == "1-2天"

    def test_supports_subtasks(self):
        assert self.workflow.supports_subtasks() is False


class TestReviewWorkflowStages:
    """测试 ReviewWorkflow 的阶段定义"""

    def setup_method(self):
        self.workflow = ReviewWorkflow()

    def test_stage_definitions_count(self):
        stage_defs = self.workflow.get_stage_definitions()
        assert len(stage_defs) == 4

    def test_stage_ids_and_order(self):
        stage_defs = self.workflow.get_stage_definitions()
        expected_ids = ["prepare", "review", "address", "complete"]
        actual_ids = [s.stage_id for s in stage_defs]
        assert actual_ids == expected_ids

    def test_stage_names(self):
        stage_defs = self.workflow.get_stage_definitions()
        assert "审查准备" in stage_defs[0].name
        assert "代码审查" in stage_defs[1].name
        assert "反馈处理" in stage_defs[2].name
        assert "审查完成" in stage_defs[3].name

    def test_all_stages_have_templates(self):
        stage_defs = self.workflow.get_stage_definitions()
        for stage_def in stage_defs:
            assert stage_def.checklist_template.startswith("workflows/review/")
            assert stage_def.checklist_template.endswith(".md")

    def test_different_completion_thresholds(self):
        stage_defs = self.workflow.get_stage_definitions()
        stage_dict = {s.stage_id: s for s in stage_defs}
        
        assert stage_dict["prepare"].metadata["required_completion_rate"] == 0.8
        assert stage_dict["review"].metadata["required_completion_rate"] == 0.85
        assert stage_dict["address"].metadata["required_completion_rate"] == 0.9
        assert stage_dict["complete"].metadata["required_completion_rate"] == 0.8


class TestReviewWorkflowValidation:
    """测试 ReviewWorkflow 的阶段验证逻辑"""

    def setup_method(self):
        self.workflow = ReviewWorkflow()

    def test_validate_prepare_stage_80_percent(self):
        checklist = {f"item{i}": i < 8 for i in range(10)}
        result = self.workflow.validate_stage_completion("prepare", checklist)
        assert result.valid is True

    def test_validate_review_stage_85_percent(self):
        checklist = {f"item{i}": i < 17 for i in range(20)}
        result = self.workflow.validate_stage_completion("review", checklist)
        assert result.valid is True
        
        checklist = {f"item{i}": i < 16 for i in range(20)}
        result = self.workflow.validate_stage_completion("review", checklist)
        assert result.valid is False

    def test_validate_address_stage_90_percent(self):
        checklist = {f"item{i}": i < 9 for i in range(10)}
        result = self.workflow.validate_stage_completion("address", checklist)
        assert result.valid is True

    def test_critical_stage_warnings(self):
        checklist = {f"item{i}": i < 5 for i in range(10)}
        
        result = self.workflow.validate_stage_completion("review", checklist)
        assert result.valid is False
        assert any("代码审查" in w or "各个维度" in w for w in result.warnings)
        
        result = self.workflow.validate_stage_completion("address", checklist)
        assert result.valid is False
        assert any("阻塞性问题" in w or "质量达标" in w for w in result.warnings)


class TestReviewWorkflowEngineIntegration:
    """测试 ReviewWorkflow 与 WorkflowEngine 的集成"""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_id = "test_review_workflow"
        self.engine = WorkflowEngine(project_id=self.project_id)
        self.engine.register_workflow_implementation(WorkflowType.REVIEW, ReviewWorkflow())

    def teardown_method(self):
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        aceflow_dir = Path.cwd() / ".aceflow"
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_start_review_work_item(self):
        result = self.engine.start_work_item(
            type=WorkflowType.REVIEW,
            title="审查用户认证PR",
            description="PR #123 的代码审查"
        )
        
        assert result['success'] is True
        assert result['type'] == 'review'
        assert result['total_stages'] == 4
        assert result['supports_subtasks'] is False

    def test_review_work_item_has_correct_stages(self):
        result = self.engine.start_work_item(
            type=WorkflowType.REVIEW,
            title="审查用户认证PR"
        )
        
        stage_ids = [s['stage_id'] for s in result['stages']]
        assert stage_ids == ["prepare", "review", "address", "complete"]


class TestReviewWorkflowMetadata:
    """测试 ReviewWorkflow 的元数据"""

    def setup_method(self):
        self.workflow = ReviewWorkflow()

    def test_review_stage_has_dimensions(self):
        stage_defs = self.workflow.get_stage_definitions()
        review_stage = stage_defs[1]
        
        assert "review_dimensions" in review_stage.metadata
        dimensions = review_stage.metadata["review_dimensions"]
        assert "correctness" in dimensions
        assert "quality" in dimensions
        assert "security" in dimensions

    def test_review_stage_has_comment_types(self):
        stage_defs = self.workflow.get_stage_definitions()
        review_stage = stage_defs[1]
        
        assert "comment_types" in review_stage.metadata
        types = review_stage.metadata["comment_types"]
        assert "blocking" in types
        assert "suggestion" in types

    def test_address_stage_has_feedback_categories(self):
        stage_defs = self.workflow.get_stage_definitions()
        address_stage = stage_defs[2]
        
        assert "feedback_categories" in address_stage.metadata
        categories = address_stage.metadata["feedback_categories"]
        assert "must_fix" in categories

    def test_complete_stage_has_merge_strategies(self):
        stage_defs = self.workflow.get_stage_definitions()
        complete_stage = stage_defs[3]
        
        assert "merge_strategies" in complete_stage.metadata
        strategies = complete_stage.metadata["merge_strategies"]
        assert "merge_commit" in strategies
        assert "squash" in strategies
