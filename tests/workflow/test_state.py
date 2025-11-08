"""
测试状态管理器

测试 aceflow.workflow.core.state.StateManager
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from aceflow.workflow.core.state import StateManager
from aceflow.workflow.models import (
    WorkflowMode,
    StageStatus,
    Stage
)


class TestStateManager:
    """测试状态管理器"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def state_manager(self, temp_dir):
        """创建状态管理器实例"""
        return StateManager(project_id="test_project", state_dir=temp_dir)

    def test_state_manager_creation(self, state_manager):
        """测试状态管理器创建"""
        assert state_manager is not None
        assert state_manager.project_id == "test_project"
        assert state_manager.state_dir.exists()

    def test_initialize_iteration(self, state_manager):
        """测试初始化迭代"""
        iteration = state_manager.initialize_iteration(
            mode=WorkflowMode.MINIMAL,
            metadata={"goal": "测试目标"}
        )

        assert iteration is not None
        assert iteration.mode == WorkflowMode.MINIMAL
        assert iteration.metadata["goal"] == "测试目标"

    def test_get_current_iteration(self, state_manager):
        """测试获取当前迭代"""
        # 初始时没有迭代
        assert state_manager.get_current_iteration() is None

        # 初始化后有迭代
        iteration = state_manager.initialize_iteration(WorkflowMode.MINIMAL)
        current = state_manager.get_current_iteration()

        assert current is not None
        assert current.iteration_id == iteration.iteration_id

    def test_get_current_stage(self, state_manager):
        """测试获取当前阶段"""
        # 初始化迭代
        iteration = state_manager.initialize_iteration(WorkflowMode.MINIMAL)

        # 添加一些阶段
        iteration.stages = [
            Stage(stage_id="P", name="规划", description="规划阶段", status=StageStatus.IN_PROGRESS),
            Stage(stage_id="D", name="开发", description="开发阶段")
        ]

        current_stage = state_manager.get_current_stage()
        assert current_stage is not None
        assert current_stage.stage_id == "P"

    def test_advance_stage(self, state_manager):
        """测试推进阶段"""
        # 初始化迭代并添加阶段
        iteration = state_manager.initialize_iteration(WorkflowMode.MINIMAL)
        iteration.stages = [
            Stage(stage_id="P", name="规划", description="规划阶段", status=StageStatus.IN_PROGRESS),
            Stage(stage_id="D", name="开发", description="开发阶段")
        ]

        # 推进到下一阶段
        success = state_manager.advance_stage()
        assert success is True

        # 验证阶段推进
        current = state_manager.get_current_stage()
        assert current is not None
        assert current.stage_id == "D"

        # 验证前一阶段已完成
        assert iteration.stages[0].status == StageStatus.COMPLETED

    def test_update_stage_progress(self, state_manager):
        """测试更新阶段进度"""
        iteration = state_manager.initialize_iteration(WorkflowMode.MINIMAL)
        iteration.stages = [
            Stage(stage_id="P", name="规划", description="规划阶段", status=StageStatus.IN_PROGRESS)
        ]

        # 更新进度
        state_manager.update_stage_progress(0.5)

        # 验证进度
        current = state_manager.get_current_stage()
        assert current.progress == 0.5

    def test_get_state_summary(self, state_manager):
        """测试获取状态摘要"""
        # 初始时没有迭代
        summary = state_manager.get_state_summary()
        assert summary['status'] == 'no_iteration'

        # 初始化迭代后
        iteration = state_manager.initialize_iteration(WorkflowMode.MINIMAL)
        iteration.stages = [
            Stage(stage_id="P", name="规划", description="规划阶段", status=StageStatus.IN_PROGRESS)
        ]

        summary = state_manager.get_state_summary()
        assert summary['status'] == 'active'
        assert 'iteration_id' in summary
        assert 'mode' in summary
        assert 'current_stage' in summary

    def test_get_transition_history(self, state_manager):
        """测试获取转换历史"""
        # 初始化迭代
        state_manager.initialize_iteration(WorkflowMode.MINIMAL)

        # 获取转换历史
        history = state_manager.get_transition_history()

        assert len(history) > 0
        assert 'from_stage' in history[0]
        assert 'to_stage' in history[0]

    def test_validate_state(self, state_manager):
        """测试状态验证"""
        # 没有迭代时应该有错误
        result = state_manager.validate_state()
        assert result['valid'] is False
        assert len(result['errors']) > 0

        # 有迭代时
        iteration = state_manager.initialize_iteration(WorkflowMode.MINIMAL)
        iteration.stages = [
            Stage(stage_id="P", name="规划", description="规划阶段", status=StageStatus.IN_PROGRESS)
        ]

        result = state_manager.validate_state()
        assert result['valid'] is True

    def test_rollback_stage(self, state_manager):
        """测试回滚阶段"""
        # 初始化迭代并添加阶段
        iteration = state_manager.initialize_iteration(WorkflowMode.MINIMAL)
        iteration.stages = [
            Stage(stage_id="P", name="规划", description="规划阶段", status=StageStatus.IN_PROGRESS),
            Stage(stage_id="D", name="开发", description="开发阶段")
        ]

        # 推进到下一阶段
        state_manager.advance_stage()
        assert state_manager.get_current_stage().stage_id == "D"

        # 回滚
        success = state_manager.rollback_stage()
        assert success is True
        assert state_manager.get_current_stage().stage_id == "P"

    def test_persistence(self, temp_dir):
        """测试持久化"""
        # 创建第一个管理器并保存数据
        manager1 = StateManager(project_id="test_persist", state_dir=temp_dir)
        iteration = manager1.initialize_iteration(WorkflowMode.MINIMAL)
        iteration.stages = [
            Stage(stage_id="P", name="规划", description="规划阶段")
        ]

        iteration_id = iteration.iteration_id

        # 创建第二个管理器，应该能加载数据
        manager2 = StateManager(project_id="test_persist", state_dir=temp_dir)
        loaded_iteration = manager2.get_current_iteration()

        assert loaded_iteration is not None
        assert loaded_iteration.iteration_id == iteration_id
