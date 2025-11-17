"""
测试 DocumentationWorkflow（文档编写工作流）
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from aceflow.workflow.workflows.documentation import DocumentationWorkflow
from aceflow.workflow.models import WorkflowType
from aceflow.workflow.core.engine import WorkflowEngine


class TestDocumentationWorkflowBasics:
    def setup_method(self):
        self.workflow = DocumentationWorkflow()

    def test_workflow_type(self):
        assert self.workflow.workflow_type == WorkflowType.DOCUMENTATION

    def test_workflow_name(self):
        assert self.workflow.workflow_name == "文档编写工作流"

    def test_estimated_duration(self):
        assert self.workflow.estimated_duration == "2-5天"

    def test_supports_subtasks(self):
        assert self.workflow.supports_subtasks() is False


class TestDocumentationWorkflowStages:
    def setup_method(self):
        self.workflow = DocumentationWorkflow()

    def test_stage_count(self):
        assert len(self.workflow.get_stage_definitions()) == 4

    def test_stage_ids(self):
        stage_defs = self.workflow.get_stage_definitions()
        ids = [s.stage_id for s in stage_defs]
        assert ids == ["plan", "write", "review", "publish"]

    def test_all_stages_have_templates(self):
        for stage_def in self.workflow.get_stage_definitions():
            assert stage_def.checklist_template.startswith("workflows/documentation/")

    def test_thresholds(self):
        stage_defs = self.workflow.get_stage_definitions()
        stage_dict = {s.stage_id: s for s in stage_defs}
        
        assert stage_dict["plan"].metadata["required_completion_rate"] == 0.8
        assert stage_dict["write"].metadata["required_completion_rate"] == 0.85
        assert stage_dict["review"].metadata["required_completion_rate"] == 0.85
        assert stage_dict["publish"].metadata["required_completion_rate"] == 0.8


class TestDocumentationWorkflowValidation:
    def setup_method(self):
        self.workflow = DocumentationWorkflow()

    def test_validate_write_stage_85_percent(self):
        checklist = {f"item{i}": i < 17 for i in range(20)}
        result = self.workflow.validate_stage_completion("write", checklist)
        assert result.valid is True

    def test_validate_review_stage_85_percent(self):
        checklist = {f"item{i}": i < 17 for i in range(20)}
        result = self.workflow.validate_stage_completion("review", checklist)
        assert result.valid is True


class TestDocumentationWorkflowEngineIntegration:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.engine = WorkflowEngine(project_id="test_doc")
        self.engine.register_workflow_implementation(
            WorkflowType.DOCUMENTATION,
            DocumentationWorkflow()
        )

    def teardown_method(self):
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        aceflow_dir = Path.cwd() / ".aceflow"
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_start_documentation_work_item(self):
        result = self.engine.start_work_item(
            type=WorkflowType.DOCUMENTATION,
            title="编写API文档"
        )
        
        assert result['success'] is True
        assert result['type'] == 'documentation'
        assert result['total_stages'] == 4


class TestDocumentationWorkflowMetadata:
    def setup_method(self):
        self.workflow = DocumentationWorkflow()

    def test_plan_stage_has_doc_types(self):
        stage_defs = self.workflow.get_stage_definitions()
        plan_stage = stage_defs[0]
        
        assert "doc_types" in plan_stage.metadata
        assert "api_docs" in plan_stage.metadata["doc_types"]

    def test_write_stage_has_best_practices(self):
        stage_defs = self.workflow.get_stage_definitions()
        write_stage = stage_defs[1]
        
        assert "best_practices" in write_stage.metadata
        assert "examples_rich" in write_stage.metadata["best_practices"]

    def test_publish_stage_has_platforms(self):
        stage_defs = self.workflow.get_stage_definitions()
        publish_stage = stage_defs[3]
        
        assert "publishing_platforms" in publish_stage.metadata
        assert "github_pages" in publish_stage.metadata["publishing_platforms"]
