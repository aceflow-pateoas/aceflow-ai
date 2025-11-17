"""
代码审查工作流 (Code Review Workflow)

适用场景：PR代码审查、质量把关，不支持子任务拆分
典型周期：1-2天
"""

from typing import List
from ..models import WorkflowType
from .base import BaseWorkflow, StageDefinition


class ReviewWorkflow(BaseWorkflow):
    """代码审查工作流 - 4阶段审查流程，确保代码质量"""

    @property
    def workflow_type(self) -> WorkflowType:
        """工作流类型：REVIEW"""
        return WorkflowType.REVIEW

    @property
    def workflow_name(self) -> str:
        """工作流名称"""
        return "代码审查工作流"

    @property
    def description(self) -> str:
        """工作流描述"""
        return "系统化的代码审查流程，包含审查准备、代码审查、反馈处理、审查完成4个阶段"

    @property
    def estimated_duration(self) -> str:
        """预计耗时"""
        return "1-2天"

    def supports_subtasks(self) -> bool:
        """是否支持子任务拆分 - 代码审查不支持"""
        return False

    def get_stage_definitions(self) -> List[StageDefinition]:
        """
        获取阶段定义列表

        4个阶段：
        1. prepare - 审查准备
        2. review - 代码审查
        3. address - 反馈处理
        4. complete - 审查完成
        """
        return [
            StageDefinition(
                stage_id="prepare",
                name="审查准备 (Review Preparation)",
                description="准备审查材料，创建PR，完成自查",
                checklist_template="workflows/review/prepare.md",
                estimated_hours="0.5-1小时",
                deliverables=[
                    "PR链接",
                    "变更说明",
                    "测试报告",
                    "审查清单",
                    "相关文档"
                ],
                metadata={
                    "stage_type": "preparation",
                    "required_completion_rate": 0.8,
                    "can_skip": False,
                    "pr_template_included": True
                }
            ),
            StageDefinition(
                stage_id="review",
                name="代码审查 (Code Review)",
                description="审查代码逻辑、质量、安全性、性能等方面",
                checklist_template="workflows/review/review.md",
                estimated_hours="1-3小时",
                deliverables=[
                    "审查评论",
                    "问题清单",
                    "审查结论（Approve/Request Changes/Comment）",
                    "建议改进"
                ],
                metadata={
                    "stage_type": "review",
                    "required_completion_rate": 0.85,  # 审查要仔细
                    "can_skip": False,
                    "review_dimensions": [
                        "correctness",
                        "quality",
                        "testing",
                        "performance",
                        "security",
                        "maintainability"
                    ],
                    "comment_types": ["blocking", "suggestion", "question", "praise"]
                }
            ),
            StageDefinition(
                stage_id="address",
                name="反馈处理 (Address Feedback)",
                description="处理审查反馈，修复问题，回复评论",
                checklist_template="workflows/review/address.md",
                estimated_hours="1-4小时",
                deliverables=[
                    "修复后的代码",
                    "回复评论",
                    "测试报告",
                    "变更说明"
                ],
                metadata={
                    "stage_type": "feedback_handling",
                    "required_completion_rate": 0.9,  # 必须处理所有阻塞性问题
                    "can_skip": False,
                    "feedback_categories": ["must_fix", "suggested", "discuss"]
                }
            ),
            StageDefinition(
                stage_id="complete",
                name="审查完成 (Review Completion)",
                description="合并代码，记录总结，分享经验",
                checklist_template="workflows/review/complete.md",
                estimated_hours="0.5-1小时",
                deliverables=[
                    "合并记录",
                    "审查总结",
                    "经验教训",
                    "知识分享（如适用）"
                ],
                metadata={
                    "stage_type": "completion",
                    "required_completion_rate": 0.8,
                    "can_skip": False,
                    "merge_strategies": ["merge_commit", "squash", "rebase"],
                    "metrics_tracked": ["review_cycle", "comments_count", "rounds"]
                }
            )
        ]

    def validate_stage_completion(self, stage_id: str, checklist: dict) -> "ValidationResult":
        """
        验证阶段完成情况（覆盖基类方法）

        代码审查工作流强调：
        - review阶段要求85%（审查要仔细）
        - address阶段要求90%（必须处理阻塞性问题）
        - prepare/complete阶段要求80%
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
            if stage_id == "review":
                warnings.append(
                    "⚠️ 代码审查需要仔细检查各个维度（正确性、质量、安全性等）"
                )
            elif stage_id == "address":
                warnings.append(
                    "⚠️ 必须处理所有阻塞性问题，确保代码质量达标"
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
