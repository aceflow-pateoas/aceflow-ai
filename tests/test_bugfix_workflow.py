"""
测试 BugfixWorkflow（Bug修复工作流）
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from aceflow.workflow.workflows.bugfix import BugfixWorkflow
from aceflow.workflow.workflows.base import ValidationResult
from aceflow.workflow.models import WorkflowType, Stage
from aceflow.workflow.core.engine import WorkflowEngine


class TestBugfixWorkflowBasics:
    """测试 BugfixWorkflow 的基本属性"""

    def setup_method(self):
        """每个测试前创建 BugfixWorkflow 实例"""
        self.workflow = BugfixWorkflow()

    def test_workflow_type(self):
        """测试工作流类型"""
        assert self.workflow.workflow_type == WorkflowType.BUGFIX

    def test_workflow_name(self):
        """测试工作流名称"""
        assert self.workflow.workflow_name == "Bug修复工作流"
        assert isinstance(self.workflow.workflow_name, str)

    def test_workflow_description(self):
        """测试工作流描述"""
        assert "Bug修复" in self.workflow.description
        assert "5个阶段" in self.workflow.description

    def test_estimated_duration(self):
        """测试预计耗时"""
        assert self.workflow.estimated_duration == "1-3天"

    def test_supports_subtasks(self):
        """测试不支持子任务拆分"""
        assert self.workflow.supports_subtasks() is False  # Bug修复不支持子任务


class TestBugfixWorkflowStages:
    """测试 BugfixWorkflow 的阶段定义"""

    def setup_method(self):
        """每个测试前创建 BugfixWorkflow 实例"""
        self.workflow = BugfixWorkflow()

    def test_stage_definitions_count(self):
        """测试阶段数量"""
        stage_defs = self.workflow.get_stage_definitions()
        assert len(stage_defs) == 5

    def test_stage_ids_and_order(self):
        """测试阶段ID和顺序"""
        stage_defs = self.workflow.get_stage_definitions()
        expected_ids = ["analyze", "locate", "fix", "verify", "release"]
        actual_ids = [s.stage_id for s in stage_defs]
        assert actual_ids == expected_ids

    def test_stage_names(self):
        """测试阶段名称"""
        stage_defs = self.workflow.get_stage_definitions()
        stage_names = [s.name for s in stage_defs]

        assert "问题分析" in stage_names[0]
        assert "定位根因" in stage_names[1]
        assert "修复实现" in stage_names[2]
        assert "验证测试" in stage_names[3]
        assert "发布说明" in stage_names[4]

    def test_all_stages_have_templates(self):
        """测试所有阶段都有模板路径"""
        stage_defs = self.workflow.get_stage_definitions()
        for stage_def in stage_defs:
            assert stage_def.checklist_template
            assert stage_def.checklist_template.startswith("workflows/bugfix/")
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

    def test_critical_stages_have_high_threshold(self):
        """测试关键阶段有更高的完成率要求"""
        stage_defs = self.workflow.get_stage_definitions()
        stage_dict = {s.stage_id: s for s in stage_defs}

        # locate, fix, verify 应该是90%阈值
        assert stage_dict["locate"].metadata["required_completion_rate"] == 0.9
        assert stage_dict["fix"].metadata["required_completion_rate"] == 0.9
        assert stage_dict["verify"].metadata["required_completion_rate"] == 0.9

        # analyze, release 是80%阈值
        assert stage_dict["analyze"].metadata["required_completion_rate"] == 0.8
        assert stage_dict["release"].metadata["required_completion_rate"] == 0.8


class TestBugfixWorkflowStageConversion:
    """测试 BugfixWorkflow 的阶段转换"""

    def setup_method(self):
        """每个测试前创建 BugfixWorkflow 实例"""
        self.workflow = BugfixWorkflow()

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
        stage = self.workflow.get_stage_by_id("analyze")
        assert stage is not None
        assert stage.stage_id == "analyze"

        stage = self.workflow.get_stage_by_id("fix")
        assert stage is not None
        assert stage.stage_id == "fix"

    def test_get_stage_by_id_not_found(self):
        """测试获取不存在的阶段"""
        stage = self.workflow.get_stage_by_id("nonexistent")
        assert stage is None

    def test_get_next_stage(self):
        """测试获取下一阶段"""
        next_stage = self.workflow.get_next_stage("analyze")
        assert next_stage is not None
        assert next_stage.stage_id == "locate"

        next_stage = self.workflow.get_next_stage("verify")
        assert next_stage is not None
        assert next_stage.stage_id == "release"

    def test_get_next_stage_at_end(self):
        """测试在最后阶段获取下一阶段"""
        next_stage = self.workflow.get_next_stage("release")
        assert next_stage is None


class TestBugfixWorkflowValidation:
    """测试 BugfixWorkflow 的阶段验证逻辑"""

    def setup_method(self):
        """每个测试前创建 BugfixWorkflow 实例"""
        self.workflow = BugfixWorkflow()

    def test_validate_analyze_stage_success(self):
        """测试分析阶段验证 - 成功（80%阈值）"""
        checklist = {
            "item1": True,
            "item2": True,
            "item3": True,
            "item4": True,
            "item5": False  # 5个中完成4个 = 80%
        }
        result = self.workflow.validate_stage_completion("analyze", checklist)
        assert result.valid is True
        assert len(result.completed_items) == 4

    def test_validate_analyze_stage_failure(self):
        """测试分析阶段验证 - 失败（低于80%）"""
        checklist = {
            "item1": True,
            "item2": True,
            "item3": False,
            "item4": False,
            "item5": False  # 5个中完成2个 = 40%
        }
        result = self.workflow.validate_stage_completion("analyze", checklist)
        assert result.valid is False
        assert len(result.warnings) > 0

    def test_validate_locate_stage_high_threshold(self):
        """测试定位阶段验证 - 更高的阈值（90%）"""
        # 90%阈值：10个中需要完成9个
        checklist = {f"item{i}": i < 9 for i in range(10)}
        result = self.workflow.validate_stage_completion("locate", checklist)
        assert result.valid is True

        # 低于90%应该失败
        checklist = {f"item{i}": i < 8 for i in range(10)}
        result = self.workflow.validate_stage_completion("locate", checklist)
        assert result.valid is False

    def test_validate_fix_stage_high_threshold(self):
        """测试修复阶段验证 - 90%阈值"""
        checklist = {f"item{i}": i < 9 for i in range(10)}
        result = self.workflow.validate_stage_completion("fix", checklist)
        assert result.valid is True

    def test_validate_verify_stage_high_threshold(self):
        """测试验证阶段验证 - 90%阈值"""
        checklist = {f"item{i}": i < 9 for i in range(10)}
        result = self.workflow.validate_stage_completion("verify", checklist)
        assert result.valid is True

    def test_critical_stage_warnings(self):
        """测试关键阶段失败时有额外警告"""
        checklist = {f"item{i}": i < 5 for i in range(10)}  # 50%完成率
        result = self.workflow.validate_stage_completion("locate", checklist)

        assert result.valid is False
        # 应该有关键阶段的额外警告
        warning_text = " ".join(result.warnings)
        assert "关键阶段" in warning_text or "⚠️" in warning_text

    def test_validate_empty_checklist(self):
        """测试空检查清单"""
        result = self.workflow.validate_stage_completion("analyze", {})
        assert result.valid is False
        assert "为空" in result.message

    def test_validate_nonexistent_stage(self):
        """测试验证不存在的阶段"""
        result = self.workflow.validate_stage_completion("nonexistent", {"item1": True})
        assert result.valid is False
        assert "未找到" in result.message


class TestBugfixWorkflowSummary:
    """测试 BugfixWorkflow 的摘要信息"""

    def setup_method(self):
        """每个测试前创建 BugfixWorkflow 实例"""
        self.workflow = BugfixWorkflow()

    def test_get_workflow_summary(self):
        """测试获取工作流摘要"""
        summary = self.workflow.get_workflow_summary()

        assert summary['type'] == 'bugfix'
        assert summary['name'] == "Bug修复工作流"
        assert summary['total_stages'] == 5
        assert summary['supports_subtasks'] is False  # Bug修复不支持子任务
        assert 'stages' in summary
        assert len(summary['stages']) == 5


class TestBugfixWorkflowEngineIntegration:
    """测试 BugfixWorkflow 与 WorkflowEngine 的集成"""

    def setup_method(self):
        """每个测试前创建临时目录和 WorkflowEngine"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_id = "test_bugfix_workflow"
        self.engine = WorkflowEngine(project_id=self.project_id)

        # 注册 BugfixWorkflow
        self.engine.register_workflow_implementation(
            WorkflowType.BUGFIX,
            BugfixWorkflow()
        )

    def teardown_method(self):
        """每个测试后清理临时目录"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        # 清理 .aceflow 目录
        aceflow_dir = Path.cwd() / ".aceflow"
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_start_bugfix_work_item(self):
        """测试启动Bug修复工作项"""
        result = self.engine.start_work_item(
            type=WorkflowType.BUGFIX,
            title="修复登录Bug",
            description="用户登录时偶现会话失效"
        )

        assert result['success'] is True
        assert result['type'] == 'bugfix'
        assert result['title'] == "修复登录Bug"
        assert result['total_stages'] == 5
        assert result['supports_subtasks'] is False

    def test_bugfix_work_item_has_correct_stages(self):
        """测试Bug修复工作项包含正确的阶段"""
        result = self.engine.start_work_item(
            type=WorkflowType.BUGFIX,
            title="修复登录Bug"
        )

        stages = result['stages']
        assert len(stages) == 5

        stage_ids = [s['stage_id'] for s in stages]
        assert stage_ids == ["analyze", "locate", "fix", "verify", "release"]

    def test_bugfix_work_item_first_stage_active(self):
        """测试Bug修复工作项第一阶段自动激活"""
        result = self.engine.start_work_item(
            type=WorkflowType.BUGFIX,
            title="修复登录Bug"
        )

        current_stage = result['current_stage']
        assert current_stage is not None
        assert current_stage['stage_id'] == "analyze"
        assert current_stage['status'] == "in_progress"

    def test_get_current_bugfix_work_item(self):
        """测试获取当前Bug修复工作项"""
        # 创建工作项
        self.engine.start_work_item(
            type=WorkflowType.BUGFIX,
            title="修复登录Bug"
        )

        # 获取当前工作项
        current = self.engine.get_current_work_item()
        assert current is not None
        assert current['type'] == 'bugfix'
        assert current['title'] == "修复登录Bug"

    def test_bugfix_workflow_duration(self):
        """测试Bug修复工作流总耗时估算"""
        stage_defs = BugfixWorkflow().get_stage_definitions()

        # 验证各阶段估时合理
        assert "1-2小时" in stage_defs[0].estimated_hours  # analyze
        assert "2-4小时" in stage_defs[1].estimated_hours  # locate
        assert "2-6小时" in stage_defs[2].estimated_hours  # fix
        assert "1-3小时" in stage_defs[3].estimated_hours  # verify
        assert "0.5-1小时" in stage_defs[4].estimated_hours  # release

        # 总计约 6.5-16 小时 (约1-3天)


class TestBugfixWorkflowComparison:
    """测试 BugfixWorkflow 与 FeatureWorkflow 的差异"""

    def test_bugfix_no_subtasks(self):
        """测试Bug修复不支持子任务，功能开发支持"""
        from aceflow.workflow.workflows.feature import FeatureWorkflow

        bugfix = BugfixWorkflow()
        feature = FeatureWorkflow()

        assert bugfix.supports_subtasks() is False
        assert feature.supports_subtasks() is True

    def test_bugfix_shorter_duration(self):
        """测试Bug修复周期更短"""
        from aceflow.workflow.workflows.feature import FeatureWorkflow

        bugfix = BugfixWorkflow()
        feature = FeatureWorkflow()

        assert "1-3天" in bugfix.estimated_duration
        assert "1-2周" in feature.estimated_duration

    def test_bugfix_different_stages(self):
        """测试Bug修复有不同的阶段设计"""
        from aceflow.workflow.workflows.feature import FeatureWorkflow

        bugfix = BugfixWorkflow()
        feature = FeatureWorkflow()

        bugfix_stages = [s.stage_id for s in bugfix.get_stage_definitions()]
        feature_stages = [s.stage_id for s in feature.get_stage_definitions()]

        # Bug修复: analyze, locate, fix, verify, release
        # 功能开发: requirement, design, implementation, testing, delivery
        assert bugfix_stages != feature_stages
        assert "analyze" in bugfix_stages
        assert "locate" in bugfix_stages
