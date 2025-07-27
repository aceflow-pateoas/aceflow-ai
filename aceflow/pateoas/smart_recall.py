"""
智能记忆召回系统
实现基于语义、时间、上下文等多因素的智能记忆检索
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .models import MemoryFragment, MemoryCategory
from .utils import calculate_similarity, extract_keywords, is_recent


@dataclass
class RecallContext:
    """召回上下文"""
    current_input: str
    current_state: Dict[str, Any]
    project_context: Dict[str, Any] = None
    temporal_context: Dict[str, Any] = None


class ContextAnalyzer:
    """上下文分析器"""
    
    def analyze_query_intent(self, query: str) -> Dict[str, float]:
        """分析查询意图"""
        intent_keywords = {
            'search': ['查找', '搜索', '找', 'find', 'search', 'look'],
            'problem': ['问题', '错误', '异常', 'issue', 'error', 'bug', 'problem'],
            'requirement': ['需求', '功能', '特性', 'requirement', 'feature', 'need'],
            'decision': ['决策', '选择', '方案', 'decision', 'choice', 'solution'],
            'learning': ['学习', '经验', '教训', 'learning', 'experience', 'lesson']
        }
        
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            intent_scores[intent] = min(1.0, score / 3.0)
        
        return intent_scores


class MemoryRecallEngine:
    """记忆召回引擎"""
    
    def __init__(self):
        self.context_analyzer = ContextAnalyzer()
    
    def recall_with_context(
        self,
        memories: List[MemoryFragment],
        query: str,
        current_state: Dict[str, Any] = None,
        project_context: Dict[str, Any] = None,
        limit: int = 10,
        min_relevance: float = 0.3
    ) -> List[Dict[str, Any]]:
        """带上下文的记忆召回"""
        
        if not memories:
            return []
        
        # 计算每个记忆的相关性
        scored_memories = []
        for memory in memories:
            relevance_score = self._calculate_enhanced_relevance(
                memory, query, current_state or {}, project_context or {}
            )
            
            if relevance_score >= min_relevance:
                scored_memories.append({
                    'memory': memory,
                    'relevance_score': relevance_score,
                    'reasoning': self._generate_reasoning(memory, query, relevance_score)
                })
        
        # 按相关性排序
        scored_memories.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # 应用多样性过滤
        diverse_memories = self._apply_diversity_filter(scored_memories, limit)
        
        # 转换为字典格式并更新访问记录
        results = []
        for item in diverse_memories:
            memory = item['memory']
            memory.access()  # 更新访问记录
            
            results.append({
                'content': memory.content,
                'category': memory.category.value,
                'importance': memory.importance,
                'relevance_score': item['relevance_score'],
                'reasoning': item['reasoning'],
                'tags': memory.tags,
                'created_at': memory.created_at.isoformat(),
                'last_accessed': memory.last_accessed.isoformat(),
                'access_count': memory.access_count,
                'relevance_factors': self._get_relevance_factors(memory, query, current_state or {})
            })
        
        return results
    
    def _calculate_enhanced_relevance(
        self, 
        memory: MemoryFragment, 
        query: str, 
        current_state: Dict[str, Any],
        project_context: Dict[str, Any]
    ) -> float:
        """计算增强的相关性分数"""
        
        # 1. 语义相似度 (40%)
        semantic_similarity = calculate_similarity(query, memory.content)
        
        # 2. 时间相关性 (20%)
        temporal_relevance = self._calculate_temporal_relevance(memory)
        
        # 3. 上下文重叠 (20%)
        context_overlap = self._calculate_context_overlap(memory, query, current_state)
        
        # 4. 重要性权重 (15%)
        importance_weight = memory.importance
        
        # 5. 访问频率 (5%)
        access_frequency = min(1.0, memory.access_count / 10.0)
        
        # 加权计算
        relevance = (
            semantic_similarity * 0.40 +
            temporal_relevance * 0.20 +
            context_overlap * 0.20 +
            importance_weight * 0.15 +
            access_frequency * 0.05
        )
        
        # 应用分类增强
        relevance += self._get_category_boost(memory, query)
        
        return min(1.0, relevance)
    
    def _calculate_temporal_relevance(self, memory: MemoryFragment) -> float:
        """计算时间相关性"""
        now = datetime.now()
        access_diff = now - memory.last_accessed
        
        if access_diff.days == 0:
            return 1.0
        elif access_diff.days <= 7:
            return 0.8
        elif access_diff.days <= 30:
            return 0.5
        else:
            return 0.2
    
    def _calculate_context_overlap(
        self, 
        memory: MemoryFragment, 
        query: str, 
        current_state: Dict[str, Any]
    ) -> float:
        """计算上下文重叠度"""
        overlap_score = 0.0
        
        # 标签重叠
        if memory.tags:
            query_keywords = extract_keywords(query, max_keywords=10)
            tag_overlap = len(set(query_keywords) & set(memory.tags))
            overlap_score += tag_overlap / max(len(memory.tags), 1) * 0.5
        
        # 技术栈匹配
        tech_stack = current_state.get('technology_stack', [])
        if tech_stack:
            memory_lower = memory.content.lower()
            tech_matches = sum(1 for tech in tech_stack if tech.lower() in memory_lower)
            overlap_score += min(0.5, tech_matches * 0.1)
        
        return min(1.0, overlap_score)
    
    def _get_category_boost(self, memory: MemoryFragment, query: str) -> float:
        """获取分类增强分数"""
        query_lower = query.lower()
        boost = 0.0
        
        # 基于查询意图的分类增强
        if any(word in query_lower for word in ['问题', '错误', 'issue', 'error', 'bug']):
            if memory.category == MemoryCategory.ISSUE:
                boost += 0.15
        
        if any(word in query_lower for word in ['需求', '功能', 'requirement', 'feature']):
            if memory.category == MemoryCategory.REQUIREMENT:
                boost += 0.1
        
        if any(word in query_lower for word in ['决策', '选择', 'decision', 'choice']):
            if memory.category == MemoryCategory.DECISION:
                boost += 0.1
        
        # 时间敏感性增强
        if is_recent(memory.last_accessed, hours=24):
            boost += 0.05
        
        return boost
    
    def _generate_reasoning(self, memory: MemoryFragment, query: str, relevance_score: float) -> str:
        """生成推理说明"""
        reasons = []
        
        semantic_sim = calculate_similarity(query, memory.content)
        if semantic_sim > 0.6:
            reasons.append(f"内容高度相关({semantic_sim:.2f})")
        elif semantic_sim > 0.3:
            reasons.append(f"内容相关({semantic_sim:.2f})")
        
        if memory.importance > 0.8:
            reasons.append("高重要性")
        
        if is_recent(memory.last_accessed, hours=24):
            reasons.append("最近访问")
        
        if memory.access_count > 5:
            reasons.append("频繁访问")
        
        return "; ".join(reasons) if reasons else "基础匹配"
    
    def _get_relevance_factors(
        self, 
        memory: MemoryFragment, 
        query: str, 
        current_state: Dict[str, Any]
    ) -> Dict[str, float]:
        """获取相关性因素分解"""
        return {
            'semantic_similarity': calculate_similarity(query, memory.content),
            'temporal_relevance': self._calculate_temporal_relevance(memory),
            'context_overlap': self._calculate_context_overlap(memory, query, current_state),
            'importance_weight': memory.importance,
            'access_frequency': min(1.0, memory.access_count / 10.0)
        }
    
    def _apply_diversity_filter(self, scored_memories: List[Dict], limit: int) -> List[Dict]:
        """应用多样性过滤"""
        if len(scored_memories) <= limit:
            return scored_memories
        
        selected = []
        category_counts = {}
        
        for item in scored_memories:
            memory = item['memory']
            category = memory.category.value
            
            # 每个分类最多占1/3
            category_limit = max(1, limit // 3)
            
            if category_counts.get(category, 0) < category_limit:
                selected.append(item)
                category_counts[category] = category_counts.get(category, 0) + 1
                
                if len(selected) >= limit:
                    break
        
        # 如果还没达到限制，添加剩余的高相关性记忆
        if len(selected) < limit:
            for item in scored_memories:
                if item not in selected:
                    selected.append(item)
                    if len(selected) >= limit:
                        break
        
        return selected
    
    def get_recall_statistics(self, recall_results: List[Dict]) -> Dict[str, Any]:
        """获取召回统计信息"""
        if not recall_results:
            return {}
        
        relevance_scores = [r['relevance_score'] for r in recall_results]
        categories = [r['category'] for r in recall_results]
        importance_scores = [r['importance'] for r in recall_results]
        
        category_dist = {}
        for category in categories:
            category_dist[category] = category_dist.get(category, 0) + 1
        
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        return {
            'total_recalled': len(recall_results),
            'avg_relevance': avg_relevance,
            'max_relevance': max(relevance_scores),
            'min_relevance': min(relevance_scores),
            'category_distribution': category_dist,
            'avg_importance': sum(importance_scores) / len(importance_scores),
            'recall_quality': 'high' if avg_relevance > 0.7 else 'medium' if avg_relevance > 0.5 else 'low'
        }