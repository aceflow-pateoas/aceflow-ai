"""
测试状态管理器

测试 aceflow.workflow.state.StateManager
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from aceflow.workflow.state import StateManager
from aceflow.workflow.models import (
    WorkflowMode,
    StageStatus,
    Stage,
    Iteration
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
        return StateManager(storage_dir=temp_dir)

    def test_create_iteration(self, state_manager):
        """测试创建迭代"""
        stages = [
            Stage(stage_id="P", name="规划", description="规划阶段"),
            Stage(stage_id="D", name="开发", description="开发阶段")
        ]

        iteration = state_manager.create_iteration(
            iteration_id="iter_001",
            mode=WorkflowMode.MINIMAL,
            stages=stages
        )

        assert iteration.iteration_id == "iter_001"
        assert iteration.mode == WorkflowMode.MINIMAL
        assert len(iteration.stages) == 2

    def test_get_iteration(self, state_manager):
        """测试获取迭代"""
        stages = [Stage(stage_id="P", name="规划", description="规划")]

        # 创建迭代
        state_manager.create_iteration(
            iteration_id="iter_001",
            mode=WorkflowMode.MINIMAL,
            stages=stages
        )

        # 获取迭代
        iteration = state_manager.get_iteration("iter_001")
        assert iteration is not None
        assert iteration.iteration_id == "iter_001"

        # 获取不存在的迭代
        iteration = state_manager.get_iteration("iter_999")
        assert iteration is None

    def test_update_iteration(self, state_manager):
        """测试更新迭代"""
        stages = [Stage(stage_id="P", name="规划", description="规划")]

        iteration = state_manager.create_iteration(
            iteration_id="iter_001",
            mode=WorkflowMode.MINIMAL,
            stages=stages
        )

        # 修改迭代
        iteration.metadata['updated'] = True

        # 更新
        success = state_manager.update_iteration(iteration)
        assert success

        # 验证更新
        updated = state_manager.get_iteration("iter_001")
        assert updated.metadata.get('updated') is True

    def test_update_stage_status(self, state_manager):
        """测试更新阶段状态"""
        stages = [
            Stage(stage_id="P", name="规划", description="规划"),
            Stage(stage_id="D", name="开发", description="开发")
        ]

        state_manager.create_iteration(
            iteration_id="iter_001",
            mode=WorkflowMode.MINIMAL,
            stages=stages
        )

        # 更新阶段状态
        success = state_manager.update_stage_status(
            "iter_001",
            "P",
            StageStatus.COMPLETED
        )
        assert success

        # 验证更新
        iteration = state_manager.get_iteration("iter_001")
        stage = iteration.get_stage_by_id("P")
        assert stage.status == StageStatus.COMPLETED

    def test_list_iterations(self, state_manager):
        """测试列出所有迭代"""
        # 创建多个迭代
        for i in range(3):
            stages = [Stage(stage_id="P", name="规划", description="规划")]
            state_manager.create_iteration(
                iteration_id=f"iter_{i:03d}",
                mode=WorkflowMode.MINIMAL,
                stages=stages
            )

        # 列出迭代
        iterations = state_manager.list_iterations()
        assert len(iterations) == 3

    def test_get_latest_iteration(self, state_manager):
        """测试获取最新迭代"""
        # 创建多个迭代
        for i in range(3):
            stages = [Stage(stage_id="P", name="规划", description="规划")]
            state_manager.create_iteration(
                iteration_id=f"iter_{i:03d}",
                mode=WorkflowMode.MINIMAL,
                stages=stages
            )

        # 获取最新
        latest = state_manager.get_latest_iteration()
        assert latest is not None
        # 最新的应该是最后创建的
        assert latest.iteration_id == "iter_002"

    def test_delete_iteration(self, state_manager):
        """测试删除迭代"""
        stages = [Stage(stage_id="P", name="规划", description="规划")]

        state_manager.create_iteration(
            iteration_id="iter_001",
            mode=WorkflowMode.MINIMAL,
            stages=stages
        )

        # 删除
        success = state_manager.delete_iteration("iter_001")
        assert success

        # 验证删除
        iteration = state_manager.get_iteration("iter_001")
        assert iteration is None

    def test_persistence(self, temp_dir):
        """测试持久化"""
        # 创建第一个管理器并保存数据
        manager1 = StateManager(storage_dir=temp_dir)
        stages = [Stage(stage_id="P", name="规划", description="规划")]
        manager1.create_iteration(
            iteration_id="iter_001",
            mode=WorkflowMode.MINIMAL,
            stages=stages
        )

        # 创建第二个管理器，应该能加载数据
        manager2 = StateManager(storage_dir=temp_dir)
        iteration = manager2.get_iteration("iter_001")

        assert iteration is not None
        assert iteration.iteration_id == "iter_001"

    def test_get_transitions(self, state_manager):
        """测试获取状态转换历史"""
        stages = [Stage(stage_id="P", name="规划", description="规划")]

        state_manager.create_iteration(
            iteration_id="iter_001",
            mode=WorkflowMode.MINIMAL,
            stages=stages
        )

        # 更新状态以产生转换记录
        state_manager.update_stage_status(
            "iter_001",
            "P",
            StageStatus.IN_PROGRESS
        )

        state_manager.update_stage_status(
            "iter_001",
            "P",
            StageStatus.COMPLETED
        )

        # 获取转换历史
        transitions = state_manager.get_transitions("iter_001")
        assert len(transitions) >= 2
