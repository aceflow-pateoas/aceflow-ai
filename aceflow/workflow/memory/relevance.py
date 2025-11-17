"""
Relevance Calculator for v4.0 - 相关性计算器

实现记忆与上下文的相关性评分算法，用于智能筛选和排序记忆。

评分公式：
    score = (keyword_match * 0.4) + (tag_match * 0.3) + (stage_match * 0.2) +
            (importance * 0.1)

设计原则：
- 纯算法实现，不调用LLM API
- 支持可配置的权重
- 返回详细的评分细节供调试
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from .v4_models import RelevanceScore, MemoryInjectionContext, TechDecision, Lesson
from .models import Memory


class RelevanceCalculator:
    """
    相关性计算器（v4.0）

    计算记忆与当前上下文的相关性分数，支持：
    - 关键词匹配（TF-IDF style）
    - 标签匹配
    - 阶段相关性
    - 重要性权重
    - 时间新近度
    """

    # 默认权重配置
    DEFAULT_WEIGHTS = {
        'keyword': 0.4,      # 关键词匹配权重
        'tag': 0.3,          # 标签匹配权重
        'stage': 0.2,        # 阶段相关性权重
        'importance': 0.1,   # 重要性权重
        'recency': 0.0       # 时间新近度权重（可选，默认不启用）
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        初始化相关性计算器

        Args:
            weights: 自定义权重配置
        """
        self.weights = weights or self.DEFAULT_WEIGHTS

    def calculate(
        self,
        memory: Memory,
        context: MemoryInjectionContext
    ) -> RelevanceScore:
        """
        计算记忆与上下文的相关性分数

        Args:
            memory: 记忆对象
            context: 注入上下文

        Returns:
            相关性评分结果
        """
        # 1. 关键词匹配得分
        keyword_score, matched_keywords = self._calculate_keyword_score(
            memory, context
        )

        # 2. 标签匹配得分
        tag_score, matched_tags = self._calculate_tag_score(
            memory, context
        )

        # 3. 阶段相关性得分
        stage_score = self._calculate_stage_score(
            memory, context
        )

        # 4. 重要性得分
        importance_score = self._get_importance_score(memory)

        # 5. 时间新近度得分（可选）
        recency_score = self._calculate_recency_score(memory)

        # 加权总分
        total_score = (
            keyword_score * self.weights['keyword'] +
            tag_score * self.weights['tag'] +
            stage_score * self.weights['stage'] +
            importance_score * self.weights['importance'] +
            recency_score * self.weights.get('recency', 0.0)
        )

        # 归一化到 [0, 1]
        total_score = min(max(total_score, 0.0), 1.0)

        # 生成评分理由
        reason = self._generate_reason(
            keyword_score, tag_score, stage_score,
            matched_keywords, matched_tags
        )

        return RelevanceScore(
            memory_id=memory.memory_id,
            total_score=total_score,
            keyword_score=keyword_score,
            tag_score=tag_score,
            stage_score=stage_score,
            importance_score=importance_score,
            recency_score=recency_score,
            matched_keywords=matched_keywords,
            matched_tags=matched_tags,
            reason=reason
        )

    def calculate_for_v4_decision(
        self,
        decision: TechDecision,
        context: MemoryInjectionContext
    ) -> RelevanceScore:
        """
        计算技术决策的相关性（v4.0专用）

        Args:
            decision: 技术决策对象
            context: 注入上下文

        Returns:
            相关性评分结果
        """
        # 构建搜索文本
        search_text = f"{decision.title} {decision.decision} {decision.reason}"
        search_text += " ".join(decision.tech_stack)

        # 关键词匹配
        keyword_score, matched_keywords = self._match_keywords(
            search_text,
            context.search_keywords
        )

        # 标签匹配
        tag_score, matched_tags = self._match_tags(
            decision.tags + decision.tech_stack,
            context.search_tags
        )

        # 阶段相关性（决策在requirement/design阶段最相关）
        stage_score = 1.0 if context.stage_type in ['requirement', 'design'] else 0.5

        # 重要性
        importance_score = decision.importance

        # 时间新近度
        recency_score = self._calculate_recency_score_from_datetime(decision.created_at)

        # 加权总分
        total_score = (
            keyword_score * self.weights['keyword'] +
            tag_score * self.weights['tag'] +
            stage_score * self.weights['stage'] +
            importance_score * self.weights['importance'] +
            recency_score * self.weights.get('recency', 0.0)
        )

        total_score = min(max(total_score, 0.0), 1.0)

        reason = self._generate_reason(
            keyword_score, tag_score, stage_score,
            matched_keywords, matched_tags
        )

        return RelevanceScore(
            memory_id=decision.decision_id,
            total_score=total_score,
            keyword_score=keyword_score,
            tag_score=tag_score,
            stage_score=stage_score,
            importance_score=importance_score,
            recency_score=recency_score,
            matched_keywords=matched_keywords,
            matched_tags=matched_tags,
            reason=reason
        )

    def calculate_for_v4_lesson(
        self,
        lesson: Lesson,
        context: MemoryInjectionContext
    ) -> RelevanceScore:
        """
        计算经验教训的相关性（v4.0专用）

        Args:
            lesson: 经验教训对象
            context: 注入上下文

        Returns:
            相关性评分结果
        """
        # 构建搜索文本
        search_text = f"{lesson.title} {lesson.content} {lesson.what_learned}"
        search_text += " ".join(lesson.applicable_scenarios)

        # 关键词匹配
        keyword_score, matched_keywords = self._match_keywords(
            search_text,
            context.search_keywords
        )

        # 标签匹配
        tag_score, matched_tags = self._match_tags(
            lesson.tags + lesson.applicable_scenarios,
            context.search_tags
        )

        # 阶段相关性（经验在implementation/testing阶段最相关）
        stage_score = 1.0 if context.stage_type in ['implementation', 'testing'] else 0.6

        # 重要性（general经验更重要）
        importance_score = lesson.importance
        if lesson.applicability == 'general':
            importance_score = min(importance_score + 0.2, 1.0)

        # 应用次数加权（经常应用的经验更可靠）
        applied_bonus = min(lesson.applied_count * 0.05, 0.2)
        importance_score = min(importance_score + applied_bonus, 1.0)

        # 时间新近度
        recency_score = self._calculate_recency_score_from_datetime(lesson.created_at)

        # 加权总分
        total_score = (
            keyword_score * self.weights['keyword'] +
            tag_score * self.weights['tag'] +
            stage_score * self.weights['stage'] +
            importance_score * self.weights['importance'] +
            recency_score * self.weights.get('recency', 0.0)
        )

        total_score = min(max(total_score, 0.0), 1.0)

        reason = self._generate_reason(
            keyword_score, tag_score, stage_score,
            matched_keywords, matched_tags
        )

        return RelevanceScore(
            memory_id=lesson.lesson_id,
            total_score=total_score,
            keyword_score=keyword_score,
            tag_score=tag_score,
            stage_score=stage_score,
            importance_score=importance_score,
            recency_score=recency_score,
            matched_keywords=matched_keywords,
            matched_tags=matched_tags,
            reason=reason
        )

    # ==================== Private Helper Methods ====================

    def _calculate_keyword_score(
        self,
        memory: Memory,
        context: MemoryInjectionContext
    ) -> Tuple[float, List[str]]:
        """计算关键词匹配得分"""
        if not context.search_keywords:
            context.extract_keywords()

        return self._match_keywords(
            memory.content,
            context.search_keywords
        )

    def _match_keywords(
        self,
        text: str,
        keywords: List[str]
    ) -> Tuple[float, List[str]]:
        """
        匹配关键词并计算得分

        使用简单的词频匹配算法

        Args:
            text: 待匹配文本
            keywords: 关键词列表

        Returns:
            (得分, 匹配的关键词列表)
        """
        if not keywords:
            return 0.0, []

        text_lower = text.lower()
        matched = []

        for keyword in keywords:
            if keyword.lower() in text_lower:
                matched.append(keyword)

        # 计算得分：匹配数量 / 总关键词数
        score = len(matched) / len(keywords) if keywords else 0.0

        return min(score, 1.0), matched

    def _calculate_tag_score(
        self,
        memory: Memory,
        context: MemoryInjectionContext
    ) -> Tuple[float, List[str]]:
        """计算标签匹配得分"""
        if not context.search_tags:
            context.extract_tags()

        return self._match_tags(memory.tags, context.search_tags)

    def _match_tags(
        self,
        memory_tags: List[str],
        context_tags: List[str]
    ) -> Tuple[float, List[str]]:
        """
        匹配标签并计算得分

        Args:
            memory_tags: 记忆的标签
            context_tags: 上下文的标签

        Returns:
            (得分, 匹配的标签列表)
        """
        if not memory_tags or not context_tags:
            return 0.0, []

        # 转小写并去重
        memory_tags_set = {tag.lower() for tag in memory_tags}
        context_tags_set = {tag.lower() for tag in context_tags}

        # 计算交集
        matched = list(memory_tags_set & context_tags_set)

        # 计算得分：匹配数量 / 上下文标签数
        score = len(matched) / len(context_tags) if context_tags else 0.0

        return min(score, 1.0), matched

    def _calculate_stage_score(
        self,
        memory: Memory,
        context: MemoryInjectionContext
    ) -> float:
        """
        计算阶段相关性得分

        逻辑：
        - 同stage_id → 1.0
        - 同stage_type → 0.8
        - 相邻阶段 → 0.6
        - 其他 → 0.4
        """
        if memory.stage_id == context.stage_id:
            return 1.0

        # 检查是否同类型阶段（简单匹配）
        if memory.stage_id and context.stage_type:
            if context.stage_type in memory.stage_id.lower():
                return 0.8

        # 相邻阶段（简单启发式）
        adjacent_stages = {
            'requirement': ['design'],
            'design': ['requirement', 'implementation'],
            'implementation': ['design', 'testing'],
            'testing': ['implementation', 'delivery']
        }

        if context.stage_type in adjacent_stages:
            if memory.stage_id in adjacent_stages[context.stage_type]:
                return 0.6

        return 0.4

    def _get_importance_score(self, memory: Memory) -> float:
        """
        获取重要性得分

        从Memory的priority字段映射到 [0, 1]
        """
        priority_map = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.5,
            'low': 0.3
        }

        priority_value = memory.priority.value if hasattr(memory.priority, 'value') else 'medium'
        return priority_map.get(priority_value, 0.5)

    def _calculate_recency_score(self, memory: Memory) -> float:
        """
        计算时间新近度得分

        逻辑：
        - 7天内 → 1.0
        - 30天内 → 0.8
        - 90天内 → 0.5
        - 更久 → 0.3
        """
        return self._calculate_recency_score_from_datetime(memory.created_at)

    def _calculate_recency_score_from_datetime(self, created_at: datetime) -> float:
        """从datetime计算新近度得分"""
        now = datetime.now()
        days_ago = (now - created_at).days

        if days_ago <= 7:
            return 1.0
        elif days_ago <= 30:
            return 0.8
        elif days_ago <= 90:
            return 0.5
        else:
            return 0.3

    def _generate_reason(
        self,
        keyword_score: float,
        tag_score: float,
        stage_score: float,
        matched_keywords: List[str],
        matched_tags: List[str]
    ) -> str:
        """生成评分理由"""
        reasons = []

        if keyword_score > 0.5:
            reasons.append(f"关键词匹配度高 ({len(matched_keywords)}个)")
        elif keyword_score > 0.0:
            reasons.append(f"部分关键词匹配 ({len(matched_keywords)}个)")

        if tag_score > 0.5:
            reasons.append(f"标签匹配度高 ({len(matched_tags)}个)")
        elif tag_score > 0.0:
            reasons.append(f"部分标签匹配 ({len(matched_tags)}个)")

        if stage_score >= 0.8:
            reasons.append("阶段高度相关")
        elif stage_score >= 0.6:
            reasons.append("阶段相关")

        if not reasons:
            reasons.append("基础匹配")

        return "；".join(reasons)


class MemoryFilter:
    """
    记忆筛选器（v4.0）

    根据相关性分数和配置筛选记忆
    """

    def __init__(self, calculator: Optional[RelevanceCalculator] = None):
        """
        初始化记忆筛选器

        Args:
            calculator: 相关性计算器实例
        """
        self.calculator = calculator or RelevanceCalculator()

    def filter_and_rank(
        self,
        memories: List[Memory],
        context: MemoryInjectionContext
    ) -> List[Tuple[Memory, RelevanceScore]]:
        """
        筛选并排序记忆

        Args:
            memories: 记忆列表
            context: 注入上下文

        Returns:
            (记忆, 评分)元组列表，按相关性降序排列
        """
        # 计算每个记忆的相关性
        scored_memories = []
        for memory in memories:
            score = self.calculator.calculate(memory, context)

            # 应用最低相关性阈值
            if score.total_score >= context.min_relevance:
                scored_memories.append((memory, score))

        # 按总分降序排序
        scored_memories.sort(key=lambda x: x[1].total_score, reverse=True)

        # 限制数量
        return scored_memories[:context.max_memories]

    def get_top_k(
        self,
        memories: List[Memory],
        context: MemoryInjectionContext,
        k: int = 5
    ) -> List[Memory]:
        """
        获取Top-K最相关的记忆

        Args:
            memories: 记忆列表
            context: 注入上下文
            k: 返回数量

        Returns:
            Top-K记忆列表
        """
        scored = self.filter_and_rank(memories, context)
        return [memory for memory, score in scored[:k]]

    def explain_ranking(
        self,
        memories: List[Memory],
        context: MemoryInjectionContext
    ) -> Dict[str, Any]:
        """
        解释排序结果（用于调试）

        Args:
            memories: 记忆列表
            context: 注入上下文

        Returns:
            排序解释信息
        """
        scored = self.filter_and_rank(memories, context)

        return {
            'total_candidates': len(memories),
            'passed_threshold': len(scored),
            'threshold': context.min_relevance,
            'top_memories': [
                {
                    'memory_id': memory.memory_id,
                    'content_preview': memory.content[:50] + '...',
                    'score': score.total_score,
                    'keyword_score': score.keyword_score,
                    'tag_score': score.tag_score,
                    'stage_score': score.stage_score,
                    'reason': score.reason,
                    'matched_keywords': score.matched_keywords,
                    'matched_tags': score.matched_tags
                }
                for memory, score in scored[:context.max_memories]
            ]
        }
