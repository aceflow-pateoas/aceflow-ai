"""
Base Workflow Class - 工作流基类

定义所有工作流类型的通用接口和行为。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from ..models import WorkflowType, Stage


@dataclass
class StageDefinition:
    """
    阶段定义

    定义工作流中的单个阶段的元数据。
    """
    stage_id: str
    name: str
    description: str
    checklist_template: str  # 模板文件路径
    estimated_hours: str = "未估算"
    deliverables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """
    验证结果

    用于阶段完成验证的结果。
    """
    valid: bool
    completed_items: List[str] = field(default_factory=list)
    missing_items: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    message: str = ""


class BaseWorkflow(ABC):
    """
    工作流基类

    所有工作流类型都必须继承此基类并实现抽象方法。
    """

    def __init__(self):
        self._stages_cache = None

    @property
    @abstractmethod
    def workflow_type(self) -> WorkflowType:
        """
        工作流类型

        Returns:
            WorkflowType枚举值
        """
        pass

    @property
    @abstractmethod
    def workflow_name(self) -> str:
        """
        工作流名称（中文）

        Returns:
            工作流的显示名称
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        工作流描述

        Returns:
            工作流的详细描述
        """
        pass

    @property
    @abstractmethod
    def estimated_duration(self) -> str:
        """
        预估工期

        Returns:
            预估完成时间（如 "3-5天"）
        """
        pass

    @abstractmethod
    def get_stage_definitions(self) -> List[StageDefinition]:
        """
        获取阶段定义列表

        Returns:
            阶段定义列表，定义工作流的所有阶段
        """
        pass

    def get_stages(self) -> List[Stage]:
        """
        获取阶段实例列表

        将StageDefinition转换为Stage模型实例。

        Returns:
            Stage实例列表
        """
        if self._stages_cache is not None:
            return self._stages_cache

        stage_defs = self.get_stage_definitions()
        stages = []

        for stage_def in stage_defs:
            stage = Stage(
                stage_id=stage_def.stage_id,
                name=stage_def.name,
                description=stage_def.description,
                deliverables=stage_def.deliverables,
                metadata={
                    'checklist_template': stage_def.checklist_template,
                    'estimated_hours': stage_def.estimated_hours,
                    **stage_def.metadata
                }
            )
            stages.append(stage)

        self._stages_cache = stages
        return stages

    @abstractmethod
    def supports_subtasks(self) -> bool:
        """
        是否支持子任务拆分

        Returns:
            True表示支持子任务，False表示不支持
        """
        pass

    def get_stage_template_path(self, stage_id: str) -> Optional[str]:
        """
        获取阶段模板路径

        Args:
            stage_id: 阶段ID

        Returns:
            模板文件路径，如果不存在则返回None
        """
        stage_defs = self.get_stage_definitions()
        for stage_def in stage_defs:
            if stage_def.stage_id == stage_id:
                return stage_def.checklist_template
        return None

    def validate_stage_completion(
        self,
        stage_id: str,
        checklist: Dict[str, bool]
    ) -> ValidationResult:
        """
        验证阶段是否完成

        默认实现：检查所有必须项是否完成。
        子类可以重写此方法实现自定义验证逻辑。

        Args:
            stage_id: 阶段ID
            checklist: 检查清单结果 {"项目名": True/False}

        Returns:
            ValidationResult验证结果
        """
        completed = [k for k, v in checklist.items() if v]
        missing = [k for k, v in checklist.items() if not v]

        # 默认验证：至少50%的项目完成
        completion_rate = len(completed) / len(checklist) if checklist else 0
        valid = completion_rate >= 0.5

        return ValidationResult(
            valid=valid,
            completed_items=completed,
            missing_items=missing,
            warnings=[] if valid else [f"完成率仅{completion_rate:.0%}，建议至少完成50%"],
            message=f"已完成 {len(completed)}/{len(checklist)} 项" if valid else "未达到最低完成标准"
        )

    def get_stage_by_id(self, stage_id: str) -> Optional[Stage]:
        """
        根据ID获取阶段

        Args:
            stage_id: 阶段ID

        Returns:
            Stage实例，如果不存在则返回None
        """
        stages = self.get_stages()
        for stage in stages:
            if stage.stage_id == stage_id:
                return stage
        return None

    def get_next_stage(self, current_stage_id: str) -> Optional[Stage]:
        """
        获取下一个阶段

        Args:
            current_stage_id: 当前阶段ID

        Returns:
            下一个阶段，如果已是最后阶段则返回None
        """
        stages = self.get_stages()
        for i, stage in enumerate(stages):
            if stage.stage_id == current_stage_id:
                if i + 1 < len(stages):
                    return stages[i + 1]
                else:
                    return None
        return None

    def get_workflow_summary(self) -> Dict[str, Any]:
        """
        获取工作流摘要信息

        Returns:
            包含工作流基本信息的字典
        """
        return {
            'type': self.workflow_type.value,
            'name': self.workflow_name,
            'description': self.description,
            'estimated_duration': self.estimated_duration,
            'total_stages': len(self.get_stage_definitions()),
            'supports_subtasks': self.supports_subtasks(),
            'stages': [
                {
                    'stage_id': stage_def.stage_id,
                    'name': stage_def.name,
                    'estimated_hours': stage_def.estimated_hours
                }
                for stage_def in self.get_stage_definitions()
            ]
        }
