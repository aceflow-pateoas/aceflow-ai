"""
优化的记忆检索系统
实现向量索引、语义缓存和高性能记忆检索
"""

import json
import time
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from collections import defaultdict, OrderedDict
import numpy as np
from dataclasses import dataclass, field

from .models import MemoryFragment, MemoryCategory
from .config import get_config
from .utils import ensure_directory, calculate_similarity


@dataclass
class VectorIndex:
    """向量索引数据结构"""
    memory_id: str
    vector: np.ndarray
    category: str
    importance: float
    timestamp: datetime
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'memory_id': self.memory_id,
            'vector': self.vector.tolist(),
            'category': self.category,
            'importance': self.importance,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorIndex':
        """从字典创建向量索引"""
        return cls(
            memory_id=data['memory_id'],
            vector=np.array(data['vector']),
            category=data['category'],
            importance=data['importance'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            tags=data.get('tags', [])
        )


@dataclass
class SemanticCacheEntry:
    """语义缓存条目"""
    query_hash: str
    query_text: str
    results: List[Dict[str, Any]]
    timestamp: datetime
    access_count: int = 0
    last_access: Optional[datetime] = None
    
    def update_access(self):
        """更新访问信息"""
        self.access_count += 1
        self.last_access = datetime.now()
    
    def is_expired(self, ttl_hours: int = 24) -> bool:
        """检查是否过期"""
        if not self.last_access:
            return (datetime.now() - self.timestamp).total_seconds() > ttl_hours * 3600
        return (datetime.now() - self.last_access).total_seconds() > ttl_hours * 3600


class VectorIndexManager:
    """向量索引管理器"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.indices: Dict[str, VectorIndex] = {}
        self.category_indices: Dict[str, Set[str]] = defaultdict(set)
        self.tag_indices: Dict[str, Set[str]] = defaultdict(set)
        self.importance_sorted: List[str] = []  # 按重要性排序的记忆ID
        self._lock = threading.RLock()
        
        # 性能统计
        self.stats = {
            'total_vectors': 0,
            'search_count': 0,
            'average_search_time': 0.0,
            'cache_hits': 0,
            'index_updates': 0
        }
    
    def add_vector(self, memory_id: str, content: str, category: str, 
                   importance: float, tags: List[str] = None) -> bool:
        """添加向量到索引"""
        with self._lock:
            try:
                # 生成向量表示
                vector = self._text_to_vector(content)
                
                # 创建向量索引
                index_entry = VectorIndex(
                    memory_id=memory_id,
                    vector=vector,
                    category=category,
                    importance=importance,
                    timestamp=datetime.now(),
                    tags=tags or []
                )
                
                # 添加到主索引
                self.indices[memory_id] = index_entry
                
                # 更新分类索引
                self.category_indices[category].add(memory_id)
                
                # 更新标签索引
                for tag in (tags or []):
                    self.tag_indices[tag].add(memory_id)
                
                # 更新重要性排序
                self._update_importance_sorting()
                
                # 更新统计
                self.stats['total_vectors'] += 1
                self.stats['index_updates'] += 1
                
                return True
                
            except Exception as e:
                print(f"添加向量索引失败: {e}")
                return False
    
    def search_similar(self, query: str, limit: int = 10, 
                      category_filter: Optional[str] = None,
                      tag_filter: Optional[List[str]] = None,
                      min_similarity: float = 0.3) -> List[Tuple[str, float]]:
        """搜索相似向量"""
        start_time = time.time()
        
        with self._lock:
            try:
                # 生成查询向量
                query_vector = self._text_to_vector(query)
                
                # 获取候选记忆ID
                candidate_ids = self._get_candidate_ids(category_filter, tag_filter)
                
                # 计算相似度
                similarities = []
                for memory_id in candidate_ids:
                    if memory_id in self.indices:
                        index_entry = self.indices[memory_id]
                        similarity = self._cosine_similarity(query_vector, index_entry.vector)
                        
                        if similarity >= min_similarity:
                            similarities.append((memory_id, similarity))
                
                # 按相似度排序
                similarities.sort(key=lambda x: x[1], reverse=True)
                
                # 更新统计
                search_time = time.time() - start_time
                self.stats['search_count'] += 1
                self._update_average_search_time(search_time)
                
                return similarities[:limit]
                
            except Exception as e:
                print(f"向量搜索失败: {e}")
                return []
    
    def get_top_important(self, limit: int = 10, 
                         category_filter: Optional[str] = None) -> List[str]:
        """获取最重要的记忆"""
        with self._lock:
            if category_filter:
                filtered_ids = [
                    mid for mid in self.importance_sorted 
                    if mid in self.indices and self.indices[mid].category == category_filter
                ]
                return filtered_ids[:limit]
            else:
                return self.importance_sorted[:limit]
    
    def remove_vector(self, memory_id: str) -> bool:
        """移除向量索引"""
        with self._lock:
            if memory_id not in self.indices:
                return False
            
            index_entry = self.indices[memory_id]
            
            # 从主索引移除
            del self.indices[memory_id]
            
            # 从分类索引移除
            self.category_indices[index_entry.category].discard(memory_id)
            
            # 从标签索引移除
            for tag in index_entry.tags:
                self.tag_indices[tag].discard(memory_id)
            
            # 从重要性排序移除
            if memory_id in self.importance_sorted:
                self.importance_sorted.remove(memory_id)
            
            # 更新统计
            self.stats['total_vectors'] -= 1
            
            return True
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            return {
                **self.stats,
                'categories': len(self.category_indices),
                'tags': len(self.tag_indices),
                'dimension': self.dimension
            }
    
    def _text_to_vector(self, text: str) -> np.ndarray:
        """将文本转换为向量（简化实现）"""
        # 这里使用简化的向量化方法
        # 在实际应用中，可以使用更复杂的嵌入模型如BERT、Sentence-BERT等
        
        # 基于字符频率的简单向量化
        vector = np.zeros(self.dimension)
        
        # 计算字符频率
        char_freq = {}
        for char in text.lower():
            if char.isalnum():
                char_freq[char] = char_freq.get(char, 0) + 1
        
        # 将字符频率映射到向量维度
        for i, char in enumerate('abcdefghijklmnopqrstuvwxyz0123456789'):
            if i < self.dimension:
                vector[i] = char_freq.get(char, 0)
        
        # 添加文本长度特征
        if self.dimension > 36:
            vector[36] = len(text)
            vector[37] = len(text.split())
        
        # 添加关键词特征
        keywords = ['项目', '需求', '设计', '实现', '测试', '部署', '问题', '解决', '学习', '决策']
        for i, keyword in enumerate(keywords):
            if 38 + i < self.dimension:
                vector[38 + i] = text.count(keyword)
        
        # 标准化向量
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _get_candidate_ids(self, category_filter: Optional[str], 
                          tag_filter: Optional[List[str]]) -> Set[str]:
        """获取候选记忆ID"""
        if category_filter and tag_filter:
            # 同时过滤分类和标签
            category_ids = self.category_indices.get(category_filter, set())
            tag_ids = set()
            for tag in tag_filter:
                tag_ids.update(self.tag_indices.get(tag, set()))
            return category_ids.intersection(tag_ids)
        
        elif category_filter:
            return self.category_indices.get(category_filter, set())
        
        elif tag_filter:
            tag_ids = set()
            for tag in tag_filter:
                tag_ids.update(self.tag_indices.get(tag, set()))
            return tag_ids
        
        else:
            return set(self.indices.keys())
    
    def _update_importance_sorting(self):
        """更新重要性排序"""
        self.importance_sorted = sorted(
            self.indices.keys(),
            key=lambda mid: self.indices[mid].importance,
            reverse=True
        )
    
    def _update_average_search_time(self, search_time: float):
        """更新平均搜索时间"""
        count = self.stats['search_count']
        current_avg = self.stats['average_search_time']
        self.stats['average_search_time'] = (current_avg * (count - 1) + search_time) / count


class SemanticCache:
    """语义缓存系统"""
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self.cache: OrderedDict[str, SemanticCacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # 统计信息
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_queries': 0
        }
    
    def get(self, query: str, similarity_threshold: float = 0.9) -> Optional[List[Dict[str, Any]]]:
        """获取缓存结果"""
        with self._lock:
            query_hash = self._hash_query(query)
            
            # 检查精确匹配
            if query_hash in self.cache:
                entry = self.cache[query_hash]
                if not entry.is_expired(self.ttl_hours):
                    entry.update_access()
                    # 移动到末尾（LRU）
                    self.cache.move_to_end(query_hash)
                    self.stats['hits'] += 1
                    return entry.results
                else:
                    # 过期，删除
                    del self.cache[query_hash]
            
            # 检查语义相似的查询
            for cached_hash, entry in self.cache.items():
                if not entry.is_expired(self.ttl_hours):
                    similarity = self._calculate_query_similarity(query, entry.query_text)
                    if similarity >= similarity_threshold:
                        entry.update_access()
                        self.cache.move_to_end(cached_hash)
                        self.stats['hits'] += 1
                        return entry.results
            
            self.stats['misses'] += 1
            return None
    
    def put(self, query: str, results: List[Dict[str, Any]]):
        """添加缓存结果"""
        with self._lock:
            query_hash = self._hash_query(query)
            
            # 检查容量
            if len(self.cache) >= self.max_size:
                # 移除最久未使用的项
                oldest_hash, _ = self.cache.popitem(last=False)
                self.stats['evictions'] += 1
            
            # 添加新条目
            entry = SemanticCacheEntry(
                query_hash=query_hash,
                query_text=query,
                results=results,
                timestamp=datetime.now()
            )
            entry.update_access()
            
            self.cache[query_hash] = entry
            self.stats['total_queries'] += 1
    
    def clear_expired(self):
        """清理过期缓存"""
        with self._lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired(self.ttl_hours)
            ]
            
            for key in expired_keys:
                del self.cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / max(1, total_requests)
            
            return {
                **self.stats,
                'hit_rate': hit_rate,
                'cache_size': len(self.cache),
                'max_size': self.max_size
            }
    
    def _hash_query(self, query: str) -> str:
        """生成查询哈希"""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def _calculate_query_similarity(self, query1: str, query2: str) -> float:
        """计算查询相似度（简化实现）"""
        # 简单的基于词汇重叠的相似度计算
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        # 增加基于字符相似度的计算
        char_similarity = self._calculate_char_similarity(query1.lower(), query2.lower())
        word_similarity = len(intersection) / len(union)
        
        # 综合相似度
        return word_similarity * 0.7 + char_similarity * 0.3
    
    def _calculate_char_similarity(self, str1: str, str2: str) -> float:
        """计算字符级相似度"""
        if not str1 or not str2:
            return 0.0
        
        # 简单的编辑距离相似度
        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return 1.0
        
        # 计算公共子串
        common_chars = 0
        for char in set(str1):
            common_chars += min(str1.count(char), str2.count(char))
        
        return common_chars / max_len


class OptimizedMemoryRetrieval:
    """优化的记忆检索系统"""
    
    def __init__(self, project_id: str = "default", vector_dimension: int = 384):
        self.project_id = project_id
        self.config = get_config()
        
        # 核心组件
        self.vector_index = VectorIndexManager(dimension=vector_dimension)
        self.semantic_cache = SemanticCache(max_size=1000, ttl_hours=24)
        
        # 记忆存储
        self.memories: Dict[str, MemoryFragment] = {}
        self.memory_metadata: Dict[str, Dict[str, Any]] = {}
        
        # 性能统计
        self.performance_stats = {
            'total_retrievals': 0,
            'cache_hits': 0,
            'vector_searches': 0,
            'average_retrieval_time': 0.0,
            'total_memories': 0
        }
        
        # 存储路径
        self.storage_dir = ensure_directory(Path(self.config.memory_storage_path) / "optimized")
        self.memories_file = self.storage_dir / f"{project_id}_memories.json"
        self.index_file = self.storage_dir / f"{project_id}_vector_index.json"
        
        # 加载现有数据
        self._load_memories_and_index()
        
        print(f"✓ 优化记忆检索系统已初始化 (项目: {project_id}, 向量维度: {vector_dimension})")
    
    def add_memory(self, content: str, category: str, importance: float = 0.5, 
                   tags: List[str] = None) -> str:
        """添加记忆"""
        start_time = time.time()
        
        # 生成记忆ID
        memory_id = f"mem_{int(time.time() * 1000)}_{hash(content) % 10000}"
        
        # 创建记忆片段
        memory = MemoryFragment(
            content=content,
            category=MemoryCategory(category),
            importance=importance,
            tags=tags or [],
            created_at=datetime.now(),
            project_id=self.project_id
        )
        
        # 存储记忆
        self.memories[memory_id] = memory
        self.memory_metadata[memory_id] = {
            'access_count': 0,
            'last_access': None,
            'creation_time': time.time()
        }
        
        # 添加到向量索引
        success = self.vector_index.add_vector(
            memory_id=memory_id,
            content=content,
            category=category,
            importance=importance,
            tags=tags or []
        )
        
        if success:
            self.performance_stats['total_memories'] += 1
            
            # 清理语义缓存（因为添加了新记忆）
            self.semantic_cache.cache.clear()
            
            # 保存数据
            self._save_memories_and_index()
        
        processing_time = time.time() - start_time
        print(f"✓ 记忆已添加 (ID: {memory_id}, 处理时间: {processing_time:.4f}s)")
        
        return memory_id
    
    def search_memories(self, query: str, limit: int = 10, 
                       category: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       min_similarity: float = 0.3,
                       use_cache: bool = True) -> Dict[str, Any]:
        """搜索记忆"""
        start_time = time.time()
        self.performance_stats['total_retrievals'] += 1
        
        # 尝试从语义缓存获取
        if use_cache:
            cached_results = self.semantic_cache.get(query, similarity_threshold=0.85)
            if cached_results is not None:
                self.performance_stats['cache_hits'] += 1
                processing_time = time.time() - start_time
                self._update_average_retrieval_time(processing_time)
                
                return {
                    'query': query,
                    'results': cached_results,
                    'total_found': len(cached_results),
                    'processing_time': processing_time,
                    'source': 'cache'
                }
        
        # 使用向量索引搜索
        self.performance_stats['vector_searches'] += 1
        
        similar_ids = self.vector_index.search_similar(
            query=query,
            limit=limit * 2,  # 获取更多候选，然后过滤
            category_filter=category,
            tag_filter=tags,
            min_similarity=min_similarity
        )
        
        # 构建结果
        results = []
        for memory_id, similarity in similar_ids:
            if memory_id in self.memories:
                memory = self.memories[memory_id]
                metadata = self.memory_metadata.get(memory_id, {})
                
                # 更新访问统计
                metadata['access_count'] = metadata.get('access_count', 0) + 1
                metadata['last_access'] = datetime.now().isoformat()
                
                result = {
                    'memory_id': memory_id,
                    'content': memory.content,
                    'category': memory.category.value,
                    'importance': memory.importance,
                    'similarity': similarity,
                    'tags': memory.tags,
                    'created_at': memory.created_at.isoformat(),
                    'access_count': metadata['access_count']
                }
                results.append(result)
        
        # 按相似度和重要性综合排序
        results.sort(key=lambda x: x['similarity'] * 0.7 + x['importance'] * 0.3, reverse=True)
        results = results[:limit]
        
        # 缓存结果
        if use_cache and results:
            self.semantic_cache.put(query, results)
        
        processing_time = time.time() - start_time
        self._update_average_retrieval_time(processing_time)
        
        return {
            'query': query,
            'results': results,
            'total_found': len(results),
            'processing_time': processing_time,
            'source': 'vector_search'
        }
    
    def search_memories_optimized(self, query: str, limit: int = 10,
                                 category: Optional[str] = None,
                                 min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """优化的记忆搜索（兼容接口）"""
        result = self.search_memories(
            query=query,
            limit=limit,
            category=category,
            min_similarity=min_similarity
        )
        return result['results']
    
    def get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取记忆"""
        if memory_id not in self.memories:
            return None
        
        memory = self.memories[memory_id]
        metadata = self.memory_metadata.get(memory_id, {})
        
        # 更新访问统计
        metadata['access_count'] = metadata.get('access_count', 0) + 1
        metadata['last_access'] = datetime.now().isoformat()
        
        return {
            'memory_id': memory_id,
            'content': memory.content,
            'category': memory.category.value,
            'importance': memory.importance,
            'tags': memory.tags,
            'created_at': memory.created_at.isoformat(),
            'access_count': metadata['access_count']
        }
    
    def get_top_memories(self, limit: int = 10, 
                        category: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取最重要的记忆"""
        top_ids = self.vector_index.get_top_important(limit=limit, category_filter=category)
        
        results = []
        for memory_id in top_ids:
            if memory_id in self.memories:
                memory_data = self.get_memory_by_id(memory_id)
                if memory_data:
                    results.append(memory_data)
        
        return results
    
    def remove_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        if memory_id not in self.memories:
            return False
        
        # 从记忆存储中删除
        del self.memories[memory_id]
        self.memory_metadata.pop(memory_id, None)
        
        # 从向量索引中删除
        self.vector_index.remove_vector(memory_id)
        
        # 清理语义缓存
        self.semantic_cache.cache.clear()
        
        # 更新统计
        self.performance_stats['total_memories'] -= 1
        
        # 保存数据
        self._save_memories_and_index()
        
        return True
    
    def optimize_indices(self):
        """优化索引"""
        print("🔧 开始索引优化...")
        
        # 清理过期缓存
        self.semantic_cache.clear_expired()
        
        # 重建向量索引（如果需要）
        if len(self.memories) != self.vector_index.stats['total_vectors']:
            print("  - 重建向量索引...")
            self._rebuild_vector_index()
        
        # 优化内存使用
        self._optimize_memory_usage()
        
        print("✓ 索引优化完成")
    
    def benchmark_performance(self, num_queries: int = 100) -> Dict[str, Any]:
        """性能基准测试"""
        print(f"🏃 开始记忆检索性能基准测试 ({num_queries} 次查询)...")
        
        # 准备测试查询
        test_queries = [
            "项目需求分析",
            "系统架构设计",
            "数据库优化",
            "用户界面设计",
            "性能测试",
            "部署配置",
            "错误处理",
            "安全考虑",
            "代码重构",
            "文档编写"
        ]
        
        # 扩展查询列表
        extended_queries = []
        for i in range(num_queries):
            base_query = test_queries[i % len(test_queries)]
            extended_queries.append(f"{base_query} {i}")
        
        # 测试向量搜索性能
        vector_times = []
        for query in extended_queries:
            start_time = time.time()
            self.search_memories(query, limit=5, use_cache=False)
            vector_times.append(time.time() - start_time)
        
        # 测试缓存性能
        cache_times = []
        for query in extended_queries[:num_queries//2]:  # 重复查询测试缓存
            start_time = time.time()
            self.search_memories(query, limit=5, use_cache=True)
            cache_times.append(time.time() - start_time)
        
        # 计算统计
        avg_vector_time = sum(vector_times) / len(vector_times)
        avg_cache_time = sum(cache_times) / len(cache_times)
        
        # 获取缓存统计
        cache_stats = self.semantic_cache.get_stats()
        vector_stats = self.vector_index.get_stats()
        
        benchmark_result = {
            'average_search_time': avg_vector_time,
            'average_cache_time': avg_cache_time,
            'queries_per_second': 1.0 / avg_vector_time,
            'cache_hit_rate': cache_stats['hit_rate'],
            'cache_speedup': avg_vector_time / max(0.001, avg_cache_time),
            'total_memories': self.performance_stats['total_memories'],
            'vector_dimension': self.vector_index.dimension,
            'performance_grade': self._calculate_performance_grade(avg_vector_time)
        }
        
        print(f"✓ 基准测试完成:")
        print(f"  - 平均搜索时间: {avg_vector_time:.6f}s")
        print(f"  - 平均缓存时间: {avg_cache_time:.6f}s")
        print(f"  - 每秒查询数: {benchmark_result['queries_per_second']:.1f}")
        print(f"  - 缓存命中率: {cache_stats['hit_rate']:.2%}")
        print(f"  - 缓存加速比: {benchmark_result['cache_speedup']:.1f}x")
        print(f"  - 性能等级: {benchmark_result['performance_grade']}")
        
        return benchmark_result
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        return {
            'retrieval_stats': self.performance_stats,
            'vector_index_stats': self.vector_index.get_stats(),
            'semantic_cache_stats': self.semantic_cache.get_stats(),
            'memory_count': len(self.memories),
            'index_health': self._assess_index_health()
        }
    
    def _rebuild_vector_index(self):
        """重建向量索引"""
        # 清空现有索引
        self.vector_index = VectorIndexManager(dimension=self.vector_index.dimension)
        
        # 重新添加所有记忆
        for memory_id, memory in self.memories.items():
            self.vector_index.add_vector(
                memory_id=memory_id,
                content=memory.content,
                category=memory.category.value,
                importance=memory.importance,
                tags=memory.tags
            )
    
    def _optimize_memory_usage(self):
        """优化内存使用"""
        # 清理长时间未访问的记忆元数据
        current_time = time.time()
        cutoff_time = current_time - (30 * 24 * 3600)  # 30天
        
        to_remove = []
        for memory_id, metadata in self.memory_metadata.items():
            last_access = metadata.get('last_access')
            if last_access:
                try:
                    last_access_time = datetime.fromisoformat(last_access).timestamp()
                    if last_access_time < cutoff_time:
                        to_remove.append(memory_id)
                except:
                    pass
        
        # 移除过期元数据（但保留记忆本身）
        for memory_id in to_remove:
            if self.memory_metadata[memory_id].get('access_count', 0) == 0:
                # 只移除从未被访问的记忆的元数据
                self.memory_metadata.pop(memory_id, None)
    
    def _update_average_retrieval_time(self, retrieval_time: float):
        """更新平均检索时间"""
        count = self.performance_stats['total_retrievals']
        current_avg = self.performance_stats['average_retrieval_time']
        
        self.performance_stats['average_retrieval_time'] = (
            (current_avg * (count - 1) + retrieval_time) / count
        )
    
    def _calculate_performance_grade(self, avg_time: float) -> str:
        """计算性能等级"""
        if avg_time < 0.001:
            return 'A+'
        elif avg_time < 0.005:
            return 'A'
        elif avg_time < 0.01:
            return 'B'
        elif avg_time < 0.05:
            return 'C'
        else:
            return 'D'
    
    def _assess_index_health(self) -> Dict[str, Any]:
        """评估索引健康度"""
        vector_stats = self.vector_index.get_stats()
        cache_stats = self.semantic_cache.get_stats()
        
        # 计算健康分数
        vector_health = min(1.0, vector_stats['total_vectors'] / max(1, len(self.memories)))
        cache_health = cache_stats['hit_rate']
        search_health = min(1.0, 1.0 / max(0.001, vector_stats['average_search_time']))
        
        overall_health = (vector_health * 0.4 + cache_health * 0.3 + search_health * 0.3)
        
        return {
            'overall_health': overall_health,
            'vector_index_health': vector_health,
            'cache_health': cache_health,
            'search_performance_health': search_health,
            'status': 'excellent' if overall_health > 0.8 else 'good' if overall_health > 0.6 else 'fair'
        }
    
    def _load_memories_and_index(self):
        """加载记忆和索引"""
        try:
            # 加载记忆
            if self.memories_file.exists():
                with open(self.memories_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 恢复记忆
                    for memory_id, memory_data in data.get('memories', {}).items():
                        memory = MemoryFragment(
                            content=memory_data['content'],
                            category=MemoryCategory(memory_data['category']),
                            importance=memory_data['importance'],
                            tags=memory_data.get('tags', []),
                            created_at=datetime.fromisoformat(memory_data['created_at']),
                            project_id=memory_data.get('project_id', self.project_id)
                        )
                        self.memories[memory_id] = memory
                    
                    # 恢复元数据
                    self.memory_metadata = data.get('metadata', {})
                    self.performance_stats.update(data.get('performance_stats', {}))
            
            # 加载向量索引
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    
                    # 恢复向量索引
                    for memory_id, vector_data in index_data.get('indices', {}).items():
                        try:
                            vector_index = VectorIndex.from_dict(vector_data)
                            self.vector_index.indices[memory_id] = vector_index
                            
                            # 重建分类和标签索引
                            self.vector_index.category_indices[vector_index.category].add(memory_id)
                            for tag in vector_index.tags:
                                self.vector_index.tag_indices[tag].add(memory_id)
                        except Exception as e:
                            print(f"恢复向量索引失败 {memory_id}: {e}")
                    
                    # 更新统计和排序
                    self.vector_index.stats.update(index_data.get('stats', {}))
                    self.vector_index._update_importance_sorting()
            
            # 如果记忆和索引不匹配，重建索引
            if len(self.memories) != len(self.vector_index.indices):
                print("⚠️ 记忆和索引不匹配，重建向量索引...")
                self._rebuild_vector_index()
                
        except Exception as e:
            print(f"⚠️ 加载记忆和索引失败: {e}")
    
    def _save_memories_and_index(self):
        """保存记忆和索引"""
        try:
            # 保存记忆
            memories_data = {
                'memories': {
                    memory_id: {
                        'content': memory.content,
                        'category': memory.category.value,
                        'importance': memory.importance,
                        'tags': memory.tags,
                        'created_at': memory.created_at.isoformat(),
                        'project_id': memory.project_id
                    }
                    for memory_id, memory in self.memories.items()
                },
                'metadata': self.memory_metadata,
                'performance_stats': self.performance_stats,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.memories_file, 'w', encoding='utf-8') as f:
                json.dump(memories_data, f, ensure_ascii=False, indent=2)
            
            # 保存向量索引
            index_data = {
                'indices': {
                    memory_id: vector_index.to_dict()
                    for memory_id, vector_index in self.vector_index.indices.items()
                },
                'stats': self.vector_index.stats,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ 保存记忆和索引失败: {e}")
    
    def __del__(self):
        """析构函数，确保数据保存"""
        try:
            self._save_memories_and_index()
        except:
            pass