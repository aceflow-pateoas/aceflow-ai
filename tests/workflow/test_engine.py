"""
测试工作流引擎

测试 aceflow.workflow.engine.WorkflowEngine
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from aceflow.workflow.engine import WorkflowEngine
from aceflow.workflow.state import StateManager
from aceflow.workflow.models import WorkflowMode, StageStatus


class TestWorkflowEngine:
    """测试工作流引擎"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def state_manager(self, temp_dir):
        """创建状态管理器"""
        return StateManager(storage_dir=temp_dir)

    @pytest.fixture
    def engine_minimal(self, state_manager):
        """创建 Minimal 模式引擎"""
        return WorkflowEngine(WorkflowMode.MINIMAL, state_manager)

    @pytest.fixture
    def engine_standard(self, state_manager):
        """创建 Standard 模式引擎"""
        return WorkflowEngine(WorkflowMode.STANDARD, state_manager)

    def test_engine_creation(self, engine_minimal):
        """测试引擎创建"""
        assert engine_minimal.mode == WorkflowMode.MINIMAL
        assert engine_minimal.workflow is not None

    def test_start_iteration(self, engine_minimal):
        """测试开始迭代"""
        iteration = engine_minimal.start_iteration()

        assert iteration is not None
        assert iteration.mode == WorkflowMode.MINIMAL
        assert len(iteration.stages) > 0  # Minimal 模式至少有阶段
        assert iteration.current_stage is not None  # 应该有当前阶段

    def test_start_iteration_with_id(self, engine_minimal):
        """测试使用指定ID开始迭代"""
        iteration = engine_minimal.start_iteration("custom_iter_001")

        assert iteration.iteration_id == "custom_iter_001"

    def test_advance_to_next_stage(self, engine_minimal):
        """测试进入下一阶段"""
        # 开始迭代
        iteration = engine_minimal.start_iteration()
        first_stage_id = iteration.current_stage.stage_id

        # 进入下一阶段
        next_stage = engine_minimal.advance_to_next_stage(iteration.iteration_id)

        if next_stage:
            # 如果有下一阶段
            assert next_stage.stage_id != first_stage_id
            assert next_stage.status == StageStatus.IN_PROGRESS

            # 验证前一阶段已完成
            updated_iteration = engine_minimal.state_manager.get_iteration(iteration.iteration_id)
            prev_stage = updated_iteration.get_stage_by_id(first_stage_id)
            assert prev_stage.status == StageStatus.COMPLETED

    def test_get_current_status(self, engine_minimal):
        """测试获取当前状态"""
        iteration = engine_minimal.start_iteration()

        status = engine_minimal.get_current_status(iteration.iteration_id)

        assert status is not None
        assert 'iteration_id' in status
        assert 'mode' in status
        assert 'current_stage' in status
        assert 'progress' in status

    def test_complete_stage(self, engine_minimal):
        """测试完成阶段"""
        iteration = engine_minimal.start_iteration()
        current_stage_id = iteration.current_stage.stage_id

        # 完成当前阶段
        success = engine_minimal.complete_stage(iteration.iteration_id, current_stage_id)
        assert success

        # 验证阶段状态
        updated_iteration = engine_minimal.state_manager.get_iteration(iteration.iteration_id)
        stage = updated_iteration.get_stage_by_id(current_stage_id)
        assert stage.status == StageStatus.COMPLETED

    def test_workflow_modes(self, state_manager):
        """测试不同工作流模式"""
        modes = [
            WorkflowMode.MINIMAL,
            WorkflowMode.STANDARD,
            WorkflowMode.COMPLETE
        ]

        for mode in modes:
            engine = WorkflowEngine(mode, state_manager)
            iteration = engine.start_iteration()

            assert iteration.mode == mode
            assert len(iteration.stages) > 0

            # Minimal 最少，Complete 最多
            if mode == WorkflowMode.MINIMAL:
                assert len(iteration.stages) <= 5
            elif mode == WorkflowMode.COMPLETE:
                assert len(iteration.stages) >= 8

    def test_smart_mode_analysis(self, state_manager):
        """测试 Smart 模式的分析功能"""
        engine = WorkflowEngine(WorkflowMode.SMART, state_manager)

        # Smart 模式应该有分析功能
        assert hasattr(engine.workflow, 'analyze_task_and_recommend')

        # 测试任务分析
        recommendation = engine.workflow.analyze_task_and_recommend(
            task_description="实现一个简单的用户登录功能",
            context={'complexity': 'low', 'urgency': 'normal'}
        )

        assert 'recommended_mode' in recommendation
        assert 'reason' in recommendation
        assert 'confidence' in recommendation
