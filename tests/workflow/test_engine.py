"""
测试工作流引擎

测试 aceflow.workflow.core.engine.WorkflowEngine
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from aceflow.workflow.core.engine import WorkflowEngine
from aceflow.workflow.core.state import StateManager
from aceflow.workflow.models import WorkflowMode, StageStatus
from aceflow.workflow.modes.minimal import MinimalWorkflow
from aceflow.workflow.modes.standard import StandardWorkflow
from aceflow.workflow.modes.complete import CompleteWorkflow


class TestWorkflowEngine:
    """测试工作流引擎"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def engine(self, temp_dir):
        """创建工作流引擎"""
        engine = WorkflowEngine(project_id="test_engine")
        engine.state_manager.state_dir = temp_dir

        # 注册工作流模式实现
        engine.register_mode_implementation(WorkflowMode.MINIMAL, MinimalWorkflow())
        engine.register_mode_implementation(WorkflowMode.STANDARD, StandardWorkflow())
        engine.register_mode_implementation(WorkflowMode.COMPLETE, CompleteWorkflow())

        return engine

    def test_engine_creation(self, engine):
        """测试引擎创建"""
        assert engine is not None
        assert engine.project_id == "test_engine"
        assert engine.state_manager is not None

    def test_initialize_minimal_mode(self, engine):
        """测试初始化 Minimal 模式"""
        result = engine.initialize(mode="minimal", metadata={"goal": "测试"})

        assert result['status'] == 'initialized'
        assert result['mode'] == 'minimal'
        assert 'iteration_id' in result
        assert result['total_stages'] > 0
        assert 'current_stage' in result

    def test_initialize_standard_mode(self, engine):
        """测试初始化 Standard 模式"""
        result = engine.initialize(mode="standard")

        assert result['status'] == 'initialized'
        assert result['mode'] == 'standard'
        assert result['total_stages'] >= 5  # Standard 模式有 5 个阶段

    def test_initialize_complete_mode(self, engine):
        """测试初始化 Complete 模式"""
        result = engine.initialize(mode="complete")

        assert result['status'] == 'initialized'
        assert result['mode'] == 'complete'
        assert result['total_stages'] >= 8  # Complete 模式有 8 个阶段

    def test_get_status(self, engine):
        """测试获取状态"""
        # 初始化工作流
        engine.initialize(mode="minimal")

        # 获取状态
        status = engine.get_status()

        assert status is not None
        assert status['status'] == 'active'
        assert 'iteration_id' in status
        assert 'mode' in status
        assert 'current_stage' in status

    def test_advance_stage(self, engine):
        """测试推进阶段"""
        # 初始化工作流
        init_result = engine.initialize(mode="minimal")
        first_stage = init_result['current_stage']['stage_id']

        # 推进到下一阶段
        advance_result = engine.advance()

        assert advance_result['success'] is True
        assert 'current_stage' in advance_result

        # 验证确实推进了
        new_stage = advance_result['current_stage']
        if new_stage:
            assert new_stage['stage_id'] != first_stage

    def test_update_progress(self, engine):
        """测试更新进度"""
        # 初始化工作流
        engine.initialize(mode="minimal")

        # 更新进度
        result = engine.update_progress(progress=0.5, metadata={"note": "半完成"})

        assert result['success'] is True
        assert 'current_stage' in result
        # 进度信息在 current_stage 中
        assert result['current_stage']['progress'] == 0.5

    def test_rollback_stage(self, engine):
        """测试回滚阶段"""
        # 初始化工作流
        engine.initialize(mode="minimal")

        # 推进到下一阶段
        engine.advance()

        # 回滚
        result = engine.rollback()

        assert result['success'] is True
        assert 'current_stage' in result

    def test_validate_state(self, engine):
        """测试状态验证"""
        # 初始化工作流
        engine.initialize(mode="minimal")

        # 验证状态
        validation = engine.validate()

        assert validation is not None
        assert 'valid' in validation
        assert validation['valid'] is True

    def test_get_history(self, engine):
        """测试获取历史"""
        # 初始化工作流
        engine.initialize(mode="minimal")

        # 推进几个阶段产生历史
        engine.advance()

        # 获取历史
        history = engine.get_history(limit=5)

        assert history is not None
        assert len(history) > 0

    def test_mode_registration(self, temp_dir):
        """测试模式注册"""
        engine = WorkflowEngine(project_id="test_registration")
        engine.state_manager.state_dir = temp_dir

        # 注册模式
        minimal_mode = MinimalWorkflow()
        engine.register_mode_implementation(WorkflowMode.MINIMAL, minimal_mode)

        # 验证可以使用注册的模式
        result = engine.initialize(mode="minimal")
        assert result['mode'] == 'minimal'

    def test_invalid_mode(self, engine):
        """测试无效模式"""
        # 尝试使用未注册的 smart 模式
        with pytest.raises(ValueError):
            engine.initialize(mode="smart")
