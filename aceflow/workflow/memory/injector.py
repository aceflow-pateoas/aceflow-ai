"""
Memory Injector v4.0 - Automatic Memory Injection into Templates

自动将相关记忆注入到阶段模板中:
- 替换 {{project_memory}} 占位符
- 基于���关性筛选和排序记忆
- 格式化记忆为Markdown列表
- 与模板系统无缝集成

设计原则:
- 使用 MemoryInjectionContext 提供上下文
- 使用 RelevanceCalculator 和 MemoryFilter 进行筛选
- 支持灵活的格式化选项
- 不调用 LLM API，纯算法实现
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .v4_models import (
    MemoryInjectionContext,
    TechDecision, Lesson, DocumentRef,
    DecisionScope, LessonCategory,
    RelevanceScore
)
from .v4_manager import V4MemoryManager
from .models import Memory


@dataclass
class InjectionResult:
    """记忆注入结果"""

    # 注入的记忆数量
    v3_memories_count: int
    decisions_count: int
    lessons_count: int
    documents_count: int
    total_count: int

    # 注入的内容
    injected_content: str

    # 元数据
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'v3_memories_count': self.v3_memories_count,
            'decisions_count': self.decisions_count,
            'lessons_count': self.lessons_count,
            'documents_count': self.documents_count,
            'total_count': self.total_count,
            'injected_content': self.injected_content,
            'metadata': self.metadata
        }


class MemoryInjector:
    """
    v4.0 记忆注入器

    将相关记忆自动注入到阶段模板中
    """

    def __init__(self, memory_manager: V4MemoryManager):
        """
        初始化记忆注入器

        Args:
            memory_manager: V4MemoryManager 实例
        """
        self.memory_manager = memory_manager

    # ==================== 主要API ====================

    def inject_memories_into_template(
        self,
        template_content: str,
        context: MemoryInjectionContext,
        placeholder: str = "{{project_memory}}",
        include_v3_memories: bool = True,
        include_decisions: bool = True,
        include_lessons: bool = True,
        include_documents: bool = True
    ) -> Tuple[str, InjectionResult]:
        """
        将相关记忆注入到模板中

        Args:
            template_content: 模板内容
            context: 记忆注入上下文
            placeholder: 占位符（默认 "{{project_memory}}"）
            include_v3_memories: 是否包含v3.0记忆
            include_decisions: 是否包含技术决策
            include_lessons: 是否包含经验教训
            include_documents: 是否包含文档引用

        Returns:
            (注入后的模板内容, InjectionResult对象)
        """
        # 1. 召回相关记忆
        v3_memories = []
        decisions = []
        lessons = []
        documents = []

        if include_v3_memories:
            v3_memories_with_scores = self.memory_manager.recall_for_work_item(context)
            v3_memories = [memory for memory, score in v3_memories_with_scores]

        if include_decisions:
            decisions_with_scores = self.memory_manager.get_relevant_decisions(context)
            decisions = [decision for decision, score in decisions_with_scores]

        if include_lessons:
            lessons_with_scores = self.memory_manager.get_relevant_lessons(context)
            lessons = [lesson for lesson, score in lessons_with_scores]

        if include_documents:
            documents = self._get_relevant_documents(context)

        # 2. 格式化记忆内容
        injected_content = self._format_memories(
            v3_memories=v3_memories,
            decisions=decisions,
            lessons=lessons,
            documents=documents,
            context=context
        )

        # 3. 替换占位符
        injected_template = template_content.replace(placeholder, injected_content)

        # 4. 创建注入结果
        injection_result = InjectionResult(
            v3_memories_count=len(v3_memories),
            decisions_count=len(decisions),
            lessons_count=len(lessons),
            documents_count=len(documents),
            total_count=len(v3_memories) + len(decisions) + len(lessons) + len(documents),
            injected_content=injected_content,
            metadata={
                'work_item_id': context.work_item_id,
                'stage_id': context.stage_id,
                'max_memories': context.max_memories,
                'min_relevance': context.min_relevance
            }
        )

        return injected_template, injection_result

    # ==================== 记忆召回 ====================

    def _get_relevant_documents(
        self,
        context: MemoryInjectionContext
    ) -> List[DocumentRef]:
        """
        获取相关文档引用

        Args:
            context: 记���注入上下文

        Returns:
            文档引用列表
        """
        # 获取所有文档
        all_docs = self.memory_manager.list_document_refs()

        # 简单过滤：按work_item_id或tags匹配
        relevant_docs = []

        for doc in all_docs:
            # 匹配work_item_id
            if doc.work_item_id == context.work_item_id:
                relevant_docs.append(doc)
                continue

            # 匹配tags
            if context.search_tags:
                common_tags = set(doc.tags) & set(context.search_tags)
                if common_tags:
                    relevant_docs.append(doc)

        # 限制数量
        return relevant_docs[:context.max_memories]

    # ==================== 格式化 ====================

    def _format_memories(
        self,
        v3_memories: List[Memory],
        decisions: List[TechDecision],
        lessons: List[Lesson],
        documents: List[DocumentRef],
        context: MemoryInjectionContext
    ) -> str:
        """
        格式化记忆为Markdown内容

        Args:
            v3_memories: v3.0记忆列表
            decisions: 技术决策列表
            lessons: 经验教训列表
            documents: 文档引用列表
            context: 记忆注入上下文

        Returns:
            格式化后的Markdown字符串
        """
        if not any([v3_memories, decisions, lessons, documents]):
            return "# 项目记忆\n\n当前阶段没有相关的项目记忆。\n"

        parts = ["# 项目记忆\n"]
        parts.append(f"以下是与当前阶段（{context.stage_name}）相关的项目记忆：\n")

        # v3.0 记忆（通用）
        if v3_memories:
            parts.append("\n## 相关背景信息\n")
            for i, memory in enumerate(v3_memories, 1):
                parts.append(f"\n### {i}. {memory.type.value.upper()}\n")
                parts.append(f"{memory.content}\n")
                if memory.tags:
                    parts.append(f"**标签**: {', '.join(memory.tags)}\n")

        # 技术决策
        if decisions:
            parts.append("\n## 相关技术决策\n")
            for i, decision in enumerate(decisions, 1):
                parts.append(f"\n### {i}. {decision.title}\n")
                parts.append(f"**决策**: {decision.decision}\n\n")
                parts.append(f"**理由**: {decision.reason}\n\n")

                if decision.alternatives:
                    parts.append(f"**备选方案**: {', '.join(decision.alternatives)}\n\n")

                if decision.tech_stack:
                    parts.append(f"**技术栈**: {', '.join(decision.tech_stack)}\n\n")

                parts.append(f"**影响范围**: {decision.scope.value}\n\n")

                if decision.impact:
                    parts.append(f"**影响**: {decision.impact}\n\n")

        # 经验教训
        if lessons:
            parts.append("\n## 相关经验教训\n")
            for i, lesson in enumerate(lessons, 1):
                parts.append(f"\n### {i}. {lesson.title}\n")
                parts.append(f"**分类**: {lesson.category.value}\n\n")
                parts.append(f"**发生了什么**: {lesson.what_happened}\n\n")
                parts.append(f"**学到了什么**: {lesson.what_learned}\n\n")
                parts.append(f"**如何应用**: {lesson.how_to_apply}\n\n")

                if lesson.applicable_scenarios:
                    parts.append(f"**适用场景**: {', '.join(lesson.applicable_scenarios)}\n\n")

                if lesson.applied_count > 0:
                    parts.append(f"**已应用次数**: {lesson.applied_count}\n\n")

        # 文档引用
        if documents:
            parts.append("\n## 相关文档\n")
            for i, doc in enumerate(documents, 1):
                parts.append(f"\n### {i}. {doc.title}\n")
                parts.append(f"**类型**: {doc.document_type}\n\n")
                parts.append(f"**路径**: `{doc.path}`\n\n")

                if doc.section:
                    parts.append(f"**章节**: {doc.section}\n\n")

                parts.append(f"**引用原因**: {doc.reason}\n\n")

                if doc.key_points:
                    parts.append("**关键点**:\n")
                    for point in doc.key_points:
                        parts.append(f"- {point}\n")
                    parts.append("\n")

        return "".join(parts)

    # ==================== 统计和报告 ====================

    def get_injection_summary(
        self,
        context: MemoryInjectionContext
    ) -> Dict[str, Any]:
        """
        获取注入摘要（不实际注入）

        Args:
            context: 记忆注入上下文

        Returns:
            摘要信息字典
        """
        # 召回记忆
        v3_memories_with_scores = self.memory_manager.recall_for_work_item(context)
        decisions_with_scores = self.memory_manager.get_relevant_decisions(context)
        lessons_with_scores = self.memory_manager.get_relevant_lessons(context)
        documents = self._get_relevant_documents(context)

        # 统计信息
        summary = {
            'work_item_id': context.work_item_id,
            'stage_id': context.stage_id,
            'stage_name': context.stage_name,
            'counts': {
                'v3_memories': len(v3_memories_with_scores),
                'decisions': len(decisions_with_scores),
                'lessons': len(lessons_with_scores),
                'documents': len(documents),
                'total': (len(v3_memories_with_scores) +
                         len(decisions_with_scores) +
                         len(lessons_with_scores) +
                         len(documents))
            },
            'details': {
                'v3_memories': [
                    {
                        'type': memory.type.value,
                        'content_preview': memory.content[:100],
                        'relevance': score.total_score
                    }
                    for memory, score in v3_memories_with_scores
                ],
                'decisions': [
                    {
                        'title': decision.title,
                        'scope': decision.scope.value,
                        'relevance': score.total_score
                    }
                    for decision, score in decisions_with_scores
                ],
                'lessons': [
                    {
                        'title': lesson.title,
                        'category': lesson.category.value,
                        'applied_count': lesson.applied_count,
                        'relevance': score.total_score
                    }
                    for lesson, score in lessons_with_scores
                ],
                'documents': [
                    {
                        'title': doc.title,
                        'type': doc.document_type,
                        'path': doc.path
                    }
                    for doc in documents
                ]
            }
        }

        return summary

    def check_template_has_placeholder(
        self,
        template_content: str,
        placeholder: str = "{{project_memory}}"
    ) -> bool:
        """
        检查模板是否包含记忆占位符

        Args:
            template_content: 模板内容
            placeholder: 占位符

        Returns:
            True如果包含占位符，否则False
        """
        return placeholder in template_content
