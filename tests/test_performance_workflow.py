"""
测试 PerformanceWorkflow（性能排查工作流）
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from aceflow.workflow.workflows.performance import PerformanceWorkflow
from aceflow.workflow.models import WorkflowType
from aceflow.workflow.core.engine import WorkflowEngine


class TestPerformanceWorkflowBasics:
    def setup_method(self):
        self.workflow = PerformanceWorkflow()

    def test_workflow_type(self):
        assert self.workflow.workflow_type == WorkflowType.PERFORMANCE

    def test_workflow_name(self):
        assert self.workflow.workflow_name == "性能排查工作流"

    def test_estimated_duration(self):
        assert self.workflow.estimated_duration == "2-5天"

    def test_supports_subtasks(self):
        assert self.workflow.supports_subtasks() is False


class TestPerformanceWorkflowStages:
    def setup_method(self):
        self.workflow = PerformanceWorkflow()

    def test_stage_count(self):
        assert len(self.workflow.get_stage_definitions()) == 4

    def test_stage_ids(self):
        stage_defs = self.workflow.get_stage_definitions()
        ids = [s.stage_id for s in stage_defs]
        assert ids == ["diagnose", "analyze", "optimize", "verify"]

    def test_all_stages_have_templates(self):
        for stage_def in self.workflow.get_stage_definitions():
            assert stage_def.checklist_template.startswith("workflows/performance/")

    def test_thresholds(self):
        stage_defs = self.workflow.get_stage_definitions()
        stage_dict = {s.stage_id: s for s in stage_defs}
        
        assert stage_dict["diagnose"].metadata["required_completion_rate"] == 0.85
        assert stage_dict["analyze"].metadata["required_completion_rate"] == 0.9
        assert stage_dict["optimize"].metadata["required_completion_rate"] == 0.9
        assert stage_dict["verify"].metadata["required_completion_rate"] == 0.85


class TestPerformanceWorkflowEngineIntegration:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.engine = WorkflowEngine(project_id="test_perf")
        self.engine.register_workflow_implementation(
            WorkflowType.PERFORMANCE,
            PerformanceWorkflow()
        )

    def teardown_method(self):
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        aceflow_dir = Path.cwd() / ".aceflow"
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_start_performance_work_item(self):
        result = self.engine.start_work_item(
            type=WorkflowType.PERFORMANCE,
            title="优化数据库查询性能"
        )
        
        assert result['success'] is True
        assert result['type'] == 'performance'
        assert result['total_stages'] == 4


class TestPerformanceWorkflowMetadata:
    def setup_method(self):
        self.workflow = PerformanceWorkflow()

    def test_diagnose_stage_has_metrics(self):
        stage_defs = self.workflow.get_stage_definitions()
        diagnose_stage = stage_defs[0]
        
        assert "metrics" in diagnose_stage.metadata
        assert "response_time" in diagnose_stage.metadata["metrics"]

    def test_analyze_stage_has_tools(self):
        stage_defs = self.workflow.get_stage_definitions()
        analyze_stage = stage_defs[1]
        
        assert "tools" in analyze_stage.metadata
        assert "profiler" in analyze_stage.metadata["tools"]

    def test_optimize_stage_has_techniques(self):
        stage_defs = self.workflow.get_stage_definitions()
        optimize_stage = stage_defs[2]
        
        assert "techniques" in optimize_stage.metadata
        assert "caching" in optimize_stage.metadata["techniques"]
