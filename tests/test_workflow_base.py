"""
Unit tests for BaseWorkflow and related classes

Tests the workflow base class and its components.
"""

import pytest
from aceflow.workflow.workflows.base import (
    BaseWorkflow, StageDefinition, ValidationResult
)
from aceflow.workflow.models import WorkflowType, Stage


# Mock implementation for testing
class MockWorkflow(BaseWorkflow):
    """Mock workflow for testing BaseWorkflow"""

    @property
    def workflow_type(self) -> WorkflowType:
        return WorkflowType.FEATURE

    @property
    def workflow_name(self) -> str:
        return "测试工作流"

    @property
    def description(self) -> str:
        return "用于测试的工作流"

    @property
    def estimated_duration(self) -> str:
        return "1-2天"

    def get_stage_definitions(self):
        return [
            StageDefinition(
                stage_id="stage_1",
                name="第一阶段",
                description="第一个阶段",
                checklist_template="workflows/test/stage_1.md",
                estimated_hours="2-4小时",
                deliverables=["交付物1"]
            ),
            StageDefinition(
                stage_id="stage_2",
                name="第二阶段",
                description="第二个阶段",
                checklist_template="workflows/test/stage_2.md",
                estimated_hours="4-6小时",
                deliverables=["交付物2", "交付物3"]
            ),
            StageDefinition(
                stage_id="stage_3",
                name="第三阶段",
                description="第三个阶段",
                checklist_template="workflows/test/stage_3.md"
            )
        ]

    def supports_subtasks(self) -> bool:
        return True


class TestStageDefinition:
    """Test StageDefinition dataclass"""

    def test_stage_definition_creation(self):
        """Test creating a stage definition"""
        stage_def = StageDefinition(
            stage_id="test_stage",
            name="测试阶段",
            description="测试描述",
            checklist_template="test.md"
        )

        assert stage_def.stage_id == "test_stage"
        assert stage_def.name == "测试阶段"
        assert stage_def.description == "测试描述"
        assert stage_def.checklist_template == "test.md"
        assert stage_def.estimated_hours == "未估算"  # default
        assert stage_def.deliverables == []  # default
        assert stage_def.metadata == {}  # default

    def test_stage_definition_with_optional_fields(self):
        """Test stage definition with all optional fields"""
        stage_def = StageDefinition(
            stage_id="test",
            name="名称",
            description="描述",
            checklist_template="test.md",
            estimated_hours="8-10小时",
            deliverables=["产物1", "产物2"],
            metadata={"key": "value"}
        )

        assert stage_def.estimated_hours == "8-10小时"
        assert len(stage_def.deliverables) == 2
        assert stage_def.metadata["key"] == "value"


class TestValidationResult:
    """Test ValidationResult dataclass"""

    def test_validation_result_creation(self):
        """Test creating a validation result"""
        result = ValidationResult(
            valid=True,
            completed_items=["item1", "item2"],
            missing_items=[],
            warnings=[],
            message="验证通过"
        )

        assert result.valid is True
        assert len(result.completed_items) == 2
        assert len(result.missing_items) == 0
        assert result.message == "验证通过"

    def test_validation_result_with_warnings(self):
        """Test validation result with warnings"""
        result = ValidationResult(
            valid=False,
            completed_items=["item1"],
            missing_items=["item2", "item3"],
            warnings=["警告：未完成必要项目"],
            message="验证失败"
        )

        assert result.valid is False
        assert len(result.warnings) == 1
        assert len(result.missing_items) == 2


class TestBaseWorkflow:
    """Test BaseWorkflow abstract class"""

    def setup_method(self):
        """Set up test workflow"""
        self.workflow = MockWorkflow()

    def test_abstract_properties(self):
        """Test that abstract properties are implemented"""
        assert self.workflow.workflow_type == WorkflowType.FEATURE
        assert self.workflow.workflow_name == "测试工作流"
        assert self.workflow.description == "用于测试的工作流"
        assert self.workflow.estimated_duration == "1-2天"

    def test_supports_subtasks(self):
        """Test supports_subtasks property"""
        assert self.workflow.supports_subtasks() is True

    def test_get_stage_definitions(self):
        """Test getting stage definitions"""
        stage_defs = self.workflow.get_stage_definitions()

        assert len(stage_defs) == 3
        assert stage_defs[0].stage_id == "stage_1"
        assert stage_defs[1].stage_id == "stage_2"
        assert stage_defs[2].stage_id == "stage_3"

    def test_get_stages(self):
        """Test converting stage definitions to Stage instances"""
        stages = self.workflow.get_stages()

        assert len(stages) == 3
        assert all(isinstance(stage, Stage) for stage in stages)
        assert stages[0].stage_id == "stage_1"
        assert stages[0].name == "第一阶段"
        assert stages[0].description == "第一个阶段"
        assert stages[0].deliverables == ["交付物1"]
        assert stages[0].metadata["checklist_template"] == "workflows/test/stage_1.md"
        assert stages[0].metadata["estimated_hours"] == "2-4小时"

    def test_get_stages_caching(self):
        """Test that get_stages caches results"""
        stages1 = self.workflow.get_stages()
        stages2 = self.workflow.get_stages()

        # Should return the same cached list
        assert stages1 is stages2

    def test_get_stage_template_path(self):
        """Test getting stage template path"""
        path = self.workflow.get_stage_template_path("stage_1")
        assert path == "workflows/test/stage_1.md"

        path = self.workflow.get_stage_template_path("stage_2")
        assert path == "workflows/test/stage_2.md"

    def test_get_stage_template_path_not_found(self):
        """Test getting template path for non-existent stage"""
        path = self.workflow.get_stage_template_path("nonexistent")
        assert path is None

    def test_validate_stage_completion_success(self):
        """Test stage validation with sufficient completion"""
        checklist = {
            "item1": True,
            "item2": True,
            "item3": True,
            "item4": False
        }

        result = self.workflow.validate_stage_completion("stage_1", checklist)

        assert result.valid is True
        assert len(result.completed_items) == 3
        assert len(result.missing_items) == 1
        assert result.completed_items == ["item1", "item2", "item3"]
        assert result.missing_items == ["item4"]

    def test_validate_stage_completion_failure(self):
        """Test stage validation with insufficient completion"""
        checklist = {
            "item1": True,
            "item2": False,
            "item3": False,
            "item4": False
        }

        result = self.workflow.validate_stage_completion("stage_1", checklist)

        assert result.valid is False
        assert len(result.completed_items) == 1
        assert len(result.missing_items) == 3
        assert len(result.warnings) > 0

    def test_validate_stage_completion_empty(self):
        """Test validation with empty checklist"""
        result = self.workflow.validate_stage_completion("stage_1", {})

        # Empty checklist should fail (0% completion)
        assert result.valid is False

    def test_get_stage_by_id(self):
        """Test getting stage by ID"""
        stage = self.workflow.get_stage_by_id("stage_2")

        assert stage is not None
        assert stage.stage_id == "stage_2"
        assert stage.name == "第二阶段"

    def test_get_stage_by_id_not_found(self):
        """Test getting non-existent stage"""
        stage = self.workflow.get_stage_by_id("nonexistent")
        assert stage is None

    def test_get_next_stage(self):
        """Test getting next stage"""
        next_stage = self.workflow.get_next_stage("stage_1")

        assert next_stage is not None
        assert next_stage.stage_id == "stage_2"

    def test_get_next_stage_at_end(self):
        """Test getting next stage when at the last stage"""
        next_stage = self.workflow.get_next_stage("stage_3")
        assert next_stage is None

    def test_get_next_stage_not_found(self):
        """Test getting next stage for non-existent current stage"""
        next_stage = self.workflow.get_next_stage("nonexistent")
        assert next_stage is None

    def test_get_workflow_summary(self):
        """Test getting workflow summary"""
        summary = self.workflow.get_workflow_summary()

        assert summary["type"] == "feature"
        assert summary["name"] == "测试工作流"
        assert summary["description"] == "用于测试的工作流"
        assert summary["estimated_duration"] == "1-2天"
        assert summary["total_stages"] == 3
        assert summary["supports_subtasks"] is True
        assert len(summary["stages"]) == 3
        assert summary["stages"][0]["stage_id"] == "stage_1"
        assert summary["stages"][0]["name"] == "第一阶段"
        assert summary["stages"][0]["estimated_hours"] == "2-4小时"


class TestBaseWorkflowAbstract:
    """Test that BaseWorkflow is properly abstract"""

    def test_cannot_instantiate_base_workflow(self):
        """Test that BaseWorkflow cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseWorkflow()

    def test_missing_abstract_methods(self):
        """Test that subclass without abstract methods cannot be instantiated"""

        class IncompleteWorkflow(BaseWorkflow):
            # Missing all abstract methods
            pass

        with pytest.raises(TypeError):
            IncompleteWorkflow()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
