"""
测试 RefactorWorkflow（重构优化工作流）
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from aceflow.workflow.workflows.refactor import RefactorWorkflow
from aceflow.workflow.workflows.base import ValidationResult
from aceflow.workflow.models import WorkflowType, Stage
from aceflow.workflow.core.engine import WorkflowEngine


class TestRefactorWorkflowBasics:
    """测试 RefactorWorkflow 的基本属性"""

    def setup_method(self):
        """每个测试前创建 RefactorWorkflow 实例"""
        self.workflow = RefactorWorkflow()

    def test_workflow_type(self):
        """测试工作流类型"""
        assert self.workflow.workflow_type == WorkflowType.REFACTOR

    def test_workflow_name(self):
        """测试工作流名称"""
        assert self.workflow.workflow_name == "重构优化工作流"
        assert isinstance(self.workflow.workflow_name, str)

    def test_workflow_description(self):
        """测试工作流描述"""
        assert "重构" in self.workflow.description
        assert "5个阶段" in self.workflow.description

    def test_estimated_duration(self):
        """测试预计耗时"""
        assert self.workflow.estimated_duration == "3-7天"

    def test_supports_subtasks(self):
        """测试不支持子任务拆分"""
        assert self.workflow.supports_subtasks() is False


class TestRefactorWorkflowStages:
    """测试 RefactorWorkflow 的阶段定义"""

    def setup_method(self):
        """每个测试前创建 RefactorWorkflow 实例"""
        self.workflow = RefactorWorkflow()

    def test_stage_definitions_count(self):
        """测试阶段数量"""
        stage_defs = self.workflow.get_stage_definitions()
        assert len(stage_defs) == 5

    def test_stage_ids_and_order(self):
        """测试阶段ID和顺序"""
        stage_defs = self.workflow.get_stage_definitions()
        expected_ids = ["assess", "plan", "refactor", "test", "document"]
        actual_ids = [s.stage_id for s in stage_defs]
        assert actual_ids == expected_ids

    def test_stage_names(self):
        """测试阶段名称"""
        stage_defs = self.workflow.get_stage_definitions()
        stage_names = [s.name for s in stage_defs]

        assert "评估分析" in stage_names[0]
        assert "方案设计" in stage_names[1]
        assert "重构实现" in stage_names[2]
        assert "测试验证" in stage_names[3]
        assert "文档更新" in stage_names[4]

    def test_all_stages_have_templates(self):
        """测试所有阶段都有模板路径"""
        stage_defs = self.workflow.get_stage_definitions()
        for stage_def in stage_defs:
            assert stage_def.checklist_template
            assert stage_def.checklist_template.startswith("workflows/refactor/")
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

    def test_different_completion_thresholds(self):
        """测试不同阶段有不同的完成率要求"""
        stage_defs = self.workflow.get_stage_definitions()
        stage_dict = {s.stage_id: s for s in stage_defs}

        # assess: 80%, plan: 85%, refactor: 90%, test: 90%, document: 80%
        assert stage_dict["assess"].metadata["required_completion_rate"] == 0.8
        assert stage_dict["plan"].metadata["required_completion_rate"] == 0.85
        assert stage_dict["refactor"].metadata["required_completion_rate"] == 0.9
        assert stage_dict["test"].metadata["required_completion_rate"] == 0.9
        assert stage_dict["document"].metadata["required_completion_rate"] == 0.8


class TestRefactorWorkflowStageConversion:
    """测试 RefactorWorkflow 的阶段转换"""

    def setup_method(self):
        """每个测试前创建 RefactorWorkflow 实例"""
        self.workflow = RefactorWorkflow()

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
        stage = self.workflow.get_stage_by_id("assess")
        assert stage is not None
        assert stage.stage_id == "assess"

        stage = self.workflow.get_stage_by_id("refactor")
        assert stage is not None
        assert stage.stage_id == "refactor"

    def test_get_stage_by_id_not_found(self):
        """测试获取不存在的阶段"""
        stage = self.workflow.get_stage_by_id("nonexistent")
        assert stage is None

    def test_get_next_stage(self):
        """测试获取下一阶段"""
        next_stage = self.workflow.get_next_stage("assess")
        assert next_stage is not None
        assert next_stage.stage_id == "plan"

        next_stage = self.workflow.get_next_stage("test")
        assert next_stage is not None
        assert next_stage.stage_id == "document"

    def test_get_next_stage_at_end(self):
        """测试在最后阶段获取下一阶段"""
        next_stage = self.workflow.get_next_stage("document")
        assert next_stage is None


class TestRefactorWorkflowValidation:
    """测试 RefactorWorkflow 的阶段验证逻辑"""

    def setup_method(self):
        """每个测试前创建 RefactorWorkflow 实例"""
        self.workflow = RefactorWorkflow()

    def test_validate_assess_stage_80_percent(self):
        """测试评估阶段验证 - 80%阈值"""
        checklist = {f"item{i}": i < 8 for i in range(10)}  # 80%
        result = self.workflow.validate_stage_completion("assess", checklist)
        assert result.valid is True

    def test_validate_plan_stage_85_percent(self):
        """测试方案设计阶段验证 - 85%阈值"""
        checklist = {f"item{i}": i < 17 for i in range(20)}  # 85%
        result = self.workflow.validate_stage_completion("plan", checklist)
        assert result.valid is True

        # 80%应该失败
        checklist = {f"item{i}": i < 16 for i in range(20)}  # 80%
        result = self.workflow.validate_stage_completion("plan", checklist)
        assert result.valid is False

    def test_validate_refactor_stage_90_percent(self):
        """测试重构实现阶段验证 - 90%阈值"""
        checklist = {f"item{i}": i < 9 for i in range(10)}  # 90%
        result = self.workflow.validate_stage_completion("refactor", checklist)
        assert result.valid is True

        # 85%应该失败
        checklist = {f"item{i}": i < 85 for i in range(100)}  # 85%
        result = self.workflow.validate_stage_completion("refactor", checklist)
        assert result.valid is False

    def test_validate_test_stage_90_percent(self):
        """测试测试验证阶段验证 - 90%阈值"""
        checklist = {f"item{i}": i < 9 for i in range(10)}  # 90%
        result = self.workflow.validate_stage_completion("test", checklist)
        assert result.valid is True

    def test_critical_stage_warnings(self):
        """测试关键阶段失败时有额外警告"""
        # plan阶段失败
        checklist = {f"item{i}": i < 5 for i in range(10)}  # 50%
        result = self.workflow.validate_stage_completion("plan", checklist)
        assert result.valid is False
        warning_text = " ".join(result.warnings)
        assert "方案设计" in warning_text or "计划" in warning_text

        # refactor阶段失败
        result = self.workflow.validate_stage_completion("refactor", checklist)
        assert result.valid is False
        warning_text = " ".join(result.warnings)
        assert "严格执行" in warning_text or "必须项" in warning_text

    def test_validate_empty_checklist(self):
        """测试空检查清单"""
        result = self.workflow.validate_stage_completion("assess", {})
        assert result.valid is False
        assert "为空" in result.message

    def test_validate_nonexistent_stage(self):
        """测试验证不存在的阶段"""
        result = self.workflow.validate_stage_completion("nonexistent", {"item1": True})
        assert result.valid is False
        assert "未找到" in result.message


class TestRefactorWorkflowSummary:
    """测试 RefactorWorkflow 的摘要信息"""

    def setup_method(self):
        """每个测试前创建 RefactorWorkflow 实例"""
        self.workflow = RefactorWorkflow()

    def test_get_workflow_summary(self):
        """测试获取工作流摘要"""
        summary = self.workflow.get_workflow_summary()

        assert summary['type'] == 'refactor'
        assert summary['name'] == "重构优化工作流"
        assert summary['total_stages'] == 5
        assert summary['supports_subtasks'] is False
        assert 'stages' in summary
        assert len(summary['stages']) == 5


class TestRefactorWorkflowEngineIntegration:
    """测试 RefactorWorkflow 与 WorkflowEngine 的集成"""

    def setup_method(self):
        """每个测试前创建临时目录和 WorkflowEngine"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_id = "test_refactor_workflow"
        self.engine = WorkflowEngine(project_id=self.project_id)

        # 注册 RefactorWorkflow
        self.engine.register_workflow_implementation(
            WorkflowType.REFACTOR,
            RefactorWorkflow()
        )

    def teardown_method(self):
        """每个测试后清理临时目录"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        # 清理 .aceflow 目录
        aceflow_dir = Path.cwd() / ".aceflow"
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_start_refactor_work_item(self):
        """测试启动重构优化工作项"""
        result = self.engine.start_work_item(
            type=WorkflowType.REFACTOR,
            title="重构用户认证模块",
            description="降低复杂度，提升可维护性"
        )

        assert result['success'] is True
        assert result['type'] == 'refactor'
        assert result['title'] == "重构用户认证模块"
        assert result['total_stages'] == 5
        assert result['supports_subtasks'] is False

    def test_refactor_work_item_has_correct_stages(self):
        """测试重构工作项包含正确的阶段"""
        result = self.engine.start_work_item(
            type=WorkflowType.REFACTOR,
            title="重构用户认证模块"
        )

        stages = result['stages']
        assert len(stages) == 5

        stage_ids = [s['stage_id'] for s in stages]
        assert stage_ids == ["assess", "plan", "refactor", "test", "document"]

    def test_refactor_work_item_first_stage_active(self):
        """测试重构工作项第一阶段自动激活"""
        result = self.engine.start_work_item(
            type=WorkflowType.REFACTOR,
            title="重构用户认证模块"
        )

        current_stage = result['current_stage']
        assert current_stage is not None
        assert current_stage['stage_id'] == "assess"
        assert current_stage['status'] == "in_progress"

    def test_get_current_refactor_work_item(self):
        """测试获取当前重构工作项"""
        # 创建工作项
        self.engine.start_work_item(
            type=WorkflowType.REFACTOR,
            title="重构用户认证模块"
        )

        # 获取当前工作项
        current = self.engine.get_current_work_item()
        assert current is not None
        assert current['type'] == 'refactor'
        assert current['title'] == "重构用户认证模块"

    def test_refactor_workflow_duration(self):
        """测试重构工作流总耗时估算"""
        stage_defs = RefactorWorkflow().get_stage_definitions()

        # 验证各阶段估时合理
        assert "4-8小时" in stage_defs[0].estimated_hours  # assess
        assert "4-8小时" in stage_defs[1].estimated_hours  # plan
        assert "16-32小时" in stage_defs[2].estimated_hours  # refactor
        assert "6-12小时" in stage_defs[3].estimated_hours  # test
        assert "2-4小时" in stage_defs[4].estimated_hours  # document

        # 总计约 32-64 小时 (约3-7天)


class TestRefactorWorkflowMetadata:
    """测试 RefactorWorkflow 的元数据"""

    def setup_method(self):
        """每个测试前创建 RefactorWorkflow 实例"""
        self.workflow = RefactorWorkflow()

    def test_assess_stage_has_metrics(self):
        """测试评估阶段包含代码指标"""
        stage_defs = self.workflow.get_stage_definitions()
        assess_stage = stage_defs[0]

        assert "metrics" in assess_stage.metadata
        metrics = assess_stage.metadata["metrics"]
        assert "complexity" in metrics
        assert "duplication" in metrics
        assert "coverage" in metrics

    def test_plan_stage_has_refactoring_techniques(self):
        """测试方案设计阶段包含重构技术"""
        stage_defs = self.workflow.get_stage_definitions()
        plan_stage = stage_defs[1]

        assert "refactoring_techniques" in plan_stage.metadata
        techniques = plan_stage.metadata["refactoring_techniques"]
        assert "Extract Method" in techniques
        assert "Extract Class" in techniques

    def test_refactor_stage_has_principles(self):
        """测试重构实现阶段包含原则"""
        stage_defs = self.workflow.get_stage_definitions()
        refactor_stage = stage_defs[2]

        assert "principles" in refactor_stage.metadata
        principles = refactor_stage.metadata["principles"]
        assert "小步前进" in principles
        assert "频繁测试" in principles
        assert "保持功能" in principles

    def test_test_stage_has_test_types(self):
        """测试测试验证阶段包含测试类型"""
        stage_defs = self.workflow.get_stage_definitions()
        test_stage = stage_defs[3]

        assert "test_types" in test_stage.metadata
        test_types = test_stage.metadata["test_types"]
        assert "unit" in test_types
        assert "integration" in test_types
        assert "regression" in test_types
        assert "performance" in test_types

    def test_document_stage_has_doc_types(self):
        """测试文档更新阶段包含文档类型"""
        stage_defs = self.workflow.get_stage_definitions()
        document_stage = stage_defs[4]

        assert "doc_types" in document_stage.metadata
        doc_types = document_stage.metadata["doc_types"]
        assert "code_comments" in doc_types
        assert "api_docs" in doc_types
        assert "changelog" in doc_types
        assert "adr" in doc_types
