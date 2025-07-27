"""
PATEOAS 核心数据模型
定义状态、记忆、行动建议等核心数据结构
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class ActionType(Enum):
    """行动类型枚举"""
    CONTINUE = "continue"
    OPTIMIZE = "optimize"
    PIVOT = "pivot"
    ESCALATE = "escalate"
    PARALLEL = "parallel"
    SKIP = "skip"
    ANALYZE = "analyze"
    REVIEW = "review"


class MemoryCategory(Enum):
    """记忆分类枚举"""
    REQUIREMENT = "requirement"
    DECISION = "decision"
    PATTERN = "pattern"
    ISSUE = "issue"
    LEARNING = "learning"
    CONTEXT = "context"


@dataclass
class MemoryFragment:
    """记忆片段数据模型"""
    content: str
    category: MemoryCategory
    importance: float  # 0.0-1.0
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    project_id: Optional[str] = None
    stage_context: Optional[str] = None
    
    def access(self):
        """记录访问"""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class NextAction:
    """下一步行动建议"""
    action_type: ActionType
    description: str
    command: str  # CLI命令
    confidence: float  # 0.0-1.0
    estimated_time: str
    prerequisites: List[str] = field(default_factory=list)
    expected_outcome: str = ""
    risk_level: str = "low"  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'action_type': self.action_type.value,
            'description': self.description,
            'command': self.command,
            'confidence': self.confidence,
            'estimated_time': self.estimated_time,
            'prerequisites': self.prerequisites,
            'expected_outcome': self.expected_outcome,
            'risk_level': self.risk_level
        }


@dataclass
class ReasoningStep:
    """推理步骤"""
    step_id: str
    description: str
    input_factors: List[str]
    logic: str
    output: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'step_id': self.step_id,
            'description': self.description,
            'input_factors': self.input_factors,
            'logic': self.logic,
            'output': self.output,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class StateTransition:
    """状态转换记录"""
    from_state: Dict[str, Any]
    to_state: Dict[str, Any]
    trigger: str
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'from_state': self.from_state,
            'to_state': self.to_state,
            'trigger': self.trigger,
            'reasoning': self.reasoning,
            'timestamp': self.timestamp.isoformat(),
            'success': self.success
        }


@dataclass
class PATEOASState:
    """PATEOAS 状态数据模型"""
    
    # 当前任务状态
    current_task: str
    task_progress: float  # 0.0-1.0
    stage_context: Dict[str, Any] = field(default_factory=dict)
    
    # 记忆片段
    memory_fragments: List[MemoryFragment] = field(default_factory=list)
    active_context: Dict[str, Any] = field(default_factory=dict)
    
    # 下一步指针
    next_suggestions: List[NextAction] = field(default_factory=list)
    alternative_paths: List[NextAction] = field(default_factory=list)
    
    # 元认知信息
    ai_confidence: float = 0.8
    reasoning_chain: List[ReasoningStep] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    
    # 状态元数据
    timestamp: datetime = field(default_factory=datetime.now)
    state_version: str = "1.0"
    transition_history: List[StateTransition] = field(default_factory=list)
    project_id: Optional[str] = None
    iteration_id: Optional[str] = None
    
    def add_memory(self, memory: MemoryFragment):
        """添加记忆片段"""
        self.memory_fragments.append(memory)
        
    def add_reasoning_step(self, step: ReasoningStep):
        """添加推理步骤"""
        self.reasoning_chain.append(step)
        
    def add_next_action(self, action: NextAction):
        """添加下一步建议"""
        self.next_suggestions.append(action)
        
    def record_transition(self, transition: StateTransition):
        """记录状态转换"""
        self.transition_history.append(transition)
        self.timestamp = datetime.now()
    
    def get_relevant_memories(self, limit: int = 5) -> List[MemoryFragment]:
        """获取相关记忆（按重要性和访问时间排序）"""
        sorted_memories = sorted(
            self.memory_fragments,
            key=lambda m: (m.importance, m.last_accessed),
            reverse=True
        )
        return sorted_memories[:limit]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'current_task': self.current_task,
            'task_progress': self.task_progress,
            'stage_context': self.stage_context,
            'memory_fragments': [
                {
                    'content': m.content,
                    'category': m.category.value,
                    'importance': m.importance,
                    'tags': m.tags,
                    'created_at': m.created_at.isoformat(),
                    'access_count': m.access_count
                } for m in self.memory_fragments
            ],
            'active_context': self.active_context,
            'next_suggestions': [action.to_dict() for action in self.next_suggestions],
            'alternative_paths': [action.to_dict() for action in self.alternative_paths],
            'ai_confidence': self.ai_confidence,
            'reasoning_chain': [step.to_dict() for step in self.reasoning_chain],
            'limitations': self.limitations,
            'timestamp': self.timestamp.isoformat(),
            'state_version': self.state_version,
            'project_id': self.project_id,
            'iteration_id': self.iteration_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PATEOASState':
        """从字典创建状态对象"""
        # 解析记忆片段
        memory_fragments = []
        for m_data in data.get('memory_fragments', []):
            memory = MemoryFragment(
                content=m_data['content'],
                category=MemoryCategory(m_data['category']),
                importance=m_data['importance'],
                tags=m_data.get('tags', []),
                created_at=datetime.fromisoformat(m_data['created_at']),
                access_count=m_data.get('access_count', 0)
            )
            memory_fragments.append(memory)
        
        # 解析下一步建议
        next_suggestions = []
        for a_data in data.get('next_suggestions', []):
            action = NextAction(
                action_type=ActionType(a_data['action_type']),
                description=a_data['description'],
                command=a_data['command'],
                confidence=a_data['confidence'],
                estimated_time=a_data['estimated_time'],
                prerequisites=a_data.get('prerequisites', []),
                expected_outcome=a_data.get('expected_outcome', ''),
                risk_level=a_data.get('risk_level', 'low')
            )
            next_suggestions.append(action)
        
        # 解析推理链
        reasoning_chain = []
        for r_data in data.get('reasoning_chain', []):
            step = ReasoningStep(
                step_id=r_data['step_id'],
                description=r_data['description'],
                input_factors=r_data['input_factors'],
                logic=r_data['logic'],
                output=r_data['output'],
                confidence=r_data['confidence'],
                timestamp=datetime.fromisoformat(r_data['timestamp'])
            )
            reasoning_chain.append(step)
        
        return cls(
            current_task=data['current_task'],
            task_progress=data['task_progress'],
            stage_context=data.get('stage_context', {}),
            memory_fragments=memory_fragments,
            active_context=data.get('active_context', {}),
            next_suggestions=next_suggestions,
            alternative_paths=[],  # 简化处理
            ai_confidence=data.get('ai_confidence', 0.8),
            reasoning_chain=reasoning_chain,
            limitations=data.get('limitations', []),
            timestamp=datetime.fromisoformat(data['timestamp']),
            state_version=data.get('state_version', '1.0'),
            project_id=data.get('project_id'),
            iteration_id=data.get('iteration_id')
        )