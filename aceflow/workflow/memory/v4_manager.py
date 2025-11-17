"""
Memory Manager v4.0 - Enhanced Memory Management

扩展v3.0 MemoryManager，添加：
- 结构化记忆类型（TechDecision, Lesson, DocumentRef）
- 自动检测和提取（DecisionDetector, LessonExtractor）
- 基于相关性的智能召回（RelevanceCalculator）
- 简化的存储路径（.aceflow/memory/memories.json）

设计原则：
- 向后兼容v3.0 MemoryManager
- 不调用LLM API，纯算法实现
- 提供用户确认机制（auto_record参数）
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import json
import uuid

from .manager import MemoryManager
from .models import Memory, MemoryType, MemoryPriority
from .v4_models import (
    TechDecision, Lesson, DocumentRef,
    DecisionScope, LessonCategory,
    MemoryInjectionContext, RelevanceScore,
    DecisionDetector, LessonExtractor,
    V4MemoryType
)
from .relevance import RelevanceCalculator, MemoryFilter


class V4MemoryManager(MemoryManager):
    """
    v4.0 增强记忆管理器

    扩展功能：
    - 结构化决策和经验存储
    - 自动检测技术决策和经验教训
    - 基于相关性的智能召回
    - 文档引用追踪
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        初始化v4.0记忆管理器

        Args:
            storage_path: 存储文件路径，默认为 .aceflow/memory/memories.json
        """
        # 简化存储路径（per user suggestion）
        if storage_path is None:
            storage_path = Path.cwd() / ".aceflow" / "memory" / "memories.json"

        super().__init__(storage_path)

        # v4.0 components
        self.relevance_calculator = RelevanceCalculator()
        self.memory_filter = MemoryFilter(self.relevance_calculator)

        # v4.0 storage paths (separate files for structured memories)
        self.v4_storage_dir = storage_path.parent
        self.decisions_file = self.v4_storage_dir / "decisions.json"
        self.lessons_file = self.v4_storage_dir / "lessons.json"
        self.documents_file = self.v4_storage_dir / "documents.json"

        # v4.0 在内存中缓存
        self.decisions: Dict[str, TechDecision] = {}
        self.lessons: Dict[str, Lesson] = {}
        self.documents: Dict[str, DocumentRef] = {}

        # 加载v4.0数据
        self._load_v4_data()

    # ==================== v4.0 TechDecision Management ====================

    def record_tech_decision(
        self,
        title: str,
        decision: str,
        reason: str,
        scope: DecisionScope = DecisionScope.LOCAL,
        alternatives: Optional[List[str]] = None,
        tech_stack: Optional[List[str]] = None,
        impact: str = "",
        work_item_id: Optional[str] = None,
        stage_id: Optional[str] = None,
        related_decisions: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TechDecision:
        """
        记录技术决策（v4.0）

        Args:
            title: 决策标题
            decision: 决策内容
            reason: 决策理由
            scope: 影响范围
            alternatives: 备选方案
            tech_stack: 涉及技术栈
            impact: 影响分析
            work_item_id: 关联工作项ID
            stage_id: 关联阶段ID
            related_decisions: 相关决策ID列表
            tags: 标签
            importance: 重要性 (0-1)
            metadata: 附加元数据

        Returns:
            TechDecision对象
        """
        decision_id = f"dec_{uuid.uuid4().hex[:8]}"

        tech_decision = TechDecision(
            decision_id=decision_id,
            title=title,
            decision=decision,
            reason=reason,
            scope=scope,
            alternatives=alternatives or [],
            tech_stack=tech_stack or [],
            impact=impact,
            work_item_id=work_item_id,
            stage_id=stage_id,
            related_decisions=related_decisions or [],
            tags=tags or [],
            importance=importance,
            created_at=datetime.now(),
            created_by="user",
            metadata=metadata or {}
        )

        # 存储到v4.0缓存
        self.decisions[decision_id] = tech_decision

        # 同时创建v3.0 Memory对象（向后兼容）
        self._create_v3_memory_for_decision(tech_decision)

        # 持久化
        self._save_decisions()

        return tech_decision

    def detect_and_record_decision(
        self,
        text: str,
        work_item_id: Optional[str] = None,
        stage_id: Optional[str] = None,
        auto_record: bool = False
    ) -> Optional[Tuple[Dict[str, Any], Optional[TechDecision]]]:
        """
        检测并记录技术决策（v4.0）

        Args:
            text: 待检测文本
            work_item_id: 关联工作项ID
            stage_id: 关联阶段ID
            auto_record: 是否自动记录（无需用户确认）

        Returns:
            (检测结果, TechDecision对象或None)
            - 检测结果包含detected、confidence、has_wide_impact等
            - 如果auto_record=True且检测成功，返回TechDecision对象
            - 如果auto_record=False，返回None（需用户确认后调用record_tech_decision）
        """
        detection_result = DecisionDetector.detect(text)

        if not detection_result or not detection_result.get('detected'):
            return None

        # 如果auto_record=False，返回检测结果供用户确认
        if not auto_record:
            return (detection_result, None)

        # auto_record=True，自动记录
        # 提取决策信息（简化版，实际可能需要更复杂的提取）
        decision_obj = self.record_tech_decision(
            title=f"Auto-detected decision from {stage_id or 'unknown'}",
            decision=text[:200],  # 截取前200字符作为决策内容
            reason="Auto-detected from stage output",
            scope=DecisionScope.ARCHITECTURE if detection_result['has_wide_impact'] else DecisionScope.LOCAL,
            tech_stack=[],  # 需要更复杂的提取逻辑
            impact=f"Confidence: {detection_result['confidence']}",
            work_item_id=work_item_id,
            stage_id=stage_id,
            tags=["auto-detected"],
            importance=detection_result['confidence'],
            metadata={'detection_result': detection_result}
        )

        return (detection_result, decision_obj)

    def get_decision(self, decision_id: str) -> Optional[TechDecision]:
        """获取技术决策（v4.0）"""
        return self.decisions.get(decision_id)

    def list_decisions(
        self,
        work_item_id: Optional[str] = None,
        scope: Optional[DecisionScope] = None,
        min_importance: float = 0.0
    ) -> List[TechDecision]:
        """
        列出技术决策（v4.0）

        Args:
            work_item_id: 过滤工作项ID
            scope: 过滤影响范围
            min_importance: 最低重要性

        Returns:
            TechDecision列表
        """
        decisions = list(self.decisions.values())

        # 过滤
        if work_item_id:
            decisions = [d for d in decisions if d.work_item_id == work_item_id]

        if scope:
            decisions = [d for d in decisions if d.scope == scope]

        if min_importance > 0:
            decisions = [d for d in decisions if d.importance >= min_importance]

        # 按重要性和创建时间排序
        decisions.sort(key=lambda d: (d.importance, d.created_at), reverse=True)

        return decisions

    # ==================== v4.0 Lesson Management ====================

    def record_lesson(
        self,
        title: str,
        content: str,
        category: LessonCategory,
        what_happened: str,
        what_learned: str,
        how_to_apply: str,
        applicability: str = "general",
        applicable_scenarios: Optional[List[str]] = None,
        work_item_id: Optional[str] = None,
        stage_id: Optional[str] = None,
        issue_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Lesson:
        """
        记录经验教训（v4.0）

        Args:
            title: 教训标题
            content: 教训内容
            category: 分类
            what_happened: 发生了什么
            what_learned: 学到了什么
            how_to_apply: 如何应用
            applicability: 适用性 (general/specific)
            applicable_scenarios: 适用场景
            work_item_id: 关联工作项ID
            stage_id: 关联阶段ID
            issue_id: 关联问题ID
            tags: 标签
            importance: 重要性 (0-1)
            metadata: 附加元数据

        Returns:
            Lesson对象
        """
        lesson_id = f"lesson_{uuid.uuid4().hex[:8]}"

        lesson = Lesson(
            lesson_id=lesson_id,
            title=title,
            content=content,
            category=category,
            what_happened=what_happened,
            what_learned=what_learned,
            how_to_apply=how_to_apply,
            applicability=applicability,
            applicable_scenarios=applicable_scenarios or [],
            work_item_id=work_item_id,
            stage_id=stage_id,
            issue_id=issue_id,
            tags=tags or [],
            importance=importance,
            created_at=datetime.now(),
            applied_count=0,
            metadata=metadata or {}
        )

        # 存储到v4.0缓存
        self.lessons[lesson_id] = lesson

        # 同时创建v3.0 Memory对象（向后兼容）
        self._create_v3_memory_for_lesson(lesson)

        # 持久化
        self._save_lessons()

        return lesson

    def detect_and_record_lesson(
        self,
        text: str,
        work_item_id: Optional[str] = None,
        stage_id: Optional[str] = None,
        auto_record: bool = False
    ) -> Optional[Tuple[Dict[str, Any], Optional[Lesson]]]:
        """
        检测并记录经验教训（v4.0）

        Args:
            text: 待检测文本
            work_item_id: 关联工作项ID
            stage_id: 关联阶段ID
            auto_record: 是否自动记录

        Returns:
            (检测结果, Lesson对象或None)
        """
        extraction_result = LessonExtractor.extract(text)

        if not extraction_result or not extraction_result.get('detected'):
            return None

        # 如果auto_record=False，返回检测结果供用户确认
        if not auto_record:
            return (extraction_result, None)

        # auto_record=True，自动记录
        lesson_obj = self.record_lesson(
            title=f"Auto-extracted lesson from {stage_id or 'unknown'}",
            content=text[:200],
            category=LessonCategory.TECHNICAL,  # 默认技术类
            what_happened=text[:100] if extraction_result['has_problem'] else "",
            what_learned=text[:100],
            how_to_apply="See content for details",
            applicability="general" if extraction_result.get('is_complete') else "specific",
            work_item_id=work_item_id,
            stage_id=stage_id,
            tags=["auto-extracted"],
            importance=extraction_result['confidence'],
            metadata={'extraction_result': extraction_result}
        )

        return (extraction_result, lesson_obj)

    def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """获取经验教训（v4.0）"""
        return self.lessons.get(lesson_id)

    def list_lessons(
        self,
        category: Optional[LessonCategory] = None,
        applicability: Optional[str] = None,
        min_importance: float = 0.0
    ) -> List[Lesson]:
        """
        列出经验教训（v4.0）

        Args:
            category: 过滤类别
            applicability: 过滤适用性 (general/specific)
            min_importance: 最低重要性

        Returns:
            Lesson列表
        """
        lessons = list(self.lessons.values())

        # 过滤
        if category:
            lessons = [l for l in lessons if l.category == category]

        if applicability:
            lessons = [l for l in lessons if l.applicability == applicability]

        if min_importance > 0:
            lessons = [l for l in lessons if l.importance >= min_importance]

        # 按重要性、应用次数、创建时间排序
        lessons.sort(
            key=lambda l: (l.importance, l.applied_count, l.created_at),
            reverse=True
        )

        return lessons

    def increment_lesson_applied_count(self, lesson_id: str) -> bool:
        """
        增加经验应用次数（v4.0）

        Args:
            lesson_id: 经验ID

        Returns:
            是否成功
        """
        lesson = self.lessons.get(lesson_id)
        if not lesson:
            return False

        lesson.applied_count += 1
        self._save_lessons()
        return True

    # ==================== v4.0 DocumentRef Management ====================

    def record_document_ref(
        self,
        title: str,
        document_type: str,
        path: str,
        section: Optional[str] = None,
        reason: str = "",
        key_points: Optional[List[str]] = None,
        work_item_id: Optional[str] = None,
        related_memories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentRef:
        """
        记录文档引用（v4.0）

        Args:
            title: 文档标题
            document_type: 文档类型 (api/design/readme/etc.)
            path: 文档路径
            section: 章节
            reason: 引用原因
            key_points: 关键点
            work_item_id: 关联工作项ID
            related_memories: 相关记忆ID列表
            tags: 标签
            metadata: 附加元数据

        Returns:
            DocumentRef对象
        """
        ref_id = f"ref_{uuid.uuid4().hex[:8]}"

        doc_ref = DocumentRef(
            ref_id=ref_id,
            title=title,
            document_type=document_type,
            path=path,
            section=section,
            reason=reason,
            key_points=key_points or [],
            work_item_id=work_item_id,
            related_memories=related_memories or [],
            tags=tags or [],
            created_at=datetime.now(),
            last_verified=None,
            metadata=metadata or {}
        )

        # 存储到v4.0缓存
        self.documents[ref_id] = doc_ref

        # 持久化
        self._save_documents()

        return doc_ref

    def get_document_ref(self, ref_id: str) -> Optional[DocumentRef]:
        """获取文档引用（v4.0）"""
        return self.documents.get(ref_id)

    def list_document_refs(
        self,
        work_item_id: Optional[str] = None,
        document_type: Optional[str] = None
    ) -> List[DocumentRef]:
        """
        列出文档引用（v4.0）

        Args:
            work_item_id: 过滤工作项ID
            document_type: 过滤文档类型

        Returns:
            DocumentRef列表
        """
        docs = list(self.documents.values())

        # 过滤
        if work_item_id:
            docs = [d for d in docs if d.work_item_id == work_item_id]

        if document_type:
            docs = [d for d in docs if d.document_type == document_type]

        # 按创建时间排序
        docs.sort(key=lambda d: d.created_at, reverse=True)

        return docs

    # ==================== v4.0 Smart Recall ====================

    def recall_for_work_item(
        self,
        context: MemoryInjectionContext
    ) -> List[Tuple[Memory, RelevanceScore]]:
        """
        为工作项召回相关记忆（v4.0智能召回）

        Args:
            context: 记忆注入上下文

        Returns:
            (记忆, 相关性评分)元组列表，按相关性降序排列
        """
        # 提取关键词和标签
        if not context.search_keywords:
            context.extract_keywords()
        if not context.search_tags:
            context.extract_tags()

        # 获取所有v3.0记忆
        all_memories = self.store.get_all()

        # 使用MemoryFilter筛选和排序
        ranked_memories = self.memory_filter.filter_and_rank(all_memories, context)

        return ranked_memories

    def get_relevant_decisions(
        self,
        context: MemoryInjectionContext
    ) -> List[Tuple[TechDecision, RelevanceScore]]:
        """
        获取相关技术决策（v4.0）

        Args:
            context: 记忆注入上下文

        Returns:
            (TechDecision, 相关性评分)元组列表
        """
        # 提取关键词和标签
        if not context.search_keywords:
            context.extract_keywords()
        if not context.search_tags:
            context.extract_tags()

        # 计算每个决策的相关性
        scored_decisions = []
        for decision in self.decisions.values():
            score = self.relevance_calculator.calculate_for_v4_decision(decision, context)

            # 应用最低相关性阈值
            if score.total_score >= context.min_relevance:
                scored_decisions.append((decision, score))

        # 按总分降序排序
        scored_decisions.sort(key=lambda x: x[1].total_score, reverse=True)

        # 限制数量
        return scored_decisions[:context.max_memories]

    def get_relevant_lessons(
        self,
        context: MemoryInjectionContext
    ) -> List[Tuple[Lesson, RelevanceScore]]:
        """
        获取相关经验教训（v4.0）

        Args:
            context: 记忆注入上下文

        Returns:
            (Lesson, 相关性评分)元组列表
        """
        # 提取关键词和标签
        if not context.search_keywords:
            context.extract_keywords()
        if not context.search_tags:
            context.extract_tags()

        # 计算每个经验的相关性
        scored_lessons = []
        for lesson in self.lessons.values():
            score = self.relevance_calculator.calculate_for_v4_lesson(lesson, context)

            # 应用最低相关性阈值
            if score.total_score >= context.min_relevance:
                scored_lessons.append((lesson, score))

        # 按总分降序排序
        scored_lessons.sort(key=lambda x: x[1].total_score, reverse=True)

        # 限制数量
        return scored_lessons[:context.max_memories]

    # ==================== v4.0 Statistics ====================

    def get_v4_statistics(self) -> Dict[str, Any]:
        """
        获取v4.0统计信息

        Returns:
            统计信息字典
        """
        return {
            'total_decisions': len(self.decisions),
            'total_lessons': len(self.lessons),
            'total_documents': len(self.documents),
            'decisions_by_scope': self._count_decisions_by_scope(),
            'lessons_by_category': self._count_lessons_by_category(),
            'lessons_applied': sum(l.applied_count for l in self.lessons.values()),
            'general_lessons': len([l for l in self.lessons.values() if l.applicability == 'general']),
            'v3_memories': len(self.store.get_all())
        }

    def _count_decisions_by_scope(self) -> Dict[str, int]:
        """统计决策按影响范围分布"""
        counts = {}
        for decision in self.decisions.values():
            scope = decision.scope.value
            counts[scope] = counts.get(scope, 0) + 1
        return counts

    def _count_lessons_by_category(self) -> Dict[str, int]:
        """统计经验按类别分布"""
        counts = {}
        for lesson in self.lessons.values():
            category = lesson.category.value
            counts[category] = counts.get(category, 0) + 1
        return counts

    # ==================== v3.0 Compatibility Helpers ====================

    def _create_v3_memory_for_decision(self, decision: TechDecision) -> Memory:
        """
        为TechDecision创建对应的v3.0 Memory对象（向后兼容）

        Args:
            decision: TechDecision对象

        Returns:
            Memory对象
        """
        memory_id = f"v3_{decision.decision_id}"

        content = f"决策: {decision.title}\n"
        content += f"内容: {decision.decision}\n"
        content += f"理由: {decision.reason}\n"
        content += f"影响: {decision.impact}"

        memory = Memory(
            memory_id=memory_id,
            type=MemoryType.DECISION,
            content=content,
            priority=self._importance_to_priority(decision.importance),
            iteration_id=decision.work_item_id,
            stage_id=decision.stage_id,
            tags=decision.tags + [decision.scope.value],
            metadata={
                'v4_type': 'tech_decision',
                'v4_id': decision.decision_id,
                'tech_stack': decision.tech_stack,
                'alternatives': decision.alternatives
            }
        )

        self.store.add(memory)
        return memory

    def _create_v3_memory_for_lesson(self, lesson: Lesson) -> Memory:
        """
        为Lesson创建对应的v3.0 Memory对象（向后兼容）

        Args:
            lesson: Lesson对象

        Returns:
            Memory对象
        """
        memory_id = f"v3_{lesson.lesson_id}"

        content = f"经验: {lesson.title}\n"
        content += f"内容: {lesson.content}\n"
        content += f"发生: {lesson.what_happened}\n"
        content += f"学到: {lesson.what_learned}\n"
        content += f"应用: {lesson.how_to_apply}"

        memory = Memory(
            memory_id=memory_id,
            type=MemoryType.LEARNING,
            content=content,
            priority=self._importance_to_priority(lesson.importance),
            iteration_id=lesson.work_item_id,
            stage_id=lesson.stage_id,
            tags=lesson.tags + [lesson.category.value, lesson.applicability],
            metadata={
                'v4_type': 'lesson',
                'v4_id': lesson.lesson_id,
                'applicable_scenarios': lesson.applicable_scenarios,
                'applied_count': lesson.applied_count
            }
        )

        self.store.add(memory)
        return memory

    def _importance_to_priority(self, importance: float) -> MemoryPriority:
        """将重要性分数转换为v3.0优先级"""
        if importance >= 0.9:
            return MemoryPriority.CRITICAL
        elif importance >= 0.7:
            return MemoryPriority.HIGH
        elif importance >= 0.5:
            return MemoryPriority.MEDIUM
        else:
            return MemoryPriority.LOW

    # ==================== v4.0 Persistence ====================

    def _load_v4_data(self):
        """加载v4.0数据"""
        self._load_decisions()
        self._load_lessons()
        self._load_documents()

    def _load_decisions(self):
        """加载技术决策"""
        if not self.decisions_file.exists():
            return

        try:
            with open(self.decisions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for decision_data in data:
                decision = TechDecision.from_dict(decision_data)
                self.decisions[decision.decision_id] = decision

        except Exception as e:
            print(f"警告: 加载决策失败: {e}")

    def _save_decisions(self) -> bool:
        """保存技术决策"""
        try:
            self.v4_storage_dir.mkdir(parents=True, exist_ok=True)

            data = [d.to_dict() for d in self.decisions.values()]

            with open(self.decisions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"警告: 保存决策失败: {e}")
            return False

    def _load_lessons(self):
        """加载经验教训"""
        if not self.lessons_file.exists():
            return

        try:
            with open(self.lessons_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for lesson_data in data:
                lesson = Lesson.from_dict(lesson_data)
                self.lessons[lesson.lesson_id] = lesson

        except Exception as e:
            print(f"警告: 加载经验失败: {e}")

    def _save_lessons(self) -> bool:
        """保存经验教训"""
        try:
            self.v4_storage_dir.mkdir(parents=True, exist_ok=True)

            data = [l.to_dict() for l in self.lessons.values()]

            with open(self.lessons_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"警告: 保存经验失败: {e}")
            return False

    def _load_documents(self):
        """加载文档引用"""
        if not self.documents_file.exists():
            return

        try:
            with open(self.documents_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for doc_data in data:
                doc = DocumentRef.from_dict(doc_data)
                self.documents[doc.ref_id] = doc

        except Exception as e:
            print(f"警告: 加载文档引用失败: {e}")

    def _save_documents(self) -> bool:
        """保存文档引用"""
        try:
            self.v4_storage_dir.mkdir(parents=True, exist_ok=True)

            data = [d.to_dict() for d in self.documents.values()]

            with open(self.documents_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"警告: 保存文档引用失败: {e}")
            return False
