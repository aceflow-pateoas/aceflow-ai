"""
状态连续性管理器
维护跨对话的项目状态连续性
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from .models import PATEOASState, StateTransition, MemoryFragment, NextAction, ActionType
from .config import get_config
from .utils import generate_id, safe_json_loads, safe_json_dumps, ensure_directory


class StateContinuityManager:
    """状态连续性管理器"""
    
    def __init__(self, project_id: Optional[str] = None):
        self.config = get_config()
        self.project_id = project_id or "default"
        self.current_state: Optional[PATEOASState] = None
        self.state_cache = {}
        
        # 确保存储目录存在
        self.state_dir = ensure_directory(self.config.state_storage_path)
        self.state_file = self.state_dir / f"{self.project_id}_state.json"
        
        # 加载现有状态
        self._load_state()
    
    def get_current_state(self) -> Dict[str, Any]:
        """获取当前完整状态"""
        if not self.current_state:
            self._initialize_default_state()
        
        return {
            'project_context': self._get_project_context(),
            'workflow_state': self._get_workflow_state(),
            'ai_memory': self._get_ai_memory(),
            'user_preferences': self._get_user_preferences(),
            'execution_history': self._get_execution_history()
        }
    
    def update_state(self, new_information: Dict[str, Any]):
        """更新状态并记录变化"""
        if not self.current_state:
            self._initialize_default_state()
        
        previous_state = self.current_state.to_dict()
        
        # 更新状态字段
        if 'current_task' in new_information:
            self.current_state.current_task = new_information['current_task']
        if 'task_progress' in new_information:
            self.current_state.task_progress = new_information['task_progress']
        if 'stage_context' in new_information:
            self.current_state.stage_context.update(new_information['stage_context'])
        if 'active_context' in new_information:
            self.current_state.active_context.update(new_information['active_context'])
        
        # 记录状态转换
        transition = StateTransition(
            from_state=previous_state,
            to_state=self.current_state.to_dict(),
            trigger=new_information.get('trigger', 'manual_update'),
            reasoning=new_information.get('reasoning', 'State updated by user')
        )
        
        self.current_state.record_transition(transition)
        self._save_state()
    
    def generate_state_declaration(self) -> Dict[str, Any]:
        """生成当前状态声明（PATEOAS核心）"""
        if not self.current_state:
            self._initialize_default_state()
        
        # 获取相关记忆并按重要性排序
        relevant_memories = self.current_state.get_relevant_memories(10)
        
        # 生成智能的下一步建议
        smart_suggestions = self._generate_smart_suggestions()
        
        # 生成上下文感知的状态摘要
        context_summary = self._generate_context_summary()
        
        return {
            'current_task': self.current_state.current_task,
            'progress': self.current_state.task_progress,
            'stage_info': {
                'current_stage': self.current_state.stage_context.get('current_stage', 'unknown'),
                'workflow_mode': self.current_state.stage_context.get('workflow_mode', 'smart'),
                'completed_stages': self.current_state.stage_context.get('completed_stages', []),
                'pending_tasks': self.current_state.stage_context.get('pending_tasks', [])
            },
            'memory_fragments': [
                {
                    'content': m.content,
                    'category': m.category.value,
                    'importance': m.importance,
                    'tags': m.tags,
                    'relevance_score': self._calculate_memory_relevance(m)
                } for m in relevant_memories
            ],
            'context_summary': context_summary,
            'next_suggestions': smart_suggestions,
            'alternative_paths': self._generate_alternative_paths(),
            'meta_cognition': self._generate_enhanced_meta_cognition(),
            'state_health': self._assess_state_health(),
            'timestamp': datetime.now().isoformat(),
            'state_id': f"{self.project_id}_{self.current_state.iteration_id}"
        }
    
    def add_memory(self, content: str, category: str, importance: float = 0.5, tags: List[str] = None):
        """添加记忆片段"""
        if not self.current_state:
            self._initialize_default_state()
        
        from .models import MemoryCategory
        memory = MemoryFragment(
            content=content,
            category=MemoryCategory(category),
            importance=importance,
            tags=tags or [],
            project_id=self.project_id
        )
        
        self.current_state.add_memory(memory)
        self._save_state()
    
    def add_next_action(self, action_type: str, description: str, command: str, confidence: float = 0.8):
        """添加下一步建议"""
        if not self.current_state:
            self._initialize_default_state()
        
        action = NextAction(
            action_type=ActionType(action_type),
            description=description,
            command=command,
            confidence=confidence,
            estimated_time="未知"
        )
        
        self.current_state.add_next_action(action)
        self._save_state()
    
    def rollback_to_previous_state(self) -> bool:
        """回滚到上一个状态"""
        if not self.current_state or len(self.current_state.transition_history) < 2:
            return False
        
        try:
            # 获取上一个状态
            previous_transition = self.current_state.transition_history[-2]
            previous_state_data = previous_transition.from_state
            
            # 恢复状态
            self.current_state = PATEOASState.from_dict(previous_state_data)
            
            # 记录回滚操作
            rollback_transition = StateTransition(
                from_state=previous_transition.to_state,
                to_state=previous_state_data,
                trigger="rollback",
                reasoning="用户请求回滚到上一个状态"
            )
            self.current_state.record_transition(rollback_transition)
            
            self._save_state()
            return True
        except Exception as e:
            print(f"状态回滚失败: {e}")
            return False
    
    def create_state_snapshot(self, name: str = None) -> str:
        """创建状态快照"""
        if not self.current_state:
            return ""
        
        snapshot_name = name or f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        snapshot_file = self.state_dir / f"{self.project_id}_{snapshot_name}.json"
        
        try:
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_state.to_dict(), f, ensure_ascii=False, indent=2)
            return snapshot_name
        except Exception as e:
            print(f"创建状态快照失败: {e}")
            return ""
    
    def restore_from_snapshot(self, snapshot_name: str) -> bool:
        """从快照恢复状态"""
        snapshot_file = self.state_dir / f"{self.project_id}_{snapshot_name}.json"
        
        if not snapshot_file.exists():
            return False
        
        try:
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 保存当前状态作为恢复前的记录
            current_data = self.current_state.to_dict() if self.current_state else {}
            
            # 恢复状态
            self.current_state = PATEOASState.from_dict(data)
            
            # 记录恢复操作
            restore_transition = StateTransition(
                from_state=current_data,
                to_state=data,
                trigger="restore_snapshot",
                reasoning=f"从快照 {snapshot_name} 恢复状态"
            )
            self.current_state.record_transition(restore_transition)
            
            self._save_state()
            return True
        except Exception as e:
            print(f"从快照恢复状态失败: {e}")
            return False
    
    def validate_state_integrity(self) -> Dict[str, Any]:
        """验证状态完整性"""
        if not self.current_state:
            return {'valid': False, 'errors': ['状态未初始化']}
        
        errors = []
        warnings = []
        
        # 检查必要字段
        if not self.current_state.current_task:
            errors.append('当前任务为空')
        
        if not (0 <= self.current_state.task_progress <= 1):
            errors.append('任务进度值无效')
        
        if not self.current_state.project_id:
            warnings.append('项目ID为空')
        
        # 检查记忆片段
        for i, memory in enumerate(self.current_state.memory_fragments):
            if not memory.content:
                warnings.append(f'记忆片段 {i} 内容为空')
            if not (0 <= memory.importance <= 1):
                errors.append(f'记忆片段 {i} 重要性值无效')
        
        # 检查状态转换历史
        if len(self.current_state.transition_history) > 1000:
            warnings.append('状态转换历史过长，建议清理')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'memory_count': len(self.current_state.memory_fragments),
            'transition_count': len(self.current_state.transition_history)
        }
    
    def analyze_state_patterns(self) -> Dict[str, Any]:
        """分析状态模式和趋势"""
        if not self.current_state or len(self.current_state.transition_history) < 2:
            return {'patterns': [], 'trends': [], 'insights': []}
        
        patterns = []
        trends = []
        insights = []
        
        # 分析任务进度趋势
        progress_changes = []
        for i in range(1, len(self.current_state.transition_history)):
            prev_state = self.current_state.transition_history[i-1].from_state
            curr_state = self.current_state.transition_history[i].to_state
            
            prev_progress = prev_state.get('task_progress', 0)
            curr_progress = curr_state.get('task_progress', 0)
            progress_changes.append(curr_progress - prev_progress)
        
        if progress_changes:
            avg_progress_change = sum(progress_changes) / len(progress_changes)
            if avg_progress_change > 0.1:
                trends.append("任务进度稳步提升")
            elif avg_progress_change < -0.05:
                trends.append("任务进度出现倒退")
            else:
                trends.append("任务进度变化平稳")
        
        # 分析状态转换频率
        recent_transitions = self.current_state.transition_history[-10:]
        transition_triggers = [t.trigger for t in recent_transitions]
        trigger_counts = {}
        for trigger in transition_triggers:
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        most_common_trigger = max(trigger_counts.items(), key=lambda x: x[1]) if trigger_counts else None
        if most_common_trigger and most_common_trigger[1] > 3:
            patterns.append(f"频繁的{most_common_trigger[0]}操作")
        
        # 分析记忆增长模式
        memory_categories = {}
        for memory in self.current_state.memory_fragments:
            cat = memory.category.value
            memory_categories[cat] = memory_categories.get(cat, 0) + 1
        
        if memory_categories:
            dominant_category = max(memory_categories.items(), key=lambda x: x[1])
            if dominant_category[1] > len(self.current_state.memory_fragments) * 0.4:
                patterns.append(f"主要关注{dominant_category[0]}类型的信息")
        
        # 生成洞察
        if self.current_state.ai_confidence < 0.6:
            insights.append("AI置信度较低，可能需要更多上下文信息")
        
        if len(self.current_state.memory_fragments) > 50:
            insights.append("记忆片段较多，建议进行整理和归档")
        
        if len(self.current_state.next_suggestions) == 0:
            insights.append("缺少下一步建议，可能需要重新评估当前状态")
        
        return {
            'patterns': patterns,
            'trends': trends,
            'insights': insights,
            'statistics': {
                'avg_progress_change': avg_progress_change if progress_changes else 0,
                'transition_frequency': len(self.current_state.transition_history),
                'memory_distribution': memory_categories,
                'confidence_level': self.current_state.ai_confidence
            }
        }
    
    def get_state_timeline(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取状态时间线"""
        if not self.current_state:
            return []
        
        timeline = []
        transitions = self.current_state.transition_history[-limit:]
        
        for transition in transitions:
            timeline_entry = {
                'timestamp': transition.timestamp.isoformat(),
                'trigger': transition.trigger,
                'reasoning': transition.reasoning,
                'success': transition.success,
                'changes': self._analyze_state_changes(transition.from_state, transition.to_state)
            }
            timeline.append(timeline_entry)
        
        return timeline
    
    def _analyze_state_changes(self, from_state: Dict[str, Any], to_state: Dict[str, Any]) -> Dict[str, Any]:
        """分析状态变化"""
        changes = {}
        
        # 检查任务变化
        if from_state.get('current_task') != to_state.get('current_task'):
            changes['task_changed'] = {
                'from': from_state.get('current_task'),
                'to': to_state.get('current_task')
            }
        
        # 检查进度变化
        from_progress = from_state.get('task_progress', 0)
        to_progress = to_state.get('task_progress', 0)
        if abs(from_progress - to_progress) > 0.01:
            changes['progress_changed'] = {
                'from': from_progress,
                'to': to_progress,
                'delta': to_progress - from_progress
            }
        
        # 检查记忆数量变化
        from_memories = len(from_state.get('memory_fragments', []))
        to_memories = len(to_state.get('memory_fragments', []))
        if from_memories != to_memories:
            changes['memory_count_changed'] = {
                'from': from_memories,
                'to': to_memories,
                'delta': to_memories - from_memories
            }
        
        return changes
    
    def cleanup_old_transitions(self, keep_count: int = 100):
        """清理旧的状态转换记录"""
        if not self.current_state or len(self.current_state.transition_history) <= keep_count:
            return
        
        # 保留最近的转换记录
        self.current_state.transition_history = self.current_state.transition_history[-keep_count:]
        self._save_state()
    
    def export_state_summary(self) -> Dict[str, Any]:
        """导出状态摘要"""
        if not self.current_state:
            return {}
        
        return {
            'project_info': {
                'project_id': self.project_id,
                'current_task': self.current_state.current_task,
                'progress': self.current_state.task_progress,
                'iteration': self.current_state.iteration_id
            },
            'memory_summary': {
                'total_memories': len(self.current_state.memory_fragments),
                'categories': self._get_memory_category_stats(),
                'avg_importance': self._get_average_memory_importance()
            },
            'activity_summary': {
                'total_transitions': len(self.current_state.transition_history),
                'recent_activity': len([t for t in self.current_state.transition_history 
                                     if (datetime.now() - t.timestamp).days < 7]),
                'success_rate': sum(1 for t in self.current_state.transition_history if t.success) / 
                               max(1, len(self.current_state.transition_history))
            },
            'ai_status': {
                'confidence': self.current_state.ai_confidence,
                'reasoning_steps': len(self.current_state.reasoning_chain),
                'limitations': len(self.current_state.limitations),
                'next_actions': len(self.current_state.next_suggestions)
            }
        }
    
    def _get_memory_category_stats(self) -> Dict[str, int]:
        """获取记忆分类统计"""
        stats = {}
        for memory in self.current_state.memory_fragments:
            category = memory.category.value
            stats[category] = stats.get(category, 0) + 1
        return stats
    
    def _get_average_memory_importance(self) -> float:
        """获取记忆平均重要性"""
        if not self.current_state.memory_fragments:
            return 0.0
        
        total_importance = sum(m.importance for m in self.current_state.memory_fragments)
        return total_importance / len(self.current_state.memory_fragments)
    
    def _initialize_default_state(self):
        """初始化默认状态"""
        self.current_state = PATEOASState(
            current_task="项目初始化",
            task_progress=0.0,
            project_id=self.project_id,
            iteration_id=generate_id("iter")
        )
        
        # 添加初始记忆
        self.add_memory(
            content="项目开始，PATEOAS 系统已激活",
            category="learning",
            importance=0.8,
            tags=["初始化", "PATEOAS"]
        )
        
        # 添加初始建议
        self.add_next_action(
            action_type="continue",
            description="开始分析项目需求",
            command="aceflow analyze",
            confidence=0.9
        )
    
    def _get_project_context(self) -> Dict[str, Any]:
        """获取项目上下文"""
        return {
            'project_id': self.project_id,
            'technology_stack': self.current_state.stage_context.get('technology_stack', []),
            'team_size': self.current_state.stage_context.get('team_size', 1),
            'complexity_level': self.current_state.stage_context.get('complexity_level', 'medium'),
            'current_iteration': self.current_state.iteration_id
        }
    
    def _get_workflow_state(self) -> Dict[str, Any]:
        """获取工作流状态"""
        return {
            'current_mode': self.current_state.stage_context.get('workflow_mode', 'smart'),
            'current_stage': self.current_state.stage_context.get('current_stage', 'S1'),
            'stage_progress': self.current_state.task_progress * 100,
            'overall_progress': self.current_state.task_progress * 100,
            'pending_tasks': self.current_state.stage_context.get('pending_tasks', []),
            'completed_stages': self.current_state.stage_context.get('completed_stages', [])
        }
    
    def _get_ai_memory(self) -> Dict[str, Any]:
        """获取AI记忆"""
        memories = self.current_state.get_relevant_memories(10)
        
        key_decisions = [m for m in memories if m.category.value == 'decision']
        learned_patterns = [m for m in memories if m.category.value == 'pattern']
        context_fragments = [m for m in memories if m.category.value == 'context']
        
        return {
            'key_decisions': [
                {
                    'decision': m.content,
                    'reasoning': f"重要性: {m.importance}",
                    'timestamp': m.created_at.isoformat()
                } for m in key_decisions[:3]
            ],
            'learned_patterns': [m.content for m in learned_patterns[:5]],
            'context_fragments': [m.content for m in context_fragments[:5]]
        }
    
    def _get_user_preferences(self) -> Dict[str, Any]:
        """获取用户偏好"""
        return self.current_state.stage_context.get('user_preferences', {})
    
    def _get_execution_history(self) -> Dict[str, Any]:
        """获取执行历史"""
        recent_transitions = self.current_state.transition_history[-5:]
        
        return {
            'recent_actions': [
                {
                    'action': t.trigger,
                    'timestamp': t.timestamp.isoformat(),
                    'result': 'success' if t.success else 'failed'
                } for t in recent_transitions
            ],
            'performance_metrics': {
                'total_transitions': len(self.current_state.transition_history),
                'success_rate': sum(1 for t in self.current_state.transition_history if t.success) / max(1, len(self.current_state.transition_history)),
                'avg_confidence': self.current_state.ai_confidence
            }
        }
    
    def _generate_meta_cognition(self) -> Dict[str, Any]:
        """生成元认知信息"""
        return {
            'current_understanding': f"正在处理: {self.current_state.current_task}",
            'confidence_level': self.current_state.ai_confidence,
            'known_limitations': self.current_state.limitations,
            'reasoning_depth': len(self.current_state.reasoning_chain),
            'memory_utilization': len(self.current_state.memory_fragments)
        }
    
    def _load_state(self):
        """从文件加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_state = PATEOASState.from_dict(data)
            except Exception as e:
                print(f"加载状态文件失败: {e}")
                self._initialize_default_state()
        else:
            self._initialize_default_state()
    
    def _save_state(self):
        """保存状态到文件"""
        if self.current_state:
            try:
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    json.dump(self.current_state.to_dict(), f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"保存状态文件失败: {e}")
    
    def _generate_smart_suggestions(self) -> List[Dict[str, Any]]:
        """生成智能的下一步建议"""
        suggestions = []
        
        # 基于当前状态生成建议
        current_progress = self.current_state.task_progress
        current_stage = self.current_state.stage_context.get('current_stage', 'S1')
        pending_tasks = self.current_state.stage_context.get('pending_tasks', [])
        
        # 添加现有建议
        for action in self.current_state.next_suggestions:
            suggestions.append(action.to_dict())
        
        # 基于进度生成智能建议
        if current_progress < 0.3:
            suggestions.append({
                'action_type': 'continue',
                'description': '继续完善需求分析和设计',
                'command': 'aceflow analyze --deep',
                'confidence': 0.8,
                'estimated_time': '30-60分钟',
                'prerequisites': [],
                'expected_outcome': '更清晰的项目需求和技术方案',
                'risk_level': 'low',
                'auto_generated': True
            })
        elif current_progress < 0.7:
            suggestions.append({
                'action_type': 'parallel',
                'description': '并行开发核心功能模块',
                'command': 'aceflow implement --parallel',
                'confidence': 0.75,
                'estimated_time': '2-4小时',
                'prerequisites': ['完成设计文档'],
                'expected_outcome': '核心功能模块实现',
                'risk_level': 'medium',
                'auto_generated': True
            })
        else:
            suggestions.append({
                'action_type': 'optimize',
                'description': '进行代码优化和测试',
                'command': 'aceflow test --comprehensive',
                'confidence': 0.9,
                'estimated_time': '1-2小时',
                'prerequisites': ['功能实现完成'],
                'expected_outcome': '高质量的代码和完整测试',
                'risk_level': 'low',
                'auto_generated': True
            })
        
        # 基于待办任务生成建议
        if pending_tasks:
            suggestions.append({
                'action_type': 'continue',
                'description': f'处理待办任务: {", ".join(pending_tasks[:3])}',
                'command': f'aceflow task --focus {pending_tasks[0]}',
                'confidence': 0.85,
                'estimated_time': '根据任务复杂度',
                'prerequisites': [],
                'expected_outcome': '完成关键待办任务',
                'risk_level': 'low',
                'auto_generated': True
            })
        
        # 去重并按置信度排序
        unique_suggestions = []
        seen_descriptions = set()
        for suggestion in suggestions:
            if suggestion['description'] not in seen_descriptions:
                unique_suggestions.append(suggestion)
                seen_descriptions.add(suggestion['description'])
        
        return sorted(unique_suggestions, key=lambda x: x['confidence'], reverse=True)
    
    def _generate_alternative_paths(self) -> List[Dict[str, Any]]:
        """生成替代路径建议"""
        alternatives = []
        
        current_stage = self.current_state.stage_context.get('current_stage', 'S1')
        workflow_mode = self.current_state.stage_context.get('workflow_mode', 'smart')
        
        # 基于当前阶段生成替代路径
        if current_stage in ['S1', 'S2']:
            alternatives.append({
                'path_type': 'fast_track',
                'description': '快速原型开发路径',
                'rationale': '如果需要快速验证概念，可以跳过详细设计直接开始原型开发',
                'estimated_time_saving': '40%',
                'risk_level': 'medium',
                'prerequisites': ['明确核心功能需求']
            })
        
        if workflow_mode != 'minimal':
            alternatives.append({
                'path_type': 'minimal_mode',
                'description': '切换到最小化模式',
                'rationale': '如果时间紧迫，可以采用最小化流程专注核心功能',
                'estimated_time_saving': '60%',
                'risk_level': 'high',
                'prerequisites': ['明确最小可行产品范围']
            })
        
        # 基于项目复杂度生成替代路径
        complexity = self.current_state.stage_context.get('complexity_level', 'medium')
        if complexity == 'high':
            alternatives.append({
                'path_type': 'modular_development',
                'description': '模块化分阶段开发',
                'rationale': '将复杂项目拆分为独立模块，降低开发风险',
                'estimated_time_saving': '0%',
                'risk_level': 'low',
                'prerequisites': ['完成模块划分设计']
            })
        
        return alternatives
    
    def _generate_context_summary(self) -> Dict[str, Any]:
        """生成上下文感知的状态摘要"""
        # 分析技术栈
        tech_stack = self.current_state.stage_context.get('technology_stack', [])
        tech_summary = "未指定" if not tech_stack else ", ".join(tech_stack)
        
        # 分析项目类型
        project_type = self._infer_project_type()
        
        # 分析当前焦点
        current_focus = self._analyze_current_focus()
        
        # 分析风险因素
        risk_factors = self._identify_risk_factors()
        
        # 分析机会点
        opportunities = self._identify_opportunities()
        
        return {
            'project_type': project_type,
            'technology_summary': tech_summary,
            'current_focus': current_focus,
            'risk_factors': risk_factors,
            'opportunities': opportunities,
            'complexity_assessment': self._assess_complexity(),
            'resource_status': self._assess_resource_status()
        }
    
    def _generate_enhanced_meta_cognition(self) -> Dict[str, Any]:
        """生成增强的元认知信息"""
        base_meta = self._generate_meta_cognition()
        
        # 添加更深层的自我认知
        enhanced_meta = {
            **base_meta,
            'knowledge_gaps': self._identify_knowledge_gaps(),
            'confidence_breakdown': self._analyze_confidence_factors(),
            'learning_opportunities': self._identify_learning_opportunities(),
            'decision_quality': self._assess_decision_quality(),
            'context_completeness': self._assess_context_completeness(),
            'next_learning_priorities': self._suggest_learning_priorities()
        }
        
        return enhanced_meta
    
    def _assess_state_health(self) -> Dict[str, Any]:
        """评估状态健康度"""
        health_score = 0.0
        health_factors = {}
        recommendations = []
        
        # 评估进度健康度
        progress = self.current_state.task_progress
        if progress > 0.8:
            health_factors['progress'] = 'excellent'
            health_score += 0.3
        elif progress > 0.5:
            health_factors['progress'] = 'good'
            health_score += 0.2
        elif progress > 0.2:
            health_factors['progress'] = 'fair'
            health_score += 0.1
        else:
            health_factors['progress'] = 'poor'
            recommendations.append('项目进度较慢，建议检查是否遇到阻碍')
        
        # 评估记忆健康度
        memory_count = len(self.current_state.memory_fragments)
        if memory_count > 20:
            health_factors['memory'] = 'rich'
            health_score += 0.2
        elif memory_count > 10:
            health_factors['memory'] = 'adequate'
            health_score += 0.15
        elif memory_count > 5:
            health_factors['memory'] = 'basic'
            health_score += 0.1
        else:
            health_factors['memory'] = 'sparse'
            recommendations.append('项目记忆较少，建议记录更多关键信息')
        
        # 评估决策健康度
        decision_count = len([m for m in self.current_state.memory_fragments if m.category.value == 'decision'])
        if decision_count > 5:
            health_factors['decisions'] = 'well_documented'
            health_score += 0.15
        elif decision_count > 2:
            health_factors['decisions'] = 'documented'
            health_score += 0.1
        else:
            health_factors['decisions'] = 'under_documented'
            recommendations.append('建议记录更多关键决策和理由')
        
        # 评估AI置信度健康度
        confidence = self.current_state.ai_confidence
        if confidence > 0.8:
            health_factors['ai_confidence'] = 'high'
            health_score += 0.2
        elif confidence > 0.6:
            health_factors['ai_confidence'] = 'medium'
            health_score += 0.15
        else:
            health_factors['ai_confidence'] = 'low'
            recommendations.append('AI置信度较低，建议提供更多上下文信息')
        
        # 评估活跃度
        recent_activity = len([t for t in self.current_state.transition_history 
                             if (datetime.now() - t.timestamp).days < 1])
        if recent_activity > 5:
            health_factors['activity'] = 'very_active'
            health_score += 0.15
        elif recent_activity > 2:
            health_factors['activity'] = 'active'
            health_score += 0.1
        elif recent_activity > 0:
            health_factors['activity'] = 'moderate'
            health_score += 0.05
        else:
            health_factors['activity'] = 'inactive'
            recommendations.append('项目活跃度较低，建议增加互动频率')
        
        # 计算总体健康等级
        if health_score > 0.8:
            overall_health = 'excellent'
        elif health_score > 0.6:
            overall_health = 'good'
        elif health_score > 0.4:
            overall_health = 'fair'
        else:
            overall_health = 'needs_attention'
        
        return {
            'overall_health': overall_health,
            'health_score': health_score,
            'health_factors': health_factors,
            'recommendations': recommendations,
            'last_assessment': datetime.now().isoformat()
        }
    
    def _calculate_memory_relevance(self, memory: MemoryFragment) -> float:
        """计算记忆相关性分数"""
        relevance = memory.importance
        
        # 基于访问频率调整
        if memory.access_count > 5:
            relevance += 0.1
        elif memory.access_count > 2:
            relevance += 0.05
        
        # 基于时间衰减
        days_old = (datetime.now() - memory.created_at).days
        if days_old < 1:
            relevance += 0.1
        elif days_old < 7:
            relevance += 0.05
        elif days_old > 30:
            relevance -= 0.1
        
        # 基于标签匹配当前任务
        current_task_lower = self.current_state.current_task.lower()
        tag_matches = sum(1 for tag in memory.tags if tag.lower() in current_task_lower)
        relevance += tag_matches * 0.05
        
        return min(1.0, max(0.0, relevance))
    
    def _infer_project_type(self) -> str:
        """推断项目类型"""
        tech_stack = self.current_state.stage_context.get('technology_stack', [])
        task_content = self.current_state.current_task.lower()
        
        # 基于技术栈推断
        if any(tech in ['react', 'vue', 'angular'] for tech in tech_stack):
            return 'web_frontend'
        elif any(tech in ['fastapi', 'django', 'flask', 'express'] for tech in tech_stack):
            return 'web_backend'
        elif any(tech in ['tensorflow', 'pytorch', 'scikit-learn'] for tech in tech_stack):
            return 'machine_learning'
        elif any(tech in ['react-native', 'flutter', 'swift', 'kotlin'] for tech in tech_stack):
            return 'mobile_app'
        
        # 基于任务内容推断
        if any(keyword in task_content for keyword in ['api', '接口', 'backend', '后端']):
            return 'api_development'
        elif any(keyword in task_content for keyword in ['ui', 'frontend', '前端', '界面']):
            return 'frontend_development'
        elif any(keyword in task_content for keyword in ['数据', 'data', '分析', 'analysis']):
            return 'data_project'
        elif any(keyword in task_content for keyword in ['测试', 'test', '自动化']):
            return 'testing_project'
        
        return 'general_development'
    
    def _analyze_current_focus(self) -> str:
        """分析当前关注焦点"""
        current_stage = self.current_state.stage_context.get('current_stage', 'S1')
        task = self.current_state.current_task.lower()
        
        if current_stage in ['S1', 'S2']:
            return '需求分析和设计'
        elif current_stage in ['S3', 'S4']:
            return '开发实现'
        elif current_stage in ['S5', 'S6']:
            return '测试和优化'
        elif '测试' in task or 'test' in task:
            return '质量保证'
        elif '优化' in task or 'optimize' in task:
            return '性能优化'
        elif '部署' in task or 'deploy' in task:
            return '部署上线'
        else:
            return '功能开发'
    
    def _identify_risk_factors(self) -> List[str]:
        """识别风险因素"""
        risks = []
        
        # 进度风险
        if self.current_state.task_progress < 0.3 and len(self.current_state.transition_history) > 10:
            risks.append('进度缓慢，可能存在技术难点')
        
        # 技术风险
        tech_stack = self.current_state.stage_context.get('technology_stack', [])
        if len(tech_stack) > 5:
            risks.append('技术栈复杂，集成风险较高')
        
        # 决策风险
        decision_memories = [m for m in self.current_state.memory_fragments if m.category.value == 'decision']
        if len(decision_memories) < 2 and self.current_state.task_progress > 0.3:
            risks.append('关键决策记录不足，可能影响后续开发')
        
        # 问题风险
        issue_memories = [m for m in self.current_state.memory_fragments if m.category.value == 'issue']
        if len(issue_memories) > 3:
            risks.append('遇到较多问题，需要关注解决方案的有效性')
        
        # 置信度风险
        if self.current_state.ai_confidence < 0.6:
            risks.append('AI置信度较低，建议增加更多上下文信息')
        
        return risks
    
    def _identify_opportunities(self) -> List[str]:
        """识别机会点"""
        opportunities = []
        
        # 并行开发机会
        pending_tasks = self.current_state.stage_context.get('pending_tasks', [])
        if len(pending_tasks) > 2:
            opportunities.append('可以考虑并行开发多个独立任务')
        
        # 自动化机会
        if self.current_state.task_progress > 0.5:
            opportunities.append('可以引入自动化测试和部署流程')
        
        # 优化机会
        pattern_memories = [m for m in self.current_state.memory_fragments if m.category.value == 'pattern']
        if len(pattern_memories) > 2:
            opportunities.append('发现了一些模式，可以考虑代码重构和优化')
        
        # 学习机会
        tech_stack = self.current_state.stage_context.get('technology_stack', [])
        if tech_stack:
            opportunities.append(f'可以深入学习 {tech_stack[0]} 的最佳实践')
        
        return opportunities
    
    def _assess_complexity(self) -> Dict[str, Any]:
        """评估复杂度"""
        tech_count = len(self.current_state.stage_context.get('technology_stack', []))
        memory_count = len(self.current_state.memory_fragments)
        transition_count = len(self.current_state.transition_history)
        
        complexity_score = (tech_count * 0.3 + memory_count * 0.1 + transition_count * 0.05) / 10
        
        if complexity_score > 0.8:
            level = 'high'
        elif complexity_score > 0.5:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'level': level,
            'score': complexity_score,
            'factors': {
                'technology_diversity': tech_count,
                'information_richness': memory_count,
                'process_complexity': transition_count
            }
        }
    
    def _assess_resource_status(self) -> Dict[str, str]:
        """评估资源状态"""
        return {
            'time_allocation': 'adequate' if self.current_state.task_progress > 0.3 else 'needs_attention',
            'information_availability': 'good' if len(self.current_state.memory_fragments) > 5 else 'limited',
            'decision_support': 'strong' if self.current_state.ai_confidence > 0.7 else 'moderate'
        }
    
    def _identify_knowledge_gaps(self) -> List[str]:
        """识别知识缺口"""
        gaps = []
        
        # 基于技术栈识别
        tech_stack = self.current_state.stage_context.get('technology_stack', [])
        if not tech_stack:
            gaps.append('技术栈选择尚未明确')
        
        # 基于记忆类型识别
        memory_categories = self._get_memory_category_stats()
        if memory_categories.get('requirement', 0) < 2:
            gaps.append('需求理解可能不够深入')
        if memory_categories.get('decision', 0) < 1:
            gaps.append('关键决策记录不足')
        
        return gaps
    
    def _analyze_confidence_factors(self) -> Dict[str, float]:
        """分析置信度因素"""
        return {
            'information_completeness': min(1.0, len(self.current_state.memory_fragments) / 10),
            'decision_clarity': min(1.0, len([m for m in self.current_state.memory_fragments if m.category.value == 'decision']) / 3),
            'progress_consistency': 1.0 if self.current_state.task_progress > 0 else 0.5,
            'context_richness': min(1.0, len(self.current_state.stage_context) / 5)
        }
    
    def _identify_learning_opportunities(self) -> List[str]:
        """识别学习机会"""
        opportunities = []
        
        issue_memories = [m for m in self.current_state.memory_fragments if m.category.value == 'issue']
        if issue_memories:
            opportunities.append('从遇到的问题中学习解决方案')
        
        tech_stack = self.current_state.stage_context.get('technology_stack', [])
        if tech_stack:
            opportunities.append(f'深入学习 {", ".join(tech_stack)} 的高级特性')
        
        return opportunities
    
    def _assess_decision_quality(self) -> Dict[str, Any]:
        """评估决策质量"""
        decision_memories = [m for m in self.current_state.memory_fragments if m.category.value == 'decision']
        
        if not decision_memories:
            return {'quality': 'unknown', 'count': 0, 'avg_importance': 0}
        
        avg_importance = sum(m.importance for m in decision_memories) / len(decision_memories)
        
        return {
            'quality': 'high' if avg_importance > 0.7 else 'medium' if avg_importance > 0.5 else 'low',
            'count': len(decision_memories),
            'avg_importance': avg_importance
        }
    
    def _assess_context_completeness(self) -> float:
        """评估上下文完整性"""
        required_contexts = ['current_task', 'technology_stack', 'current_stage']
        available_contexts = 0
        
        if self.current_state.current_task:
            available_contexts += 1
        if self.current_state.stage_context.get('technology_stack'):
            available_contexts += 1
        if self.current_state.stage_context.get('current_stage'):
            available_contexts += 1
        
        return available_contexts / len(required_contexts)
    
    def _suggest_learning_priorities(self) -> List[str]:
        """建议学习优先级"""
        priorities = []
        
        # 基于当前阶段
        current_stage = self.current_state.stage_context.get('current_stage', 'S1')
        if current_stage in ['S1', 'S2']:
            priorities.append('需求分析和系统设计方法')
        elif current_stage in ['S3', 'S4']:
            priorities.append('编程最佳实践和代码质量')
        elif current_stage in ['S5', 'S6']:
            priorities.append('测试策略和性能优化')
        
        # 基于技术栈
        tech_stack = self.current_state.stage_context.get('technology_stack', [])
        if tech_stack:
            priorities.append(f'{tech_stack[0]} 框架深度学习')
        
        return priorities