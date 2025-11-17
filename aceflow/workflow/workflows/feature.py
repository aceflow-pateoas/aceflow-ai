"""
功能开发工作流 (Feature Development Workflow)

适用场景：新功能开发，支持子任务拆分
典型周期：1-2周
"""

from typing import List
from ..models import WorkflowType
from .base import BaseWorkflow, StageDefinition


class FeatureWorkflow(BaseWorkflow):
    """功能开发工作流 - 完整的5阶段开发流程，支持子任务拆分"""

    @property
    def workflow_type(self) -> WorkflowType:
        """工作流类型：FEATURE"""
        return WorkflowType.FEATURE

    @property
    def workflow_name(self) -> str:
        """工作流名称"""
        return "功能开发工作流"

    @property
    def description(self) -> str:
        """工作流描述"""
        return "完整的功能开发流程，包含需求分析、设计、实现、测试、交付5个阶段，支持子任务拆分"

    @property
    def estimated_duration(self) -> str:
        """预计耗时"""
        return "1-2周"

    def supports_subtasks(self) -> bool:
        """是否支持子任务拆分"""
        return True

    def get_stage_definitions(self) -> List[StageDefinition]:
        """
        获取阶段定义列表

        5个阶段：
        1. requirement - 需求梳理
        2. design - 设计方案
        3. implementation - 编码实现
        4. testing - 功能测试
        5. delivery - 完成交付
        """
        return [
            StageDefinition(
                stage_id="requirement",
                name="需求梳理 (Requirement Analysis)",
                description="明确功能需求，定义接口和数据模型，识别技术方案",
                checklist_template="workflows/feature/requirement.md",
                estimated_hours="4-8小时",
                deliverables=[
                    "接口定义文档（API路径、入参、出参）",
                    "核心逻辑设计（伪代码或流程图）",
                    "技术方案确认（使用的库、框架、存储方案）",
                    "数据模型设计",
                    "潜在问题识别"
                ],
                metadata={
                    "stage_type": "analysis",
                    "required_completion_rate": 0.8,  # 至少完成80%的检查清单
                    "can_skip": False
                }
            ),
            StageDefinition(
                stage_id="design",
                name="设计方案 (Design Specification)",
                description="详细设计架构、接口、数据库Schema、错误处理和安全方案",
                checklist_template="workflows/feature/design.md",
                estimated_hours="6-12小时",
                deliverables=[
                    "系统架构设计（架构图、模块划分）",
                    "详细接口设计（包含边界情况）",
                    "数据库设计（表结构、索引、约束、迁移脚本）",
                    "错误处理方案",
                    "安全方案（认证、授权、加密、输入验证）"
                ],
                metadata={
                    "stage_type": "design",
                    "required_completion_rate": 0.8,
                    "can_skip": False
                }
            ),
            StageDefinition(
                stage_id="implementation",
                name="编码实现 (Implementation)",
                description="根据设计方案编写代码，遵循编码规范，编写单元测试",
                checklist_template="workflows/feature/implementation.md",
                estimated_hours="20-40小时",
                deliverables=[
                    "核心功能代码",
                    "单元测试（覆盖率 ≥ 70%）",
                    "代码注释和文档字符串",
                    "依赖管理（requirements.txt / package.json等）",
                    "本地测试验证"
                ],
                metadata={
                    "stage_type": "implementation",
                    "required_completion_rate": 0.9,  # 实现阶段要求更高
                    "can_skip": False
                }
            ),
            StageDefinition(
                stage_id="testing",
                name="功能测试 (Testing & QA)",
                description="执行单元测试、集成测试、手动测试，修复发现的Bug",
                checklist_template="workflows/feature/testing.md",
                estimated_hours="8-16小时",
                deliverables=[
                    "单元测试全部通过",
                    "集成测试完成",
                    "手动测试报告",
                    "边界情况测试结果",
                    "错误处理验证",
                    "Bug修复记录"
                ],
                metadata={
                    "stage_type": "testing",
                    "required_completion_rate": 0.9,
                    "can_skip": False
                }
            ),
            StageDefinition(
                stage_id="delivery",
                name="完成交付 (Delivery)",
                description="代码提交、文档更新、变更记录、部署说明、知识归档",
                checklist_template="workflows/feature/delivery.md",
                estimated_hours="2-4小时",
                deliverables=[
                    "代码提交到版本控制",
                    "README和API文档更新",
                    "CHANGELOG.md更新",
                    "部署说明文档",
                    "技术决策记录",
                    "经验教训总结"
                ],
                metadata={
                    "stage_type": "delivery",
                    "required_completion_rate": 0.8,
                    "can_skip": False
                }
            )
        ]

    def validate_stage_completion(self, stage_id: str, checklist: dict) -> "ValidationResult":
        """
        验证阶段完成情况（覆盖基类方法以实现自定义验证逻辑）

        Args:
            stage_id: 阶段ID
            checklist: 检查清单结果 {"item1": True, "item2": False, ...}

        Returns:
            ValidationResult: 验证结果
        """
        from .base import ValidationResult

        # 获取阶段定义
        stage_def = None
        for s in self.get_stage_definitions():
            if s.stage_id == stage_id:
                stage_def = s
                break

        if not stage_def:
            return ValidationResult(
                valid=False,
                message=f"未找到阶段: {stage_id}"
            )

        # 计算完成率
        if not checklist:
            return ValidationResult(
                valid=False,
                completed_items=[],
                missing_items=[],
                warnings=["检查清单为空"],
                message="检查清单为空，无法验证完成情况"
            )

        completed = [k for k, v in checklist.items() if v]
        missing = [k for k, v in checklist.items() if not v]
        completion_rate = len(completed) / len(checklist)

        # 获取该阶段要求的最低完成率
        required_rate = stage_def.metadata.get('required_completion_rate', 0.5)

        # 验证是否达标
        valid = completion_rate >= required_rate

        # 构建验证结果
        warnings = []
        if not valid:
            warnings.append(
                f"完成率 {completion_rate:.0%} 低于要求的 {required_rate:.0%}"
            )
        elif completion_rate < 1.0:
            warnings.append(
                f"尚有 {len(missing)} 项未完成，建议补充完整"
            )

        return ValidationResult(
            valid=valid,
            completed_items=completed,
            missing_items=missing,
            warnings=warnings,
            message=f"已完成 {len(completed)}/{len(checklist)} 项 ({completion_rate:.0%})"
        )
