"""
优化的状态管理器
实现LRU缓存、异步处理和内存索引的高性能状态管理
"""

import asyncio
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
import hashlib

from .models import PATEOASState, StateTransition, MemoryFragment
from .config import get_config
from .utils import generate_id, ensure_directory


class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.access_times = {}
        self.hit_count = 0
        self.miss_count = 0
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存项"""
        with self._lock:
            if key in self.cache:
                # 移动到末尾（最近使用）
                value = self.cache.pop(key)
                self.cache[key] = value
                self.access_times[key] = time.time()
                self.hit_count += 1
                return value
            else:
                self.miss_count += 1
                return None
    
    def put(self, key: str, value: Any) -> None:
        """添加缓存项"""
        with self._lock:
            if key in self.cache:
                # 更新现有项
                self.cache.pop(key)
            elif len(self.cache) >= self.capacity:
                # 移除最久未使用的项
                oldest_key = next(iter(self.cache))
                self.cache.pop(oldest_key)
                self.access_times.pop(oldest_key, None)
            
            self.cache[key] = value
            self.access_times[key] = time.time()
    
    def remove(self, key: str) -> bool:
        """移除缓存项"""
        with self._lock:
            if key in self.cache:
                self.cache.pop(key)
                self.access_times.pop(key, None)
                return True
            return False
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self.cache.clear()
            self.access_times.clear()
            self.hit_count = 0
            self.miss_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            total_requests = self.hit_count + self.miss_count
            hit_rate = self.hit_count / max(1, total_requests)
            
            return {
                'capacity': self.capacity,
                'size': len(self.cache),
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'hit_rate': hit_rate,
                'total_requests': total_requests
            }


class StateIndex:
    """状态索引，用于快速检索"""
    
    def __init__(self):
        self.project_index = {}  # project_id -> state_keys
        self.timestamp_index = {}  # timestamp -> state_keys
        self.tag_index = {}  # tag -> state_keys
        self.content_hash_index = {}  # content_hash -> state_key
        self._lock = threading.RLock()
    
    def add_state(self, state_key: str, project_id: str, timestamp: datetime, 
                  tags: List[str] = None, content_hash: str = None):
        """添加状态到索引"""
        with self._lock:
            # 项目索引
            if project_id not in self.project_index:
                self.project_index[project_id] = set()
            self.project_index[project_id].add(state_key)
            
            # 时间戳索引（按小时分组）
            hour_key = timestamp.strftime('%Y-%m-%d-%H')
            if hour_key not in self.timestamp_index:
                self.timestamp_index[hour_key] = set()
            self.timestamp_index[hour_key].add(state_key)
            
            # 标签索引
            if tags:
                for tag in tags:
                    if tag not in self.tag_index:
                        self.tag_index[tag] = set()
                    self.tag_index[tag].add(state_key)
            
            # 内容哈希索引
            if content_hash:
                self.content_hash_index[content_hash] = state_key
    
    def find_by_project(self, project_id: str) -> List[str]:
        """根据项目ID查找状态"""
        with self._lock:
            return list(self.project_index.get(project_id, set()))
    
    def find_by_timerange(self, start_time: datetime, end_time: datetime) -> List[str]:
        """根据时间范围查找状态"""
        with self._lock:
            result = set()
            current = start_time
            
            while current <= end_time:
                hour_key = current.strftime('%Y-%m-%d-%H')
                if hour_key in self.timestamp_index:
                    result.update(self.timestamp_index[hour_key])
                current += timedelta(hours=1)
            
            return list(result)
    
    def find_by_tags(self, tags: List[str]) -> List[str]:
        """根据标签查找状态"""
        with self._lock:
            if not tags:
                return []
            
            result = self.tag_index.get(tags[0], set())
            for tag in tags[1:]:
                if tag in self.tag_index:
                    result = result.intersection(self.tag_index[tag])
                else:
                    return []
            
            return list(result)
    
    def find_by_content_hash(self, content_hash: str) -> Optional[str]:
        """根据内容哈希查找状态"""
        with self._lock:
            return self.content_hash_index.get(content_hash)
    
    def remove_state(self, state_key: str):
        """从索引中移除状态"""
        with self._lock:
            # 从所有索引中移除
            for project_states in self.project_index.values():
                project_states.discard(state_key)
            
            for timestamp_states in self.timestamp_index.values():
                timestamp_states.discard(state_key)
            
            for tag_states in self.tag_index.values():
                tag_states.discard(state_key)
            
            # 从内容哈希索引中移除
            to_remove = []
            for hash_key, key in self.content_hash_index.items():
                if key == state_key:
                    to_remove.append(hash_key)
            
            for hash_key in to_remove:
                self.content_hash_index.pop(hash_key)


class AsyncStateProcessor:
    """异步状态处理器"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.pending_operations = {}
        self._lock = threading.RLock()
    
    async def process_state_async(self, operation: str, state_data: Dict[str, Any], 
                                  callback: Optional[callable] = None) -> Any:
        """异步处理状态操作"""
        loop = asyncio.get_event_loop()
        
        # 在线程池中执行状态操作
        future = loop.run_in_executor(
            self.executor, 
            self._execute_state_operation, 
            operation, 
            state_data
        )
        
        # 记录待处理操作
        operation_id = generate_id()
        with self._lock:
            self.pending_operations[operation_id] = {
                'operation': operation,
                'start_time': time.time(),
                'future': future
            }
        
        try:
            result = await future
            
            # 执行回调
            if callback:
                callback(result)
            
            return result
        
        finally:
            # 清理待处理操作
            with self._lock:
                self.pending_operations.pop(operation_id, None)
    
    def _execute_state_operation(self, operation: str, state_data: Dict[str, Any]) -> Any:
        """执行状态操作"""
        if operation == 'serialize':
            return self._serialize_state(state_data)
        elif operation == 'deserialize':
            return self._deserialize_state(state_data)
        elif operation == 'validate':
            return self._validate_state(state_data)
        elif operation == 'compress':
            return self._compress_state(state_data)
        elif operation == 'decompress':
            return self._decompress_state(state_data)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def _serialize_state(self, state_data: Dict[str, Any]) -> str:
        """序列化状态数据"""
        return json.dumps(state_data, ensure_ascii=False, separators=(',', ':'))
    
    def _deserialize_state(self, serialized_data: Dict[str, Any]) -> Dict[str, Any]:
        """反序列化状态数据"""
        if isinstance(serialized_data, str):
            return json.loads(serialized_data)
        return serialized_data
    
    def _validate_state(self, state_data: Dict[str, Any]) -> bool:
        """验证状态数据"""
        required_fields = ['project_id', 'timestamp', 'workflow_state']
        return all(field in state_data for field in required_fields)
    
    def _compress_state(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """压缩状态数据（移除冗余信息）"""
        compressed = state_data.copy()
        
        # 移除空值和默认值
        if 'execution_history' in compressed and not compressed['execution_history']:
            compressed.pop('execution_history')
        
        if 'ai_memory' in compressed and not compressed['ai_memory']:
            compressed.pop('ai_memory')
        
        return compressed
    
    def _decompress_state(self, compressed_data: Dict[str, Any]) -> Dict[str, Any]:
        """解压缩状态数据（恢复默认值）"""
        decompressed = compressed_data.copy()
        
        # 恢复默认值
        if 'execution_history' not in decompressed:
            decompressed['execution_history'] = []
        
        if 'ai_memory' not in decompressed:
            decompressed['ai_memory'] = []
        
        return decompressed
    
    def get_pending_operations(self) -> Dict[str, Any]:
        """获取待处理操作统计"""
        with self._lock:
            return {
                'count': len(self.pending_operations),
                'operations': [
                    {
                        'id': op_id,
                        'operation': op_info['operation'],
                        'duration': time.time() - op_info['start_time']
                    }
                    for op_id, op_info in self.pending_operations.items()
                ]
            }
    
    def shutdown(self):
        """关闭异步处理器"""
        self.executor.shutdown(wait=True)


class OptimizedStateManager:
    """优化的状态管理器"""
    
    def __init__(self, project_id: str = "default", cache_size: int = 1000):
        self.project_id = project_id
        self.config = get_config()
        
        # 核心组件
        self.cache = LRUCache(capacity=cache_size)
        self.index = StateIndex()
        self.async_processor = AsyncStateProcessor()
        
        # 状态存储
        self.current_state: Optional[Dict[str, Any]] = None
        self.state_history: List[Dict[str, Any]] = []
        
        # 性能统计
        self.performance_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'async_operations': 0,
            'sync_operations': 0,
            'average_operation_time': 0.0,
            'total_operations': 0
        }
        
        # 存储配置
        self.state_dir = ensure_directory(Path(self.config.state_storage_path) / "optimized")
        self.state_file = self.state_dir / f"{project_id}_optimized_state.json"
        self.index_file = self.state_dir / f"{project_id}_state_index.json"
        
        # 初始化
        self._load_state_and_index()
        
        print(f"✓ 优化状态管理器已初始化 (项目: {project_id}, 缓存容量: {cache_size})")
    
    def get_current_state(self) -> Dict[str, Any]:
        """获取当前状态（优化版）"""
        start_time = time.time()
        
        # 尝试从缓存获取
        cache_key = f"current_state_{self.project_id}"
        cached_state = self.cache.get(cache_key)
        
        if cached_state:
            self.performance_stats['cache_hits'] += 1
            self._update_performance_stats(time.time() - start_time)
            return cached_state
        
        self.performance_stats['cache_misses'] += 1
        
        # 缓存未命中，构建状态
        if not self.current_state:
            self._initialize_default_state()
        
        state = {
            'project_id': self.project_id,
            'timestamp': datetime.now().isoformat(),
            'project_context': self._get_project_context(),
            'workflow_state': self._get_workflow_state(),
            'ai_memory': self._get_ai_memory(),
            'user_preferences': self._get_user_preferences(),
            'execution_history': self._get_execution_history(),
            'performance_metrics': self._get_performance_metrics()
        }
        
        # 添加到缓存
        self.cache.put(cache_key, state)
        
        # 添加到索引
        content_hash = self._calculate_content_hash(state)
        self.index.add_state(
            state_key=cache_key,
            project_id=self.project_id,
            timestamp=datetime.now(),
            tags=['current', 'active'],
            content_hash=content_hash
        )
        
        self._update_performance_stats(time.time() - start_time)
        return state
    
    async def get_current_state_async(self) -> Dict[str, Any]:
        """异步获取当前状态"""
        self.performance_stats['async_operations'] += 1
        
        # 异步处理状态构建
        state_data = {'project_id': self.project_id}
        
        processed_state = await self.async_processor.process_state_async(
            operation='deserialize',
            state_data=state_data
        )
        
        return self.get_current_state()
    
    def update_state(self, new_information: Dict[str, Any], async_mode: bool = False):
        """更新状态（支持异步模式）"""
        start_time = time.time()
        
        if async_mode:
            return self._update_state_async(new_information)
        else:
            return self._update_state_sync(new_information, start_time)
    
    def _update_state_sync(self, new_information: Dict[str, Any], start_time: float):
        """同步更新状态"""
        self.performance_stats['sync_operations'] += 1
        
        if not self.current_state:
            self._initialize_default_state()
        
        # 记录状态变化
        old_state = self.current_state.copy() if self.current_state else {}
        
        # 更新状态
        self._merge_state_information(new_information)
        
        # 记录状态转换
        transition = {
            'timestamp': datetime.now().isoformat(),
            'changes': self._calculate_state_changes(old_state, self.current_state),
            'trigger': new_information.get('trigger', 'manual_update')
        }
        
        # 添加到历史
        self.state_history.append(transition)
        
        # 保持历史记录在合理范围内
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-50:]
        
        # 更新缓存 - 移除旧缓存，下次获取时会重新构建
        cache_key = f"current_state_{self.project_id}"
        self.cache.remove(cache_key)  # 移除旧缓存
        
        # 保存状态
        self._save_state()
        
        self._update_performance_stats(time.time() - start_time)
    
    async def _update_state_async(self, new_information: Dict[str, Any]):
        """异步更新状态"""
        self.performance_stats['async_operations'] += 1
        
        # 异步处理状态更新
        await self.async_processor.process_state_async(
            operation='validate',
            state_data=new_information,
            callback=lambda result: self._update_state_sync(new_information, time.time())
        )
    
    def get_state_history(self, limit: int = 10, 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """获取状态历史（支持时间范围查询）"""
        start_op_time = time.time()
        
        # 使用索引快速查找
        if start_time and end_time:
            state_keys = self.index.find_by_timerange(start_time, end_time)
            
            # 从缓存或存储中获取状态
            history = []
            for key in state_keys[:limit]:
                cached_state = self.cache.get(key)
                if cached_state:
                    history.append(cached_state)
        else:
            # 返回最近的历史记录
            history = self.state_history[-limit:] if self.state_history else []
        
        self._update_performance_stats(time.time() - start_op_time)
        return history
    
    def find_similar_states(self, target_state: Dict[str, Any], 
                           similarity_threshold: float = 0.8) -> List[Tuple[str, float]]:
        """查找相似状态"""
        start_time = time.time()
        
        target_hash = self._calculate_content_hash(target_state)
        
        # 首先检查是否有完全相同的状态
        exact_match = self.index.find_by_content_hash(target_hash)
        if exact_match:
            self._update_performance_stats(time.time() - start_time)
            return [(exact_match, 1.0)]
        
        # 查找相似状态（简化实现）
        similar_states = []
        
        # 基于项目ID查找候选状态
        project_states = self.index.find_by_project(self.project_id)
        
        for state_key in project_states:
            cached_state = self.cache.get(state_key)
            if cached_state:
                similarity = self._calculate_state_similarity(target_state, cached_state)
                if similarity >= similarity_threshold:
                    similar_states.append((state_key, similarity))
        
        # 按相似度排序
        similar_states.sort(key=lambda x: x[1], reverse=True)
        
        self._update_performance_stats(time.time() - start_time)
        return similar_states[:10]  # 返回前10个最相似的状态
    
    def optimize_cache(self):
        """优化缓存性能"""
        print("🔧 开始缓存优化...")
        
        # 获取缓存统计
        cache_stats = self.cache.get_stats()
        print(f"  - 缓存命中率: {cache_stats['hit_rate']:.2%}")
        print(f"  - 缓存使用率: {cache_stats['size']}/{cache_stats['capacity']}")
        
        # 如果命中率低，增加缓存容量
        if cache_stats['hit_rate'] < 0.7 and cache_stats['size'] >= cache_stats['capacity'] * 0.9:
            new_capacity = int(cache_stats['capacity'] * 1.5)
            print(f"  - 扩展缓存容量: {cache_stats['capacity']} -> {new_capacity}")
            
            # 创建新的更大缓存
            old_cache = self.cache
            self.cache = LRUCache(capacity=new_capacity)
            
            # 迁移热点数据
            for key, value in old_cache.cache.items():
                self.cache.put(key, value)
        
        # 清理过期的索引项
        self._cleanup_expired_index_items()
        
        print("✓ 缓存优化完成")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        cache_stats = self.cache.get_stats()
        pending_ops = self.async_processor.get_pending_operations()
        
        return {
            'cache_performance': cache_stats,
            'operation_stats': self.performance_stats,
            'async_operations': pending_ops,
            'index_stats': {
                'projects': len(self.index.project_index),
                'timestamps': len(self.index.timestamp_index),
                'tags': len(self.index.tag_index),
                'content_hashes': len(self.index.content_hash_index)
            },
            'memory_usage': {
                'state_history_size': len(self.state_history),
                'cache_size': cache_stats['size']
            }
        }
    
    def benchmark_performance(self, num_operations: int = 100) -> Dict[str, Any]:
        """性能基准测试"""
        print(f"🏃 开始性能基准测试 ({num_operations} 次操作)...")
        
        # 测试状态获取性能
        get_times = []
        for i in range(num_operations):
            start_time = time.time()
            self.get_current_state()
            get_times.append(time.time() - start_time)
        
        # 测试状态更新性能
        update_times = []
        for i in range(num_operations // 10):  # 更新操作较少
            start_time = time.time()
            self.update_state({
                'test_update': f'benchmark_{i}',
                'timestamp': datetime.now().isoformat()
            })
            update_times.append(time.time() - start_time)
        
        # 测试缓存性能
        cache_stats = self.cache.get_stats()
        
        avg_get_time = sum(get_times) / len(get_times)
        avg_update_time = sum(update_times) / len(update_times)
        
        performance_grade = 'A' if avg_get_time < 0.001 else 'B' if avg_get_time < 0.01 else 'C'
        
        benchmark_result = {
            'average_get_time': avg_get_time,
            'average_update_time': avg_update_time,
            'operations_per_second': 1.0 / avg_get_time,
            'cache_hit_rate': cache_stats['hit_rate'],
            'performance_grade': performance_grade,
            'total_operations': num_operations,
            'cache_efficiency': cache_stats['hit_rate'] * (1.0 / max(0.001, avg_get_time))
        }
        
        print(f"✓ 基准测试完成:")
        print(f"  - 平均获取时间: {avg_get_time:.6f}s")
        print(f"  - 平均更新时间: {avg_update_time:.6f}s")
        print(f"  - 每秒操作数: {benchmark_result['operations_per_second']:.1f}")
        print(f"  - 缓存命中率: {cache_stats['hit_rate']:.2%}")
        print(f"  - 性能等级: {performance_grade}")
        
        return benchmark_result
    
    def _initialize_default_state(self):
        """初始化默认状态"""
        self.current_state = {
            'project_id': self.project_id,
            'created_at': datetime.now().isoformat(),
            'workflow_state': {
                'current_stage': 'S1',
                'stage_progress': 0.0,
                'completed_stages': [],
                'active_tasks': []
            },
            'project_context': {
                'project_type': 'general',
                'complexity': 'medium',
                'team_size': 1,
                'timeline': 'flexible'
            },
            'ai_memory': [],
            'user_preferences': {},
            'execution_history': []
        }
    
    def _get_project_context(self) -> Dict[str, Any]:
        """获取项目上下文"""
        if self.current_state and 'project_context' in self.current_state:
            return self.current_state['project_context']
        return {
            'project_type': 'general',
            'complexity': 'medium',
            'team_size': 1,
            'timeline': 'flexible'
        }
    
    def _get_workflow_state(self) -> Dict[str, Any]:
        """获取工作流状态"""
        if self.current_state and 'workflow_state' in self.current_state:
            return self.current_state['workflow_state']
        return {
            'current_stage': 'S1',
            'stage_progress': 0.0,
            'completed_stages': [],
            'active_tasks': []
        }
    
    def _get_ai_memory(self) -> List[Dict[str, Any]]:
        """获取AI记忆"""
        if self.current_state and 'ai_memory' in self.current_state:
            return self.current_state['ai_memory']
        return []
    
    def _get_user_preferences(self) -> Dict[str, Any]:
        """获取用户偏好"""
        if self.current_state and 'user_preferences' in self.current_state:
            return self.current_state['user_preferences']
        return {}
    
    def _get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        if self.current_state and 'execution_history' in self.current_state:
            return self.current_state['execution_history']
        return []
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            'cache_hit_rate': self.cache.get_stats()['hit_rate'],
            'total_operations': self.performance_stats['total_operations'],
            'average_operation_time': self.performance_stats['average_operation_time']
        }
    
    def _merge_state_information(self, new_information: Dict[str, Any]):
        """合并状态信息"""
        if not self.current_state:
            self._initialize_default_state()
        
        # 深度合并状态信息
        for key, value in new_information.items():
            if key in self.current_state and isinstance(self.current_state[key], dict) and isinstance(value, dict):
                # 递归合并字典
                self._deep_merge_dict(self.current_state[key], value)
            else:
                self.current_state[key] = value
        
        # 更新时间戳
        self.current_state['last_updated'] = datetime.now().isoformat()
    
    def _deep_merge_dict(self, target: Dict[str, Any], source: Dict[str, Any]):
        """深度合并字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge_dict(target[key], value)
            else:
                target[key] = value
    
    def _calculate_state_changes(self, old_state: Dict[str, Any], new_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """计算状态变化"""
        changes = []
        
        # 简化的变化检测
        for key, new_value in new_state.items():
            if key not in old_state:
                changes.append({
                    'type': 'added',
                    'field': key,
                    'new_value': new_value
                })
            elif old_state[key] != new_value:
                changes.append({
                    'type': 'modified',
                    'field': key,
                    'old_value': old_state[key],
                    'new_value': new_value
                })
        
        for key in old_state:
            if key not in new_state:
                changes.append({
                    'type': 'removed',
                    'field': key,
                    'old_value': old_state[key]
                })
        
        return changes
    
    def _calculate_content_hash(self, state: Dict[str, Any]) -> str:
        """计算状态内容哈希"""
        # 移除时间戳等变化字段
        hashable_state = state.copy()
        hashable_state.pop('timestamp', None)
        hashable_state.pop('last_updated', None)
        
        content_str = json.dumps(hashable_state, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _calculate_state_similarity(self, state1: Dict[str, Any], state2: Dict[str, Any]) -> float:
        """计算状态相似度"""
        # 简化的相似度计算
        common_keys = set(state1.keys()) & set(state2.keys())
        if not common_keys:
            return 0.0
        
        matching_values = 0
        for key in common_keys:
            if state1[key] == state2[key]:
                matching_values += 1
        
        return matching_values / len(common_keys)
    
    def _update_performance_stats(self, operation_time: float):
        """更新性能统计"""
        self.performance_stats['total_operations'] += 1
        
        # 更新平均操作时间
        total_ops = self.performance_stats['total_operations']
        current_avg = self.performance_stats['average_operation_time']
        
        self.performance_stats['average_operation_time'] = (
            (current_avg * (total_ops - 1) + operation_time) / total_ops
        )
    
    def _cleanup_expired_index_items(self):
        """清理过期的索引项"""
        # 清理超过24小时的时间戳索引
        cutoff_time = datetime.now() - timedelta(hours=24)
        expired_hours = []
        
        for hour_key in self.index.timestamp_index.keys():
            try:
                hour_time = datetime.strptime(hour_key, '%Y-%m-%d-%H')
                if hour_time < cutoff_time:
                    expired_hours.append(hour_key)
            except ValueError:
                expired_hours.append(hour_key)  # 无效格式也清理
        
        for hour_key in expired_hours:
            self.index.timestamp_index.pop(hour_key, None)
    
    def _load_state_and_index(self):
        """加载状态和索引"""
        try:
            # 加载状态
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_state = data.get('current_state')
                    self.state_history = data.get('state_history', [])
                    self.performance_stats.update(data.get('performance_stats', {}))
            
            # 加载索引
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    # 重建索引，将列表转换为集合
                    project_index_data = index_data.get('project_index', {})
                    self.index.project_index = {k: set(v) for k, v in project_index_data.items()}
                    
                    tag_index_data = index_data.get('tag_index', {})
                    self.index.tag_index = {k: set(v) for k, v in tag_index_data.items()}
                    
        except Exception as e:
            print(f"⚠️ 加载状态失败: {e}")
            self._initialize_default_state()
    
    def _save_state(self):
        """保存状态和索引"""
        try:
            # 保存状态
            state_data = {
                'current_state': self.current_state,
                'state_history': self.state_history,
                'performance_stats': self.performance_stats,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            
            # 保存索引
            index_data = {
                'project_index': {k: list(v) for k, v in self.index.project_index.items()},
                'tag_index': {k: list(v) for k, v in self.index.tag_index.items()},
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ 保存状态失败: {e}")
    
    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            self.async_processor.shutdown()
        except:
            pass