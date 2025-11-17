"""
Memory Models for v4.0 - 增强记忆系统数据模型

基于Cline Memory Bank研究，为AceFlow v4.0设计的增强记忆模型，包括：
1. 技术决策专用模型 (TechDecision)
2. 经验教训专用模型 (Lesson)
3. 文档引用模型 (DocumentRef)
4. 相关性评分机制 (RelevanceScore)
5. 记忆注入上下文 (MemoryInjectionContext)

设计原则：
- 不破坏v3.0兼容性，扩展而非替换
- 使用规则算法而非LLM推理
- 优化存储路径：.aceflow/memory/memories.json（用户建议）
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re


# ==================== v4.0 Enums ====================

class V4MemoryType(Enum):
    """v4.0 记忆类型（扩展v3.0）"""
    # v3.0 types (保持兼容)
    STAGE_OUTPUT = "stage_output"
    DECISION = "decision"
    ISSUE = "issue"
    LEARNING = "learning"
    CONTEXT = "context"
    GATE_RESULT = "gate_result"

    # v4.0 new types
    TECH_DECISION = "tech_decision"      # 技术决策（结构化）
    LESSON = "lesson"                    # 经验教训（结构化）
    DOCUMENT_REF = "document_ref"        # 文档引用
    WORK_ITEM_CONTEXT = "work_item_context"  # 工作项上下文


class DecisionScope(Enum):
    """决策影响范围"""
    LOCAL = "local"          # 本模块/本功能
    MODULE = "module"        # 跨模块
    ARCHITECTURE = "architecture"  # 架构级别
    PROJECT = "project"      # 整个项目


class LessonCategory(Enum):
    """经验教训分类"""
    TECHNICAL = "technical"      # 技术类
    PROCESS = "process"          # 流程类
    TEAM = "team"                # 团队协作类
    TOOLING = "tooling"          # 工具使用类
    BEST_PRACTICE = "best_practice"  # 最佳实践


# ==================== v4.0 Data Models ====================

@dataclass
class TechDecision:
    """
    技术决策模型（v4.0）

    用于记录重要的技术决策，包含完整的决策上下文、替代方案、影响分析。
    """
    decision_id: str
    title: str                           # 决策标题
    decision: str                        # 决策内容
    reason: str                          # 决策理由

    # 决策上下文
    scope: DecisionScope                 # 影响范围
    alternatives: List[str] = field(default_factory=list)  # 备选方案
    tech_stack: List[str] = field(default_factory=list)    # 涉及技术栈
    impact: str = ""                     # 影响分析

    # 关联信息
    work_item_id: Optional[str] = None   # 关联工作项
    stage_id: Optional[str] = None       # 决策阶段
    related_decisions: List[str] = field(default_factory=list)  # 相关决策ID

    # 元数据
    tags: List[str] = field(default_factory=list)
    importance: float = 0.8              # 重要性 (0-1)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "ai"               # ai/user
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'decision_id': self.decision_id,
            'title': self.title,
            'decision': self.decision,
            'reason': self.reason,
            'scope': self.scope.value,
            'alternatives': self.alternatives,
            'tech_stack': self.tech_stack,
            'impact': self.impact,
            'work_item_id': self.work_item_id,
            'stage_id': self.stage_id,
            'related_decisions': self.related_decisions,
            'tags': self.tags,
            'importance': self.importance,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechDecision':
        """从字典创建"""
        return cls(
            decision_id=data['decision_id'],
            title=data['title'],
            decision=data['decision'],
            reason=data['reason'],
            scope=DecisionScope(data.get('scope', 'local')),
            alternatives=data.get('alternatives', []),
            tech_stack=data.get('tech_stack', []),
            impact=data.get('impact', ''),
            work_item_id=data.get('work_item_id'),
            stage_id=data.get('stage_id'),
            related_decisions=data.get('related_decisions', []),
            tags=data.get('tags', []),
            importance=data.get('importance', 0.8),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            created_by=data.get('created_by', 'ai'),
            metadata=data.get('metadata', {})
        )


@dataclass
class Lesson:
    """
    经验教训模型（v4.0）

    用于记录项目中获得的经验教训，支持分类和适用范围标记。
    """
    lesson_id: str
    title: str                           # 教训标题
    content: str                         # 教训内容
    category: LessonCategory             # 分类

    # 上下文
    what_happened: str = ""              # 发生了什么
    what_learned: str = ""               # 学到了什么
    how_to_apply: str = ""               # 如何应用

    # 适用性
    applicability: str = "general"       # general/specific
    applicable_scenarios: List[str] = field(default_factory=list)  # 适用场景

    # 关联信息
    work_item_id: Optional[str] = None
    stage_id: Optional[str] = None
    issue_id: Optional[str] = None       # 关联的问题ID

    # 元数据
    tags: List[str] = field(default_factory=list)
    importance: float = 0.7              # 重要性 (0-1)
    created_at: datetime = field(default_factory=datetime.now)
    applied_count: int = 0               # 应用次数
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'lesson_id': self.lesson_id,
            'title': self.title,
            'content': self.content,
            'category': self.category.value,
            'what_happened': self.what_happened,
            'what_learned': self.what_learned,
            'how_to_apply': self.how_to_apply,
            'applicability': self.applicability,
            'applicable_scenarios': self.applicable_scenarios,
            'work_item_id': self.work_item_id,
            'stage_id': self.stage_id,
            'issue_id': self.issue_id,
            'tags': self.tags,
            'importance': self.importance,
            'created_at': self.created_at.isoformat(),
            'applied_count': self.applied_count,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Lesson':
        """从字典创建"""
        return cls(
            lesson_id=data['lesson_id'],
            title=data['title'],
            content=data['content'],
            category=LessonCategory(data.get('category', 'technical')),
            what_happened=data.get('what_happened', ''),
            what_learned=data.get('what_learned', ''),
            how_to_apply=data.get('how_to_apply', ''),
            applicability=data.get('applicability', 'general'),
            applicable_scenarios=data.get('applicable_scenarios', []),
            work_item_id=data.get('work_item_id'),
            stage_id=data.get('stage_id'),
            issue_id=data.get('issue_id'),
            tags=data.get('tags', []),
            importance=data.get('importance', 0.7),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            applied_count=data.get('applied_count', 0),
            metadata=data.get('metadata', {})
        )


@dataclass
class DocumentRef:
    """
    文档引用模型（v4.0）

    用于记录重要文档的引用，建立记忆与文档之间的关联。
    """
    ref_id: str
    title: str                           # 文档标题
    document_type: str                   # api/design/readme/etc.
    path: str                            # 文档路径
    section: Optional[str] = None        # 章节

    # 引用上下文
    reason: str = ""                     # 引用原因
    key_points: List[str] = field(default_factory=list)  # 关键点

    # 关联信息
    work_item_id: Optional[str] = None
    related_memories: List[str] = field(default_factory=list)  # 相关记忆ID

    # 元数据
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_verified: Optional[datetime] = None  # 最后验证时间
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'ref_id': self.ref_id,
            'title': self.title,
            'document_type': self.document_type,
            'path': self.path,
            'section': self.section,
            'reason': self.reason,
            'key_points': self.key_points,
            'work_item_id': self.work_item_id,
            'related_memories': self.related_memories,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'last_verified': self.last_verified.isoformat() if self.last_verified else None,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentRef':
        """从字典创建"""
        return cls(
            ref_id=data['ref_id'],
            title=data['title'],
            document_type=data['document_type'],
            path=data['path'],
            section=data.get('section'),
            reason=data.get('reason', ''),
            key_points=data.get('key_points', []),
            work_item_id=data.get('work_item_id'),
            related_memories=data.get('related_memories', []),
            tags=data.get('tags', []),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            last_verified=datetime.fromisoformat(data['last_verified']) if data.get('last_verified') else None,
            metadata=data.get('metadata', {})
        )


# ==================== v4.0 Relevance Scoring ====================

@dataclass
class RelevanceScore:
    """
    相关性评分结果（v4.0）

    用于记录记忆与当前上下文的相关性分数及其计算细节。
    """
    memory_id: str
    total_score: float                   # 总分 (0-1)

    # 分项得分
    keyword_score: float = 0.0           # 关键词匹配得分
    tag_score: float = 0.0               # 标签匹配得分
    stage_score: float = 0.0             # 阶段相关性得分
    importance_score: float = 0.0        # 重要性得分
    recency_score: float = 0.0           # 时间新近度得分

    # 解释信息
    matched_keywords: List[str] = field(default_factory=list)
    matched_tags: List[str] = field(default_factory=list)
    reason: str = ""                     # 评分理由

    def __lt__(self, other: 'RelevanceScore') -> bool:
        """支持排序（按总分降序）"""
        return self.total_score > other.total_score


@dataclass
class MemoryInjectionContext:
    """
    记忆注入上下文（v4.0）

    用于描述记忆注入的上下文信息，指导记忆筛选和排序。
    """
    # 工作项上下文
    work_item_id: str
    work_item_type: str                  # feature/bugfix/refactor/etc.
    work_item_title: str
    work_item_description: str

    # 阶段上下文
    stage_id: str
    stage_name: str
    stage_type: str                      # requirement/design/implementation/etc.

    # 筛选配置
    max_memories: int = 5                # 最多注入记忆数
    min_relevance: float = 0.3           # 最低相关性阈值
    memory_types: Optional[List[str]] = None  # 指定记忆类型

    # 优先级配置
    prefer_recent: bool = True           # 优先最近的记忆
    prefer_important: bool = True        # 优先重要的记忆
    prefer_applied: bool = False         # 优先已应用的经验

    # 计算的搜索关键词
    search_keywords: List[str] = field(default_factory=list)
    search_tags: List[str] = field(default_factory=list)

    def extract_keywords(self) -> List[str]:
        """
        从标题和描述中提取关键词（简单分词）

        Returns:
            关键词列表
        """
        text = f"{self.work_item_title} {self.work_item_description}".lower()

        # 移除标点符号
        text = re.sub(r'[^\w\s]', ' ', text)

        # 分词
        words = text.split()

        # 过滤常见停用词
        stop_words = {'的', '了', '和', '与', '或', '等', '及', 'the', 'a', 'an', 'and', 'or', 'but'}
        keywords = [w for w in words if w not in stop_words and len(w) > 1]

        # 去重
        self.search_keywords = list(set(keywords))
        return self.search_keywords

    def extract_tags(self) -> List[str]:
        """
        提取标签（技术栈、框架、关键词等）

        Returns:
            标签列表
        """
        tags = [self.work_item_type, self.stage_type]

        # 添加技术栈相关标签（简单模式匹配）
        tech_patterns = {
            'auth': ['认证', '登录', 'login', 'auth', 'jwt', 'token'],
            'database': ['数据库', 'db', 'sql', 'mysql', 'postgres', 'redis'],
            'api': ['api', 'rest', 'graphql', '接口', 'endpoint'],
            'frontend': ['前端', 'ui', 'react', 'vue', 'angular', '页面'],
            'backend': ['后端', 'server', '服务器', 'service'],
            'test': ['测试', 'test', 'unittest', '单元测试']
        }

        text = f"{self.work_item_title} {self.work_item_description}".lower()
        for tech_tag, patterns in tech_patterns.items():
            if any(pattern in text for pattern in patterns):
                tags.append(tech_tag)

        self.search_tags = list(set(tags))
        return self.search_tags


# ==================== v4.0 Detection Rules ====================

class DecisionDetector:
    """
    决策自动检测器（v4.0）

    使用A+B+C规则检测技术决策（无需LLM推理）：
    - A: 决策关键词（必须满足）
    - B: 影响范围广（满足任一）
    - C: 技术选型类（满足任一）

    满足 A + (B 或 C) → 识别为技术决策
    """

    # 决策关键词（规则A）
    DECISION_KEYWORDS = [
        # 中文
        '选择', '决定', '使用', '采用', '方案', '选型', '确定',
        # 英文
        'choose', 'decide', 'use', 'adopt', 'select', 'option'
    ]

    # 影响范围关键词（规则B）
    WIDE_IMPACT_KEYWORDS = [
        # 中文
        '多模块', '架构', '长期', '全局', '整体', '系统级',
        # 英文
        'architecture', 'system-wide', 'global', 'long-term', 'multiple modules'
    ]

    # 技术选型关键词（规则C）
    TECH_SELECTION_KEYWORDS = [
        # 中文
        '库', '框架', '数据库', '技术栈', '工具', '平台', '语言',
        # 英文
        'library', 'framework', 'database', 'stack', 'tool', 'platform', 'language'
    ]

    @classmethod
    def detect(cls, text: str) -> Optional[Dict[str, Any]]:
        """
        检测文本中是否包含技术决策

        Args:
            text: 文本内容

        Returns:
            检测到的决策信息，或None
        """
        text_lower = text.lower()

        # 规则A: 检查决策关键词
        has_decision_keyword = any(kw in text_lower for kw in cls.DECISION_KEYWORDS)

        if not has_decision_keyword:
            return None

        # 规则B: 检查影响范围
        has_wide_impact = any(kw in text_lower for kw in cls.WIDE_IMPACT_KEYWORDS)

        # 规则C: 检查技术选型
        is_tech_selection = any(kw in text_lower for kw in cls.TECH_SELECTION_KEYWORDS)

        # A + (B 或 C) → 识别为决策
        if has_wide_impact or is_tech_selection:
            # 提取决策标题（取第一句）
            title = text.split('。')[0].split('\n')[0][:50]

            return {
                'detected': True,
                'title': title,
                'has_wide_impact': has_wide_impact,
                'is_tech_selection': is_tech_selection,
                'confidence': 0.9 if (has_wide_impact and is_tech_selection) else 0.7
            }

        return None


class LessonExtractor:
    """
    经验教训提取器（v4.0）

    使用关键词模式识别经验教训（无需LLM推理）
    """

    # 经验教训关键词
    LESSON_KEYWORDS = [
        # 中文
        '经验', '教训', '学到', '总结', '注意', '避免', '建议', '最佳实践',
        '不要', '应该', '推荐', '问题', '解决方案',
        # 英文
        'learned', 'lesson', 'experience', 'best practice', 'tip',
        'avoid', 'should', 'recommend', 'problem', 'solution'
    ]

    # 问题指示词
    PROBLEM_KEYWORDS = ['问题', '错误', 'error', 'issue', 'bug', '失败', 'fail']

    # 解决指示词
    SOLUTION_KEYWORDS = ['解决', '修复', 'fix', 'solve', '方法', 'approach']

    @classmethod
    def extract(cls, text: str) -> Optional[Dict[str, Any]]:
        """
        从文本中提取经验教训

        Args:
            text: 文本内容

        Returns:
            提取的经验信息，或None
        """
        text_lower = text.lower()

        # 检查是否包含经验关键词
        has_lesson_keyword = any(kw in text_lower for kw in cls.LESSON_KEYWORDS)

        if not has_lesson_keyword:
            return None

        # 检查是否包含问题和解决方案（完整经验）
        has_problem = any(kw in text_lower for kw in cls.PROBLEM_KEYWORDS)
        has_solution = any(kw in text_lower for kw in cls.SOLUTION_KEYWORDS)

        title = text.split('。')[0].split('\n')[0][:50]

        return {
            'detected': True,
            'title': title,
            'has_problem': has_problem,
            'has_solution': has_solution,
            'is_complete': has_problem and has_solution,
            'confidence': 0.9 if (has_problem and has_solution) else 0.6
        }
