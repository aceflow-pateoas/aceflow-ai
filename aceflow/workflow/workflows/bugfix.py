"""
Bug修复工作流 (Bugfix Workflow)

适用场景：快速修复线上Bug，不支持子任务拆分
典型周期：1-3天
"""

from typing import List
from ..models import WorkflowType
from .base import BaseWorkflow, StageDefinition


class BugfixWorkflow(BaseWorkflow):
    """Bug修复工作流 - 快速的5阶段修复流程，聚焦问题定位和验证"""

    @property
    def workflow_type(self) -> WorkflowType:
        """工作流类型：BUGFIX"""
        return WorkflowType.BUGFIX

    @property
    def workflow_name(self) -> str:
        """工作流名称"""
        return "Bug修复工作流"

    @property
    def description(self) -> str:
        """工作流描述"""
        return "快速Bug修复流程，包含问题分析、定位根因、修复实现、验证测试、发布说明5个阶段"

    @property
    def estimated_duration(self) -> str:
        """预计耗时"""
        return "1-3天"

    def supports_subtasks(self) -> bool:
        """是否支持子任务拆分 - Bug修复不支持"""
        return False

    def get_stage_definitions(self) -> List[StageDefinition]:
        """
        获取阶段定义列表

        5个阶段：
        1. analyze - 问题分析
        2. locate - 定位根因
        3. fix - 修复实现
        4. verify - 验证测试
        5. release - 发布说明
        """
        return [
            StageDefinition(
                stage_id="analyze",
                name="问题分析 (Problem Analysis)",
                description="复现Bug、收集信息、评估影响范围和优先级",
                checklist_template="workflows/bugfix/analyze.md",
                estimated_hours="1-2小时",
                deliverables=[
                    "Bug复现步骤",
                    "环境信息记录",
                    "错误日志/截图",
                    "影响评估报告",
                    "优先级标签"
                ],
                metadata={
                    "stage_type": "analysis",
                    "required_completion_rate": 0.8,
                    "can_skip": False,
                    "priority_levels": ["P0", "P1", "P2", "P3"]
                }
            ),
            StageDefinition(
                stage_id="locate",
                name="定位根因 (Root Cause Analysis)",
                description="通过调试和代码审查找到问题的根本原因",
                checklist_template="workflows/bugfix/locate.md",
                estimated_hours="2-4小时",
                deliverables=[
                    "问题代码位置",
                    "根因分析报告",
                    "修复方案设计",
                    "影响分析"
                ],
                metadata={
                    "stage_type": "diagnosis",
                    "required_completion_rate": 0.9,  # 定位要准确
                    "can_skip": False
                }
            ),
            StageDefinition(
                stage_id="fix",
                name="修复实现 (Fix Implementation)",
                description="编写修复代码、添加测试用例、本地验证",
                checklist_template="workflows/bugfix/fix.md",
                estimated_hours="2-6小时",
                deliverables=[
                    "修复代码",
                    "新增测试用例",
                    "本地验证结果",
                    "代码审查链接"
                ],
                metadata={
                    "stage_type": "implementation",
                    "required_completion_rate": 0.9,
                    "can_skip": False
                }
            ),
            StageDefinition(
                stage_id="verify",
                name="验证测试 (Verification & Testing)",
                description="全面测试修复效果，确保没有引入新问题",
                checklist_template="workflows/bugfix/verify.md",
                estimated_hours="1-3小时",
                deliverables=[
                    "测试报告",
                    "修复验证记录",
                    "回归测试结果",
                    "性能测试结果（如适用）"
                ],
                metadata={
                    "stage_type": "testing",
                    "required_completion_rate": 0.9,  # 验证要充分
                    "can_skip": False
                }
            ),
            StageDefinition(
                stage_id="release",
                name="发布说明 (Release Notes)",
                description="合并代码、更新文档、编写发布说明",
                checklist_template="workflows/bugfix/release.md",
                estimated_hours="0.5-1小时",
                deliverables=[
                    "代码合并记录",
                    "CHANGELOG条目",
                    "发布说明",
                    "版本标签",
                    "用户通知（如需要）"
                ],
                metadata={
                    "stage_type": "release",
                    "required_completion_rate": 0.8,
                    "can_skip": False,
                    "version_type": "patch"  # Bug修复通常是patch版本
                }
            )
        ]

    def validate_stage_completion(self, stage_id: str, checklist: dict) -> "ValidationResult":
        """
        验证阶段完成情况（覆盖基类方法）

        Bug修复工作流的验证更加严格，特别是定位、修复、验证阶段要求90%完成率
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
            # Bug修复的关键阶段提供额外警告
            if stage_id in ['locate', 'fix', 'verify']:
                warnings.append(
                    f"⚠️ {stage_def.name}是关键阶段，建议完成所有必须项"
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
