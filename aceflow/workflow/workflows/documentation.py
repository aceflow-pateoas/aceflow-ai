"""
文档编写工作流 (Documentation Workflow)

适用场景：编写用户文档、API文档、设计文档，不支持子任务拆分
典型周期：2-5天
"""

from typing import List
from ..models import WorkflowType
from .base import BaseWorkflow, StageDefinition


class DocumentationWorkflow(BaseWorkflow):
    """文档编写工作流 - 4阶段文档创建流程，确保文档质量"""

    @property
    def workflow_type(self) -> WorkflowType:
        """工作流类型：DOCUMENTATION"""
        return WorkflowType.DOCUMENTATION

    @property
    def workflow_name(self) -> str:
        """工作流名称"""
        return "文档编写工作流"

    @property
    def description(self) -> str:
        """工作流描述"""
        return "系统化的文档创建流程，包含文档规划、文档编写、文档审查、文档发布4个阶段"

    @property
    def estimated_duration(self) -> str:
        """预计耗时"""
        return "2-5天"

    def supports_subtasks(self) -> bool:
        """是否支持子任务拆分 - 文档编写不支持"""
        return False

    def get_stage_definitions(self) -> List[StageDefinition]:
        """
        获取阶段定义列表

        4个阶段：
        1. plan - 文档规划
        2. write - 文档编写
        3. review - 文档审查
        4. publish - 文档发布
        """
        return [
            StageDefinition(
                stage_id="plan",
                name="文档规划 (Documentation Planning)",
                description="确定文档目标、受众、大纲和素材",
                checklist_template="workflows/documentation/plan.md",
                estimated_hours="2-4小时",
                deliverables=[
                    "文档大纲",
                    "目标读者描述",
                    "参考资料清单",
                    "示例素材"
                ],
                metadata={
                    "stage_type": "planning",
                    "required_completion_rate": 0.8,
                    "can_skip": False,
                    "doc_types": [
                        "user_manual",
                        "api_docs",
                        "tutorial",
                        "design_doc",
                        "deployment_guide"
                    ]
                }
            ),
            StageDefinition(
                stage_id="write",
                name="文档编写 (Documentation Writing)",
                description="按照大纲编写文档内容，添加示例和图表",
                checklist_template="workflows/documentation/write.md",
                estimated_hours="8-20小时",
                deliverables=[
                    "完整的文档内容",
                    "代码示例",
                    "图表和截图",
                    "相关链接"
                ],
                metadata={
                    "stage_type": "writing",
                    "required_completion_rate": 0.85,  # 编写要完整
                    "can_skip": False,
                    "best_practices": [
                        "structure_clear",
                        "language_concise",
                        "examples_rich",
                        "visual_aids"
                    ]
                }
            ),
            StageDefinition(
                stage_id="review",
                name="文档审查 (Documentation Review)",
                description="审查文档质量，测试代码示例，检查格式",
                checklist_template="workflows/documentation/review.md",
                estimated_hours="2-6小时",
                deliverables=[
                    "审查报告",
                    "修订后的文档",
                    "测试记录"
                ],
                metadata={
                    "stage_type": "review",
                    "required_completion_rate": 0.85,
                    "can_skip": False,
                    "review_dimensions": [
                        "content_quality",
                        "readability",
                        "usability",
                        "format_compliance"
                    ]
                }
            ),
            StageDefinition(
                stage_id="publish",
                name="文档发布 (Documentation Publishing)",
                description="发布文档到站点，通知团队，建立反馈渠道",
                checklist_template="workflows/documentation/publish.md",
                estimated_hours="1-3小时",
                deliverables=[
                    "发布的文档链接",
                    "CHANGELOG条目",
                    "发布公告",
                    "团队通知记录"
                ],
                metadata={
                    "stage_type": "publishing",
                    "required_completion_rate": 0.8,
                    "can_skip": False,
                    "publishing_platforms": [
                        "github_pages",
                        "read_the_docs",
                        "docusaurus",
                        "mkdocs"
                    ]
                }
            )
        ]

    def validate_stage_completion(self, stage_id: str, checklist: dict) -> "ValidationResult":
        """
        验证阶段完成情况（覆盖基类方法）

        文档编写工作流强调：
        - write/review阶段要求85%（内容要完整）
        - plan/publish阶段要求80%
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
            if stage_id == "write":
                warnings.append(
                    "⚠️ 文档编写要确保内容完整，所有章节都要覆盖"
                )
            elif stage_id == "review":
                warnings.append(
                    "⚠️ 文档审查要仔细检查准确性和可用性"
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
