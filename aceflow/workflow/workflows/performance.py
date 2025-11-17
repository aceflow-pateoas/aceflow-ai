"""
性能排查工作流 (Performance Workflow)

适用场景：性能问题诊断和优化，不支持子任务拆分
典型周期：2-5天
"""

from typing import List
from ..models import WorkflowType
from .base import BaseWorkflow, StageDefinition


class PerformanceWorkflow(BaseWorkflow):
    """性能排查工作流 - 4阶段性能优化流程"""

    @property
    def workflow_type(self) -> WorkflowType:
        """工作流类型：PERFORMANCE"""
        return WorkflowType.PERFORMANCE

    @property
    def workflow_name(self) -> str:
        """工作流名称"""
        return "性能排查工作流"

    @property
    def description(self) -> str:
        """工作流描述"""
        return "系统化的性能优化流程，包含问题诊断、根因分析、性能优化、效果验证4个阶段"

    @property
    def estimated_duration(self) -> str:
        """预计耗时"""
        return "2-5天"

    def supports_subtasks(self) -> bool:
        """是否支持子任务拆分"""
        return False

    def get_stage_definitions(self) -> List[StageDefinition]:
        """获取阶段定义列表"""
        return [
            StageDefinition(
                stage_id="diagnose",
                name="问题诊断 (Problem Diagnosis)",
                description="复现性能问题，收集性能指标，建立基准数据",
                checklist_template="workflows/performance/diagnose.md",
                estimated_hours="4-8小时",
                deliverables=[
                    "性能问题描述",
                    "性能指标数据",
                    "复现步骤",
                    "基准数据"
                ],
                metadata={
                    "stage_type": "diagnosis",
                    "required_completion_rate": 0.85,
                    "can_skip": False,
                    "metrics": ["response_time", "throughput", "cpu", "memory"]
                }
            ),
            StageDefinition(
                stage_id="analyze",
                name="根因分析 (Root Cause Analysis)",
                description="使用profiling工具定位瓶颈，分析根本原因",
                checklist_template="workflows/performance/analyze.md",
                estimated_hours="6-12小时",
                deliverables=[
                    "Profiling报告",
                    "瓶颈分析",
                    "根因说明",
                    "优化方案"
                ],
                metadata={
                    "stage_type": "analysis",
                    "required_completion_rate": 0.9,
                    "can_skip": False,
                    "tools": ["profiler", "monitoring", "tracing"]
                }
            ),
            StageDefinition(
                stage_id="optimize",
                name="性能优化 (Performance Optimization)",
                description="实施优化方案，验证功能正确性",
                checklist_template="workflows/performance/optimize.md",
                estimated_hours="8-20小时",
                deliverables=[
                    "优化后的代码",
                    "测试结果",
                    "性能对比数据"
                ],
                metadata={
                    "stage_type": "optimization",
                    "required_completion_rate": 0.9,
                    "can_skip": False,
                    "techniques": ["caching", "indexing", "algorithm", "concurrency"]
                }
            ),
            StageDefinition(
                stage_id="verify",
                name="效果验证 (Performance Verification)",
                description="测试性能提升，量化优化效果，编写报告",
                checklist_template="workflows/performance/verify.md",
                estimated_hours="4-8小时",
                deliverables=[
                    "性能测试报告",
                    "优化效果总结",
                    "经验教训"
                ],
                metadata={
                    "stage_type": "verification",
                    "required_completion_rate": 0.85,
                    "can_skip": False,
                    "comparison_metrics": ["before_after", "improvement_rate"]
                }
            )
        ]
