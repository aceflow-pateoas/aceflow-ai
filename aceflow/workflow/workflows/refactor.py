"""
重构优化工作流 (Refactor Workflow)

适用场景：代码重构、架构优化、消除技术债，不支持子任务拆分
典型周期：3-7天
"""

from typing import List
from ..models import WorkflowType
from .base import BaseWorkflow, StageDefinition


class RefactorWorkflow(BaseWorkflow):
    """重构优化工作流 - 系统化的5阶段重构流程，聚焦代码质量提升"""

    @property
    def workflow_type(self) -> WorkflowType:
        """工作流类型：REFACTOR"""
        return WorkflowType.REFACTOR

    @property
    def workflow_name(self) -> str:
        """工作流名称"""
        return "重构优化工作流"

    @property
    def description(self) -> str:
        """工作流描述"""
        return "系统化的重构流程，包含评估分析、方案设计、重构实现、测试验证、文档更新5个阶段"

    @property
    def estimated_duration(self) -> str:
        """预计耗时"""
        return "3-7天"

    def supports_subtasks(self) -> bool:
        """是否支持子任务拆分 - 重构优化不支持"""
        return False

    def get_stage_definitions(self) -> List[StageDefinition]:
        """
        获取阶段定义列表

        5个阶段：
        1. assess - 评估分析
        2. plan - 方案设计
        3. refactor - 重构实现
        4. test - 测试验证
        5. document - 文档更新
        """
        return [
            StageDefinition(
                stage_id="assess",
                name="评估分析 (Assessment & Analysis)",
                description="分析需要重构的代码，评估收益和风险，明确重构目标",
                checklist_template="workflows/refactor/assess.md",
                estimated_hours="4-8小时",
                deliverables=[
                    "重构目标文档",
                    "目标代码清单",
                    "代码质量问题列表",
                    "收益评估报告",
                    "风险评估"
                ],
                metadata={
                    "stage_type": "analysis",
                    "required_completion_rate": 0.8,
                    "can_skip": False,
                    "metrics": ["complexity", "duplication", "coverage"]
                }
            ),
            StageDefinition(
                stage_id="plan",
                name="方案设计 (Refactoring Plan)",
                description="设计详细的重构方案，制定分步执行计划和测试策略",
                checklist_template="workflows/refactor/plan.md",
                estimated_hours="4-8小时",
                deliverables=[
                    "重构方案文档",
                    "分步执行计划",
                    "测试策略",
                    "回滚方案",
                    "影响分析"
                ],
                metadata={
                    "stage_type": "design",
                    "required_completion_rate": 0.85,  # 计划要更详细
                    "can_skip": False,
                    "refactoring_techniques": [
                        "Extract Method",
                        "Extract Class",
                        "Move Method",
                        "Simplify Conditional"
                    ]
                }
            ),
            StageDefinition(
                stage_id="refactor",
                name="重构实现 (Refactoring Implementation)",
                description="按计划执行重构，保持功能不变，小步前进频繁测试",
                checklist_template="workflows/refactor/refactor.md",
                estimated_hours="16-32小时",
                deliverables=[
                    "重构后的代码",
                    "Git提交历史（小步提交）",
                    "测试运行记录",
                    "代码审查链接"
                ],
                metadata={
                    "stage_type": "implementation",
                    "required_completion_rate": 0.9,  # 实施要严格
                    "can_skip": False,
                    "principles": [
                        "小步前进",
                        "频繁测试",
                        "保持功能",
                        "可回退"
                    ]
                }
            ),
            StageDefinition(
                stage_id="test",
                name="测试验证 (Testing & Verification)",
                description="全面测试重构结果，验证功能正确性和性能指标",
                checklist_template="workflows/refactor/test.md",
                estimated_hours="6-12小时",
                deliverables=[
                    "测试报告",
                    "代码覆盖率报告",
                    "性能对比报告",
                    "回归测试结果",
                    "问题清单（如有）"
                ],
                metadata={
                    "stage_type": "testing",
                    "required_completion_rate": 0.9,  # 测试要充分
                    "can_skip": False,
                    "test_types": [
                        "unit",
                        "integration",
                        "regression",
                        "performance"
                    ]
                }
            ),
            StageDefinition(
                stage_id="document",
                name="文档更新 (Documentation Update)",
                description="更新代码注释、API文档、CHANGELOG和技术决策记录",
                checklist_template="workflows/refactor/document.md",
                estimated_hours="2-4小时",
                deliverables=[
                    "更新的代码注释",
                    "更新的API文档",
                    "CHANGELOG条目",
                    "技术决策记录（ADR）",
                    "重构总结报告"
                ],
                metadata={
                    "stage_type": "documentation",
                    "required_completion_rate": 0.8,
                    "can_skip": False,
                    "doc_types": ["code_comments", "api_docs", "changelog", "adr"]
                }
            )
        ]

    def validate_stage_completion(self, stage_id: str, checklist: dict) -> "ValidationResult":
        """
        验证阶段完成情况（覆盖基类方法）

        重构工作流强调：
        - plan阶段要求85%（计划要详细）
        - refactor/test阶段要求90%（执行和验证要严格）
        - assess/document阶段要求80%
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

        # 空检查清单
        if not checklist:
            return ValidationResult(
                valid=False,
                completed_items=[],
                missing_items=[],
                warnings=["检查清单为空"],
                message="检查清单为空，无法验证完成情况"
            )

        # 计算完成率
        completed = [k for k, v in checklist.items() if v]
        missing = [k for k, v in checklist.items() if not v]
        completion_rate = len(completed) / len(checklist)

        # 获取要求的最低完成率
        required_rate = stage_def.metadata.get('required_completion_rate', 0.8)

        # 验证是否达标
        valid = completion_rate >= required_rate

        # 构建验证结果
        warnings = []
        if not valid:
            warnings.append(
                f"完成率 {completion_rate:.0%} 低于要求的 {required_rate:.0%}"
            )
            # 关键阶段提供额外建议
            if stage_id == "plan":
                warnings.append(
                    "⚠️ 方案设计是重构成功的关键，建议完善所有计划项"
                )
            elif stage_id in ["refactor", "test"]:
                warnings.append(
                    f"⚠️ {stage_def.name}阶段要求严格执行，建议完成所有必须项"
                )
        elif completion_rate < 1.0:
            warnings.append(
                f"尚有 {len(missing)} 项未完成"
            )

        return ValidationResult(
            valid=valid,
            completed_items=completed,
            missing_items=missing,
            warnings=warnings,
            message=f"已完成 {len(completed)}/{len(checklist)} 项 ({completion_rate:.0%})"
        )
