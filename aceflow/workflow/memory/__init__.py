"""
Memory - 工作流记忆管理系统

为工作流引擎提供上下文记忆能力:
- 阶段间信息传递
- 迭代间经验积累
- 决策历史追踪
- 智能上下文召回

v4.0 增强:
- 技术决策自动检测和结构化存储
- 经验教训自动提炼
- 基于相关性的智能记忆注入
- 不调用LLM API，纯算法实现

与 aceflow/pateoas/memory_system.py 的区别:
- 专注于工作流状态和阶段上下文
- 简化的接口，更适合工作流场景
- 与 StateManager 紧密集成
"""

# v3.0 exports (向后兼容)
from .manager import MemoryManager
from .models import (
    Memory,
    MemoryType,
    MemoryPriority,
    MemoryQuery
)
from .store import MemoryStore

# v4.0 exports (新增)
from .v4_models import (
    V4MemoryType,
    DecisionScope,
    LessonCategory,
    TechDecision,
    Lesson,
    DocumentRef,
    RelevanceScore,
    MemoryInjectionContext,
    DecisionDetector,
    LessonExtractor
)

from .relevance import (
    RelevanceCalculator,
    MemoryFilter
)

from .v4_manager import V4MemoryManager
from .extractor import MemoryExtractor, ExtractionResult
from .injector import MemoryInjector, InjectionResult

__all__ = [
    # v3.0 (向后兼容)
    'MemoryManager',
    'Memory',
    'MemoryType',
    'MemoryPriority',
    'MemoryQuery',
    'MemoryStore',

    # v4.0 新增
    'V4MemoryType',
    'DecisionScope',
    'LessonCategory',
    'TechDecision',
    'Lesson',
    'DocumentRef',
    'RelevanceScore',
    'MemoryInjectionContext',
    'DecisionDetector',
    'LessonExtractor',
    'RelevanceCalculator',
    'MemoryFilter',
    'V4MemoryManager',    # v4.0 enhanced manager
    'MemoryExtractor',    # v4.0 memory extraction
    'ExtractionResult',   # v4.0 extraction result
    'MemoryInjector',     # v4.0 memory injection
    'InjectionResult'     # v4.0 injection result
]
