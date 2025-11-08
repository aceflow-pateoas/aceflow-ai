"""
测试核心数据模型

测试 aceflow.workflow.models 模块
"""

import pytest
from datetime import datetime
from aceflow.workflow.models import (
    WorkflowMode,
    StageStatus,
    IterationStatus,
    Stage,
    Iteration,
    StateTransition
)


class TestWorkflowMode:
    """测试工作流模式枚举"""

    def test_mode_values(self):
        """测试模式值"""
        assert WorkflowMode.MINIMAL.value == "minimal"
        assert WorkflowMode.STANDARD.value == "standard"
        assert WorkflowMode.COMPLETE.value == "complete"
        assert WorkflowMode.SMART.value == "smart"

    def test_mode_from_string(self):
        """测试从字符串创建模式"""
        mode = WorkflowMode("minimal")
        assert mode == WorkflowMode.MINIMAL


class TestStageStatus:
    """测试阶段状态枚举"""

    def test_status_values(self):
        """测试状态值"""
        assert StageStatus.PENDING.value == "pending"
        assert StageStatus.IN_PROGRESS.value == "in_progress"
        assert StageStatus.COMPLETED.value == "completed"
        assert StageStatus.SKIPPED.value == "skipped"
        assert StageStatus.FAILED.value == "failed"


class TestStage:
    """测试阶段数据模型"""

    def test_stage_creation(self):
        """测试创建阶段"""
        stage = Stage(
            stage_id="P1",
            name="需求分析",
            description="分析需求",
            tasks=["任务1", "任务2"],
            deliverables=["文档1"]
        )

        assert stage.stage_id == "P1"
        assert stage.name == "需求分析"
        assert stage.status == StageStatus.PENDING
        assert len(stage.tasks) == 2
        assert len(stage.deliverables) == 1

    def test_stage_to_dict(self):
        """测试阶段转字典"""
        stage = Stage(
            stage_id="P1",
            name="需求分析",
            description="分析需求"
        )

        data = stage.to_dict()

        assert data['stage_id'] == "P1"
        assert data['name'] == "需求分析"
        assert data['status'] == "pending"
        assert 'created_at' in data

    def test_stage_from_dict(self):
        """测试从字典创建阶段"""
        data = {
            'stage_id': "P1",
            'name': "需求分析",
            'description': "分析需求",
            'status': "completed",
            'tasks': ["任务1"],
            'deliverables': [],
            'metadata': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        stage = Stage.from_dict(data)

        assert stage.stage_id == "P1"
        assert stage.status == StageStatus.COMPLETED


class TestIteration:
    """测试迭代数据模型"""

    def test_iteration_creation(self):
        """测试创建迭代"""
        stages = [
            Stage(stage_id="P1", name="规划", description="规划阶段"),
            Stage(stage_id="D1", name="开发", description="开发阶段")
        ]

        iteration = Iteration(
            iteration_id="iter_001",
            mode=WorkflowMode.MINIMAL,
            stages=stages
        )

        assert iteration.iteration_id == "iter_001"
        assert iteration.mode == WorkflowMode.MINIMAL
        assert len(iteration.stages) == 2
        assert iteration.status == IterationStatus.IN_PROGRESS

    def test_iteration_current_stage(self):
        """测试当前阶段属性"""
        stages = [
            Stage(stage_id="P1", name="规划", description="规划阶段"),
            Stage(stage_id="D1", name="开发", description="开发阶段", status=StageStatus.IN_PROGRESS)
        ]

        iteration = Iteration(
            iteration_id="iter_001",
            mode=WorkflowMode.MINIMAL,
            stages=stages
        )

        # 第一个 in_progress 的阶段是当前阶段
        assert iteration.current_stage is not None
        assert iteration.current_stage.stage_id == "D1"

    def test_iteration_get_stage_by_id(self):
        """测试根据ID获取阶段"""
        stages = [
            Stage(stage_id="P1", name="规划", description="规划阶段"),
            Stage(stage_id="D1", name="开发", description="开发阶段")
        ]

        iteration = Iteration(
            iteration_id="iter_001",
            mode=WorkflowMode.MINIMAL,
            stages=stages
        )

        stage = iteration.get_stage_by_id("D1")
        assert stage is not None
        assert stage.name == "开发"

        # 不存在的阶段
        stage = iteration.get_stage_by_id("X1")
        assert stage is None

    def test_iteration_to_dict(self):
        """测试迭代转字典"""
        stages = [Stage(stage_id="P1", name="规划", description="规划")]

        iteration = Iteration(
            iteration_id="iter_001",
            mode=WorkflowMode.MINIMAL,
            stages=stages,
            metadata={"goal": "测试目标"}
        )

        data = iteration.to_dict()

        assert data['iteration_id'] == "iter_001"
        assert data['mode'] == "minimal"
        assert len(data['stages']) == 1
        assert data['metadata']['goal'] == "测试目标"

    def test_iteration_from_dict(self):
        """测试从字典创建迭代"""
        data = {
            'iteration_id': "iter_001",
            'mode': "standard",
            'status': "in_progress",
            'stages': [
                {
                    'stage_id': "P1",
                    'name': "规划",
                    'description': "规划阶段",
                    'status': "pending",
                    'tasks': [],
                    'deliverables': [],
                    'metadata': {},
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
            ],
            'metadata': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        iteration = Iteration.from_dict(data)

        assert iteration.iteration_id == "iter_001"
        assert iteration.mode == WorkflowMode.STANDARD
        assert len(iteration.stages) == 1


class TestStateTransition:
    """测试状态转换记录"""

    def test_transition_creation(self):
        """测试创建转换记录"""
        transition = StateTransition(
            from_status=StageStatus.PENDING,
            to_status=StageStatus.IN_PROGRESS,
            stage_id="P1",
            reason="开始工作"
        )

        assert transition.from_status == StageStatus.PENDING
        assert transition.to_status == StageStatus.IN_PROGRESS
        assert transition.stage_id == "P1"
        assert transition.reason == "开始工作"

    def test_transition_to_dict(self):
        """测试转换记录转字典"""
        transition = StateTransition(
            from_status=StageStatus.PENDING,
            to_status=StageStatus.COMPLETED,
            stage_id="P1"
        )

        data = transition.to_dict()

        assert data['from_status'] == "pending"
        assert data['to_status'] == "completed"
        assert 'timestamp' in data
