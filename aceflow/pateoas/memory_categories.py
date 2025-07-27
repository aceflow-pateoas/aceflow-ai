"""
记忆分类存储系统
为不同类型的记忆提供专门的存储和检索机制
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
from pathlib import Path

from .models import MemoryFragment, MemoryCategory
from .utils import calculate_similarity, extract_keywords, is_recent


class BaseMemoryStore(ABC):
    """记忆存储基类"""
    
    def __init__(self, category: MemoryCategory, storage_path: Path):
        self.category = category
        self.storage_path = storage_path
        self.memories: List[MemoryFragment] = []
        self.load_memories()
    
    @abstractmethod
    def store(self, memory: MemoryFragment) -> bool:
        """存储记忆"""
        pass
    
    @abstractmethod
    def search_similar(self, query: str, context: Dict[str, Any], limit: int = 5) -> List[MemoryFragment]:
        """搜索相似记忆"""
        pass
    
    def get_all_memories(self) -> List[MemoryFragment]:
        """获取所有记忆"""
        return self.memories.copy()
    
    def get_recent_memories(self, hours: int = 24) -> List[MemoryFragment]:
        """获取最近的记忆"""
        return [m for m in self.memories if is_recent(m.last_accessed, hours)]
    
    def get_important_memories(self, threshold: float = 0.7) -> List[MemoryFragment]:
        """获取重要记忆"""
        return [m for m in self.memories if m.importance >= threshold]
    
    def cleanup_old_memories(self, days: int = 90) -> int:
        """清理旧记忆"""
        cutoff_date = datetime.now() - timedelta(days=days)
        original_count = len(self.memories)
        
        # 保留重要记忆和最近访问的记忆
        self.memories = [
            m for m in self.memories 
            if m.importance > 0.7 or m.last_accessed > cutoff_date or m.created_at > cutoff_date
        ]
        
        cleaned_count = original_count - len(self.memories)
        if cleaned_count > 0:
            self.save_memories()
        
        return cleaned_count
    
    def load_memories(self):
        """从文件加载记忆"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    self.memories = []
                    for memory_data in data:
                        memory = MemoryFragment(
                            content=memory_data['content'],
                            category=MemoryCategory(memory_data['category']),
                            importance=memory_data['importance'],
                            tags=memory_data.get('tags', []),
                            created_at=datetime.fromisoformat(memory_data['created_at']),
                            last_accessed=datetime.fromisoformat(memory_data.get('last_accessed', memory_data['created_at'])),
                            access_count=memory_data.get('access_count', 0),
                            project_id=memory_data.get('project_id')
                        )
                        self.memories.append(memory)
            except Exception as e:
                print(f"加载{self.category.value}记忆失败: {e}")
    
    def save_memories(self):
        """保存记忆到文件"""
        try:
            data = [
                {
                    'content': m.content,
                    'category': m.category.value,
                    'importance': m.importance,
                    'tags': m.tags,
                    'created_at': m.created_at.isoformat(),
                    'last_accessed': m.last_accessed.isoformat(),
                    'access_count': m.access_count,
                    'project_id': m.project_id
                } for m in self.memories
            ]
            
            # 确保目录存在
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存{self.category.value}记忆失败: {e}")


class RequirementsMemory(BaseMemoryStore):
    """需求记忆存储"""
    
    def __init__(self, storage_path: Path):
        super().__init__(MemoryCategory.REQUIREMENT, storage_path)
    
    def store(self, memory: MemoryFragment) -> bool:
        """存储需求记忆"""
        if memory.category != MemoryCategory.REQUIREMENT:
            return False
        
        # 检查是否已存在相似需求
        for existing in self.memories:
            if calculate_similarity(memory.content, existing.content) > 0.8:
                # 更新现有记忆而不是添加新的
                existing.importance = max(existing.importance, memory.importance)
                existing.tags = list(set(existing.tags + memory.tags))
                existing.last_accessed = datetime.now()
                self.save_memories()
                return True
        
        self.memories.append(memory)
        self.save_memories()
        return True
    
    def search_similar(self, query: str, context: Dict[str, Any], limit: int = 5) -> List[MemoryFragment]:
        """搜索相似需求"""
        scored_memories = []
        
        for memory in self.memories:
            # 计算相似度
            similarity = calculate_similarity(query, memory.content)
            
            # 需求相关性加权
            if any(keyword in query.lower() for keyword in ['需求', '功能', '特性', 'requirement', 'feature']):
                similarity *= 1.2
            
            # 标签匹配加权
            query_keywords = extract_keywords(query, max_keywords=5)
            tag_overlap = len(set(query_keywords) & set(memory.tags))
            if tag_overlap > 0:
                similarity += tag_overlap * 0.1
            
            if similarity > 0.3:
                scored_memories.append((memory, similarity))
        
        # 按相似度排序
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # 更新访问记录
        results = []
        for memory, score in scored_memories[:limit]:
            memory.access()
            results.append(memory)
        
        if results:
            self.save_memories()
        
        return results
    
    def get_functional_requirements(self) -> List[MemoryFragment]:
        """获取功能性需求"""
        return [m for m in self.memories if any(tag in ['功能', '特性', 'function', 'feature'] for tag in m.tags)]
    
    def get_non_functional_requirements(self) -> List[MemoryFragment]:
        """获取非功能性需求"""
        return [m for m in self.memories if any(tag in ['性能', '安全', '可用性', 'performance', 'security', 'usability'] for tag in m.tags)]


class DecisionMemory(BaseMemoryStore):
    """决策记忆存储"""
    
    def __init__(self, storage_path: Path):
        super().__init__(MemoryCategory.DECISION, storage_path)
    
    def store(self, memory: MemoryFragment) -> bool:
        """存储决策记忆"""
        if memory.category != MemoryCategory.DECISION:
            return False
        
        # 决策记忆通常都是重要的，提升重要性
        memory.importance = min(1.0, memory.importance + 0.1)
        
        self.memories.append(memory)
        self.save_memories()
        return True
    
    def search_similar(self, query: str, context: Dict[str, Any], limit: int = 5) -> List[MemoryFragment]:
        """搜索相似决策"""
        scored_memories = []
        
        for memory in self.memories:
            similarity = calculate_similarity(query, memory.content)
            
            # 决策相关性加权
            if any(keyword in query.lower() for keyword in ['决策', '选择', '方案', 'decision', 'choice', 'solution']):
                similarity *= 1.3
            
            # 技术决策特别加权
            if any(keyword in query.lower() for keyword in ['技术', '架构', '框架', 'technology', 'architecture', 'framework']):
                if any(tag in ['技术', '架构', 'tech', 'architecture'] for tag in memory.tags):
                    similarity *= 1.2
            
            if similarity > 0.3:
                scored_memories.append((memory, similarity))
        
        scored_memories.sort(key=lambda x: (x[1], x[0].importance), reverse=True)
        
        results = []
        for memory, score in scored_memories[:limit]:
            memory.access()
            results.append(memory)
        
        if results:
            self.save_memories()
        
        return results
    
    def get_technical_decisions(self) -> List[MemoryFragment]:
        """获取技术决策"""
        return [m for m in self.memories if any(tag in ['技术', '架构', '框架', 'tech', 'architecture', 'framework'] for tag in m.tags)]
    
    def get_business_decisions(self) -> List[MemoryFragment]:
        """获取业务决策"""
        return [m for m in self.memories if any(tag in ['业务', '产品', '商业', 'business', 'product'] for tag in m.tags)]


class PatternMemory(BaseMemoryStore):
    """模式记忆存储"""
    
    def __init__(self, storage_path: Path):
        super().__init__(MemoryCategory.PATTERN, storage_path)
    
    def store(self, memory: MemoryFragment) -> bool:
        """存储模式记忆"""
        if memory.category != MemoryCategory.PATTERN:
            return False
        
        self.memories.append(memory)
        self.save_memories()
        return True
    
    def search_similar(self, query: str, context: Dict[str, Any], limit: int = 5) -> List[MemoryFragment]:
        """搜索相似模式"""
        scored_memories = []
        
        for memory in self.memories:
            similarity = calculate_similarity(query, memory.content)
            
            # 模式相关性加权
            if any(keyword in query.lower() for keyword in ['模式', '规律', '趋势', 'pattern', 'trend']):
                similarity *= 1.2
            
            # 基于上下文的相关性
            if context.get('current_stage'):
                stage_keywords = extract_keywords(context['current_stage'], max_keywords=3)
                memory_keywords = extract_keywords(memory.content, max_keywords=10)
                overlap = len(set(stage_keywords) & set(memory_keywords))
                if overlap > 0:
                    similarity += overlap * 0.05
            
            if similarity > 0.25:
                scored_memories.append((memory, similarity))
        
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for memory, score in scored_memories[:limit]:
            memory.access()
            results.append(memory)
        
        if results:
            self.save_memories()
        
        return results
    
    def get_code_patterns(self) -> List[MemoryFragment]:
        """获取代码模式"""
        return [m for m in self.memories if any(tag in ['代码', '编程', 'code', 'programming'] for tag in m.tags)]
    
    def get_design_patterns(self) -> List[MemoryFragment]:
        """获取设计模式"""
        return [m for m in self.memories if any(tag in ['设计', '架构', 'design', 'architecture'] for tag in m.tags)]


class IssueMemory(BaseMemoryStore):
    """问题记忆存储"""
    
    def __init__(self, storage_path: Path):
        super().__init__(MemoryCategory.ISSUE, storage_path)
    
    def store(self, memory: MemoryFragment) -> bool:
        """存储问题记忆"""
        if memory.category != MemoryCategory.ISSUE:
            return False
        
        # 问题记忆重要性较高
        memory.importance = min(1.0, memory.importance + 0.15)
        
        self.memories.append(memory)
        self.save_memories()
        return True
    
    def search_similar(self, query: str, context: Dict[str, Any], limit: int = 5) -> List[MemoryFragment]:
        """搜索相似问题"""
        scored_memories = []
        
        for memory in self.memories:
            similarity = calculate_similarity(query, memory.content)
            
            # 问题相关性加权
            if any(keyword in query.lower() for keyword in ['问题', '错误', '异常', 'issue', 'error', 'exception', 'bug']):
                similarity *= 1.4
            
            # 解决方案相关性
            if any(keyword in query.lower() for keyword in ['解决', '修复', 'solve', 'fix', 'resolve']):
                if any(keyword in memory.content.lower() for keyword in ['解决', '修复', 'solved', 'fixed', 'resolved']):
                    similarity *= 1.3
            
            if similarity > 0.3:
                scored_memories.append((memory, similarity))
        
        scored_memories.sort(key=lambda x: (x[1], x[0].importance), reverse=True)
        
        results = []
        for memory, score in scored_memories[:limit]:
            memory.access()
            results.append(memory)
        
        if results:
            self.save_memories()
        
        return results
    
    def get_resolved_issues(self) -> List[MemoryFragment]:
        """获取已解决的问题"""
        return [m for m in self.memories if any(keyword in m.content.lower() for keyword in ['解决', '修复', 'solved', 'fixed', 'resolved'])]
    
    def get_open_issues(self) -> List[MemoryFragment]:
        """获取未解决的问题"""
        resolved = self.get_resolved_issues()
        resolved_contents = {m.content for m in resolved}
        return [m for m in self.memories if m.content not in resolved_contents]


class LearningMemory(BaseMemoryStore):
    """学习记忆存储"""
    
    def __init__(self, storage_path: Path):
        super().__init__(MemoryCategory.LEARNING, storage_path)
    
    def store(self, memory: MemoryFragment) -> bool:
        """存储学习记忆"""
        if memory.category != MemoryCategory.LEARNING:
            return False
        
        self.memories.append(memory)
        self.save_memories()
        return True
    
    def search_similar(self, query: str, context: Dict[str, Any], limit: int = 5) -> List[MemoryFragment]:
        """搜索相似学习经验"""
        scored_memories = []
        
        for memory in self.memories:
            similarity = calculate_similarity(query, memory.content)
            
            # 学习相关性加权
            if any(keyword in query.lower() for keyword in ['学习', '经验', '教训', 'learning', 'experience', 'lesson']):
                similarity *= 1.2
            
            # 技能相关性
            if context.get('technology_stack'):
                tech_keywords = [tech.lower() for tech in context['technology_stack']]
                memory_lower = memory.content.lower()
                tech_matches = sum(1 for tech in tech_keywords if tech in memory_lower)
                if tech_matches > 0:
                    similarity += tech_matches * 0.1
            
            if similarity > 0.25:
                scored_memories.append((memory, similarity))
        
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for memory, score in scored_memories[:limit]:
            memory.access()
            results.append(memory)
        
        if results:
            self.save_memories()
        
        return results
    
    def get_technical_learnings(self) -> List[MemoryFragment]:
        """获取技术学习"""
        return [m for m in self.memories if any(tag in ['技术', '编程', '框架', 'tech', 'programming', 'framework'] for tag in m.tags)]
    
    def get_process_learnings(self) -> List[MemoryFragment]:
        """获取流程学习"""
        return [m for m in self.memories if any(tag in ['流程', '方法', '过程', 'process', 'method', 'workflow'] for tag in m.tags)]


class ContextMemory(BaseMemoryStore):
    """上下文记忆存储"""
    
    def __init__(self, storage_path: Path):
        super().__init__(MemoryCategory.CONTEXT, storage_path)
    
    def store(self, memory: MemoryFragment) -> bool:
        """存储上下文记忆"""
        if memory.category != MemoryCategory.CONTEXT:
            return False
        
        # 限制上下文记忆数量，保持最新的
        max_context_memories = 200
        if len(self.memories) >= max_context_memories:
            # 移除最旧且不重要的记忆
            self.memories.sort(key=lambda m: (m.importance, m.last_accessed))
            self.memories = self.memories[50:]  # 保留最新的150个
        
        self.memories.append(memory)
        self.save_memories()
        return True
    
    def search_similar(self, query: str, context: Dict[str, Any], limit: int = 5) -> List[MemoryFragment]:
        """搜索相似上下文"""
        scored_memories = []
        
        for memory in self.memories:
            similarity = calculate_similarity(query, memory.content)
            
            # 时间相关性加权
            if is_recent(memory.last_accessed, hours=24):
                similarity *= 1.3
            elif is_recent(memory.last_accessed, hours=168):  # 一周内
                similarity *= 1.1
            
            # 项目相关性
            if context.get('project_id') and memory.project_id == context.get('project_id'):
                similarity *= 1.2
            
            if similarity > 0.2:
                scored_memories.append((memory, similarity))
        
        scored_memories.sort(key=lambda x: (x[1], x[0].last_accessed), reverse=True)
        
        results = []
        for memory, score in scored_memories[:limit]:
            memory.access()
            results.append(memory)
        
        if results:
            self.save_memories()
        
        return results
    
    def get_recent_context(self, hours: int = 24) -> List[MemoryFragment]:
        """获取最近的上下文"""
        recent = [m for m in self.memories if is_recent(m.last_accessed, hours)]
        return sorted(recent, key=lambda m: m.last_accessed, reverse=True)