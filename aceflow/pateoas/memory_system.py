"""
上下文记忆系统
智能存储和召回项目相关信息
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from .models import MemoryFragment, MemoryCategory
from .config import get_config
from .utils import calculate_similarity, extract_keywords, ensure_directory, is_recent
from .memory_categories import (
    RequirementsMemory, DecisionMemory, PatternMemory, 
    IssueMemory, LearningMemory, ContextMemory
)
# from .smart_recall import MemoryRecallEngine, RecallContext


class ContextMemorySystem:
    """上下文记忆系统"""
    
    def __init__(self, project_id: Optional[str] = None):
        self.config = get_config()
        self.project_id = project_id or "default"
        
        # 记忆存储目录
        self.memory_dir = ensure_directory(self.config.memory_storage_path)
        
        # 专门的记忆分类存储器
        self.memory_stores = {
            'requirement': RequirementsMemory(self.memory_dir / f"{self.project_id}_requirements.json"),
            'decision': DecisionMemory(self.memory_dir / f"{self.project_id}_decisions.json"),
            'pattern': PatternMemory(self.memory_dir / f"{self.project_id}_patterns.json"),
            'issue': IssueMemory(self.memory_dir / f"{self.project_id}_issues.json"),
            'learning': LearningMemory(self.memory_dir / f"{self.project_id}_learning.json"),
            'context': ContextMemory(self.memory_dir / f"{self.project_id}_context.json")
        }
        
        # 智能记忆召回引擎 (暂时禁用)
        # self.recall_engine = MemoryRecallEngine()
        
        # 兼容性：保持旧的接口
        self.memory_categories = {
            category: store.get_all_memories() 
            for category, store in self.memory_stores.items()
        }
    
    def store_interaction(self, user_input: str, ai_response: Dict[str, Any]):
        """存储交互记忆"""
        # 提取上下文信息
        context = self._extract_context(user_input, ai_response)
        importance = self._calculate_importance(user_input, ai_response)
        tags = extract_keywords(user_input + " " + str(ai_response), max_keywords=5)
        
        # 创建记忆条目
        memory_entry = MemoryFragment(
            content=f"用户输入: {user_input}\nAI响应: {str(ai_response)[:200]}...",
            category=self._classify_memory_content(user_input, ai_response),
            importance=importance,
            tags=tags,
            project_id=self.project_id
        )
        
        # 使用专门的存储器存储
        category_key = memory_entry.category.value
        if category_key in self.memory_stores:
            self.memory_stores[category_key].store(memory_entry)
            # 更新兼容性接口
            self.memory_categories[category_key] = self.memory_stores[category_key].get_all_memories()
    
    def recall_relevant_context(self, current_input: str, current_state: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """召回相关上下文（增强版）"""
        all_relevant_memories = []
        
        # 使用专门的存储器进行智能搜索
        for category, store in self.memory_stores.items():
            # 每个分类最多返回 limit//2 个记忆，确保多样性
            category_limit = max(1, limit // 2)
            similar_memories = store.search_similar(current_input, current_state, category_limit)
            all_relevant_memories.extend(similar_memories)
        
        if not all_relevant_memories:
            return []
        
        # 计算综合相关性分数
        scored_memories = []
        for memory in all_relevant_memories:
            relevance_score = self._calculate_relevance(memory, current_input, current_state)
            if relevance_score > 0.3:  # 过滤低相关性记忆
                scored_memories.append({
                    'memory': memory,
                    'relevance_score': relevance_score
                })
        
        # 按相关性排序
        scored_memories.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # 返回前N个相关记忆，确保分类多样性
        relevant_memories = []
        category_counts = {}
        
        for item in scored_memories:
            memory = item['memory']
            category = memory.category.value
            
            # 限制每个分类的数量，确保多样性
            if category_counts.get(category, 0) >= max(1, limit // 3):
                continue
            
            memory.access()  # 记录访问
            category_counts[category] = category_counts.get(category, 0) + 1
            
            relevant_memories.append({
                'content': memory.content,
                'category': memory.category.value,
                'importance': memory.importance,
                'relevance_score': item['relevance_score'],
                'tags': memory.tags,
                'created_at': memory.created_at.isoformat()
            })
            
            if len(relevant_memories) >= limit:
                break
        
        # 保存访问记录
        for store in self.memory_stores.values():
            store.save_memories()
        
        return relevant_memories
    
    def intelligent_recall(
        self, 
        query: str, 
        current_state: Dict[str, Any] = None,
        limit: int = 10,
        min_relevance: float = 0.3,
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """智能记忆召回（增强接口）"""
        
        # 收集记忆
        if category_filter and category_filter in self.memory_categories:
            memories = self.memory_categories[category_filter]
        else:
            memories = []
            for category_memories in self.memory_categories.values():
                memories.extend(category_memories)
        
        if not memories:
            return {
                'results': [],
                'statistics': {},
                'query_analysis': {}
            }
        
        # 使用增强的相关性计算进行智能召回
        scored_memories = []
        for memory in memories:
            relevance_score = self._calculate_enhanced_relevance(
                memory, query, current_state or {}
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
        
        # 转换为结果格式
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
        
        # 分析查询意图
        query_analysis = self._analyze_query_intent(query)
        
        # 计算统计信息
        statistics = self._calculate_recall_statistics(results)
        
        # 保存访问记录
        for store in self.memory_stores.values():
            store.save_memories()
        
        return {
            'results': results,
            'statistics': statistics,
            'query_analysis': query_analysis,
            'total_searched': len(memories),
            'total_recalled': len(results)
        }
    
    def add_memory(self, content: str, category: str, importance: float = 0.5, tags: List[str] = None):
        """手动添加记忆"""
        try:
            memory_category = MemoryCategory(category)
        except ValueError:
            memory_category = MemoryCategory.CONTEXT
        
        memory = MemoryFragment(
            content=content,
            category=memory_category,
            importance=importance,
            tags=tags or [],
            project_id=self.project_id
        )
        
        # 使用专门的存储器存储
        category_key = memory_category.value
        if category_key in self.memory_stores:
            self.memory_stores[category_key].store(memory)
            # 更新兼容性接口
            self.memory_categories[category_key] = self.memory_stores[category_key].get_all_memories()
    
    def search_memories(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索记忆"""
        memories_to_search = []
        
        if category and category in self.memory_categories:
            memories_to_search = self.memory_categories[category]
        else:
            for memories in self.memory_categories.values():
                memories_to_search.extend(memories)
        
        # 计算相似度并排序
        scored_memories = []
        for memory in memories_to_search:
            similarity = calculate_similarity(query, memory.content)
            if similarity > 0.2:
                scored_memories.append({
                    'memory': memory,
                    'similarity': similarity
                })
        
        scored_memories.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 返回结果
        results = []
        for item in scored_memories[:limit]:
            memory = item['memory']
            results.append({
                'content': memory.content,
                'category': memory.category.value,
                'importance': memory.importance,
                'similarity': item['similarity'],
                'tags': memory.tags,
                'created_at': memory.created_at.isoformat()
            })
        
        return results
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        total_memories = sum(len(memories) for memories in self.memory_categories.values())
        
        category_stats = {}
        for category, memories in self.memory_categories.items():
            if memories:
                avg_importance = sum(m.importance for m in memories) / len(memories)
                recent_count = sum(1 for m in memories if is_recent(m.created_at, hours=24))
            else:
                avg_importance = 0
                recent_count = 0
            
            category_stats[category] = {
                'count': len(memories),
                'avg_importance': avg_importance,
                'recent_count': recent_count
            }
        
        return {
            'total_memories': total_memories,
            'categories': category_stats,
            'project_id': self.project_id
        }
    
    def cleanup_old_memories(self, days: int = 90):
        """清理旧记忆"""
        total_cleaned = 0
        
        # 使用专门存储器的清理功能
        for category, store in self.memory_stores.items():
            cleaned_count = store.cleanup_old_memories(days)
            total_cleaned += cleaned_count
            # 更新兼容性接口
            self.memory_categories[category] = store.get_all_memories()
        
        return total_cleaned
    
    def optimize_memory_storage(self):
        """优化记忆存储"""
        optimization_stats = {
            'duplicates_removed': 0,
            'low_importance_removed': 0,
            'merged_similar': 0
        }
        
        # 使用专门存储器的优化功能（如果有的话）
        for category, store in self.memory_stores.items():
            # 获取当前记忆
            memories = store.get_all_memories()
            if not memories:
                continue
            
            # 1. 移除重复记忆
            unique_memories = []
            seen_contents = set()
            
            for memory in memories:
                content_hash = hash(memory.content)
                if content_hash not in seen_contents:
                    unique_memories.append(memory)
                    seen_contents.add(content_hash)
                else:
                    optimization_stats['duplicates_removed'] += 1
            
            # 2. 移除低重要性且很少访问的记忆
            filtered_memories = []
            for memory in unique_memories:
                if memory.importance < 0.3 and memory.access_count < 2 and not is_recent(memory.last_accessed, hours=168):  # 一周
                    optimization_stats['low_importance_removed'] += 1
                else:
                    filtered_memories.append(memory)
            
            # 3. 合并相似记忆
            merged_memories = self._merge_similar_memories(filtered_memories)
            optimization_stats['merged_similar'] += len(filtered_memories) - len(merged_memories)
            
            # 更新存储器
            store.memories = merged_memories
            store.save_memories()
            
            # 更新兼容性接口
            self.memory_categories[category] = merged_memories
        
        return optimization_stats
    
    def _merge_similar_memories(self, memories: List[MemoryFragment], similarity_threshold: float = 0.8) -> List[MemoryFragment]:
        """合并相似记忆"""
        if len(memories) <= 1:
            return memories
        
        merged = []
        processed = set()
        
        for i, memory1 in enumerate(memories):
            if i in processed:
                continue
            
            similar_memories = [memory1]
            
            for j, memory2 in enumerate(memories[i+1:], i+1):
                if j in processed:
                    continue
                
                similarity = calculate_similarity(memory1.content, memory2.content)
                if similarity >= similarity_threshold:
                    similar_memories.append(memory2)
                    processed.add(j)
            
            if len(similar_memories) > 1:
                # 合并相似记忆
                merged_memory = self._create_merged_memory(similar_memories)
                merged.append(merged_memory)
            else:
                merged.append(memory1)
            
            processed.add(i)
        
        return merged
    
    def _create_merged_memory(self, memories: List[MemoryFragment]) -> MemoryFragment:
        """创建合并后的记忆"""
        # 选择最重要的记忆作为基础
        base_memory = max(memories, key=lambda m: m.importance)
        
        # 合并内容
        contents = [m.content for m in memories]
        merged_content = f"合并记忆 ({len(memories)} 条):\n" + "\n---\n".join(contents)
        
        # 合并标签
        all_tags = []
        for memory in memories:
            all_tags.extend(memory.tags)
        unique_tags = list(set(all_tags))
        
        # 计算平均重要性
        avg_importance = sum(m.importance for m in memories) / len(memories)
        
        # 累计访问次数
        total_access_count = sum(m.access_count for m in memories)
        
        # 使用最早的创建时间
        earliest_created = min(m.created_at for m in memories)
        
        # 使用最近的访问时间
        latest_accessed = max(m.last_accessed for m in memories)
        
        return MemoryFragment(
            content=merged_content,
            category=base_memory.category,
            importance=min(1.0, avg_importance * 1.1),  # 略微提升重要性
            tags=unique_tags,
            created_at=earliest_created,
            last_accessed=latest_accessed,
            access_count=total_access_count,
            project_id=base_memory.project_id
        )
    
    def build_memory_index(self):
        """构建记忆索引（增强实现）"""
        self.memory_index = {
            'by_category': {},
            'by_tags': {},
            'by_importance': {},
            'by_recency': {},
            'by_project': {},
            'statistics': {}
        }
        
        all_memories = []
        for memories in self.memory_categories.values():
            all_memories.extend(memories)
        
        # 按分类索引
        for category, memories in self.memory_categories.items():
            self.memory_index['by_category'][category] = [
                {
                    'id': id(m), 
                    'content_preview': m.content[:100],
                    'importance': m.importance,
                    'access_count': m.access_count,
                    'tags': m.tags[:3]  # 只显示前3个标签
                } for m in memories
            ]
        
        # 按标签索引
        tag_stats = {}
        for memory in all_memories:
            for tag in memory.tags:
                if tag not in self.memory_index['by_tags']:
                    self.memory_index['by_tags'][tag] = []
                    tag_stats[tag] = {'count': 0, 'avg_importance': 0, 'total_importance': 0}
                
                self.memory_index['by_tags'][tag].append({
                    'id': id(memory),
                    'content_preview': memory.content[:100],
                    'importance': memory.importance,
                    'category': memory.category.value
                })
                
                tag_stats[tag]['count'] += 1
                tag_stats[tag]['total_importance'] += memory.importance
        
        # 计算标签平均重要性
        for tag, stats in tag_stats.items():
            stats['avg_importance'] = stats['total_importance'] / stats['count']
        
        # 按重要性索引
        importance_ranges = [(0.8, 1.0), (0.6, 0.8), (0.4, 0.6), (0.0, 0.4)]
        for min_imp, max_imp in importance_ranges:
            range_key = f"{min_imp}-{max_imp}"
            range_memories = [m for m in all_memories if min_imp <= m.importance < max_imp]
            self.memory_index['by_importance'][range_key] = [
                {
                    'id': id(m), 
                    'content_preview': m.content[:100], 
                    'importance': m.importance,
                    'category': m.category.value,
                    'access_count': m.access_count
                } for m in range_memories
            ]
        
        # 按时间索引
        time_ranges = [
            ('today', lambda m: is_recent(m.last_accessed, hours=24)),
            ('week', lambda m: is_recent(m.last_accessed, hours=168)),
            ('month', lambda m: is_recent(m.last_accessed, hours=720)),
            ('older', lambda m: not is_recent(m.last_accessed, hours=720))
        ]
        
        for range_name, filter_func in time_ranges:
            range_memories = [m for m in all_memories if filter_func(m)]
            self.memory_index['by_recency'][range_name] = [
                {
                    'id': id(m), 
                    'content_preview': m.content[:100], 
                    'last_accessed': m.last_accessed.isoformat(),
                    'category': m.category.value,
                    'importance': m.importance
                } for m in range_memories
            ]
        
        # 按项目索引
        project_memories = {}
        for memory in all_memories:
            project_id = memory.project_id or 'unknown'
            if project_id not in project_memories:
                project_memories[project_id] = []
            project_memories[project_id].append(memory)
        
        for project_id, memories in project_memories.items():
            self.memory_index['by_project'][project_id] = {
                'count': len(memories),
                'avg_importance': sum(m.importance for m in memories) / len(memories),
                'categories': {},
                'recent_count': sum(1 for m in memories if is_recent(m.last_accessed, hours=24))
            }
            
            # 项目内分类统计
            for memory in memories:
                category = memory.category.value
                if category not in self.memory_index['by_project'][project_id]['categories']:
                    self.memory_index['by_project'][project_id]['categories'][category] = 0
                self.memory_index['by_project'][project_id]['categories'][category] += 1
        
        # 统计信息
        self.memory_index['statistics'] = {
            'total_memories': len(all_memories),
            'categories_count': {cat: len(mems) for cat, mems in self.memory_categories.items()},
            'avg_importance': sum(m.importance for m in all_memories) / len(all_memories) if all_memories else 0,
            'total_access_count': sum(m.access_count for m in all_memories),
            'most_accessed': max(all_memories, key=lambda m: m.access_count) if all_memories else None,
            'most_important': max(all_memories, key=lambda m: m.importance) if all_memories else None,
            'tag_statistics': tag_stats,
            'recent_activity': sum(1 for m in all_memories if is_recent(m.last_accessed, hours=24))
        }
        
        return self.memory_index
    
    def get_specialized_memories(self, memory_type: str, **kwargs) -> List[Dict[str, Any]]:
        """获取专门类型的记忆"""
        results = []
        
        if memory_type == 'requirements':
            store = self.memory_stores['requirement']
            if hasattr(store, 'get_functional_requirements'):
                if kwargs.get('functional_only'):
                    memories = store.get_functional_requirements()
                elif kwargs.get('non_functional_only'):
                    memories = store.get_non_functional_requirements()
                else:
                    memories = store.get_all_memories()
            else:
                memories = store.get_all_memories()
                
        elif memory_type == 'decisions':
            store = self.memory_stores['decision']
            if hasattr(store, 'get_technical_decisions'):
                if kwargs.get('technical_only'):
                    memories = store.get_technical_decisions()
                elif kwargs.get('business_only'):
                    memories = store.get_business_decisions()
                else:
                    memories = store.get_all_memories()
            else:
                memories = store.get_all_memories()
                
        elif memory_type == 'patterns':
            store = self.memory_stores['pattern']
            if hasattr(store, 'get_code_patterns'):
                if kwargs.get('code_only'):
                    memories = store.get_code_patterns()
                elif kwargs.get('design_only'):
                    memories = store.get_design_patterns()
                else:
                    memories = store.get_all_memories()
            else:
                memories = store.get_all_memories()
                
        elif memory_type == 'issues':
            store = self.memory_stores['issue']
            if hasattr(store, 'get_resolved_issues'):
                if kwargs.get('resolved_only'):
                    memories = store.get_resolved_issues()
                elif kwargs.get('open_only'):
                    memories = store.get_open_issues()
                else:
                    memories = store.get_all_memories()
            else:
                memories = store.get_all_memories()
                
        elif memory_type == 'learning':
            store = self.memory_stores['learning']
            if hasattr(store, 'get_technical_learnings'):
                if kwargs.get('technical_only'):
                    memories = store.get_technical_learnings()
                elif kwargs.get('process_only'):
                    memories = store.get_process_learnings()
                else:
                    memories = store.get_all_memories()
            else:
                memories = store.get_all_memories()
                
        elif memory_type == 'context':
            store = self.memory_stores['context']
            if hasattr(store, 'get_recent_context'):
                hours = kwargs.get('hours', 24)
                memories = store.get_recent_context(hours)
            else:
                memories = store.get_all_memories()
        else:
            return []
        
        # 转换为字典格式
        for memory in memories:
            results.append({
                'content': memory.content,
                'category': memory.category.value,
                'importance': memory.importance,
                'tags': memory.tags,
                'created_at': memory.created_at.isoformat(),
                'last_accessed': memory.last_accessed.isoformat(),
                'access_count': memory.access_count,
                'project_id': memory.project_id
            })
        
        return results
    
    def analyze_memory_patterns(self) -> Dict[str, Any]:
        """分析记忆模式"""
        all_memories = []
        for memories in self.memory_categories.values():
            all_memories.extend(memories)
        
        if not all_memories:
            return {'patterns': [], 'insights': [], 'recommendations': []}
        
        patterns = []
        insights = []
        recommendations = []
        
        # 分析访问模式
        high_access_memories = [m for m in all_memories if m.access_count > 5]
        if high_access_memories:
            patterns.append(f"发现 {len(high_access_memories)} 个高频访问记忆")
            insights.append("某些信息被频繁引用，可能是核心知识点")
        
        # 分析重要性分布
        high_importance = len([m for m in all_memories if m.importance > 0.8])
        medium_importance = len([m for m in all_memories if 0.5 <= m.importance <= 0.8])
        low_importance = len([m for m in all_memories if m.importance < 0.5])
        
        patterns.append(f"重要性分布: 高({high_importance}) 中({medium_importance}) 低({low_importance})")
        
        if low_importance > len(all_memories) * 0.6:
            insights.append("大量低重要性记忆，建议清理")
            recommendations.append("运行记忆优化以清理低价值信息")
        
        # 分析分类分布
        category_counts = {}
        for memory in all_memories:
            category = memory.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        dominant_category = max(category_counts.items(), key=lambda x: x[1])
        if dominant_category[1] > len(all_memories) * 0.5:
            patterns.append(f"主导分类: {dominant_category[0]} ({dominant_category[1]} 条)")
            insights.append(f"项目主要关注 {dominant_category[0]} 类型的信息")
        
        # 分析时间模式
        recent_memories = [m for m in all_memories if is_recent(m.last_accessed, hours=24)]
        if len(recent_memories) < len(all_memories) * 0.1:
            insights.append("最近活跃度较低，可能需要更多交互")
            recommendations.append("增加与系统的交互频率以保持记忆活跃")
        
        # 分析标签使用
        all_tags = []
        for memory in all_memories:
            all_tags.extend(memory.tags)
        
        if all_tags:
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            most_common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            patterns.append(f"常用标签: {', '.join([f'{tag}({count})' for tag, count in most_common_tags])}")
        
        return {
            'patterns': patterns,
            'insights': insights,
            'recommendations': recommendations,
            'statistics': {
                'total_memories': len(all_memories),
                'category_distribution': category_counts,
                'importance_distribution': {
                    'high': high_importance,
                    'medium': medium_importance,
                    'low': low_importance
                },
                'access_statistics': {
                    'avg_access_count': sum(m.access_count for m in all_memories) / len(all_memories),
                    'max_access_count': max(m.access_count for m in all_memories),
                    'high_access_count': len(high_access_memories)
                }
            }
        }
    
    def _extract_context(self, user_input: str, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """提取上下文信息"""
        return {
            'input_length': len(user_input),
            'response_type': type(ai_response).__name__,
            'timestamp': datetime.now().isoformat(),
            'keywords': extract_keywords(user_input, max_keywords=3)
        }
    
    def _calculate_importance(self, user_input: str, ai_response: Dict[str, Any]) -> float:
        """计算记忆重要性"""
        importance_factors = []
        
        # 基于输入长度
        if len(user_input) > 100:
            importance_factors.append(0.3)
        elif len(user_input) > 50:
            importance_factors.append(0.2)
        else:
            importance_factors.append(0.1)
        
        # 基于关键词
        important_keywords = ['错误', '问题', '决策', '重要', '关键', '架构', '设计']
        keyword_score = sum(0.1 for keyword in important_keywords if keyword in user_input.lower())
        importance_factors.append(min(0.5, keyword_score))
        
        # 基于响应复杂度
        response_str = str(ai_response)
        if len(response_str) > 500:
            importance_factors.append(0.3)
        elif len(response_str) > 200:
            importance_factors.append(0.2)
        else:
            importance_factors.append(0.1)
        
        return min(1.0, sum(importance_factors))
    
    def _classify_memory_content(self, user_input: str, ai_response: Dict[str, Any]) -> MemoryCategory:
        """分类记忆内容"""
        text = (user_input + " " + str(ai_response)).lower()
        
        # 关键词分类
        if any(word in text for word in ['需求', '要求', 'requirement', '功能']):
            return MemoryCategory.REQUIREMENT
        elif any(word in text for word in ['决策', '选择', 'decision', '决定']):
            return MemoryCategory.DECISION
        elif any(word in text for word in ['模式', '模板', 'pattern', '规律']):
            return MemoryCategory.PATTERN
        elif any(word in text for word in ['问题', '错误', 'issue', 'error', 'bug']):
            return MemoryCategory.ISSUE
        elif any(word in text for word in ['学习', '经验', 'learning', '教训']):
            return MemoryCategory.LEARNING
        else:
            return MemoryCategory.CONTEXT
    
    def _calculate_relevance(self, memory: MemoryFragment, current_input: str, current_state: Dict[str, Any]) -> float:
        """计算记忆相关性"""
        relevance_factors = {
            'semantic_similarity': calculate_similarity(current_input, memory.content),
            'temporal_relevance': self._temporal_relevance(memory),
            'importance_weight': memory.importance,
            'access_frequency': min(1.0, memory.access_count / 10.0),
            'tag_overlap': self._tag_overlap(current_input, memory.tags)
        }
        
        # 权重配置
        weights = {
            'semantic_similarity': 0.4,
            'temporal_relevance': 0.2,
            'importance_weight': 0.2,
            'access_frequency': 0.1,
            'tag_overlap': 0.1
        }
        
        total_relevance = sum(
            relevance_factors[factor] * weights[factor]
            for factor in relevance_factors
        )
        
        return min(1.0, total_relevance)
    
    def _temporal_relevance(self, memory: MemoryFragment) -> float:
        """计算时间相关性"""
        now = datetime.now()
        time_diff = now - memory.last_accessed
        
        # 最近访问的记忆更相关
        if time_diff.days == 0:
            return 1.0
        elif time_diff.days <= 7:
            return 0.8
        elif time_diff.days <= 30:
            return 0.5
        else:
            return 0.2
    
    def _tag_overlap(self, current_input: str, memory_tags: List[str]) -> float:
        """计算标签重叠度"""
        if not memory_tags:
            return 0.0
        
        input_keywords = extract_keywords(current_input, max_keywords=10)
        overlap = len(set(input_keywords) & set(memory_tags))
        
        return overlap / max(len(memory_tags), 1)
    
    def _load_memory(self):
        """从文件加载记忆"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for category, memory_data_list in data.items():
                        if category in self.memory_categories:
                            memories = []
                            for memory_data in memory_data_list:
                                memory = MemoryFragment(
                                    content=memory_data['content'],
                                    category=MemoryCategory(memory_data['category']),
                                    importance=memory_data['importance'],
                                    tags=memory_data.get('tags', []),
                                    created_at=datetime.fromisoformat(memory_data['created_at']),
                                    last_accessed=datetime.fromisoformat(memory_data.get('last_accessed', memory_data['created_at'])),
                                    access_count=memory_data.get('access_count', 0),
                                    project_id=memory_data.get('project_id', self.project_id)
                                )
                                memories.append(memory)
                            self.memory_categories[category] = memories
            except Exception as e:
                print(f"加载记忆文件失败: {e}")
    
    def _save_memory(self):
        """保存记忆到文件"""
        try:
            data = {}
            for category, memories in self.memory_categories.items():
                data[category] = [
                    {
                        'content': m.content,
                        'category': m.category.value,
                        'importance': m.importance,
                        'tags': m.tags,
                        'created_at': m.created_at.isoformat(),
                        'last_accessed': m.last_accessed.isoformat(),
                        'access_count': m.access_count,
                        'project_id': m.project_id
                    } for m in memories
                ]
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记忆文件失败: {e}")
    
    def _calculate_enhanced_relevance(
        self, 
        memory: MemoryFragment, 
        query: str, 
        current_state: Dict[str, Any]
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
    
    def _analyze_query_intent(self, query: str) -> Dict[str, float]:
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
    
    def _calculate_recall_statistics(self, recall_results: List[Dict]) -> Dict[str, Any]:
        """计算召回统计信息"""
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