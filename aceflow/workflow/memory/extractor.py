"""
Memory Extractor v4.0 - Automatic Memory Extraction from Stage Outputs

从阶段输出中自动提取技术决策和经验教训:
- 集成 DecisionDetector 和 LessonExtractor
- 支持批量提取和单个提取
- 提供用户确认工作流
- 与 V4MemoryManager 无缝集成

设计原则:
- 不调用 LLM API，纯算法实现
- 提供详细的提取结果和置信度
- 支持 auto_record 参数控制自动记录
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from .v4_models import (
    TechDecision, Lesson,
    DecisionScope, LessonCategory,
    DecisionDetector, LessonExtractor
)
from .v4_manager import V4MemoryManager


@dataclass
class ExtractionResult:
    """记忆提取结果"""

    # 提取类型
    extraction_type: str  # "decision" or "lesson"

    # 检测结果
    detected: bool
    confidence: float

    # 提取的文本片段
    text_snippet: str

    # 检测详情
    detection_details: Dict[str, Any]

    # 如果已记录，存储记录的对象
    recorded_object: Optional[Any] = None  # TechDecision or Lesson

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'extraction_type': self.extraction_type,
            'detected': self.detected,
            'confidence': self.confidence,
            'text_snippet': self.text_snippet,
            'detection_details': self.detection_details,
            'metadata': self.metadata
        }

        if self.recorded_object:
            if hasattr(self.recorded_object, 'decision_id'):
                result['recorded_id'] = self.recorded_object.decision_id
            elif hasattr(self.recorded_object, 'lesson_id'):
                result['recorded_id'] = self.recorded_object.lesson_id

        return result


class MemoryExtractor:
    """
    v4.0 记忆提取器

    从阶段输出文本中自动提取技术决策和经验教训
    """

    def __init__(self, memory_manager: V4MemoryManager):
        """
        初始化记忆提取器

        Args:
            memory_manager: V4MemoryManager 实例
        """
        self.memory_manager = memory_manager

    # ==================== 批量提取 ====================

    def extract_from_stage_output(
        self,
        stage_output: str,
        work_item_id: str,
        stage_id: str,
        auto_record: bool = False,
        extract_decisions: bool = True,
        extract_lessons: bool = True
    ) -> Dict[str, Any]:
        """
        从阶段输出中提取记忆（批量）

        Args:
            stage_output: 阶段输出文本
            work_item_id: 工作项ID
            stage_id: 阶段ID
            auto_record: 是否自动记录（无需用户确认）
            extract_decisions: 是否提取技术决策
            extract_lessons: 是否提取经验教训

        Returns:
            {
                'decisions': List[ExtractionResult],
                'lessons': List[ExtractionResult],
                'summary': {
                    'total_decisions': int,
                    'total_lessons': int,
                    'high_confidence_count': int,
                    'recorded_count': int
                }
            }
        """
        results = {
            'decisions': [],
            'lessons': [],
            'summary': {
                'total_decisions': 0,
                'total_lessons': 0,
                'high_confidence_count': 0,
                'recorded_count': 0
            }
        }

        # 分段处理（按段落或句子分割）
        segments = self._segment_text(stage_output)

        # 提取决策
        if extract_decisions:
            for segment in segments:
                decision_result = self._extract_decision_from_segment(
                    segment, work_item_id, stage_id, auto_record
                )
                if decision_result:
                    results['decisions'].append(decision_result)
                    results['summary']['total_decisions'] += 1
                    if decision_result.confidence >= 0.8:
                        results['summary']['high_confidence_count'] += 1
                    if decision_result.recorded_object:
                        results['summary']['recorded_count'] += 1

        # 提取经验教训
        if extract_lessons:
            for segment in segments:
                lesson_result = self._extract_lesson_from_segment(
                    segment, work_item_id, stage_id, auto_record
                )
                if lesson_result:
                    results['lessons'].append(lesson_result)
                    results['summary']['total_lessons'] += 1
                    if lesson_result.confidence >= 0.8:
                        results['summary']['high_confidence_count'] += 1
                    if lesson_result.recorded_object:
                        results['summary']['recorded_count'] += 1

        return results

    # ==================== 单个提取 ====================

    def extract_decision(
        self,
        text: str,
        work_item_id: str,
        stage_id: str,
        auto_record: bool = False
    ) -> Optional[ExtractionResult]:
        """
        提取单个技术决策

        Args:
            text: 文本
            work_item_id: 工作项ID
            stage_id: 阶段ID
            auto_record: 是否自动记录

        Returns:
            ExtractionResult 或 None
        """
        return self._extract_decision_from_segment(text, work_item_id, stage_id, auto_record)

    def extract_lesson(
        self,
        text: str,
        work_item_id: str,
        stage_id: str,
        auto_record: bool = False
    ) -> Optional[ExtractionResult]:
        """
        提取单个经验教训

        Args:
            text: 文本
            work_item_id: 工作项ID
            stage_id: 阶段ID
            auto_record: 是否自动记录

        Returns:
            ExtractionResult 或 None
        """
        return self._extract_lesson_from_segment(text, work_item_id, stage_id, auto_record)

    # ==================== 用户确认工作流 ====================

    def confirm_and_record_decision(
        self,
        extraction_result: ExtractionResult,
        title: str,
        decision: str,
        reason: str,
        scope: DecisionScope = DecisionScope.LOCAL,
        alternatives: Optional[List[str]] = None,
        tech_stack: Optional[List[str]] = None,
        impact: str = "",
        related_decisions: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> TechDecision:
        """
        用户确认后记录技术决策

        Args:
            extraction_result: 提取结果
            title: 决策标题（用户提供或修改）
            decision: 决策内容
            reason: 决策理由
            ... (其他参数同 record_tech_decision)

        Returns:
            TechDecision 对象
        """
        work_item_id = extraction_result.metadata.get('work_item_id')
        stage_id = extraction_result.metadata.get('stage_id')

        tech_decision = self.memory_manager.record_tech_decision(
            title=title,
            decision=decision,
            reason=reason,
            scope=scope,
            alternatives=alternatives,
            tech_stack=tech_stack,
            impact=impact,
            work_item_id=work_item_id,
            stage_id=stage_id,
            related_decisions=related_decisions,
            tags=tags or [],
            importance=extraction_result.confidence,
            metadata={
                'extraction_confidence': extraction_result.confidence,
                'detection_details': extraction_result.detection_details
            }
        )

        # 更新提取结果
        extraction_result.recorded_object = tech_decision

        return tech_decision

    def confirm_and_record_lesson(
        self,
        extraction_result: ExtractionResult,
        title: str,
        content: str,
        category: LessonCategory,
        what_happened: str,
        what_learned: str,
        how_to_apply: str,
        applicability: str = "general",
        applicable_scenarios: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Lesson:
        """
        用户确认后记录经验教训

        Args:
            extraction_result: 提取结果
            title: 教训标题（用户提供或修改）
            content: 教训内容
            category: 分类
            what_happened: 发生了什么
            what_learned: 学到了什么
            how_to_apply: 如何应用
            ... (其他参数同 record_lesson)

        Returns:
            Lesson 对象
        """
        work_item_id = extraction_result.metadata.get('work_item_id')
        stage_id = extraction_result.metadata.get('stage_id')

        lesson = self.memory_manager.record_lesson(
            title=title,
            content=content,
            category=category,
            what_happened=what_happened,
            what_learned=what_learned,
            how_to_apply=how_to_apply,
            applicability=applicability,
            applicable_scenarios=applicable_scenarios,
            work_item_id=work_item_id,
            stage_id=stage_id,
            tags=tags or [],
            importance=extraction_result.confidence,
            metadata={
                'extraction_confidence': extraction_result.confidence,
                'detection_details': extraction_result.detection_details
            }
        )

        # 更新提取结果
        extraction_result.recorded_object = lesson

        return lesson

    # ==================== 辅助方法 ====================

    def _segment_text(self, text: str) -> List[str]:
        """
        分割文本为段落

        策略：
        1. 按双换行符分割（段落）
        2. 每个段落至少包含50个字符
        3. 过滤空段落

        Args:
            text: 原始文本

        Returns:
            段落列表
        """
        # 按双换行符或单换行符分割
        segments = text.split('\n\n')

        # 如果没有双换行符，尝试单换行符
        if len(segments) == 1:
            segments = text.split('\n')

        # 过滤和清理
        filtered_segments = []
        for segment in segments:
            segment = segment.strip()
            # 至少50个字符
            if len(segment) >= 50:
                filtered_segments.append(segment)

        # 如果没有足够长的段落，返回整个文本
        if not filtered_segments:
            return [text]

        return filtered_segments

    def _extract_decision_from_segment(
        self,
        segment: str,
        work_item_id: str,
        stage_id: str,
        auto_record: bool
    ) -> Optional[ExtractionResult]:
        """
        从单个文本段中提取技术决策

        Args:
            segment: 文本段
            work_item_id: 工作项ID
            stage_id: 阶段ID
            auto_record: 是否自动记录

        Returns:
            ExtractionResult 或 None
        """
        # 使用 DecisionDetector
        detection_result = DecisionDetector.detect(segment)

        if not detection_result or not detection_result.get('detected'):
            return None

        # 创建提取结果
        extraction_result = ExtractionResult(
            extraction_type='decision',
            detected=True,
            confidence=detection_result['confidence'],
            text_snippet=segment[:200],  # 前200字符
            detection_details=detection_result,
            metadata={
                'work_item_id': work_item_id,
                'stage_id': stage_id
            }
        )

        # 如果 auto_record=True，自动记录
        if auto_record:
            result = self.memory_manager.detect_and_record_decision(
                text=segment,
                work_item_id=work_item_id,
                stage_id=stage_id,
                auto_record=True
            )
            if result:
                _, decision_obj = result
                extraction_result.recorded_object = decision_obj

        return extraction_result

    def _extract_lesson_from_segment(
        self,
        segment: str,
        work_item_id: str,
        stage_id: str,
        auto_record: bool
    ) -> Optional[ExtractionResult]:
        """
        从单个文本段中提取经验教训

        Args:
            segment: 文本段
            work_item_id: 工作项ID
            stage_id: 阶段ID
            auto_record: 是否自动记录

        Returns:
            ExtractionResult 或 None
        """
        # 使用 LessonExtractor
        extraction_result_dict = LessonExtractor.extract(segment)

        if not extraction_result_dict or not extraction_result_dict.get('detected'):
            return None

        # 创建提取结果
        extraction_result = ExtractionResult(
            extraction_type='lesson',
            detected=True,
            confidence=extraction_result_dict['confidence'],
            text_snippet=segment[:200],
            detection_details=extraction_result_dict,
            metadata={
                'work_item_id': work_item_id,
                'stage_id': stage_id
            }
        )

        # 如果 auto_record=True，自动记录
        if auto_record:
            result = self.memory_manager.detect_and_record_lesson(
                text=segment,
                work_item_id=work_item_id,
                stage_id=stage_id,
                auto_record=True
            )
            if result:
                _, lesson_obj = result
                extraction_result.recorded_object = lesson_obj

        return extraction_result

    # ==================== 统计和报告 ====================

    def get_extraction_summary(
        self,
        extraction_results: Dict[str, Any]
    ) -> str:
        """
        生成提取摘要报告

        Args:
            extraction_results: extract_from_stage_output 的返回值

        Returns:
            Markdown 格式的摘要报告
        """
        summary = extraction_results['summary']
        decisions = extraction_results['decisions']
        lessons = extraction_results['lessons']

        report = "# 记忆提取摘要\n\n"

        # 统计信息
        report += "## 统计\n\n"
        report += f"- **技术决策**: {summary['total_decisions']} 个\n"
        report += f"- **经验教训**: {summary['total_lessons']} 个\n"
        report += f"- **高置信度**: {summary['high_confidence_count']} 个 (≥80%)\n"
        report += f"- **已记录**: {summary['recorded_count']} 个\n\n"

        # 决策列表
        if decisions:
            report += "## 检测到的技术决策\n\n"
            for i, decision in enumerate(decisions, 1):
                report += f"### 决策 {i} (置信度: {decision.confidence:.0%})\n\n"
                report += f"```\n{decision.text_snippet}\n```\n\n"
                if decision.detection_details.get('has_wide_impact'):
                    report += "- ✅ 影响范围广\n"
                if decision.detection_details.get('is_tech_selection'):
                    report += "- ✅ 技术选型\n"
                if decision.recorded_object:
                    report += f"- ✅ 已记录 (ID: {decision.recorded_object.decision_id})\n"
                else:
                    report += "- ⚠️ 待确认\n"
                report += "\n"

        # 经验列表
        if lessons:
            report += "## 检测到的经验教训\n\n"
            for i, lesson in enumerate(lessons, 1):
                report += f"### 经验 {i} (置信度: {lesson.confidence:.0%})\n\n"
                report += f"```\n{lesson.text_snippet}\n```\n\n"
                if lesson.detection_details.get('has_problem'):
                    report += "- ✅ 包含问题描述\n"
                if lesson.detection_details.get('has_solution'):
                    report += "- ✅ 包含解决方案\n"
                if lesson.recorded_object:
                    report += f"- ✅ 已记录 (ID: {lesson.recorded_object.lesson_id})\n"
                else:
                    report += "- ⚠️ 待确认\n"
                report += "\n"

        # 建议
        report += "## 下一步建议\n\n"
        pending_count = summary['total_decisions'] + summary['total_lessons'] - summary['recorded_count']
        if pending_count > 0:
            report += f"有 {pending_count} 个待确认的记忆，建议使用 `confirm_and_record_*` 方法记录。\n"
        else:
            report += "所有检测到的记忆已自动记录。\n"

        return report
