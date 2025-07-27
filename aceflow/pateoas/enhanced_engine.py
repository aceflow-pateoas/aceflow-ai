"""
PATEOAS增强引擎
整合所有PATEOAS组件，提供统一的智能工作流处理接口
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

from .models import PATEOASState, MemoryFragment, NextAction, ActionType, MemoryCategory
from .state_manager import StateContinuityManager
from .memory_system import ContextMemorySystem
from .flow_controller import AdaptiveFlowControllerWithPATEOAS
from .performance_monitor import PATEOASPerformanceMonitor
from .adaptive_recovery import AdaptiveRecoveryStrategy
from .config import get_config
from .utils import calculate_confidence


class PATEOASEnhancedEngine:
    """PATEOAS增强引擎 - 整合所有智能组件的统一接口"""
    
    def __init__(self, project_id: str = None):
        """
        初始化PATEOAS增强引擎
        
        Args:
            project_id: 项目ID，用于状态和记忆管理
        """
        self.project_id = project_id or f"project_{int(time.time())}"
        self.config = get_config()
        
        # 初始化核心组件
        self.state_manager = StateContinuityManager(project_id=self.project_id)
        self.memory_system = ContextMemorySystem(project_id=self.project_id)
        self.flow_controller = AdaptiveFlowControllerWithPATEOAS()
        
        # 初始化决策门（延迟导入）
        self.decision_gates = self._initialize_decision_gates()
        
        # 初始化性能监控系统
        self.performance_monitor = PATEOASPerformanceMonitor(project_id=self.project_id)
        
        # 初始化自适应恢复策略
        self.recovery_strategy = AdaptiveRecoveryStrategy()
        
        # 兼容性：保持旧的性能指标接口
        self.performance_metrics = self.performance_monitor.current_metrics
        
        # 会话状态
        self.current_session = {
            'session_id': f"session_{int(time.time())}",
            'start_time': datetime.now(),
            'interaction_count': 0,
            'last_action': None,
            'context_cache': {}
        }
        
        print(f"✓ PATEOAS增强引擎已初始化 (项目ID: {self.project_id})")
    
    def _initialize_decision_gates(self) -> Dict[str, Any]:
        """初始化决策门（延迟导入）"""
        try:
            from .decision_gates import OptimizedDG1, OptimizedDG2
            return {
                'DG1': OptimizedDG1(),
                'DG2': OptimizedDG2()
            }
        except ImportError as e:
            print(f"⚠️ 决策门导入失败: {e}")
            # 返回空的决策门，避免系统崩溃
            return {}
    
    def process_with_state_awareness(
        self,
        user_input: str,
        current_context: Dict[str, Any] = None,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        带状态感知的用户输入处理
        
        Args:
            user_input: 用户输入
            current_context: 当前上下文信息
            options: 处理选项
            
        Returns:
            增强的处理结果
        """
        start_time = time.time()
        self.performance_metrics['total_requests'] += 1
        self.current_session['interaction_count'] += 1
        
        try:
            # 1. 加载项目状态
            op_id = self.performance_monitor.start_operation("load_project_state")
            project_state = self.state_manager.get_current_state()
            self.performance_monitor.end_operation(op_id, "state_manager", True)
            
            # 2. 获取相关记忆
            op_id = self.performance_monitor.start_operation("retrieve_memories")
            relevant_memories = self._retrieve_relevant_memories(user_input, current_context)
            self.performance_monitor.end_operation(op_id, "memory_system", True)
            
            # 3. 更新当前状态
            op_id = self.performance_monitor.start_operation("update_state")
            updated_state = self._update_current_state(
                project_state, user_input, current_context, relevant_memories
            )
            self.performance_monitor.end_operation(op_id, "state_processor", True)
            
            # 4. 智能决策处理
            op_id = self.performance_monitor.start_operation("decision_making")
            decision_result = self.flow_controller.decide_next_action(
                user_input=user_input,
                current_state=updated_state,
                memory_context=[m.__dict__ for m in relevant_memories]
            )
            
            # 标准化决策结果格式
            decision_result = self._normalize_decision_result(decision_result)
            self.performance_monitor.end_operation(op_id, "flow_controller", True)
            
            # 5. 决策门评估
            op_id = self.performance_monitor.start_operation("decision_gates")
            gate_evaluations = self._evaluate_decision_gates(updated_state, relevant_memories)
            self.performance_monitor.end_operation(op_id, "decision_gates", True)
            
            # 6. 生成增强结果
            op_id = self.performance_monitor.start_operation("result_enhancement")
            enhanced_result = self._enhance_result_with_pateoas(
                decision_result, gate_evaluations, updated_state, relevant_memories
            )
            self.performance_monitor.end_operation(op_id, "result_enhancer", True)
            
            # 7. 保存状态和记忆
            op_id = self.performance_monitor.start_operation("save_state")
            self._save_interaction_state(
                user_input, enhanced_result, updated_state, relevant_memories
            )
            self.performance_monitor.end_operation(op_id, "state_persistence", True)
            
            # 8. 更新性能指标
            processing_time = time.time() - start_time
            self.performance_monitor.record_decision_accuracy(enhanced_result['confidence'])
            self._update_performance_metrics(processing_time, True)
            
            # 记录用户满意度（基于结果质量）
            satisfaction_score = self._calculate_user_satisfaction(enhanced_result)
            self.performance_monitor.record_user_satisfaction(satisfaction_score)
            
            # 记录记忆效率
            memory_efficiency = self._calculate_memory_efficiency(relevant_memories, user_input)
            self.performance_monitor.record_memory_efficiency(memory_efficiency)
            
            self.performance_metrics['successful_requests'] += 1
            self.current_session['last_action'] = enhanced_result['primary_action']
            
            return enhanced_result
            
        except Exception as e:
            # 错误处理
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time, False)
            
            error_result = self._handle_processing_error(e, user_input, current_context)
            return error_result
    
    def _retrieve_relevant_memories(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None
    ) -> List[MemoryFragment]:
        """检索相关记忆"""
        
        # 使用智能召回系统
        query_context = {
            'user_input': user_input,
            'current_stage': context.get('current_stage', 'S1') if context else 'S1',
            'session_context': self.current_session
        }
        
        # 使用智能召回系统
        recall_result = self.memory_system.intelligent_recall(
            query=user_input,
            current_state=query_context,
            limit=10
        )
        
        # 转换为MemoryFragment对象列表
        relevant_memories = []
        for result in recall_result.get('results', []):
            memory = MemoryFragment(
                content=result['content'],
                category=MemoryCategory(result['category']),
                importance=result['importance'],
                tags=result['tags'],
                created_at=datetime.fromisoformat(result['created_at'])
            )
            relevant_memories.append(memory)
        
        return relevant_memories
    
    def _update_current_state(
        self,
        project_state: PATEOASState,
        user_input: str,
        context: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """更新当前状态"""
        
        # 基础状态信息
        current_state = {
            'project_id': self.project_id,
            'session_id': self.current_session['session_id'],
            'current_stage': self._extract_current_stage(project_state),
            'task_progress': self._extract_task_progress(project_state),
            'interaction_count': self.current_session['interaction_count'],
            'timestamp': datetime.now().isoformat()
        }
        
        # 合并外部上下文
        if context:
            current_state.update(context)
        
        # 基于记忆推断状态信息
        if memories:
            recent_issues = len([m for m in memories if m.category.value == 'issue'])
            recent_decisions = len([m for m in memories if m.category.value == 'decision'])
            recent_learning = len([m for m in memories if m.category.value == 'learning'])
            
            current_state.update({
                'recent_issues_count': recent_issues,
                'recent_decisions_count': recent_decisions,
                'recent_learning_count': recent_learning,
                'memory_context_richness': len(memories) / 10.0  # 标准化
            })
        
        # 推断项目复杂度和团队经验
        if not current_state.get('project_complexity'):
            current_state['project_complexity'] = self._infer_project_complexity(memories)
        
        if not current_state.get('team_experience'):
            current_state['team_experience'] = self._infer_team_experience(memories)
        
        return current_state
    
    def _evaluate_decision_gates(
        self, 
        current_state: Dict[str, Any], 
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """评估决策门"""
        
        evaluations = {}
        current_stage = current_state.get('current_stage', 'S1')
        
        # 根据当前阶段选择合适的决策门
        if self.decision_gates and current_stage in ['S1', 'S2'] and 'DG1' in self.decision_gates:
            # 开发前检查
            dg1_evaluation = self.decision_gates['DG1'].evaluate(current_state, memories, {})
            evaluations['DG1'] = {
                'result': dg1_evaluation.result.value,
                'confidence': dg1_evaluation.confidence,
                'score': dg1_evaluation.score,
                'recommendations': dg1_evaluation.recommendations,
                'risk_factors': dg1_evaluation.risk_factors
            }
        
        if self.decision_gates and current_stage in ['S3', 'S4', 'S5'] and 'DG2' in self.decision_gates:
            # 任务循环控制
            dg2_evaluation = self.decision_gates['DG2'].evaluate(current_state, memories, {})
            evaluations['DG2'] = {
                'result': dg2_evaluation.result.value,
                'confidence': dg2_evaluation.confidence,
                'score': dg2_evaluation.score,
                'recommendations': dg2_evaluation.recommendations,
                'risk_factors': dg2_evaluation.risk_factors
            }
        
        return evaluations
    
    def _enhance_result_with_pateoas(
        self,
        decision_result: Dict[str, Any],
        gate_evaluations: Dict[str, Any],
        current_state: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """使用PATEOAS信息增强结果 - 简化稳定版"""
        
        # 基础增强结果
        enhanced_result = {
            'primary_action': decision_result['primary_action'],
            'alternative_actions': decision_result['alternative_actions'],
            'confidence': decision_result['confidence'],
            'reasoning_chain': decision_result['reasoning_chain'],
            
            # PATEOAS状态信息
            'pateoas_state': {
                'project_id': self.project_id,
                'session_id': self.current_session['session_id'],
                'current_stage': current_state.get('current_stage', 'S1'),
                'task_progress': current_state.get('task_progress', 0.0),
                'interaction_count': self.current_session['interaction_count'],
                'timestamp': datetime.now().isoformat()
            },
            
            # 记忆上下文
            'memory_context': {
                'relevant_memories_count': len(memories),
                'memory_categories': self._analyze_memory_categories(memories),
                'context_richness': len(memories) / 10.0
            },
            
            # 决策门评估
            'decision_gates': gate_evaluations,
            
            # 下一步行动建议
            'next_actions_suggestions': self._generate_next_actions_suggestions(
                decision_result, gate_evaluations, current_state
            ),
            
            # 替代路径推荐
            'alternative_paths': [
                {
                    'path_type': 'fast_track',
                    'description': '快速原型开发路径',
                    'estimated_time_saving': '40%',
                    'risk_level': 'medium'
                },
                {
                    'path_type': 'thorough',
                    'description': '详细分析和设计路径',
                    'estimated_time_saving': '0%',
                    'risk_level': 'low'
                }
            ],
            
            # 工作流优化建议
            'workflow_optimization': self._get_workflow_optimization_suggestions(
                current_state, memories
            ),
            
            # 性能洞察
            'performance_insights': {
                'processing_efficiency': self._calculate_processing_efficiency(),
                'recommendation_quality': self._assess_recommendation_quality(decision_result),
                'user_satisfaction_estimate': self.performance_metrics.get('user_satisfaction', 0.8)
            },
            
            # 上下文洞察
            'contextual_insights': self._generate_contextual_insights(
                current_state, memories, decision_result
            ),
            
            # 元信息
            'meta_information': {
                'timestamp': datetime.now().isoformat(),
                'processing_time': 0.0,
                'pateoas_version': '2.0.0',
                'enhancement_level': 'standard',
                'components_used': ['state_manager', 'memory_system', 'flow_controller', 'decision_gates']
            }
        }
        
        return enhanced_result
    
    def _save_interaction_state(
        self,
        user_input: str,
        result: Dict[str, Any],
        current_state: Dict[str, Any],
        memories: List[MemoryFragment]
    ):
        """保存交互状态"""
        
        # 1. 更新项目状态
        new_state = PATEOASState(
            current_task=f"处理用户请求: {user_input[:50]}...",
            task_progress=current_state.get('task_progress', 0.0),
            stage_context=current_state,
            project_id=self.project_id
        )
        
        # 更新状态管理器的当前状态
        self.state_manager.current_state = new_state
        self.state_manager._save_state()
        
        # 2. 保存新的记忆片段
        interaction_memory = MemoryFragment(
            content=f"用户输入: {user_input}; AI建议: {result['primary_action'].description}",
            category=MemoryCategory.CONTEXT,  # 默认为上下文类别
            importance=result['confidence'],
            tags=self._extract_tags_from_interaction(user_input, result),
            created_at=datetime.now()
        )
        
        self.memory_system.add_memory(
            content=interaction_memory.content,
            category=interaction_memory.category.value,
            importance=interaction_memory.importance,
            tags=interaction_memory.tags
        )
        
        # 3. 更新会话缓存
        self.current_session['context_cache'] = {
            'last_user_input': user_input,
            'last_result': result,
            'last_state': current_state,
            'timestamp': datetime.now().isoformat()
        }
    
    def _handle_processing_error(
        self, 
        error: Exception, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理处理错误 - 使用自适应恢复策略"""
        
        # 使用自适应恢复策略分析和处理错误
        recovery_context = {
            'user_input': user_input,
            'system_state': context or {},
            'component': 'enhanced_engine'
        }
        
        recovery_analysis = self.recovery_strategy.analyze_and_recover(
            error, recovery_context, 'enhanced_engine'
        )
        
        # 构建增强的错误结果
        error_result = {
            'primary_action': recovery_analysis['next_action'],
            'alternative_actions': [
                action.to_next_action() for action in recovery_analysis['available_strategies'][:2]
            ],
            'confidence': recovery_analysis['confidence'],
            'reasoning_chain': [
                {
                    'step_id': 'error_analysis',
                    'description': f"检测到错误: {recovery_analysis['error_pattern']}",
                    'confidence': 0.9
                },
                {
                    'step_id': 'recovery_strategy',
                    'description': f"推荐恢复策略: {recovery_analysis['recommended_strategy'].strategy.value}",
                    'confidence': recovery_analysis['confidence']
                }
            ],
            'error_info': {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'error_pattern': recovery_analysis['error_pattern'],
                'severity': recovery_analysis['recovery_context'].severity,
                'timestamp': datetime.now().isoformat()
            },
            'recovery_info': {
                'recovery_type': recovery_analysis['recovery_type'].value,
                'available_strategies': len(recovery_analysis['available_strategies']),
                'recommended_strategy': recovery_analysis['recommended_strategy'].strategy.value,
                'manual_instructions': recovery_analysis.get('manual_instructions'),
                'recovery_result': recovery_analysis.get('recovery_result')
            },
            'pateoas_state': {
                'project_id': self.project_id,
                'error_occurred': True,
                'recovery_mode': True,
                'recovery_type': recovery_analysis['recovery_type'].value
            }
        }
        
        # 记录错误和恢复信息到记忆系统
        error_memory = MemoryFragment(
            content=f"系统错误及恢复: {str(error)} | 恢复策略: {recovery_analysis['recommended_strategy'].strategy.value}",
            category=MemoryCategory.ISSUE,
            importance=0.8,
            tags=['error', 'recovery', 'system', recovery_analysis['error_pattern']],
            created_at=datetime.now()
        )
        
        try:
            self.memory_system.add_memory(
                content=error_memory.content,
                category=error_memory.category.value,
                importance=error_memory.importance,
                tags=error_memory.tags
            )
        except:
            pass  # 避免错误处理中的二次错误
        
        return error_result
    
    def _infer_project_complexity(self, memories: List[MemoryFragment]) -> str:
        """推断项目复杂度"""
        
        if not memories:
            return 'medium'
        
        # 基于记忆内容分析复杂度
        complexity_indicators = {
            'high': ['微服务', 'microservice', '分布式', 'distributed', '高并发', 'scalability', '架构', 'architecture'],
            'low': ['简单', 'simple', '基础', 'basic', '小型', 'small', '快速', 'quick']
        }
        
        high_count = 0
        low_count = 0
        
        for memory in memories:
            content = memory.content.lower()
            for indicator in complexity_indicators['high']:
                if indicator in content:
                    high_count += 1
            for indicator in complexity_indicators['low']:
                if indicator in content:
                    low_count += 1
        
        if high_count > low_count * 2:
            return 'high'
        elif low_count > high_count * 2:
            return 'low'
        else:
            return 'medium'
    
    def _infer_team_experience(self, memories: List[MemoryFragment]) -> str:
        """推断团队经验水平"""
        
        if not memories:
            return 'medium'
        
        # 基于学习记忆和决策质量推断经验
        learning_memories = [m for m in memories if m.category.value == 'learning']
        decision_memories = [m for m in memories if m.category.value == 'decision']
        
        # 基于学习频率和决策质量评估经验
        if len(learning_memories) > 5:
            # 学习记忆多，可能是新手团队在学习
            avg_learning_importance = sum(m.importance for m in learning_memories) / len(learning_memories)
            if avg_learning_importance > 0.8:
                return 'junior'  # 高重要性学习记忆多，说明在学习基础知识
        
        if len(decision_memories) > 3:
            # 决策记忆多且质量高，可能是经验丰富的团队
            avg_decision_importance = sum(m.importance for m in decision_memories) / len(decision_memories)
            if avg_decision_importance > 0.8:
                return 'senior'
        
        return 'medium'
    
    def _analyze_memory_categories(self, memories: List[MemoryFragment]) -> Dict[str, int]:
        """分析记忆类别分布"""
        categories = {}
        for memory in memories:
            category = memory.category.value
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _generate_next_actions_suggestions(
        self,
        decision_result: Dict[str, Any],
        gate_evaluations: Dict[str, Any],
        current_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成下一步行动建议"""
        
        suggestions = []
        
        # 基于决策门结果生成建议
        for gate_id, evaluation in gate_evaluations.items():
            if evaluation['result'] == 'fail':
                suggestions.append({
                    'type': 'quality_improvement',
                    'description': f'{gate_id}未通过，需要改进质量',
                    'recommendations': evaluation['recommendations'],
                    'priority': 'high'
                })
            elif evaluation['result'] == 'warning':
                suggestions.append({
                    'type': 'attention_needed',
                    'description': f'{gate_id}需要注意，建议谨慎进行',
                    'recommendations': evaluation['recommendations'],
                    'priority': 'medium'
                })
        
        # 基于当前状态生成建议
        current_stage = current_state.get('current_stage', 'S1')
        task_progress = current_state.get('task_progress', 0.0)
        
        if task_progress < 0.5 and current_stage in ['S3', 'S4']:
            suggestions.append({
                'type': 'progress_acceleration',
                'description': '当前阶段进度较慢，建议优化工作流程',
                'priority': 'medium'
            })
        
        # 基于记忆上下文生成建议
        if current_state.get('recent_issues_count', 0) > 3:
            suggestions.append({
                'type': 'issue_resolution',
                'description': '最近问题较多，建议进行问题分析和预防',
                'priority': 'high'
            })
        
        return suggestions
    
    def _get_workflow_optimization_suggestions(
        self,
        current_state: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """获取工作流优化建议"""
        
        # 使用流程控制器的优化功能
        try:
            optimization_result = self.flow_controller.optimize_workflow_with_pateoas(
                current_state=current_state,
                memories=memories
            )
            return optimization_result['recommendation']
        except:
            # 如果优化失败，返回基础建议
            return {
                'mode': 'standard',
                'strategy': 'balanced',
                'actions': [],
                'confidence': 0.5,
                'reasoning': '无法获取详细优化建议，建议使用标准模式'
            }
    
    def _calculate_processing_efficiency(self) -> float:
        """计算处理效率"""
        if self.performance_metrics['total_requests'] == 0:
            return 0.8
        
        success_rate = self.performance_metrics['successful_requests'] / self.performance_metrics['total_requests']
        avg_response_time = self.performance_metrics['average_response_time']
        
        # 基于成功率和响应时间计算效率
        time_efficiency = max(0.1, min(1.0, 2.0 - avg_response_time))  # 假设2秒是理想响应时间
        overall_efficiency = success_rate * 0.7 + time_efficiency * 0.3
        
        return overall_efficiency
    
    def _assess_recommendation_quality(self, decision_result: Dict[str, Any]) -> float:
        """评估推荐质量"""
        
        # 基于置信度、推理链完整性和替代方案数量评估质量
        confidence = decision_result.get('confidence', 0.5)
        reasoning_chain_length = len(decision_result.get('reasoning_chain', []))
        alternatives_count = len(decision_result.get('alternative_actions', []))
        
        # 推理链长度评分（3-5步为理想）
        reasoning_score = min(1.0, reasoning_chain_length / 5.0)
        
        # 替代方案评分（2-3个为理想）
        alternatives_score = min(1.0, alternatives_count / 3.0)
        
        # 综合质量评分
        quality_score = confidence * 0.5 + reasoning_score * 0.3 + alternatives_score * 0.2
        
        return quality_score
    
    def _generate_contextual_insights(
        self,
        current_state: Dict[str, Any],
        memories: List[MemoryFragment],
        decision_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成上下文感知的洞察"""
        
        insights = {
            'project_health': self._assess_project_health(current_state, memories),
            'team_dynamics': self._analyze_team_dynamics(memories),
            'risk_assessment': self._comprehensive_risk_assessment(current_state, memories),
            'learning_opportunities': self._identify_learning_opportunities(memories),
            'efficiency_insights': self._analyze_efficiency_patterns(current_state, memories)
        }
        
        return insights
    
    def _assess_project_health(self, current_state: Dict[str, Any], memories: List[MemoryFragment]) -> Dict[str, Any]:
        """评估项目健康度"""
        
        # 基于进度、问题数量、决策质量评估健康度
        task_progress = current_state.get('task_progress', 0.0)
        issues_count = current_state.get('recent_issues_count', 0)
        decisions_count = current_state.get('recent_decisions_count', 0)
        
        # 进度健康度
        progress_health = min(1.0, task_progress * 1.2)  # 80%以上进度为健康
        
        # 问题健康度
        issue_health = max(0.0, 1.0 - issues_count / 10.0)  # 问题越少越健康
        
        # 决策活跃度
        decision_activity = min(1.0, decisions_count / 5.0)  # 适度的决策活动为健康
        
        overall_health = (progress_health * 0.4 + issue_health * 0.4 + decision_activity * 0.2)
        
        health_level = 'excellent' if overall_health > 0.8 else 'good' if overall_health > 0.6 else 'fair' if overall_health > 0.4 else 'poor'
        
        return {
            'overall_health': overall_health,
            'health_level': health_level,
            'progress_health': progress_health,
            'issue_health': issue_health,
            'decision_activity': decision_activity
        }
    
    def _analyze_team_dynamics(self, memories: List[MemoryFragment]) -> Dict[str, Any]:
        """分析团队动态"""
        
        learning_memories = [m for m in memories if m.category.value == 'learning']
        decision_memories = [m for m in memories if m.category.value == 'decision']
        issue_memories = [m for m in memories if m.category.value == 'issue']
        
        # 学习活跃度
        learning_activity = len(learning_memories) / max(1, len(memories))
        
        # 决策效率
        decision_efficiency = len(decision_memories) / max(1, len(memories))
        
        # 问题解决能力
        problem_solving = 1.0 - (len(issue_memories) / max(1, len(memories)))
        
        return {
            'learning_activity': learning_activity,
            'decision_efficiency': decision_efficiency,
            'problem_solving_capability': problem_solving,
            'team_collaboration_score': (learning_activity + decision_efficiency + problem_solving) / 3.0
        }
    
    def _comprehensive_risk_assessment(self, current_state: Dict[str, Any], memories: List[MemoryFragment]) -> Dict[str, Any]:
        """综合风险评估"""
        
        risks = []
        risk_score = 0.0
        
        # 进度风险
        task_progress = current_state.get('task_progress', 0.0)
        current_stage = current_state.get('current_stage', 'S1')
        
        if task_progress < 0.3 and current_stage in ['S3', 'S4']:
            risks.append('进度落后风险')
            risk_score += 0.3
        
        # 质量风险
        issues_count = current_state.get('recent_issues_count', 0)
        if issues_count > 5:
            risks.append('质量问题风险')
            risk_score += 0.4
        
        # 技术风险
        learning_count = current_state.get('recent_learning_count', 0)
        if learning_count < 2 and current_stage in ['S3', 'S4']:
            risks.append('技术准备不足风险')
            risk_score += 0.2
        
        # 团队风险
        if current_state.get('team_experience') == 'junior' and current_state.get('project_complexity') == 'high':
            risks.append('团队经验与项目复杂度不匹配风险')
            risk_score += 0.3
        
        risk_level = 'high' if risk_score > 0.6 else 'medium' if risk_score > 0.3 else 'low'
        
        return {
            'risks': risks,
            'risk_score': min(1.0, risk_score),
            'risk_level': risk_level,
            'mitigation_suggestions': self._generate_risk_mitigation_suggestions(risks)
        }
    
    def _identify_learning_opportunities(self, memories: List[MemoryFragment]) -> List[Dict[str, Any]]:
        """识别学习机会"""
        
        opportunities = []
        
        # 基于问题记忆识别学习机会
        issue_memories = [m for m in memories if m.category.value == 'issue']
        if issue_memories:
            common_issues = {}
            for memory in issue_memories:
                for tag in memory.tags:
                    common_issues[tag] = common_issues.get(tag, 0) + 1
            
            # 找出最常见的问题类型
            if common_issues:
                most_common_issue = max(common_issues.items(), key=lambda x: x[1])
                opportunities.append({
                    'type': 'problem_solving',
                    'description': f'针对 {most_common_issue[0]} 相关问题的深入学习',
                    'priority': 'high' if most_common_issue[1] > 2 else 'medium'
                })
        
        # 基于技术栈识别学习机会
        pattern_memories = [m for m in memories if m.category.value == 'pattern']
        if pattern_memories:
            opportunities.append({
                'type': 'pattern_optimization',
                'description': '基于已识别模式的最佳实践学习',
                'priority': 'medium'
            })
        
        return opportunities
    
    def _analyze_efficiency_patterns(self, current_state: Dict[str, Any], memories: List[MemoryFragment]) -> Dict[str, Any]:
        """分析效率模式"""
        
        # 基于交互历史分析效率模式
        interaction_count = current_state.get('interaction_count', 0)
        task_progress = current_state.get('task_progress', 0.0)
        
        # 交互效率
        interaction_efficiency = task_progress / max(1, interaction_count / 10.0)
        
        # 记忆利用效率
        memory_richness = current_state.get('memory_context_richness', 0.0)
        memory_efficiency = min(1.0, memory_richness * 2.0)
        
        return {
            'interaction_efficiency': min(1.0, interaction_efficiency),
            'memory_utilization_efficiency': memory_efficiency,
            'overall_efficiency_trend': 'improving' if interaction_efficiency > 0.7 else 'stable' if interaction_efficiency > 0.5 else 'declining'
        }
    
    def _generate_risk_mitigation_suggestions(self, risks: List[str]) -> List[str]:
        """生成风险缓解建议"""
        
        suggestions = []
        
        for risk in risks:
            if '进度落后' in risk:
                suggestions.append('考虑并行执行任务或简化非关键功能')
            elif '质量问题' in risk:
                suggestions.append('增加代码审查和测试覆盖率')
            elif '技术准备不足' in risk:
                suggestions.append('安排技术培训或寻求专家支持')
            elif '团队经验' in risk:
                suggestions.append('增加高级开发者指导或降低项目复杂度')
        
        return suggestions
    
    def _extract_tags_from_interaction(self, user_input: str, result: Dict[str, Any]) -> List[str]:
        """从交互中提取标签"""
        
        tags = ['interaction']
        
        # 从用户输入提取标签
        if '问题' in user_input or 'issue' in user_input.lower():
            tags.append('problem')
        if '优化' in user_input or 'optimize' in user_input.lower():
            tags.append('optimization')
        if '继续' in user_input or 'continue' in user_input.lower():
            tags.append('continuation')
        
        # 从结果提取标签
        action_type = result['primary_action'].action_type.value
        tags.append(action_type)
        
        return tags
    
    def _update_performance_metrics(self, processing_time: float, success: bool):
        """更新性能指标"""
        
        # 更新平均响应时间
        total_requests = self.performance_metrics['total_requests']
        current_avg = self.performance_metrics['average_response_time']
        
        new_avg = (current_avg * (total_requests - 1) + processing_time) / total_requests
        self.performance_metrics['average_response_time'] = new_avg
        
        # 更新决策准确性（简化实现）
        if success:
            self.performance_metrics['decision_accuracy'] = min(0.95, self.performance_metrics['decision_accuracy'] + 0.01)
        else:
            self.performance_metrics['decision_accuracy'] = max(0.5, self.performance_metrics['decision_accuracy'] - 0.02)
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        
        return {
            'project_id': self.project_id,
            'session_info': self.current_session,
            'performance_metrics': self.performance_metrics,
            'components_status': {
                'state_manager': 'active',
                'memory_system': 'active',
                'flow_controller': 'active',
                'decision_gates': 'active'
            },
            'system_health': 'healthy' if self.performance_metrics['decision_accuracy'] > 0.7 else 'degraded'
        }
    
    def reset_session(self):
        """重置会话"""
        
        self.current_session = {
            'session_id': f"session_{int(time.time())}",
            'start_time': datetime.now(),
            'interaction_count': 0,
            'last_action': None,
            'context_cache': {}
        }
        
        print(f"✓ 会话已重置 (新会话ID: {self.current_session['session_id']})")   
 
    def _analyze_memory_categories(self, memories: List[MemoryFragment]) -> Dict[str, int]:
        """分析记忆类别分布"""
        categories = {}
        for memory in memories:
            category = memory.category.value
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _generate_next_actions_suggestions(
        self,
        decision_result: Dict[str, Any],
        gate_evaluations: Dict[str, Any],
        current_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成下一步行动建议"""
        
        suggestions = []
        
        # 基于决策门结果生成建议
        for gate_id, evaluation in gate_evaluations.items():
            if evaluation['result'] == 'fail':
                suggestions.append({
                    'type': 'quality_improvement',
                    'description': f'{gate_id}未通过，需要改进质量',
                    'recommendations': evaluation['recommendations'],
                    'priority': 'high'
                })
            elif evaluation['result'] == 'warning':
                suggestions.append({
                    'type': 'attention_needed',
                    'description': f'{gate_id}需要注意，建议谨慎进行',
                    'recommendations': evaluation['recommendations'],
                    'priority': 'medium'
                })
        
        # 基于当前状态生成建议
        current_stage = current_state.get('current_stage', 'S1')
        task_progress = current_state.get('task_progress', 0.0)
        
        if task_progress < 0.5 and current_stage in ['S3', 'S4']:
            suggestions.append({
                'type': 'progress_acceleration',
                'description': '当前阶段进度较慢，建议优化工作流程',
                'priority': 'medium'
            })
        
        # 基于记忆上下文生成建议
        if current_state.get('recent_issues_count', 0) > 3:
            suggestions.append({
                'type': 'issue_resolution',
                'description': '最近问题较多，建议进行问题分析和预防',
                'priority': 'high'
            })
        
        return suggestions
    
    def _get_workflow_optimization_suggestions(
        self,
        current_state: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """获取工作流优化建议"""
        
        # 使用流程控制器的优化功能
        try:
            optimization_result = self.flow_controller.optimize_workflow_with_pateoas(
                current_state=current_state,
                memories=memories
            )
            return optimization_result['recommendation']
        except:
            # 如果优化失败，返回基础建议
            return {
                'mode': 'standard',
                'strategy': 'balanced',
                'actions': [],
                'confidence': 0.5,
                'reasoning': '无法获取详细优化建议，建议使用标准模式'
            }
    
    def _calculate_processing_efficiency(self) -> float:
        """计算处理效率"""
        if self.performance_metrics['total_requests'] == 0:
            return 0.8
        
        success_rate = self.performance_metrics['successful_requests'] / self.performance_metrics['total_requests']
        avg_response_time = self.performance_metrics['average_response_time']
        
        # 基于成功率和响应时间计算效率
        time_efficiency = max(0.1, min(1.0, 2.0 - avg_response_time))  # 假设2秒是理想响应时间
        overall_efficiency = success_rate * 0.7 + time_efficiency * 0.3
        
        return overall_efficiency
    
    def _assess_recommendation_quality(self, decision_result: Dict[str, Any]) -> float:
        """评估推荐质量"""
        
        # 基于置信度、推理链完整性和替代方案数量评估质量
        confidence = decision_result.get('confidence', 0.5)
        reasoning_chain_length = len(decision_result.get('reasoning_chain', []))
        alternatives_count = len(decision_result.get('alternative_actions', []))
        
        # 推理链长度评分（3-5步为理想）
        reasoning_score = min(1.0, reasoning_chain_length / 5.0)
        
        # 替代方案评分（2-3个为理想）
        alternatives_score = min(1.0, alternatives_count / 3.0)
        
        # 综合质量评分
        quality_score = confidence * 0.5 + reasoning_score * 0.3 + alternatives_score * 0.2
        
        return quality_score
    
    def _generate_contextual_insights(
        self,
        current_state: Dict[str, Any],
        memories: List[MemoryFragment],
        decision_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成上下文感知的洞察"""
        
        insights = {
            'project_health': self._assess_project_health(current_state, memories),
            'team_dynamics': self._analyze_team_dynamics(memories),
            'risk_assessment': self._comprehensive_risk_assessment(current_state, memories),
            'learning_opportunities': self._identify_learning_opportunities(memories),
            'efficiency_insights': self._analyze_efficiency_patterns(current_state, memories)
        }
        
        return insights
    
    def _assess_project_health(self, current_state: Dict[str, Any], memories: List[MemoryFragment]) -> Dict[str, Any]:
        """评估项目健康度"""
        
        # 基于进度、问题数量、决策质量评估健康度
        task_progress = current_state.get('task_progress', 0.0)
        issues_count = current_state.get('recent_issues_count', 0)
        decisions_count = current_state.get('recent_decisions_count', 0)
        
        # 进度健康度
        progress_health = min(1.0, task_progress * 1.2)  # 80%以上进度为健康
        
        # 问题健康度
        issue_health = max(0.0, 1.0 - issues_count / 10.0)  # 问题越少越健康
        
        # 决策活跃度
        decision_activity = min(1.0, decisions_count / 5.0)  # 适度的决策活动为健康
        
        overall_health = (progress_health * 0.4 + issue_health * 0.4 + decision_activity * 0.2)
        
        health_level = 'excellent' if overall_health > 0.8 else 'good' if overall_health > 0.6 else 'fair' if overall_health > 0.4 else 'poor'
        
        return {
            'overall_health': overall_health,
            'health_level': health_level,
            'progress_health': progress_health,
            'issue_health': issue_health,
            'decision_activity': decision_activity
        }
    
    def _analyze_team_dynamics(self, memories: List[MemoryFragment]) -> Dict[str, Any]:
        """分析团队动态"""
        
        learning_memories = [m for m in memories if m.category.value == 'learning']
        decision_memories = [m for m in memories if m.category.value == 'decision']
        issue_memories = [m for m in memories if m.category.value == 'issue']
        
        # 学习活跃度
        learning_activity = len(learning_memories) / max(1, len(memories))
        
        # 决策效率
        decision_efficiency = len(decision_memories) / max(1, len(memories))
        
        # 问题解决能力
        problem_solving = 1.0 - (len(issue_memories) / max(1, len(memories)))
        
        return {
            'learning_activity': learning_activity,
            'decision_efficiency': decision_efficiency,
            'problem_solving_capability': problem_solving,
            'team_collaboration_score': (learning_activity + decision_efficiency + problem_solving) / 3.0
        }
    
    def _comprehensive_risk_assessment(self, current_state: Dict[str, Any], memories: List[MemoryFragment]) -> Dict[str, Any]:
        """综合风险评估"""
        
        risks = []
        risk_score = 0.0
        
        # 进度风险
        task_progress = current_state.get('task_progress', 0.0)
        current_stage = current_state.get('current_stage', 'S1')
        
        if task_progress < 0.3 and current_stage in ['S3', 'S4']:
            risks.append('进度落后风险')
            risk_score += 0.3
        
        # 质量风险
        issues_count = current_state.get('recent_issues_count', 0)
        if issues_count > 5:
            risks.append('质量问题风险')
            risk_score += 0.4
        
        # 技术风险
        learning_count = current_state.get('recent_learning_count', 0)
        if learning_count < 2 and current_stage in ['S3', 'S4']:
            risks.append('技术准备不足风险')
            risk_score += 0.2
        
        # 团队风险
        if current_state.get('team_experience') == 'junior' and current_state.get('project_complexity') == 'high':
            risks.append('团队经验与项目复杂度不匹配风险')
            risk_score += 0.3
        
        risk_level = 'high' if risk_score > 0.6 else 'medium' if risk_score > 0.3 else 'low'
        
        return {
            'risks': risks,
            'risk_score': min(1.0, risk_score),
            'risk_level': risk_level,
            'mitigation_suggestions': self._generate_risk_mitigation_suggestions(risks)
        }
    
    def _identify_learning_opportunities(self, memories: List[MemoryFragment]) -> List[Dict[str, Any]]:
        """识别学习机会"""
        
        opportunities = []
        
        # 基于问题记忆识别学习机会
        issue_memories = [m for m in memories if m.category.value == 'issue']
        if issue_memories:
            common_issues = {}
            for memory in issue_memories:
                for tag in memory.tags:
                    common_issues[tag] = common_issues.get(tag, 0) + 1
            
            # 找出最常见的问题类型
            if common_issues:
                most_common_issue = max(common_issues.items(), key=lambda x: x[1])
                opportunities.append({
                    'type': 'problem_solving',
                    'description': f'针对 {most_common_issue[0]} 相关问题的深入学习',
                    'priority': 'high' if most_common_issue[1] > 2 else 'medium'
                })
        
        # 基于技术栈识别学习机会
        pattern_memories = [m for m in memories if m.category.value == 'pattern']
        if pattern_memories:
            opportunities.append({
                'type': 'pattern_optimization',
                'description': '基于已识别模式的最佳实践学习',
                'priority': 'medium'
            })
        
        return opportunities
    
    def _analyze_efficiency_patterns(self, current_state: Dict[str, Any], memories: List[MemoryFragment]) -> Dict[str, Any]:
        """分析效率模式"""
        
        # 基于交互历史分析效率模式
        interaction_count = current_state.get('interaction_count', 0)
        task_progress = current_state.get('task_progress', 0.0)
        
        # 交互效率
        interaction_efficiency = task_progress / max(1, interaction_count / 10.0)
        
        # 记忆利用效率
        memory_richness = current_state.get('memory_context_richness', 0.0)
        memory_efficiency = min(1.0, memory_richness * 2.0)
        
        return {
            'interaction_efficiency': min(1.0, interaction_efficiency),
            'memory_utilization_efficiency': memory_efficiency,
            'overall_efficiency_trend': 'improving' if interaction_efficiency > 0.7 else 'stable' if interaction_efficiency > 0.5 else 'declining'
        }
    
    def _generate_risk_mitigation_suggestions(self, risks: List[str]) -> List[str]:
        """生成风险缓解建议"""
        
        suggestions = []
        
        for risk in risks:
            if '进度落后' in risk:
                suggestions.append('考虑并行执行任务或简化非关键功能')
            elif '质量问题' in risk:
                suggestions.append('增加代码审查和测试覆盖率')
            elif '技术准备不足' in risk:
                suggestions.append('安排技术培训或寻求专家支持')
            elif '团队经验' in risk:
                suggestions.append('增加高级开发者指导或降低项目复杂度')
        
        return suggestions
    
    def _extract_tags_from_interaction(self, user_input: str, result: Dict[str, Any]) -> List[str]:
        """从交互中提取标签"""
        
        tags = ['interaction']
        
        # 从用户输入提取标签
        if '问题' in user_input or 'issue' in user_input.lower():
            tags.append('problem')
        if '优化' in user_input or 'optimize' in user_input.lower():
            tags.append('optimization')
        if '继续' in user_input or 'continue' in user_input.lower():
            tags.append('continuation')
        
        # 从结果提取标签
        action_type = result['primary_action'].action_type.value
        tags.append(action_type)
        
        return tags
    
    def _update_performance_metrics(self, processing_time: float, success: bool):
        """更新性能指标"""
        
        # 更新平均响应时间
        total_requests = self.performance_metrics['total_requests']
        current_avg = self.performance_metrics['average_response_time']
        
        new_avg = (current_avg * (total_requests - 1) + processing_time) / total_requests
        self.performance_metrics['average_response_time'] = new_avg
        
        # 更新决策准确性（简化实现）
        if success:
            self.performance_metrics['decision_accuracy'] = min(0.95, self.performance_metrics['decision_accuracy'] + 0.01)
        else:
            self.performance_metrics['decision_accuracy'] = max(0.5, self.performance_metrics['decision_accuracy'] - 0.02)
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        
        return {
            'project_id': self.project_id,
            'session_info': self.current_session,
            'performance_metrics': self.performance_metrics,
            'components_status': {
                'state_manager': 'active',
                'memory_system': 'active',
                'flow_controller': 'active',
                'decision_gates': 'active'
            },
            'system_health': 'healthy' if self.performance_metrics['decision_accuracy'] > 0.7 else 'degraded'
        }
    
    def reset_session(self):
        """重置会话"""
        
        self.current_session = {
            'session_id': f"session_{int(time.time())}",
            'start_time': datetime.now(),
            'interaction_count': 0,
            'last_action': None,
            'context_cache': {}
        }
        
        print(f"✓ 会话已重置 (新会话ID: {self.current_session['session_id']})") 
   
    def _extract_current_stage(self, project_state: Dict[str, Any]) -> str:
        """从项目状态中提取当前阶段"""
        if not project_state:
            return 'S1'
        
        # 从workflow_state中提取
        workflow_state = project_state.get('workflow_state', {})
        current_stage = workflow_state.get('current_stage', 'S1')
        
        return current_stage
    
    def _extract_task_progress(self, project_state: Dict[str, Any]) -> float:
        """从项目状态中提取任务进度"""
        if not project_state:
            return 0.0
        
        # 从workflow_state中提取
        workflow_state = project_state.get('workflow_state', {})
        task_progress = workflow_state.get('stage_progress', 0.0)
        
        return task_progress
    
    def _normalize_decision_result(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """标准化决策结果格式"""
        
        # 确保有必需的字段
        normalized = {
            'primary_action': None,
            'alternative_actions': [],
            'confidence': 0.5,
            'reasoning_chain': []
        }
        
        # 处理主要行动
        if 'recommended_action' in decision_result:
            # 如果是字符串，转换为NextAction对象
            if isinstance(decision_result['recommended_action'], str):
                normalized['primary_action'] = NextAction(
                    action_type=ActionType.CONTINUE,
                    description=decision_result['recommended_action'],
                    command="aceflow continue",
                    confidence=decision_result.get('confidence', 0.5),
                    estimated_time="5-15分钟"
                )
            else:
                normalized['primary_action'] = decision_result['recommended_action']
        elif 'primary_action' in decision_result:
            normalized['primary_action'] = decision_result['primary_action']
        else:
            # 创建默认行动
            normalized['primary_action'] = NextAction(
                action_type=ActionType.CONTINUE,
                description="继续当前工作流程，注意问题预防",
                command="aceflow continue",
                confidence=0.6,
                estimated_time="10-20分钟"
            )
        
        # 处理替代行动
        if 'alternative_actions' in decision_result:
            normalized['alternative_actions'] = decision_result['alternative_actions']
        else:
            # 创建默认替代行动
            normalized['alternative_actions'] = [
                NextAction(
                    action_type=ActionType.ANALYZE,
                    description="分析当前项目状态",
                    command="aceflow status --detailed",
                    confidence=0.7,
                    estimated_time="5分钟"
                ),
                NextAction(
                    action_type=ActionType.OPTIMIZE,
                    description="优化工作流程",
                    command="aceflow optimize",
                    confidence=0.6,
                    estimated_time="10-15分钟"
                ),
                NextAction(
                    action_type=ActionType.REVIEW,
                    description="回顾项目进展",
                    command="aceflow review",
                    confidence=0.5,
                    estimated_time="15-20分钟"
                )
            ]
        
        # 处理置信度
        normalized['confidence'] = decision_result.get('confidence', 0.5)
        
        # 处理推理链
        if 'reasoning' in decision_result:
            if isinstance(decision_result['reasoning'], str):
                normalized['reasoning_chain'] = [
                    ReasoningStep(
                        step_type="analysis",
                        description=decision_result['reasoning'],
                        confidence=normalized['confidence']
                    )
                ]
            elif isinstance(decision_result['reasoning'], list):
                normalized['reasoning_chain'] = decision_result['reasoning']
        else:
            # 创建默认推理链
            normalized['reasoning_chain'] = [
                ReasoningStep(
                    step_type="context_analysis",
                    description="分析当前项目上下文和状态",
                    confidence=0.7
                ),
                ReasoningStep(
                    step_type="decision_making",
                    description="基于状态和记忆做出决策",
                    confidence=normalized['confidence']
                ),
                ReasoningStep(
                    step_type="action_selection",
                    description="选择最适合的下一步行动",
                    confidence=normalized['confidence']
                )
            ]
        
        return normalized
    
    def _generate_enhanced_pateoas_state(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """生成增强的PATEOAS状态信息"""
        
        base_state = {
            'project_id': self.project_id,
            'session_id': self.current_session['session_id'],
            'current_stage': current_state.get('current_stage'),
            'task_progress': current_state.get('task_progress'),
            'interaction_count': self.current_session['interaction_count']
        }
        
        # 增强状态信息
        enhanced_state = {
            **base_state,
            'project_context': {
                'complexity': current_state.get('project_complexity', 'medium'),
                'team_experience': current_state.get('team_experience', 'medium'),
                'project_type': current_state.get('project_type', 'unknown'),
                'technology_stack': current_state.get('technology_stack', [])
            },
            'workflow_context': {
                'current_mode': current_state.get('workflow_mode', 'smart'),
                'stage_progress_percentage': round(current_state.get('task_progress', 0.0) * 100, 1),
                'estimated_completion': self._estimate_completion_time(current_state),
                'bottlenecks': self._identify_current_bottlenecks(current_state)
            },
            'session_context': {
                'session_duration': self._calculate_session_duration(),
                'interactions_per_hour': self._calculate_interaction_rate(),
                'last_activity': self.current_session.get('last_action')
            },
            'health_indicators': {
                'system_health': 'healthy',
                'performance_score': self._calculate_overall_performance_score(),
                'user_satisfaction_estimate': self.performance_metrics.get('user_satisfaction', 0.8)
            }
        }
        
        return enhanced_state
    
    def _generate_enhanced_memory_context(self, memories: List[MemoryFragment], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """生成增强的记忆上下文"""
        
        base_context = {
            'relevant_memories_count': len(memories),
            'memory_categories': self._analyze_memory_categories(memories),
            'context_richness': current_state.get('memory_context_richness', 0.0)
        }
        
        # 增强记忆上下文
        enhanced_context = {
            **base_context,
            'memory_insights': {
                'most_relevant_category': self._find_most_relevant_category(memories),
                'knowledge_gaps': self._identify_knowledge_gaps_from_memories(memories),
                'learning_patterns': self._analyze_learning_patterns(memories),
                'decision_history': self._extract_decision_history(memories)
            },
            'memory_quality': {
                'average_importance': self._calculate_average_memory_importance(memories),
                'recency_score': self._calculate_memory_recency_score(memories),
                'diversity_score': self._calculate_memory_diversity_score(memories)
            },
            'contextual_relevance': {
                'stage_specific_memories': self._count_stage_specific_memories(memories, current_state),
                'project_specific_memories': self._count_project_specific_memories(memories),
                'actionable_insights': self._extract_actionable_insights(memories)
            }
        }
        
        return enhanced_context
    
    def _generate_enhanced_next_actions(
        self, 
        decision_result: Dict[str, Any], 
        gate_evaluations: Dict[str, Any], 
        current_state: Dict[str, Any], 
        memories: List[MemoryFragment]
    ) -> List[Dict[str, Any]]:
        """生成增强的下一步行动建议"""
        
        # 基础建议
        base_suggestions = self._generate_next_actions_suggestions(
            decision_result, gate_evaluations, current_state
        )
        
        # 增强建议
        enhanced_suggestions = []
        
        # 1. 基于当前阶段的智能建议
        stage_suggestions = self._generate_stage_specific_suggestions(current_state)
        enhanced_suggestions.extend(stage_suggestions)
        
        # 2. 基于历史模式的建议
        pattern_suggestions = self._generate_pattern_based_suggestions(memories, current_state)
        enhanced_suggestions.extend(pattern_suggestions)
        
        # 3. 基于风险评估的建议
        risk_suggestions = self._generate_risk_based_suggestions(current_state, memories)
        enhanced_suggestions.extend(risk_suggestions)
        
        # 4. 基于性能优化的建议
        performance_suggestions = self._generate_performance_suggestions(current_state)
        enhanced_suggestions.extend(performance_suggestions)
        
        # 合并并去重
        all_suggestions = base_suggestions + enhanced_suggestions
        unique_suggestions = self._deduplicate_suggestions(all_suggestions)
        
        # 按优先级和置信度排序
        return sorted(unique_suggestions, key=lambda x: (
            self._get_priority_score(x.get('priority', 'medium')),
            x.get('confidence', 0.5)
        ), reverse=True)[:10]  # 返回前10个最佳建议
    
    def _generate_enhanced_alternative_paths(
        self, 
        decision_result: Dict[str, Any], 
        current_state: Dict[str, Any], 
        memories: List[MemoryFragment]
    ) -> List[Dict[str, Any]]:
        """生成增强的替代路径推荐"""
        
        alternative_paths = []
        
        # 1. 基于项目类型的替代路径
        project_type = current_state.get('project_type', 'unknown')
        if project_type == 'web':
            alternative_paths.extend(self._generate_web_project_alternatives(current_state))
        elif project_type == 'mobile':
            alternative_paths.extend(self._generate_mobile_project_alternatives(current_state))
        elif project_type == 'api':
            alternative_paths.extend(self._generate_api_project_alternatives(current_state))
        
        # 2. 基于团队经验的替代路径
        team_experience = current_state.get('team_experience', 'medium')
        if team_experience == 'junior':
            alternative_paths.extend(self._generate_junior_team_alternatives(current_state))
        elif team_experience == 'senior':
            alternative_paths.extend(self._generate_senior_team_alternatives(current_state))
        
        # 3. 基于项目复杂度的替代路径
        complexity = current_state.get('project_complexity', 'medium')
        if complexity == 'high':
            alternative_paths.extend(self._generate_high_complexity_alternatives(current_state))
        elif complexity == 'low':
            alternative_paths.extend(self._generate_low_complexity_alternatives(current_state))
        
        # 4. 基于历史成功模式的替代路径
        success_patterns = self._extract_success_patterns(memories)
        alternative_paths.extend(self._generate_pattern_based_alternatives(success_patterns, current_state))
        
        return alternative_paths[:8]  # 返回前8个最佳替代路径
    
    def _generate_enhanced_performance_insights(
        self, 
        decision_result: Dict[str, Any], 
        current_state: Dict[str, Any], 
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """生成增强的性能洞察"""
        
        base_insights = {
            'decision_confidence': decision_result['confidence'],
            'processing_efficiency': self._calculate_processing_efficiency(),
            'recommendation_quality': self._assess_recommendation_quality(decision_result)
        }
        
        # 增强性能洞察
        enhanced_insights = {
            **base_insights,
            'productivity_metrics': {
                'tasks_per_session': self._calculate_tasks_per_session(),
                'decision_speed': self._calculate_decision_speed(),
                'context_switch_frequency': self._calculate_context_switches(),
                'learning_velocity': self._calculate_learning_velocity(memories)
            },
            'quality_metrics': {
                'decision_accuracy_trend': self._analyze_decision_accuracy_trend(),
                'error_rate': self._calculate_error_rate(),
                'user_satisfaction_trend': self._analyze_satisfaction_trend(),
                'system_reliability': self._calculate_system_reliability()
            },
            'efficiency_insights': {
                'bottleneck_analysis': self._analyze_current_bottlenecks(current_state),
                'optimization_opportunities': self._identify_optimization_opportunities(current_state),
                'resource_utilization': self._analyze_resource_utilization(),
                'workflow_efficiency': self._calculate_workflow_efficiency(current_state)
            },
            'predictive_insights': {
                'completion_probability': self._predict_completion_probability(current_state),
                'risk_forecast': self._forecast_project_risks(current_state, memories),
                'performance_trajectory': self._predict_performance_trajectory(),
                'recommended_adjustments': self._suggest_performance_adjustments(current_state)
            }
        }
        
        return enhanced_insights
    
    def _generate_pateoas_links(self, current_state: Dict[str, Any], decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成PATEOAS链接和导航"""
        
        current_stage = current_state.get('current_stage', 'S1')
        
        links = {
            'self': {
                'href': f'/api/projects/{self.project_id}/state',
                'method': 'GET',
                'description': '获取当前项目状态'
            },
            'actions': {
                'primary': {
                    'href': f'/api/projects/{self.project_id}/actions/primary',
                    'method': 'POST',
                    'description': f'执行主要建议: {decision_result["primary_action"].description}',
                    'command': decision_result["primary_action"].command
                },
                'alternatives': [
                    {
                        'href': f'/api/projects/{self.project_id}/actions/alternative/{i}',
                        'method': 'POST',
                        'description': action.description,
                        'command': action.command
                    } for i, action in enumerate(decision_result.get('alternative_actions', []))
                ]
            },
            'navigation': {
                'previous_stage': {
                    'href': f'/api/projects/{self.project_id}/stages/previous',
                    'method': 'POST',
                    'description': '回到上一个阶段',
                    'available': current_stage != 'S1'
                },
                'next_stage': {
                    'href': f'/api/projects/{self.project_id}/stages/next',
                    'method': 'POST',
                    'description': '进入下一个阶段',
                    'available': self._can_advance_stage(current_state)
                },
                'stage_jump': {
                    'href': f'/api/projects/{self.project_id}/stages/jump',
                    'method': 'POST',
                    'description': '跳转到指定阶段',
                    'available_stages': self._get_available_stages(current_state)
                }
            },
            'resources': {
                'memory': {
                    'href': f'/api/projects/{self.project_id}/memory',
                    'method': 'GET',
                    'description': '访问项目记忆'
                },
                'history': {
                    'href': f'/api/projects/{self.project_id}/history',
                    'method': 'GET',
                    'description': '查看项目历史'
                },
                'analytics': {
                    'href': f'/api/projects/{self.project_id}/analytics',
                    'method': 'GET',
                    'description': '查看项目分析'
                }
            },
            'related': {
                'similar_projects': {
                    'href': f'/api/projects/similar/{self.project_id}',
                    'method': 'GET',
                    'description': '查找相似项目'
                },
                'templates': {
                    'href': f'/api/templates/{current_state.get("project_type", "general")}',
                    'method': 'GET',
                    'description': '获取项目模板'
                }
            }
        }
        
        return links
    
    def _generate_user_experience_enhancements(
        self, 
        current_state: Dict[str, Any], 
        decision_result: Dict[str, Any], 
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """生成用户体验增强信息"""
        
        return {
            'personalization': {
                'preferred_workflow_mode': self._detect_preferred_workflow_mode(),
                'interaction_style': self._analyze_interaction_style(),
                'learning_preferences': self._detect_learning_preferences(memories),
                'communication_style': self._analyze_communication_preferences()
            },
            'guidance': {
                'next_steps_explanation': self._generate_next_steps_explanation(decision_result),
                'context_help': self._generate_context_help(current_state),
                'tips_and_tricks': self._generate_contextual_tips(current_state),
                'best_practices': self._suggest_best_practices(current_state)
            },
            'feedback': {
                'confidence_explanation': self._explain_confidence_level(decision_result['confidence']),
                'uncertainty_areas': self._identify_uncertainty_areas(decision_result),
                'improvement_suggestions': self._suggest_improvements(current_state),
                'learning_opportunities': self._highlight_learning_opportunities(memories)
            },
            'visualization': {
                'progress_indicators': self._generate_progress_indicators(current_state),
                'workflow_visualization': self._generate_workflow_visualization(current_state),
                'decision_tree': self._generate_decision_tree(decision_result),
                'timeline': self._generate_project_timeline(current_state)
            },
            'accessibility': {
                'summary': self._generate_accessible_summary(decision_result),
                'key_points': self._extract_key_points(decision_result),
                'action_priorities': self._rank_action_priorities(decision_result),
                'quick_actions': self._identify_quick_actions(decision_result)
            }
        }
    
    def _generate_enhanced_contextual_insights(
        self, 
        current_state: Dict[str, Any], 
        memories: List[MemoryFragment], 
        decision_result: Dict[str, Any], 
        gate_evaluations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成增强的上下文洞察"""
        
        base_insights = self._generate_contextual_insights(current_state, memories, decision_result)
        
        # 增强洞察
        enhanced_insights = {
            **base_insights,
            'strategic_insights': {
                'project_trajectory': self._analyze_project_trajectory(current_state, memories),
                'success_probability': self._calculate_success_probability(current_state, memories),
                'critical_success_factors': self._identify_critical_success_factors(current_state),
                'competitive_advantages': self._identify_competitive_advantages(current_state)
            },
            'tactical_insights': {
                'immediate_priorities': self._identify_immediate_priorities(decision_result, gate_evaluations),
                'resource_optimization': self._suggest_resource_optimization(current_state),
                'workflow_improvements': self._suggest_workflow_improvements(current_state, memories),
                'quality_enhancements': self._suggest_quality_enhancements(gate_evaluations)
            },
            'predictive_insights': {
                'trend_analysis': self._analyze_project_trends(memories),
                'pattern_recognition': self._recognize_success_patterns(memories),
                'anomaly_detection': self._detect_anomalies(current_state, memories),
                'future_recommendations': self._generate_future_recommendations(current_state, memories)
            },
            'collaborative_insights': {
                'team_dynamics': self._analyze_enhanced_team_dynamics(memories),
                'communication_patterns': self._analyze_communication_patterns(memories),
                'knowledge_sharing': self._analyze_knowledge_sharing_patterns(memories),
                'collaboration_opportunities': self._identify_collaboration_opportunities(current_state)
            }
        }
        
        return enhanced_insights   
 
    # === 辅助方法实现 ===
    
    def _estimate_completion_time(self, current_state: Dict[str, Any]) -> str:
        """估算完成时间"""
        progress = current_state.get('task_progress', 0.0)
        if progress < 0.1:
            return "2-4小时"
        elif progress < 0.5:
            return "1-2小时"
        elif progress < 0.8:
            return "30-60分钟"
        else:
            return "10-30分钟"
    
    def _identify_current_bottlenecks(self, current_state: Dict[str, Any]) -> List[str]:
        """识别当前瓶颈"""
        bottlenecks = []
        
        if current_state.get('recent_issues_count', 0) > 3:
            bottlenecks.append("问题解决速度")
        
        if current_state.get('task_progress', 0.0) < 0.3:
            bottlenecks.append("进度推进缓慢")
        
        if current_state.get('recent_decisions_count', 0) < 2:
            bottlenecks.append("决策制定不足")
        
        return bottlenecks
    
    def _calculate_session_duration(self) -> str:
        """计算会话持续时间"""
        start_time = self.current_session.get('start_time', datetime.now())
        duration = datetime.now() - start_time
        minutes = int(duration.total_seconds() / 60)
        
        if minutes < 60:
            return f"{minutes}分钟"
        else:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            return f"{hours}小时{remaining_minutes}分钟"
    
    def _calculate_interaction_rate(self) -> float:
        """计算交互频率"""
        start_time = self.current_session.get('start_time', datetime.now())
        duration_hours = (datetime.now() - start_time).total_seconds() / 3600
        
        if duration_hours > 0:
            return round(self.current_session['interaction_count'] / duration_hours, 2)
        return 0.0
    
    def _calculate_overall_performance_score(self) -> float:
        """计算整体性能评分"""
        metrics = self.performance_metrics
        
        # 综合多个指标
        efficiency = metrics.get('efficiency', 0.8)
        quality = metrics.get('quality', 0.8)
        speed = metrics.get('speed', 0.8)
        decision_accuracy = metrics.get('decision_accuracy', 0.8)
        
        return round((efficiency + quality + speed + decision_accuracy) / 4, 2)
    
    def _find_most_relevant_category(self, memories: List[MemoryFragment]) -> str:
        """找到最相关的记忆类别"""
        if not memories:
            return "无"
        
        category_counts = {}
        for memory in memories:
            category = memory.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else "无"
    
    def _identify_knowledge_gaps_from_memories(self, memories: List[MemoryFragment]) -> List[str]:
        """从记忆中识别知识缺口"""
        gaps = []
        
        # 分析记忆类别分布
        categories = [m.category.value for m in memories]
        
        if 'requirement' not in categories:
            gaps.append("需求分析")
        if 'decision' not in categories:
            gaps.append("决策记录")
        if 'pattern' not in categories:
            gaps.append("模式识别")
        if 'learning' not in categories:
            gaps.append("学习总结")
        
        return gaps
    
    def _analyze_learning_patterns(self, memories: List[MemoryFragment]) -> Dict[str, Any]:
        """分析学习模式"""
        learning_memories = [m for m in memories if m.category.value == 'learning']
        
        return {
            'learning_frequency': len(learning_memories),
            'avg_importance': sum(m.importance for m in learning_memories) / len(learning_memories) if learning_memories else 0,
            'recent_learning': len([m for m in learning_memories if (datetime.now() - m.created_at).days < 7])
        }
    
    def _extract_decision_history(self, memories: List[MemoryFragment]) -> List[Dict[str, Any]]:
        """提取决策历史"""
        decision_memories = [m for m in memories if m.category.value == 'decision']
        
        return [
            {
                'content': m.content[:100] + "..." if len(m.content) > 100 else m.content,
                'importance': m.importance,
                'created_at': m.created_at.isoformat(),
                'tags': m.tags[:3]  # 只显示前3个标签
            } for m in decision_memories[-5:]  # 最近5个决策
        ]
    
    def _calculate_average_memory_importance(self, memories: List[MemoryFragment]) -> float:
        """计算记忆平均重要性"""
        if not memories:
            return 0.0
        return round(sum(m.importance for m in memories) / len(memories), 2)
    
    def _calculate_memory_recency_score(self, memories: List[MemoryFragment]) -> float:
        """计算记忆新近度评分"""
        if not memories:
            return 0.0
        
        now = datetime.now()
        recency_scores = []
        
        for memory in memories:
            days_old = (now - memory.last_accessed).days
            # 越新的记忆评分越高
            score = max(0, 1 - days_old / 30)  # 30天内的记忆有较高评分
            recency_scores.append(score)
        
        return round(sum(recency_scores) / len(recency_scores), 2)
    
    def _calculate_memory_diversity_score(self, memories: List[MemoryFragment]) -> float:
        """计算记忆多样性评分"""
        if not memories:
            return 0.0
        
        categories = set(m.category.value for m in memories)
        max_categories = len(MemoryCategory)
        
        return round(len(categories) / max_categories, 2)
    
    def _count_stage_specific_memories(self, memories: List[MemoryFragment], current_state: Dict[str, Any]) -> int:
        """统计阶段特定记忆"""
        current_stage = current_state.get('current_stage', 'S1')
        return len([m for m in memories if current_stage in m.content or current_stage in str(m.tags)])
    
    def _count_project_specific_memories(self, memories: List[MemoryFragment]) -> int:
        """统计项目特定记忆"""
        return len([m for m in memories if m.project_id == self.project_id])
    
    def _extract_actionable_insights(self, memories: List[MemoryFragment]) -> List[str]:
        """提取可行动的洞察"""
        insights = []
        
        # 从高重要性记忆中提取洞察
        high_importance_memories = [m for m in memories if m.importance > 0.7]
        
        for memory in high_importance_memories[:3]:  # 前3个最重要的记忆
            if any(keyword in memory.content.lower() for keyword in ['建议', '应该', '需要', '优化']):
                insight = memory.content[:80] + "..." if len(memory.content) > 80 else memory.content
                insights.append(insight)
        
        return insights
    
    def _generate_stage_specific_suggestions(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成阶段特定建议"""
        current_stage = current_state.get('current_stage', 'S1')
        suggestions = []
        
        if current_stage == 'S1':
            suggestions.append({
                'type': 'stage_specific',
                'description': '完善需求分析，确保需求清晰完整',
                'priority': 'high',
                'confidence': 0.9,
                'estimated_time': '30-60分钟'
            })
        elif current_stage == 'S2':
            suggestions.append({
                'type': 'stage_specific',
                'description': '进行技术方案设计，选择合适的架构',
                'priority': 'high',
                'confidence': 0.85,
                'estimated_time': '1-2小时'
            })
        elif current_stage in ['S3', 'S4']:
            suggestions.append({
                'type': 'stage_specific',
                'description': '开始核心功能实现，遵循最佳实践',
                'priority': 'high',
                'confidence': 0.8,
                'estimated_time': '2-4小时'
            })
        
        return suggestions
    
    def _generate_pattern_based_suggestions(self, memories: List[MemoryFragment], current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于模式生成建议"""
        suggestions = []
        
        # 分析成功模式
        pattern_memories = [m for m in memories if m.category.value == 'pattern']
        
        if pattern_memories:
            suggestions.append({
                'type': 'pattern_based',
                'description': '应用已识别的成功模式到当前任务',
                'priority': 'medium',
                'confidence': 0.75,
                'estimated_time': '15-30分钟'
            })
        
        return suggestions
    
    def _generate_risk_based_suggestions(self, current_state: Dict[str, Any], memories: List[MemoryFragment]) -> List[Dict[str, Any]]:
        """基于风险生成建议"""
        suggestions = []
        
        # 检查风险指标
        issues_count = current_state.get('recent_issues_count', 0)
        
        if issues_count > 2:
            suggestions.append({
                'type': 'risk_mitigation',
                'description': '进行风险评估和问题预防措施',
                'priority': 'high',
                'confidence': 0.8,
                'estimated_time': '20-40分钟'
            })
        
        return suggestions
    
    def _generate_performance_suggestions(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成性能建议"""
        suggestions = []
        
        progress = current_state.get('task_progress', 0.0)
        
        if progress < 0.3:
            suggestions.append({
                'type': 'performance',
                'description': '加速项目进度，考虑并行执行任务',
                'priority': 'medium',
                'confidence': 0.7,
                'estimated_time': '规划10分钟，执行时间视任务而定'
            })
        
        return suggestions
    
    def _deduplicate_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重建议"""
        seen_descriptions = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            description = suggestion.get('description', '')
            if description not in seen_descriptions:
                unique_suggestions.append(suggestion)
                seen_descriptions.add(description)
        
        return unique_suggestions
    
    def _get_priority_score(self, priority: str) -> int:
        """获取优先级评分"""
        priority_scores = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priority_scores.get(priority, 2)
    
    def _generate_web_project_alternatives(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成Web项目替代路径"""
        return [
            {
                'path_type': 'frontend_first',
                'description': '前端优先开发路径',
                'rationale': '快速构建用户界面原型，获得早期反馈',
                'estimated_time_saving': '20%',
                'risk_level': 'low'
            },
            {
                'path_type': 'api_first',
                'description': 'API优先开发路径',
                'rationale': '先构建稳定的后端API，确保数据架构正确',
                'estimated_time_saving': '15%',
                'risk_level': 'low'
            }
        ]
    
    def _generate_mobile_project_alternatives(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成移动项目替代路径"""
        return [
            {
                'path_type': 'cross_platform',
                'description': '跨平台开发路径',
                'rationale': '使用React Native或Flutter减少开发工作量',
                'estimated_time_saving': '40%',
                'risk_level': 'medium'
            }
        ]
    
    def _generate_api_project_alternatives(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成API项目替代路径"""
        return [
            {
                'path_type': 'microservices',
                'description': '微服务架构路径',
                'rationale': '将API拆分为独立的微服务，提高可维护性',
                'estimated_time_saving': '0%',
                'risk_level': 'medium'
            }
        ]
    
    def _generate_junior_team_alternatives(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成初级团队替代路径"""
        return [
            {
                'path_type': 'guided_development',
                'description': '指导式开发路径',
                'rationale': '增加代码审查和结对编程，提高代码质量',
                'estimated_time_saving': '-10%',
                'risk_level': 'low'
            }
        ]
    
    def _generate_senior_team_alternatives(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成高级团队替代路径"""
        return [
            {
                'path_type': 'autonomous_development',
                'description': '自主开发路径',
                'rationale': '减少监督，让经验丰富的团队自主决策',
                'estimated_time_saving': '25%',
                'risk_level': 'low'
            }
        ]
    
    def _generate_high_complexity_alternatives(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成高复杂度项目替代路径"""
        return [
            {
                'path_type': 'phased_approach',
                'description': '分阶段开发路径',
                'rationale': '将复杂项目分解为多个阶段，降低风险',
                'estimated_time_saving': '0%',
                'risk_level': 'low'
            }
        ]
    
    def _generate_low_complexity_alternatives(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成低复杂度项目替代路径"""
        return [
            {
                'path_type': 'rapid_prototype',
                'description': '快速原型路径',
                'rationale': '对于简单项目，可以快速构建原型验证想法',
                'estimated_time_saving': '50%',
                'risk_level': 'medium'
            }
        ]
    
    def _extract_success_patterns(self, memories: List[MemoryFragment]) -> List[str]:
        """提取成功模式"""
        patterns = []
        
        # 从高重要性的模式记忆中提取
        pattern_memories = [m for m in memories if m.category.value == 'pattern' and m.importance > 0.7]
        
        for memory in pattern_memories:
            patterns.append(memory.content[:100])
        
        return patterns
    
    def _generate_pattern_based_alternatives(self, success_patterns: List[str], current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于成功模式生成替代路径"""
        alternatives = []
        
        if success_patterns:
            alternatives.append({
                'path_type': 'proven_pattern',
                'description': '应用已验证的成功模式',
                'rationale': '基于历史成功经验，降低项目风险',
                'estimated_time_saving': '15%',
                'risk_level': 'low'
            })
        
        return alternatives    

    # === 用户体验增强辅助方法 ===
    
    def _detect_preferred_workflow_mode(self) -> str:
        """检测偏好的工作流模式"""
        # 基于历史交互模式分析
        interaction_count = self.current_session['interaction_count']
        
        if interaction_count > 10:
            return 'detailed'  # 喜欢详细交互
        elif interaction_count < 3:
            return 'minimal'  # 喜欢简洁交互
        else:
            return 'standard'  # 标准交互偏好
    
    def _calculate_tasks_per_session(self) -> float:
        """计算每会话任务数"""
        interaction_count = self.current_session.get('interaction_count', 1)
        return max(1.0, interaction_count / 5.0)  # 假设每5次交互完成1个任务
    
    def _calculate_session_duration(self) -> str:
        """计算会话持续时间"""
        start_time = self.current_session.get('start_time', datetime.now())
        duration = datetime.now() - start_time
        minutes = int(duration.total_seconds() / 60)
        return f"{minutes}分钟"
    
    def _calculate_interaction_rate(self) -> float:
        """计算交互频率"""
        start_time = self.current_session.get('start_time', datetime.now())
        duration_hours = max(0.1, (datetime.now() - start_time).total_seconds() / 3600)
        interaction_count = self.current_session.get('interaction_count', 1)
        return round(interaction_count / duration_hours, 2)
    
    def _calculate_overall_performance_score(self) -> float:
        """计算整体性能分数"""
        metrics = self.performance_metrics
        return (metrics['decision_accuracy'] * 0.4 + 
                metrics['user_satisfaction'] * 0.3 + 
                metrics['memory_efficiency'] * 0.3)
    
    def _estimate_completion_time(self, current_state: Dict[str, Any]) -> str:
        """估算完成时间"""
        progress = current_state.get('task_progress', 0.0)
        if progress > 0.8:
            return "即将完成"
        elif progress > 0.5:
            return "1-2小时"
        elif progress > 0.2:
            return "2-4小时"
        else:
            return "4小时以上"
    
    def _identify_current_bottlenecks(self, current_state: Dict[str, Any]) -> List[str]:
        """识别当前瓶颈"""
        bottlenecks = []
        progress = current_state.get('task_progress', 0.0)
        issues_count = current_state.get('recent_issues_count', 0)
        
        if progress < 0.3:
            bottlenecks.append("进度缓慢")
        if issues_count > 3:
            bottlenecks.append("问题较多")
        if not bottlenecks:
            bottlenecks.append("无明显瓶颈")
        
        return bottlenecks 
   
    def _calculate_decision_speed(self) -> float:
        """计算决策速度"""
        return self.performance_metrics.get('average_response_time', 1.0)
    
    def _calculate_memory_utilization(self) -> float:
        """计算记忆利用率"""
        return self.performance_metrics.get('memory_efficiency', 0.8)
    
    def _analyze_memory_categories(self, memories) -> Dict[str, int]:
        """分析记忆分类"""
        categories = {}
        for memory in memories:
            category = memory.category.value
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _calculate_memory_relevance(self, memory) -> float:
        """计算记忆相关性"""
        return memory.importance * 0.8 + (memory.access_count / 10.0) * 0.2
    
    def _generate_enhanced_next_actions(self, decision_result, gate_evaluations, current_state, memories):
        """生成增强的下一步行动"""
        actions = []
        
        # 基于决策结果
        if decision_result.get('primary_action'):
            actions.append({
                'type': 'primary',
                'description': decision_result['primary_action'].description,
                'confidence': decision_result['confidence'],
                'estimated_time': decision_result['primary_action'].estimated_time
            })
        
        # 基于决策门结果
        for gate_id, evaluation in gate_evaluations.items():
            if evaluation['result'] == 'fail':
                actions.append({
                    'type': 'improvement',
                    'description': f'改进{gate_id}评估结果',
                    'confidence': 0.8,
                    'estimated_time': '15-30分钟'
                })
        
        return actions
    
    def _generate_enhanced_alternative_paths(self, decision_result, current_state, memories):
        """生成增强的替代路径"""
        paths = []
        
        # 基于当前状态生成替代路径
        current_stage = current_state.get('current_stage', 'S1')
        
        if current_stage in ['S1', 'S2']:
            paths.append({
                'path_type': 'fast_track',
                'description': '快速原型开发路径',
                'time_saving': '40%',
                'risk_level': 'medium'
            })
        
        paths.append({
            'path_type': 'standard',
            'description': '标准开发流程',
            'time_saving': '0%',
            'risk_level': 'low'
        })
        
        return paths
    
    def _generate_pateoas_links(self, current_state, decision_result):
        """生成PATEOAS链接"""
        links = {
            'self': f'/api/projects/{self.project_id}/state',
            'next': f'/api/projects/{self.project_id}/actions',
            'history': f'/api/projects/{self.project_id}/history'
        }
        
        # 基于当前状态添加相关链接
        current_stage = current_state.get('current_stage', 'S1')
        links[f'stage_{current_stage}'] = f'/api/projects/{self.project_id}/stages/{current_stage}'
        
        return links
    
    def _generate_user_experience_enhancements(self, current_state, decision_result, memories):
        """生成用户体验增强"""
        return {
            'interaction_style': self._infer_user_interaction_style(),
            'preferred_detail_level': self._infer_user_detail_preference(),
            'suggested_ui_mode': 'guided' if current_state.get('task_progress', 0) < 0.3 else 'expert',
            'help_suggestions': self._generate_contextual_help(current_state)
        }
    
    def _infer_user_interaction_style(self) -> str:
        """推断用户交互风格"""
        interaction_count = self.current_session.get('interaction_count', 1)
        if interaction_count > 10:
            return 'detailed'
        elif interaction_count < 3:
            return 'minimal'
        else:
            return 'standard'
    
    def _infer_user_detail_preference(self) -> str:
        """推断用户详细程度偏好"""
        return 'medium'  # 简化实现
    
    def _generate_contextual_help(self, current_state) -> List[str]:
        """生成上下文帮助"""
        help_items = []
        progress = current_state.get('task_progress', 0.0)
        
        if progress < 0.2:
            help_items.append('建议先完善项目需求分析')
        elif progress < 0.5:
            help_items.append('可以开始技术方案设计')
        else:
            help_items.append('准备进入实现阶段')
            
        return help_items
    
    def _generate_enhanced_contextual_insights(self, current_state, memories, decision_result, gate_evaluations):
        """生成增强的上下文洞察"""
        return {
            'project_health_score': 0.8,
            'team_efficiency_trend': 'stable',
            'risk_level': 'low',
            'optimization_opportunities': ['并行开发', '自动化测试'],
            'success_probability': 0.85
        }
    
    def _calculate_tasks_per_session(self) -> float:
        """计算每会话任务数"""
        return self.current_session['interaction_count'] / max(1, self._calculate_session_duration())
    
    def _calculate_session_duration(self) -> float:
        """计算会话持续时间（小时）"""
        start_time = self.current_session.get('start_time', datetime.now())
        duration = (datetime.now() - start_time).total_seconds() / 3600
        return max(0.1, duration)
    
    def _calculate_interaction_rate(self) -> float:
        """计算交互频率"""
        return self._calculate_tasks_per_session()
    
    def _calculate_overall_performance_score(self) -> float:
        """计算整体性能分数"""
        return (self.performance_metrics['decision_accuracy'] + 
                self.performance_metrics['user_satisfaction'] + 
                self.performance_metrics['memory_efficiency']) / 3.0
    
    def _estimate_completion_time(self, current_state: Dict[str, Any]) -> str:
        """估算完成时间"""
        progress = current_state.get('task_progress', 0.0)
        if progress > 0.8:
            return "1-2小时"
        elif progress > 0.5:
            return "2-4小时"
        elif progress > 0.2:
            return "4-8小时"
        else:
            return "8+小时"
    
    def _identify_current_bottlenecks(self, current_state: Dict[str, Any]) -> List[str]:
        """识别当前瓶颈"""
        bottlenecks = []
        if current_state.get('recent_issues_count', 0) > 3:
            bottlenecks.append("问题频发")
        if current_state.get('task_progress', 0.0) < 0.3:
            bottlenecks.append("进度缓慢")
        return bottlenecks
    
    def _analyze_memory_categories(self, memories: List[MemoryFragment]) -> Dict[str, int]:
        """分析记忆类别分布"""
        categories = {}
        for memory in memories:
            category = memory.category.value
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _calculate_memory_relevance(self, memory: MemoryFragment) -> float:
        """计算记忆相关性"""
        return memory.importance * (1.0 + memory.access_count * 0.1)
    
    def _generate_enhanced_meta_cognition(self) -> Dict[str, Any]:
        """生成增强的元认知信息"""
        return {
            'confidence_level': self.performance_metrics['decision_accuracy'],
            'system_health': 'healthy',
            'learning_progress': 'active'
        }
    
    def _assess_state_health(self) -> Dict[str, Any]:
        """评估状态健康度"""
        return {
            'overall_health': 0.8,
            'status': 'healthy'
        }
    
    def _extract_tags_from_interaction(self, user_input: str, result: Dict[str, Any]) -> List[str]:
        """从交互中提取标签"""
        tags = ['interaction']
        if '问题' in user_input:
            tags.append('problem')
        if '优化' in user_input:
            tags.append('optimization')
        return tags
    
    def _generate_risk_mitigation_suggestions(self, risks: List[str]) -> List[str]:
        """生成风险缓解建议"""
        suggestions = []
        
        for risk in risks:
            if '进度落后' in risk:
                suggestions.append('增加资源投入或调整项目范围')
            elif '质量问题' in risk:
                suggestions.append('加强代码审查和测试覆盖')
            elif '技术准备不足' in risk:
                suggestions.append('安排技术培训或引入技术专家')
            elif '团队经验' in risk:
                suggestions.append('提供指导支持或简化项目复杂度')
        
        return suggestions
    
    def _identify_learning_opportunities(self, memories: List[MemoryFragment]) -> List[Dict[str, Any]]:
        """识别学习机会"""
        opportunities = []
        
        # 分析记忆中的技术栈和模式
        tech_mentions = {}
        for memory in memories:
            content = memory.content.lower()
            # 简单的技术栈识别
            techs = ['python', 'javascript', 'react', 'django', 'flask', 'docker', 'kubernetes']
            for tech in techs:
                if tech in content:
                    tech_mentions[tech] = tech_mentions.get(tech, 0) + 1
        
        # 基于技术提及频率推荐学习机会
        for tech, count in tech_mentions.items():
            if count >= 2:  # 多次提及的技术
                opportunities.append({
                    'type': 'technology_deepening',
                    'topic': tech,
                    'relevance': min(1.0, count / 5.0),
                    'description': f'深入学习{tech}技术'
                })
        
        return opportunities
    
    def _analyze_efficiency_patterns(self, current_state: Dict[str, Any], memories: List[MemoryFragment]) -> Dict[str, Any]:
        """分析效率模式"""
        
        # 基于交互历史分析效率模式
        interaction_count = self.current_session['interaction_count']
        session_duration = (datetime.now() - self.current_session['start_time']).total_seconds() / 3600  # 小时
        
        interactions_per_hour = interaction_count / max(0.1, session_duration)
        
        # 决策效率
        decision_memories = [m for m in memories if m.category.value == 'decision']
        decision_quality = sum(m.importance for m in decision_memories) / max(1, len(decision_memories))
        
        return {
            'interaction_frequency': interactions_per_hour,
            'decision_quality_avg': decision_quality,
            'session_productivity': min(1.0, interactions_per_hour / 10.0),  # 假设10次/小时为高效
            'efficiency_trend': 'improving' if interactions_per_hour > 5 else 'stable'
        }
    
    def _calculate_user_satisfaction(self, result: Dict[str, Any]) -> float:
        """计算用户满意度"""
        
        # 基于结果质量估算用户满意度
        confidence = result.get('confidence', 0.5)
        alternatives_count = len(result.get('alternative_actions', []))
        reasoning_quality = len(result.get('reasoning_chain', [])) / 5.0  # 标准化到0-1
        
        # 综合满意度评分
        satisfaction = (
            confidence * 0.4 +
            min(1.0, alternatives_count / 3.0) * 0.3 +
            min(1.0, reasoning_quality) * 0.3
        )
        
        return min(1.0, max(0.1, satisfaction))
    
    def _calculate_memory_efficiency(self, memories: List[MemoryFragment], user_input: str) -> float:
        """计算记忆效率"""
        
        if not memories:
            return 0.5
        
        # 基于记忆相关性和数量计算效率
        total_memories = len(memories)
        high_importance_memories = len([m for m in memories if m.importance > 0.7])
        
        # 相关性评分（简化版）
        relevance_score = high_importance_memories / max(1, total_memories)
        
        # 数量效率（太多或太少都不好）
        quantity_efficiency = 1.0 - abs(total_memories - 5) / 10.0  # 5个记忆为理想
        quantity_efficiency = max(0.1, min(1.0, quantity_efficiency))
        
        # 综合效率
        efficiency = relevance_score * 0.6 + quantity_efficiency * 0.4
        
        return min(1.0, max(0.1, efficiency))
    
    def _extract_current_stage(self, project_state: PATEOASState) -> str:
        """从项目状态提取当前阶段"""
        if hasattr(project_state, 'workflow_state') and project_state.workflow_state:
            return project_state.workflow_state.get('current_stage', 'S1')
        return 'S1'
    
    def _extract_task_progress(self, project_state: PATEOASState) -> float:
        """从项目状态提取任务进度"""
        if hasattr(project_state, 'task_progress'):
            return project_state.task_progress
        if hasattr(project_state, 'workflow_state') and project_state.workflow_state:
            return project_state.workflow_state.get('stage_progress', 0.0)
        return 0.0
    
    def _extract_tags_from_interaction(self, user_input: str, result: Dict[str, Any]) -> List[str]:
        """从交互中提取标签"""
        tags = ['interaction', 'user_input']
        
        # 基于用户输入提取标签
        input_lower = user_input.lower()
        if any(word in input_lower for word in ['问题', 'error', 'bug', '错误']):
            tags.append('issue')
        if any(word in input_lower for word in ['学习', 'learn', '教程', 'tutorial']):
            tags.append('learning')
        if any(word in input_lower for word in ['决策', 'decision', '选择', 'choose']):
            tags.append('decision')
        
        # 基于结果类型提取标签
        primary_action = result.get('primary_action')
        if primary_action and hasattr(primary_action, 'action_type'):
            tags.append(primary_action.action_type.value)
        
        return tags
    
    def _normalize_decision_result(self, decision_result: Any) -> Dict[str, Any]:
        """标准化决策结果格式"""
        
        if isinstance(decision_result, dict):
            return decision_result
        
        # 如果是其他格式，尝试转换
        try:
            if hasattr(decision_result, '__dict__'):
                result_dict = decision_result.__dict__
            else:
                result_dict = {
                    'primary_action': decision_result,
                    'alternative_actions': [],
                    'confidence': 0.7,
                    'reasoning_chain': []
                }
            
            # 确保必需字段存在
            required_fields = ['primary_action', 'alternative_actions', 'confidence', 'reasoning_chain']
            for field in required_fields:
                if field not in result_dict:
                    if field == 'alternative_actions':
                        result_dict[field] = []
                    elif field == 'confidence':
                        result_dict[field] = 0.7
                    elif field == 'reasoning_chain':
                        result_dict[field] = []
                    else:
                        result_dict[field] = None
            
            return result_dict
            
        except Exception as e:
            # 如果转换失败，返回默认结果
            return {
                'primary_action': NextAction(
                    action_type=ActionType.ANALYZE,
                    description="处理用户请求",
                    estimated_time="5分钟",
                    confidence=0.7
                ),
                'alternative_actions': [],
                'confidence': 0.7,
                'reasoning_chain': [
                    {
                        'step_id': 'fallback',
                        'description': '使用默认处理逻辑',
                        'confidence': 0.7
                    }
                ]
            }
    
    def _update_performance_metrics(self, processing_time: float, success: bool):
        """更新性能指标"""
        
        # 更新平均响应时间
        total_requests = self.performance_metrics['total_requests']
        current_avg = self.performance_metrics['average_response_time']
        
        if total_requests > 0:
            self.performance_metrics['average_response_time'] = (
                (current_avg * (total_requests - 1) + processing_time) / total_requests
            )
        else:
            self.performance_metrics['average_response_time'] = processing_time
        
        # 更新成功/失败计数
        if success:
            self.performance_metrics['successful_requests'] += 1
        else:
            self.performance_metrics['failed_requests'] += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要 - 委托给性能监控器"""
        return self.performance_monitor.get_performance_summary()
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告 - 委托给性能监控器"""
        return self.performance_monitor.generate_performance_report()
    
    def reset_session(self):
        """重置会话状态"""
        self.current_session = {
            'session_id': f"session_{int(time.time())}",
            'start_time': datetime.now(),
            'interaction_count': 0,
            'last_action': None,
            'context_cache': {}
        }
        
        # 重置性能指标
        self.performance_metrics.update({
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0
        })
        
        print(f"✓ 会话已重置 (新会话ID: {self.current_session['session_id']})")
    
    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        session_duration = (datetime.now() - self.current_session['start_time']).total_seconds()
        
        return {
            'session_id': self.current_session['session_id'],
            'start_time': self.current_session['start_time'].isoformat(),
            'duration_seconds': session_duration,
            'interaction_count': self.current_session['interaction_count'],
            'last_action': self.current_session['last_action'].__dict__ if self.current_session['last_action'] else None,
            'performance_summary': self.get_performance_summary()
        }
    
    def analyze_and_recommend(self, task_description: str, project_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        智能任务分析和模式推荐
        
        Args:
            task_description: 任务描述
            project_context: 项目上下文信息
            
        Returns:
            包含分析结果和推荐的字典
        """
        try:
            start_time = time.time()
            
            # 默认项目上下文
            if project_context is None:
                project_context = {}
            
            # 获取当前状态和记忆
            current_state = self.state_manager.get_current_state()
            relevant_memories = self.memory_system.recall_relevant_context(
                task_description, current_state
            )
            
            # 1. 任务复杂度分析
            task_complexity = self._analyze_task_complexity(task_description, relevant_memories)
            
            # 2. 团队和项目因素分析
            team_factors = self._analyze_team_factors(project_context)
            
            # 3. 历史模式分析
            historical_patterns = self._analyze_historical_patterns(relevant_memories)
            
            # 4. 综合模式推荐
            mode_recommendation = self._generate_mode_recommendation(
                task_complexity, team_factors, historical_patterns, project_context
            )
            
            # 5. 优化建议生成
            optimization_suggestions = self._generate_optimization_suggestions(
                task_description, mode_recommendation, current_state, relevant_memories
            )
            
            # 6. 风险评估
            risk_assessment = self._assess_project_risks(
                task_description, mode_recommendation, project_context
            )
            
            # 构建分析结果
            analysis_result = {
                'task_analysis': {
                    'description': task_description,
                    'complexity_factors': task_complexity,
                    'estimated_effort': self._estimate_effort(task_complexity, team_factors),
                    'key_challenges': self._identify_key_challenges(task_description, relevant_memories)
                },
                'mode_recommendation': mode_recommendation,
                'optimization_suggestions': optimization_suggestions,
                'risk_assessment': risk_assessment,
                'contextual_insights': {
                    'similar_projects': self._find_similar_projects(relevant_memories),
                    'team_readiness': team_factors,
                    'resource_requirements': self._estimate_resource_requirements(task_complexity, team_factors)
                },
                'analysis_metadata': {
                    'analysis_time': datetime.now().isoformat(),
                    'processing_duration': time.time() - start_time,
                    'confidence_score': mode_recommendation.get('confidence', 0.8),
                    'data_sources': {
                        'historical_memories': len(relevant_memories),
                        'context_factors': len(project_context),
                        'analysis_version': '1.0'
                    }
                }
            }
            
            # 记录分析到记忆系统
            self.memory_system.add_memory(
                content=f"任务分析: {task_description} -> 推荐模式: {mode_recommendation['recommended_mode']}",
                category=MemoryCategory.DECISION,
                importance=0.7,
                tags=['任务分析', '模式推荐', mode_recommendation['recommended_mode']]
            )
            
            return analysis_result
            
        except Exception as e:
            return self._handle_analysis_error(e, task_description, project_context)
    
    def _analyze_task_complexity(self, task_description: str, memories: List[MemoryFragment]) -> Dict[str, Any]:
        """分析任务复杂度"""
        
        # 基于关键词的复杂度指标
        complexity_keywords = {
            'high': ['系统', '架构', '平台', '框架', '重构', '迁移', '集成', '分布式'],
            'medium': ['功能', '模块', '接口', 'API', '数据库', '算法', '优化'],
            'low': ['修复', 'bug', '文档', '配置', '样式', '调试', '测试']
        }
        
        task_lower = task_description.lower()
        complexity_scores = {'high': 0, 'medium': 0, 'low': 0}
        
        for level, keywords in complexity_keywords.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            complexity_scores[level] = score
        
        # 确定主要复杂度
        max_score = max(complexity_scores.values())
        if max_score == 0:
            primary_complexity = 'medium'  # 默认中等复杂度
        else:
            primary_complexity = max(complexity_scores.keys(), key=complexity_scores.get)
        
        # 基于历史记忆调整
        similar_tasks = [m for m in memories if m.category == MemoryCategory.DECISION and '任务分析' in str(m.tags)]
        historical_adjustment = 0.0
        if similar_tasks:
            # 如果历史上类似任务较复杂，适当提升复杂度评估
            avg_importance = sum(m.importance for m in similar_tasks) / len(similar_tasks)
            if avg_importance > 0.8:
                historical_adjustment = 0.1
        
        return {
            'primary_level': primary_complexity,
            'keyword_scores': complexity_scores,
            'estimated_duration': self._estimate_duration_by_complexity(primary_complexity),
            'technical_depth': self._assess_technical_depth(task_description),
            'integration_complexity': self._assess_integration_complexity(task_description),
            'historical_adjustment': historical_adjustment,
            'confidence': min(0.95, 0.7 + (max_score / 10))
        }
    
    def _analyze_team_factors(self, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """分析团队因素"""
        
        team_size = project_context.get('team_size', 5)
        urgency = project_context.get('urgency', 'normal')
        project_type = project_context.get('project_type', 'unknown')
        
        # 团队规模影响
        if team_size <= 2:
            team_scale_factor = 'small'
            recommended_approach = 'agile'
        elif team_size <= 8:
            team_scale_factor = 'medium'
            recommended_approach = 'structured'
        else:
            team_scale_factor = 'large'
            recommended_approach = 'enterprise'
        
        # 紧急程度影响
        urgency_impact = {
            'low': {'process_overhead': 'acceptable', 'documentation_level': 'detailed'},
            'normal': {'process_overhead': 'moderate', 'documentation_level': 'standard'},
            'high': {'process_overhead': 'minimal', 'documentation_level': 'essential'},
            'emergency': {'process_overhead': 'none', 'documentation_level': 'minimal'}
        }.get(urgency, {'process_overhead': 'moderate', 'documentation_level': 'standard'})
        
        return {
            'team_size': team_size,
            'scale_factor': team_scale_factor,
            'recommended_approach': recommended_approach,
            'urgency_level': urgency,
            'urgency_impact': urgency_impact,
            'project_type': project_type,
            'collaboration_complexity': 'high' if team_size > 5 else 'medium' if team_size > 2 else 'low'
        }
    
    def _generate_mode_recommendation(self, task_complexity: Dict, team_factors: Dict, 
                                    historical_patterns: Dict, project_context: Dict) -> Dict[str, Any]:
        """生成模式推荐"""
        
        # 基础模式映射
        complexity_level = task_complexity['primary_level']
        team_size = team_factors['team_size']
        urgency = team_factors['urgency_level']
        
        # 模式选择逻辑
        if urgency in ['high', 'emergency'] or complexity_level == 'low':
            if team_size <= 3:
                recommended_mode = 'minimal'
                reasoning = f"基于{urgency}紧急程度和{complexity_level}复杂度，小团队适合轻量级流程"
            else:
                recommended_mode = 'standard'
                reasoning = f"基于{urgency}紧急程度，但团队规模需要结构化流程"
        elif complexity_level == 'high' or team_size > 8:
            recommended_mode = 'complete'
            reasoning = f"基于{complexity_level}复杂度和{team_size}人团队规模，需要完整流程控制"
        else:
            recommended_mode = 'standard'
            reasoning = f"基于{complexity_level}复杂度和中等团队规模，标准流程最适合"
        
        # 历史模式调整
        if historical_patterns.get('successful_mode'):
            historical_mode = historical_patterns['successful_mode']
            if historical_mode != recommended_mode:
                reasoning += f"；但历史经验显示{historical_mode}模式成功率更高"
        
        # 计算置信度
        confidence_factors = [
            task_complexity.get('confidence', 0.7),
            0.9 if team_size in [3, 5, 8] else 0.7,  # 标准团队规模置信度更高
            0.8 if urgency in ['normal', 'high'] else 0.6,  # 常见紧急程度置信度更高
            historical_patterns.get('confidence', 0.5)
        ]
        overall_confidence = sum(confidence_factors) / len(confidence_factors)
        
        return {
            'recommended_mode': recommended_mode,
            'confidence': min(0.95, overall_confidence),
            'reasoning': reasoning,
            'factors': {
                'task_complexity': complexity_level,
                'team_size': team_size,
                'urgency': urgency,
                'historical_success': historical_patterns.get('successful_mode'),
            },
            'alternative_modes': self._generate_alternative_modes(recommended_mode, task_complexity, team_factors),
            'mode_justification': self._generate_mode_justification(recommended_mode, task_complexity, team_factors)
        }
    
    def _generate_optimization_suggestions(self, task_description: str, mode_recommendation: Dict,
                                         current_state: Dict, memories: List[MemoryFragment]) -> Dict[str, Any]:
        """生成优化建议"""
        
        suggestions = {
            'workflow_optimizations': [],
            'parallel_execution': [],
            'risk_mitigation': [],
            'efficiency_improvements': []
        }
        
        recommended_mode = mode_recommendation['recommended_mode']
        
        # 基于模式的工作流优化
        if recommended_mode == 'standard':
            suggestions['parallel_execution'].append({
                'type': 'design_development_parallel',
                'description': '设计阶段(P2)和开发准备可以部分并行进行',
                'time_saving': '20-30%',
                'risk_level': 'low'
            })
        
        if recommended_mode == 'complete':
            suggestions['parallel_execution'].extend([
                {
                    'type': 'test_design_implementation',
                    'description': '测试设计(S3)可与功能实现(S4)并行',
                    'time_saving': '25%',
                    'risk_level': 'medium'
                },
                {
                    'type': 'documentation_development',
                    'description': '文档编写可与开发并行进行',
                    'time_saving': '15%',
                    'risk_level': 'low'
                }
            ])
        
        # 基于任务特点的优化建议
        if 'API' in task_description or '接口' in task_description:
            suggestions['workflow_optimizations'].append({
                'type': 'api_first_design',
                'description': '建议采用API优先设计，提前定义接口契约',
                'benefit': '提高前后端并行开发效率'
            })
        
        if '数据库' in task_description or 'database' in task_description.lower():
            suggestions['workflow_optimizations'].append({
                'type': 'schema_first_approach',
                'description': '建议优先设计数据库模式，确保数据一致性',
                'benefit': '减少后期重构风险'
            })
        
        # 基于历史经验的建议
        similar_memories = [m for m in memories if m.category == MemoryCategory.LEARNING]
        if similar_memories:
            for memory in similar_memories[:3]:  # 取前3个相关经验
                if 'optimization' in memory.tags or '优化' in memory.tags:
                    suggestions['efficiency_improvements'].append({
                        'type': 'historical_learning',
                        'description': f"历史经验: {memory.content[:100]}...",
                        'source': 'previous_project',
                        'confidence': memory.importance
                    })
        
        return suggestions
    
    def _handle_analysis_error(self, error: Exception, task_description: str, 
                             project_context: Dict[str, Any]) -> Dict[str, Any]:
        """处理分析错误"""
        
        # 记录错误
        self.memory_system.add_memory(
            content=f"任务分析失败: {str(error)} (任务: {task_description})",
            category=MemoryCategory.ISSUE,
            importance=0.6,
            tags=['分析错误', '异常处理']
        )
        
        # 返回降级分析结果
        return {
            'task_analysis': {
                'description': task_description,
                'complexity_factors': {'primary_level': 'medium', 'confidence': 0.5},
                'estimated_effort': '3-5天',
                'key_challenges': ['分析过程中遇到技术问题，建议人工评估']
            },
            'mode_recommendation': {
                'recommended_mode': 'standard',
                'confidence': 0.5,
                'reasoning': '由于分析异常，采用标准模式作为安全选择',
                'factors': {'fallback_mode': True}
            },
            'optimization_suggestions': {
                'workflow_optimizations': [],
                'parallel_execution': [],
                'risk_mitigation': [
                    {
                        'type': 'analysis_limitation',
                        'description': '智能分析功能异常，建议进行人工复核',
                        'priority': 'high'
                    }
                ]
            },
            'error_info': {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'timestamp': datetime.now().isoformat(),
                'fallback_used': True
            }
        }
    
    # 辅助方法的简化实现
    def _analyze_historical_patterns(self, memories: List[MemoryFragment]) -> Dict[str, Any]:
        """分析历史模式"""
        if not memories:
            return {'successful_mode': None, 'confidence': 0.5}
        
        # 统计历史成功模式
        mode_counts = {}
        for memory in memories:
            if 'mode' in memory.tags:
                for tag in memory.tags:
                    if tag in ['minimal', 'standard', 'complete']:
                        mode_counts[tag] = mode_counts.get(tag, 0) + memory.importance
        
        if mode_counts:
            successful_mode = max(mode_counts.keys(), key=mode_counts.get)
            return {'successful_mode': successful_mode, 'confidence': 0.8}
        
        return {'successful_mode': None, 'confidence': 0.5}
    
    def _estimate_effort(self, task_complexity: Dict, team_factors: Dict) -> str:
        """估算工作量"""
        complexity = task_complexity['primary_level']
        team_size = team_factors['team_size']
        
        base_days = {'low': 1, 'medium': 3, 'high': 7}[complexity]
        if team_size > 5:
            base_days = int(base_days * 0.7)  # 大团队效率提升
        elif team_size < 3:
            base_days = int(base_days * 1.3)  # 小团队可能效率降低
        
        return f"{base_days}-{base_days + 2}天"
    
    def _identify_key_challenges(self, task_description: str, memories: List[MemoryFragment]) -> List[str]:
        """识别关键挑战"""
        challenges = []
        
        task_lower = task_description.lower()
        if '集成' in task_description or 'integration' in task_lower:
            challenges.append('系统集成复杂度高')
        if '性能' in task_description or 'performance' in task_lower:
            challenges.append('性能优化要求严格')
        if '安全' in task_description or 'security' in task_lower:
            challenges.append('安全性要求需要专业评估')
        
        # 从历史记忆中学习挑战
        issue_memories = [m for m in memories if m.category == MemoryCategory.ISSUE]
        for memory in issue_memories[:2]:
            challenges.append(f"历史经验: {memory.content[:50]}...")
        
        return challenges or ['常规开发挑战']
    
    def _estimate_duration_by_complexity(self, complexity: str) -> str:
        """根据复杂度估算持续时间"""
        duration_map = {
            'low': '1-2天',
            'medium': '3-5天', 
            'high': '1-2周'
        }
        return duration_map.get(complexity, '3-5天')
    
    def _assess_technical_depth(self, task_description: str) -> str:
        """评估技术深度"""
        tech_keywords = ['算法', '架构', '框架', '底层', '内核', 'algorithm', 'architecture']
        task_lower = task_description.lower()
        
        if any(keyword in task_lower for keyword in tech_keywords):
            return 'high'
        elif any(keyword in task_lower for keyword in ['数据库', '接口', 'database', 'api']):
            return 'medium'
        else:
            return 'low'
    
    def _assess_integration_complexity(self, task_description: str) -> str:
        """评估集成复杂度"""
        integration_keywords = ['集成', '对接', '第三方', '微服务', 'integration', 'microservice']
        task_lower = task_description.lower()
        
        if any(keyword in task_lower for keyword in integration_keywords):
            return 'high'
        else:
            return 'low'
    
    def _find_similar_projects(self, memories: List[MemoryFragment]) -> List[Dict[str, Any]]:
        """查找相似项目"""
        similar = []
        for memory in memories[:3]:  # 取前3个相关记忆
            if memory.category in [MemoryCategory.CONTEXT, MemoryCategory.DECISION]:
                similar.append({
                    'description': memory.content[:80] + '...',
                    'similarity': memory.importance,
                    'date': memory.created_at.strftime('%Y-%m-%d') if memory.created_at else 'unknown'
                })
        return similar
    
    def _estimate_resource_requirements(self, task_complexity: Dict, team_factors: Dict) -> Dict[str, Any]:
        """估算资源需求"""
        complexity = task_complexity['primary_level']
        team_size = team_factors['team_size']
        
        return {
            'developer_hours': {'low': 8, 'medium': 24, 'high': 80}[complexity],
            'testing_hours': {'low': 4, 'medium': 12, 'high': 40}[complexity],
            'review_hours': {'low': 2, 'medium': 6, 'high': 20}[complexity],
            'team_coordination': 'minimal' if team_size <= 3 else 'moderate' if team_size <= 6 else 'intensive'
        }
    
    def _generate_alternative_modes(self, recommended_mode: str, task_complexity: Dict, team_factors: Dict) -> List[Dict[str, Any]]:
        """生成备选模式"""
        alternatives = []
        modes = ['minimal', 'standard', 'complete']
        
        for mode in modes:
            if mode != recommended_mode:
                alternatives.append({
                    'mode': mode,
                    'suitability': self._calculate_mode_suitability(mode, task_complexity, team_factors),
                    'trade_offs': self._describe_mode_tradeoffs(mode, recommended_mode)
                })
        
        return sorted(alternatives, key=lambda x: x['suitability'], reverse=True)[:2]
    
    def _calculate_mode_suitability(self, mode: str, task_complexity: Dict, team_factors: Dict) -> float:
        """计算模式适用性分数"""
        complexity = task_complexity['primary_level']
        team_size = team_factors['team_size']
        
        suitability_matrix = {
            'minimal': {'low': 0.9, 'medium': 0.6, 'high': 0.3},
            'standard': {'low': 0.7, 'medium': 0.9, 'high': 0.7},
            'complete': {'low': 0.4, 'medium': 0.7, 'high': 0.9}
        }
        
        base_score = suitability_matrix[mode][complexity]
        
        # 团队规模调整
        if mode == 'minimal' and team_size > 5:
            base_score *= 0.7
        elif mode == 'complete' and team_size < 3:
            base_score *= 0.6
        
        return min(0.95, base_score)
    
    def _describe_mode_tradeoffs(self, alternative_mode: str, recommended_mode: str) -> str:
        """描述模式权衡"""
        tradeoffs = {
            ('minimal', 'standard'): '更快但文档较少',
            ('minimal', 'complete'): '快速但缺乏严格质控',
            ('standard', 'minimal'): '更规范但时间较长',
            ('standard', 'complete'): '平衡但不如完整模式严格',
            ('complete', 'minimal'): '严格质控但耗时更长',
            ('complete', 'standard'): '最严格但可能过度工程化'
        }
        
        return tradeoffs.get((alternative_mode, recommended_mode), '不同的流程权衡')
    
    def _generate_mode_justification(self, mode: str, task_complexity: Dict, team_factors: Dict) -> str:
        """生成模式选择理由"""
        complexity = task_complexity['primary_level']
        team_size = team_factors['team_size']
        urgency = team_factors['urgency_level']
        
        justifications = {
            'minimal': f"轻量级模式适合{complexity}复杂度任务，{team_size}人团队可快速迭代",
            'standard': f"标准模式平衡了{complexity}复杂度管控和{team_size}人团队效率",
            'complete': f"完整模式确保{complexity}复杂度任务的质量，适合{team_size}人规模团队"
        }
        
        base_justification = justifications.get(mode, "标准流程选择")
        
        if urgency in ['high', 'emergency']:
            base_justification += f"，考虑到{urgency}紧急程度已适当简化流程"
        
        return base_justification
    
    def _assess_project_risks(self, task_description: str, mode_recommendation: Dict, project_context: Dict) -> Dict[str, Any]:
        """评估项目风险"""
        risks = {
            'technical_risks': [],
            'process_risks': [],
            'resource_risks': [],
            'timeline_risks': []
        }
        
        # 技术风险
        task_lower = task_description.lower()
        if '新技术' in task_description or 'new' in task_lower:
            risks['technical_risks'].append({
                'risk': '新技术学习曲线',
                'impact': 'medium',
                'mitigation': '预留技术调研时间'
            })
        
        # 流程风险
        recommended_mode = mode_recommendation['recommended_mode']
        if mode_recommendation['confidence'] < 0.7:
            risks['process_risks'].append({
                'risk': '模式选择不确定性',
                'impact': 'medium', 
                'mitigation': '定期评估和调整流程'
            })
        
        # 资源风险
        team_size = project_context.get('team_size', 5)
        if team_size < 3 and recommended_mode == 'complete':
            risks['resource_risks'].append({
                'risk': '团队规模与流程不匹配',
                'impact': 'high',
                'mitigation': '考虑简化流程或增加人员'
            })
        
        return risks
    
    def get_pateoas_status(self) -> Dict[str, Any]:
        """获取PATEOAS系统完整状态"""
        try:
            # 系统信息
            system_info = {
                'status': 'active',
                'project_id': self.project_id,
                'start_time': self.current_session['start_time'].isoformat(),
                'uptime': str(datetime.now() - self.current_session['start_time']),
                'version': '1.0.0'
            }
            
            # 性能指标
            performance_metrics = {
                'total_interactions': self.current_session['interaction_count'],
                'success_rate': self._calculate_success_rate(),
                'avg_response_time': self.performance_metrics.get('average_response_time', 0),
                'error_count': self.performance_metrics.get('failed_requests', 0)
            }
            
            # 记忆信息
            memory_stats = self.memory_system.get_memory_stats()
            memory_info = {
                'total_memories': memory_stats.get('total_memories', 0),
                'category_breakdown': memory_stats.get('category_breakdown', {}),
                'recent_activities': memory_stats.get('recent_activities', [])
            }
            
            # 当前状态
            current_state = self.state_manager.get_current_state()
            
            # 决策门状态
            decision_gates_status = []
            for gate_id, gate in self.decision_gates.items():
                try:
                    gate_status = {
                        'gate_id': gate_id,
                        'name': getattr(gate, 'name', gate_id),
                        'status': 'active',
                        'performance': getattr(gate, 'performance_metrics', {})
                    }
                    decision_gates_status.append(gate_status)
                except:
                    pass
            
            return {
                'system_info': system_info,
                'performance_metrics': performance_metrics,
                'memory_info': memory_info,
                'current_state': current_state,
                'decision_gates': decision_gates_status,
                'configuration': {
                    'memory_retention_days': getattr(self.config, 'memory_retention_days', 90),
                    'performance_monitoring': getattr(self.config, 'performance_monitoring', True),
                    'auto_optimization': getattr(self.config, 'auto_optimization', True)
                },
                'health_check': {
                    'memory_system': 'healthy',
                    'state_manager': 'healthy',
                    'flow_controller': 'healthy',
                    'decision_gates': 'healthy'
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            # 降级状态信息
            return {
                'system_info': {
                    'status': 'error',
                    'project_id': self.project_id,
                    'error': str(e)
                },
                'performance_metrics': {
                    'total_interactions': 0,
                    'success_rate': 0,
                    'error_count': 1
                },
                'memory_info': {
                    'total_memories': 0,
                    'status': 'error'
                },
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        total = self.performance_metrics.get('total_requests', 0)
        failed = self.performance_metrics.get('failed_requests', 0)
        
        if total == 0:
            return 1.0
        
        successful = total - failed
        return successful / total