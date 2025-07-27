"""
自适应流程控制器
基于项目状态动态调整工作流
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from .models import NextAction, ActionType, ReasoningStep, MemoryFragment, MemoryCategory
from .config import get_config
from .utils import analyze_task_complexity, detect_project_type, calculate_confidence, is_recent
from .workflow_optimizer import WorkflowOptimizer, OptimizationContext, WorkflowMode as OptimizerWorkflowMode, OptimizationStrategy


class WorkflowMode(Enum):
    """工作流模式"""
    SMART = "smart"
    MINIMAL = "minimal"
    STANDARD = "standard"
    COMPLETE = "complete"
    EMERGENCY = "emergency"


class ParallelOpportunity:
    """并行执行机会"""
    def __init__(self, opportunity_type: str, stages: List[str], time_saving: str, risk_level: str):
        self.type = opportunity_type
        self.stages = stages
        self.estimated_time_saving = time_saving
        self.risk_level = risk_level
        self.confidence = 0.8


class AdaptiveFlowController:
    """自适应流程控制器"""
    
    def __init__(self):
        self.config = get_config()
        self.bottleneck_detector = BottleneckDetector()
        self.parallel_optimizer = ParallelExecutionOptimizer()
        self.flow_optimizer = FlowOptimizer()
        self.workflow_optimizer = WorkflowOptimizer()
        self.current_mode = "smart"
        self.adaptation_history = []
        self.performance_metrics = {
            'efficiency': 0.8,
            'quality': 0.8,
            'speed': 0.8
        }
    
    def optimize_workflow(self, current_state: Dict[str, Any], project_context: Dict[str, Any]) -> Dict[str, Any]:
        """优化工作流执行"""
        optimizations = {}
        
        # 1. 检测当前瓶颈
        bottlenecks = self.bottleneck_detector.detect(current_state)
        optimizations['bottlenecks'] = bottlenecks
        
        # 2. 分析并行执行可能性
        parallel_opportunities = self.parallel_optimizer.analyze_parallelization_opportunities(current_state)
        optimizations['parallel_execution'] = [
            {
                'type': opp.type,
                'stages': opp.stages,
                'time_saving': opp.estimated_time_saving,
                'risk_level': opp.risk_level,
                'confidence': opp.confidence
            } for opp in parallel_opportunities
        ]
        
        # 3. 阶段重排序建议
        reordering = self.flow_optimizer.suggest_stage_reordering(current_state, project_context)
        optimizations['stage_reordering'] = reordering
        
        # 4. 阶段跳过建议
        skipping = self.flow_optimizer.suggest_stage_skipping(current_state, project_context)
        optimizations['stage_skipping'] = skipping
        
        # 5. 资源分配优化
        resource_allocation = self.flow_optimizer.optimize_resource_allocation(current_state, project_context)
        optimizations['resource_allocation'] = resource_allocation
        
        return optimizations
    
    def decide_next_action(self, user_input: str, current_state: Dict[str, Any], memory_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """决定下一步行动"""
        # 1. 分析用户意图
        intent = self._analyze_user_intent(user_input, current_state)
        
        # 2. 基于状态和记忆做决策
        decision = {
            'recommended_action': self._recommend_action(intent, current_state, memory_context),
            'alternative_actions': self._generate_alternatives(intent, current_state),
            'reasoning': self._generate_reasoning(intent, current_state, memory_context),
            'confidence': self._calculate_confidence(intent, current_state, memory_context)
        }
        
        return decision
    
    def select_optimal_workflow_mode(self, task_description: str, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """选择最优工作流模式"""
        # 分析任务复杂度
        complexity_analysis = analyze_task_complexity(task_description)
        
        # 获取项目信息
        team_size = project_context.get('team_size', 1)
        urgency = self._detect_urgency(task_description)
        project_type = project_context.get('project_type', 'unknown')
        
        # 决策逻辑
        if urgency == 'emergency':
            recommended_mode = WorkflowMode.EMERGENCY
            confidence = 0.95
        elif complexity_analysis['level'] == 'low' and team_size <= 5:
            recommended_mode = WorkflowMode.MINIMAL
            confidence = 0.85
        elif complexity_analysis['level'] == 'high' or team_size > 10:
            recommended_mode = WorkflowMode.COMPLETE
            confidence = 0.9
        elif complexity_analysis['level'] == 'medium' or team_size <= 10:
            recommended_mode = WorkflowMode.STANDARD
            confidence = 0.8
        else:
            recommended_mode = WorkflowMode.SMART
            confidence = 0.7
        
        return {
            'recommended_mode': recommended_mode.value,
            'confidence': confidence,
            'reasoning': f"基于任务复杂度({complexity_analysis['level']})、团队规模({team_size})和紧急程度({urgency})的分析",
            'complexity_analysis': complexity_analysis,
            'factors': {
                'task_complexity': complexity_analysis['level'],
                'team_size': team_size,
                'urgency': urgency,
                'project_type': project_type
            }
        }
    
    def _analyze_user_intent(self, user_input: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户意图"""
        text = user_input.lower()
        
        # 意图分类
        intent_keywords = {
            'start_project': ['开始', '启动', '新建', 'start', 'begin', 'create'],
            'continue_work': ['继续', '下一步', 'continue', 'next', '进行'],
            'check_status': ['状态', '进度', '如何', 'status', 'progress', 'how'],
            'fix_issue': ['问题', '错误', '修复', 'issue', 'error', 'fix', 'bug'],
            'optimize': ['优化', '改进', '提升', 'optimize', 'improve', 'enhance'],
            'complete_stage': ['完成', '结束', 'complete', 'finish', 'done']
        }
        
        detected_intents = []
        for intent, keywords in intent_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_intents.append(intent)
        
        primary_intent = detected_intents[0] if detected_intents else 'general_query'
        
        return {
            'primary_intent': primary_intent,
            'all_intents': detected_intents,
            'confidence': 0.8 if detected_intents else 0.5,
            'user_input': user_input
        }
    
    def _recommend_action(self, intent: Dict[str, Any], current_state: Dict[str, Any], memory_context: List[Dict[str, Any]]) -> NextAction:
        """推荐行动"""
        primary_intent = intent['primary_intent']
        current_stage = current_state.get('workflow_state', {}).get('current_stage', 'S1')
        
        if primary_intent == 'start_project':
            return NextAction(
                action_type=ActionType.CONTINUE,
                description="开始项目分析和需求收集",
                command="aceflow start --mode smart",
                confidence=0.9,
                estimated_time="2-4小时"
            )
        elif primary_intent == 'continue_work':
            return NextAction(
                action_type=ActionType.CONTINUE,
                description=f"继续执行当前阶段 {current_stage}",
                command=f"aceflow run {current_stage}",
                confidence=0.85,
                estimated_time="1-3小时"
            )
        elif primary_intent == 'check_status':
            return NextAction(
                action_type=ActionType.CONTINUE,
                description="查看项目状态和进度",
                command="aceflow status --verbose",
                confidence=0.95,
                estimated_time="5分钟"
            )
        elif primary_intent == 'fix_issue':
            return NextAction(
                action_type=ActionType.OPTIMIZE,
                description="分析和修复当前问题",
                command="aceflow analyze --focus issues",
                confidence=0.8,
                estimated_time="30分钟-2小时"
            )
        elif primary_intent == 'optimize':
            return NextAction(
                action_type=ActionType.OPTIMIZE,
                description="优化当前工作流程",
                command="aceflow optimize --current-stage",
                confidence=0.75,
                estimated_time="1-2小时"
            )
        else:
            return NextAction(
                action_type=ActionType.CONTINUE,
                description="继续当前工作流程",
                command="aceflow status",
                confidence=0.6,
                estimated_time="未知"
            )
    
    def _generate_alternatives(self, intent: Dict[str, Any], current_state: Dict[str, Any]) -> List[NextAction]:
        """生成替代行动"""
        alternatives = []
        
        # 基于当前状态生成替代方案
        current_stage = current_state.get('workflow_state', {}).get('current_stage', 'S1')
        
        alternatives.append(NextAction(
            action_type=ActionType.PARALLEL,
            description="并行执行多个任务",
            command="aceflow run --parallel",
            confidence=0.7,
            estimated_time="节省20-40%时间"
        ))
        
        alternatives.append(NextAction(
            action_type=ActionType.SKIP,
            description="跳过非关键阶段",
            command="aceflow skip --non-critical",
            confidence=0.6,
            estimated_time="节省1-2小时"
        ))
        
        alternatives.append(NextAction(
            action_type=ActionType.ESCALATE,
            description="请求人工协助",
            command="aceflow escalate --reason complexity",
            confidence=0.8,
            estimated_time="等待人工响应"
        ))
        
        return alternatives
    
    def _generate_reasoning(self, intent: Dict[str, Any], current_state: Dict[str, Any], memory_context: List[Dict[str, Any]]) -> List[ReasoningStep]:
        """生成推理链"""
        reasoning_chain = []
        
        # 步骤1：意图分析
        reasoning_chain.append(ReasoningStep(
            step_id="intent_analysis",
            description="分析用户意图",
            input_factors=[intent['user_input']],
            logic=f"基于关键词匹配识别用户意图为: {intent['primary_intent']}",
            output=f"用户意图: {intent['primary_intent']}",
            confidence=intent['confidence']
        ))
        
        # 步骤2：状态评估
        current_stage = current_state.get('workflow_state', {}).get('current_stage', 'unknown')
        progress = current_state.get('workflow_state', {}).get('stage_progress', 0)
        
        reasoning_chain.append(ReasoningStep(
            step_id="state_assessment",
            description="评估当前项目状态",
            input_factors=[f"当前阶段: {current_stage}", f"进度: {progress}%"],
            logic="分析当前工作流状态和进度",
            output=f"项目处于 {current_stage} 阶段，进度 {progress}%",
            confidence=0.9
        ))
        
        # 步骤3：记忆召回
        if memory_context:
            relevant_memories = [m['content'][:50] + "..." for m in memory_context[:3]]
            reasoning_chain.append(ReasoningStep(
                step_id="memory_recall",
                description="召回相关历史信息",
                input_factors=relevant_memories,
                logic="基于相似性召回相关历史记忆",
                output=f"找到 {len(memory_context)} 条相关记忆",
                confidence=0.8
            ))
        
        # 步骤4：决策制定
        reasoning_chain.append(ReasoningStep(
            step_id="decision_making",
            description="制定行动建议",
            input_factors=["用户意图", "当前状态", "历史记忆"],
            logic="综合分析用户意图、项目状态和历史经验",
            output="生成推荐行动和替代方案",
            confidence=0.85
        ))
        
        return reasoning_chain
    
    def _calculate_confidence(self, intent: Dict[str, Any], current_state: Dict[str, Any], memory_context: List[Dict[str, Any]]) -> float:
        """计算决策置信度"""
        factors = {
            'intent_clarity': intent['confidence'],
            'state_completeness': 0.9 if current_state.get('workflow_state') else 0.5,
            'memory_relevance': min(1.0, len(memory_context) / 5.0),
            'context_consistency': 0.8  # 简化实现
        }
        
        weights = {
            'intent_clarity': 0.3,
            'state_completeness': 0.3,
            'memory_relevance': 0.2,
            'context_consistency': 0.2
        }
        
        return calculate_confidence(factors, weights)
    
    def _detect_urgency(self, task_description: str) -> str:
        """检测任务紧急程度"""
        text = task_description.lower()
        
        emergency_keywords = ['紧急', '立即', '马上', 'urgent', 'emergency', 'critical', '故障', '线上']
        high_keywords = ['重要', '优先', 'important', 'priority', '尽快']
        
        if any(keyword in text for keyword in emergency_keywords):
            return 'emergency'
        elif any(keyword in text for keyword in high_keywords):
            return 'high'
        else:
            return 'normal'


class BottleneckDetector:
    """瓶颈检测器"""
    
    def detect(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测工作流瓶颈"""
        bottlenecks = []
        
        workflow_state = current_state.get('workflow_state', {})
        current_stage = workflow_state.get('current_stage', '')
        stage_progress = workflow_state.get('stage_progress', 0)
        
        # 检测进度停滞
        if stage_progress < 50 and current_stage in ['S2', 'S3', 'S4']:
            bottlenecks.append({
                'type': 'progress_stall',
                'stage': current_stage,
                'description': f'{current_stage} 阶段进度缓慢',
                'severity': 'medium',
                'suggestion': '考虑分解任务或寻求帮助'
            })
        
        # 检测依赖阻塞
        pending_tasks = workflow_state.get('pending_tasks', [])
        if len(pending_tasks) > 5:
            bottlenecks.append({
                'type': 'dependency_blocking',
                'description': f'有 {len(pending_tasks)} 个待处理任务',
                'severity': 'high',
                'suggestion': '优先处理关键依赖任务'
            })
        
        return bottlenecks


class ParallelExecutionOptimizer:
    """并行执行优化器"""
    
    def analyze_parallelization_opportunities(self, workflow_state: Dict[str, Any]) -> List[ParallelOpportunity]:
        """分析并行执行机会"""
        opportunities = []
        
        current_stage = workflow_state.get('workflow_state', {}).get('current_stage', '')
        technology_stack = workflow_state.get('project_context', {}).get('technology_stack', [])
        
        # 1. 前后端任务并行
        if self._has_frontend_backend_separation(technology_stack):
            opportunities.append(ParallelOpportunity(
                opportunity_type='frontend_backend_parallel',
                stages=['S4_frontend', 'S4_backend'],
                time_saving='40%',
                risk_level='low'
            ))
        
        # 2. 测试用例设计与实现并行
        if current_stage in ['S2', 'S3'] and self._can_parallel_test_design(workflow_state):
            opportunities.append(ParallelOpportunity(
                opportunity_type='test_implementation_parallel',
                stages=['S3_test_design', 'S4_implementation'],
                time_saving='25%',
                risk_level='medium'
            ))
        
        # 3. 文档生成并行
        if current_stage in ['S4', 'S5']:
            opportunities.append(ParallelOpportunity(
                opportunity_type='documentation_parallel',
                stages=['S4_implementation', 'documentation'],
                time_saving='15%',
                risk_level='low'
            ))
        
        return opportunities
    
    def _has_frontend_backend_separation(self, technology_stack: List[str]) -> bool:
        """检查是否有前后端分离"""
        frontend_techs = ['react', 'vue', 'angular', 'javascript', 'typescript']
        backend_techs = ['python', 'java', 'nodejs', 'go', 'php']
        
        has_frontend = any(tech in technology_stack for tech in frontend_techs)
        has_backend = any(tech in technology_stack for tech in backend_techs)
        
        return has_frontend and has_backend
    
    def _can_parallel_test_design(self, workflow_state: Dict[str, Any]) -> bool:
        """检查是否可以并行设计测试"""
        # 简化实现：如果有明确的需求文档就可以并行
        return workflow_state.get('workflow_state', {}).get('completed_stages', []).count('S1') > 0


class FlowOptimizer:
    """流程优化器"""
    
    def suggest_stage_reordering(self, current_state: Dict[str, Any], project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """建议阶段重排序"""
        suggestions = []
        
        current_stage = current_state.get('workflow_state', {}).get('current_stage', '')
        project_urgency = project_context.get('urgency', 'normal')
        
        if project_urgency == 'high' and current_stage == 'S3':
            suggestions.append({
                'type': 'reorder',
                'description': '高优先级项目可以先开始实现，后补充测试',
                'original_order': ['S3', 'S4'],
                'suggested_order': ['S4', 'S3'],
                'risk_level': 'medium',
                'time_saving': '1-2天'
            })
        
        return suggestions
    
    def suggest_stage_skipping(self, current_state: Dict[str, Any], project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """建议阶段跳过"""
        suggestions = []
        
        team_experience = project_context.get('team_experience', 'medium')
        project_complexity = project_context.get('complexity', 'medium')
        
        if team_experience == 'senior' and project_complexity == 'low':
            suggestions.append({
                'type': 'skip',
                'stage': 'S7',
                'description': '经验丰富的团队处理简单项目可跳过正式演示',
                'risk_level': 'low',
                'time_saving': '2-4小时'
            })
        
        return suggestions
    
    def optimize_resource_allocation(self, current_state: Dict[str, Any], project_context: Dict[str, Any]) -> Dict[str, Any]:
        """优化资源分配"""
        team_size = project_context.get('team_size', 1)
        current_stage = current_state.get('workflow_state', {}).get('current_stage', '')
        
        allocation = {
            'recommended_allocation': {},
            'bottleneck_stages': [],
            'parallel_opportunities': []
        }
        
        if team_size > 3 and current_stage == 'S4':
            allocation['recommended_allocation'] = {
                'frontend': '40%',
                'backend': '40%',
                'testing': '20%'
            }
            allocation['parallel_opportunities'].append('前后端并行开发')
        
        return allocation


class AdaptiveFlowControllerWithPATEOAS(AdaptiveFlowController):
    """带PATEOAS功能的自适应流程控制器"""
    
    def optimize_workflow_with_pateoas(
        self,
        current_state: Dict[str, Any],
        memories: List[MemoryFragment],
        project_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """使用PATEOAS优化工作流"""
        
        # 构建优化上下文
        optimization_context = self._build_optimization_context(
            current_state, memories, project_context or {}
        )
        
        # 获取当前工作流模式
        current_workflow_mode = self._get_current_workflow_mode()
        
        # 执行工作流优化
        recommendation = self.workflow_optimizer.optimize_workflow(
            optimization_context, memories, current_workflow_mode
        )
        
        # 应用优化建议
        optimization_result = self._apply_optimization_recommendation(
            recommendation, current_state
        )
        
        # 记录优化历史
        self._record_optimization_history(recommendation, optimization_result)
        
        return {
            'recommendation': {
                'mode': recommendation.recommended_mode.value,
                'strategy': recommendation.optimization_strategy.value,
                'actions': recommendation.suggested_actions,
                'time_saving': recommendation.estimated_time_saving,
                'quality_impact': recommendation.quality_impact,
                'confidence': recommendation.confidence,
                'reasoning': recommendation.reasoning
            },
            'optimization_result': optimization_result,
            'performance_impact': self._calculate_performance_impact(recommendation)
        }
    
    def _build_optimization_context(
        self,
        current_state: Dict[str, Any],
        memories: List[MemoryFragment],
        project_context: Dict[str, Any]
    ) -> OptimizationContext:
        """构建优化上下文"""
        
        # 分析时间约束
        time_constraints = {
            'urgent': current_state.get('urgency_level', 'normal') == 'high',
            'deadline_pressure': current_state.get('deadline_pressure', False),
            'elapsed_ratio': current_state.get('elapsed_time_ratio', 0.5)
        }
        
        # 分析资源可用性
        resource_availability = {
            'development_time': current_state.get('available_dev_time', 0.8),
            'team_capacity': current_state.get('team_capacity', 0.8),
            'technical_resources': current_state.get('tech_resources', 0.8)
        }
        
        # 分析质量要求
        quality_requirements = {
            'high_quality': current_state.get('quality_priority', 'medium') == 'high',
            'quality_threshold': current_state.get('quality_threshold', 0.8)
        }
        
        # 分析历史性能
        historical_performance = {
            'success_rate': self.performance_metrics.get('efficiency', 0.8),
            'average_quality': self.performance_metrics.get('quality', 0.8),
            'speed_performance': self.performance_metrics.get('speed', 0.8)
        }
        
        return OptimizationContext(
            current_stage=current_state.get('current_stage', 'S1'),
            project_progress=current_state.get('task_progress', 0.0),
            time_constraints=time_constraints,
            resource_availability=resource_availability,
            quality_requirements=quality_requirements,
            historical_performance=historical_performance,
            user_preferences=current_state.get('user_preferences', {})
        )
    
    def _get_current_workflow_mode(self) -> OptimizerWorkflowMode:
        """获取当前工作流模式"""
        mode_mapping = {
            'minimal': OptimizerWorkflowMode.MINIMAL,
            'standard': OptimizerWorkflowMode.STANDARD,
            'comprehensive': OptimizerWorkflowMode.COMPREHENSIVE,
            'smart': OptimizerWorkflowMode.SMART
        }
        return mode_mapping.get(self.current_mode, OptimizerWorkflowMode.STANDARD)
    
    def _apply_optimization_recommendation(
        self,
        recommendation,
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用优化建议"""
        
        applied_changes = []
        
        # 应用工作流模式变更
        if recommendation.recommended_mode.value != self.current_mode:
            old_mode = self.current_mode
            self.current_mode = recommendation.recommended_mode.value
            applied_changes.append({
                'type': 'mode_change',
                'from': old_mode,
                'to': self.current_mode,
                'reason': 'optimization_recommendation'
            })
        
        # 应用建议的行动
        for action in recommendation.suggested_actions:
            if action['priority'] == 'high':
                applied_changes.append({
                    'type': 'action_applied',
                    'action': action,
                    'status': 'applied'
                })
            else:
                applied_changes.append({
                    'type': 'action_suggested',
                    'action': action,
                    'status': 'suggested'
                })
        
        return {
            'applied_changes': applied_changes,
            'new_mode': self.current_mode,
            'optimization_strategy': recommendation.optimization_strategy.value,
            'timestamp': datetime.now().isoformat()
        }
    
    def _record_optimization_history(
        self,
        recommendation,
        optimization_result: Dict[str, Any]
    ):
        """记录优化历史"""
        
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'strategy': recommendation.optimization_strategy.value,
            'recommended_mode': recommendation.recommended_mode.value,
            'confidence': recommendation.confidence,
            'estimated_benefits': {
                'time_saving': recommendation.estimated_time_saving,
                'quality_impact': recommendation.quality_impact
            },
            'applied_changes': len(optimization_result['applied_changes']),
            'reasoning': recommendation.reasoning
        }
        
        self.adaptation_history.append(history_entry)
        
        # 保持历史记录在合理范围内
        if len(self.adaptation_history) > 50:
            self.adaptation_history = self.adaptation_history[-50:]
    
    def _calculate_performance_impact(
        self,
        recommendation
    ) -> Dict[str, float]:
        """计算性能影响"""
        
        # 基于优化策略计算预期性能影响
        strategy = recommendation.optimization_strategy
        
        if strategy == OptimizationStrategy.SPEED:
            return {
                'speed_improvement': recommendation.estimated_time_saving,
                'quality_impact': -0.1,  # 速度优化可能略微影响质量
                'efficiency_improvement': recommendation.estimated_time_saving * 0.8
            }
        elif strategy == OptimizationStrategy.QUALITY:
            return {
                'speed_impact': -0.1,  # 质量优化可能略微影响速度
                'quality_improvement': recommendation.quality_impact,
                'efficiency_improvement': recommendation.quality_impact * 0.6
            }
        elif strategy == OptimizationStrategy.BALANCED:
            return {
                'speed_improvement': recommendation.estimated_time_saving * 0.7,
                'quality_improvement': recommendation.quality_impact * 0.7,
                'efficiency_improvement': (recommendation.estimated_time_saving + recommendation.quality_impact) * 0.5
            }
        else:  # ADAPTIVE
            return {
                'speed_improvement': recommendation.estimated_time_saving * 0.8,
                'quality_improvement': recommendation.quality_impact * 0.8,
                'efficiency_improvement': (recommendation.estimated_time_saving + recommendation.quality_impact) * 0.7
            }
    
    def get_optimization_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取优化历史"""
        return self.adaptation_history[-limit:]
    
    def analyze_optimization_effectiveness(self) -> Dict[str, Any]:
        """分析优化效果"""
        if not self.adaptation_history:
            return {'status': 'no_data', 'message': '暂无优化历史数据'}
        
        recent_optimizations = self.adaptation_history[-10:]
        
        # 计算平均置信度
        avg_confidence = sum(opt['confidence'] for opt in recent_optimizations) / len(recent_optimizations)
        
        # 计算策略分布
        strategy_counts = {}
        for opt in recent_optimizations:
            strategy = opt['strategy']
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        # 计算预期收益
        total_time_saving = sum(opt['estimated_benefits']['time_saving'] for opt in recent_optimizations)
        total_quality_impact = sum(opt['estimated_benefits']['quality_impact'] for opt in recent_optimizations)
        
        return {
            'status': 'analyzed',
            'optimization_count': len(recent_optimizations),
            'avg_confidence': avg_confidence,
            'strategy_distribution': strategy_counts,
            'cumulative_benefits': {
                'time_saving': total_time_saving,
                'quality_improvement': total_quality_impact
            },
            'most_used_strategy': max(strategy_counts.items(), key=lambda x: x[1])[0] if strategy_counts else None,
            'effectiveness_score': min(1.0, avg_confidence * 0.6 + (total_time_saving + total_quality_impact) * 0.4)
        }
    
    def decide_next_action_with_intelligence(
        self,
        user_input: str,
        current_state: Dict[str, Any],
        memories: List[MemoryFragment],
        project_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """智能决策下一步行动"""
        
        # 1. 分析用户意图（增强版）
        intent_analysis = self._analyze_user_intent_enhanced(user_input, current_state, memories)
        
        # 2. 上下文感知决策
        context_aware_decision = self._make_context_aware_decision(
            intent_analysis, current_state, memories, project_context or {}
        )
        
        # 3. 生成智能推荐
        intelligent_recommendations = self._generate_intelligent_recommendations(
            context_aware_decision, current_state, memories
        )
        
        # 4. 计算决策置信度
        decision_confidence = self._calculate_decision_confidence(
            intent_analysis, context_aware_decision, memories
        )
        
        # 5. 生成推理链
        reasoning_chain = self._generate_decision_reasoning_chain(
            intent_analysis, context_aware_decision, memories
        )
        
        return {
            'primary_action': context_aware_decision['primary_action'],
            'alternative_actions': intelligent_recommendations,
            'confidence': decision_confidence,
            'reasoning_chain': reasoning_chain,
            'intent_analysis': intent_analysis,
            'context_factors': context_aware_decision['context_factors'],
            'risk_assessment': context_aware_decision['risk_assessment']
        }
    
    def _analyze_user_intent_enhanced(
        self,
        user_input: str,
        current_state: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """增强的用户意图分析"""
        
        text = user_input.lower()
        
        # 基础意图分类
        intent_keywords = {
            'start_project': ['开始', '启动', '新建', 'start', 'begin', 'create', '创建'],
            'continue_work': ['继续', '下一步', 'continue', 'next', '进行', '接下来'],
            'check_status': ['状态', '进度', '如何', 'status', 'progress', 'how', '查看'],
            'fix_issue': ['问题', '错误', '修复', 'issue', 'error', 'fix', 'bug', '解决'],
            'optimize': ['优化', '改进', '提升', 'optimize', 'improve', 'enhance', '加速'],
            'complete_stage': ['完成', '结束', 'complete', 'finish', 'done', '结束'],
            'review': ['审查', '检查', '评估', 'review', 'check', 'evaluate', '验证'],
            'test': ['测试', 'test', '验证', 'verify', '检验'],
            'deploy': ['部署', 'deploy', '发布', 'release', '上线']
        }
        
        detected_intents = []
        intent_scores = {}
        
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                detected_intents.append(intent)
                intent_scores[intent] = score
        
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0] if intent_scores else 'general_query'
        
        # 情感分析
        urgency_keywords = ['紧急', '急', 'urgent', 'asap', '马上', '立即']
        uncertainty_keywords = ['不确定', '不知道', 'unsure', 'confused', '困惑']
        confidence_keywords = ['确定', '明确', 'sure', 'certain', '清楚']
        
        emotional_context = {
            'urgency': any(keyword in text for keyword in urgency_keywords),
            'uncertainty': any(keyword in text for keyword in uncertainty_keywords),
            'confidence': any(keyword in text for keyword in confidence_keywords)
        }
        
        # 基于历史记忆的意图增强
        relevant_memories = self._find_relevant_memories_for_intent(user_input, memories)
        
        return {
            'primary_intent': primary_intent,
            'all_intents': detected_intents,
            'intent_scores': intent_scores,
            'emotional_context': emotional_context,
            'confidence': len(detected_intents) / max(1, len(intent_keywords)) * 0.8 + 0.2,
            'user_input': user_input,
            'relevant_memories': relevant_memories
        }
    
    def _make_context_aware_decision(
        self,
        intent_analysis: Dict[str, Any],
        current_state: Dict[str, Any],
        memories: List[MemoryFragment],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """上下文感知决策"""
        
        primary_intent = intent_analysis['primary_intent']
        current_stage = current_state.get('current_stage', 'S1')
        project_progress = current_state.get('task_progress', 0.0)
        
        # 上下文因素分析
        context_factors = {
            'stage_appropriateness': self._assess_stage_appropriateness(primary_intent, current_stage),
            'progress_alignment': self._assess_progress_alignment(primary_intent, project_progress),
            'resource_availability': self._assess_resource_availability(current_state),
            'historical_patterns': self._analyze_historical_patterns(primary_intent, memories),
            'project_constraints': self._analyze_project_constraints(project_context)
        }
        
        # 风险评估
        risk_assessment = {
            'time_risk': self._assess_time_risk(intent_analysis, current_state),
            'quality_risk': self._assess_quality_risk(intent_analysis, memories),
            'complexity_risk': self._assess_complexity_risk(intent_analysis, project_context),
            'dependency_risk': self._assess_dependency_risk(current_state, memories)
        }
        
        # 基于上下文生成主要行动
        primary_action = self._generate_context_aware_action(
            intent_analysis, context_factors, risk_assessment, current_state
        )
        
        return {
            'primary_action': primary_action,
            'context_factors': context_factors,
            'risk_assessment': risk_assessment,
            'decision_rationale': self._generate_decision_rationale(
                intent_analysis, context_factors, risk_assessment
            )
        }
    
    def _generate_intelligent_recommendations(
        self,
        context_decision: Dict[str, Any],
        current_state: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> List[NextAction]:
        """生成智能推荐"""
        
        recommendations = []
        primary_action = context_decision['primary_action']
        risk_assessment = context_decision['risk_assessment']
        
        # 基于风险的替代方案
        if risk_assessment['time_risk'] > 0.7:
            recommendations.append(NextAction(
                action_type=ActionType.OPTIMIZE,
                description="启用时间优化模式",
                command="aceflow optimize --focus time",
                confidence=0.8,
                estimated_time="立即生效"
            ))
        
        if risk_assessment['quality_risk'] > 0.7:
            recommendations.append(NextAction(
                action_type=ActionType.CONTINUE,
                description="增加质量检查步骤",
                command="aceflow quality-check --comprehensive",
                confidence=0.85,
                estimated_time="30分钟-1小时"
            ))
        
        # 基于历史成功模式的推荐
        successful_patterns = [m for m in memories if m.category == MemoryCategory.PATTERN and m.importance > 0.7]
        if successful_patterns:
            recommendations.append(NextAction(
                action_type=ActionType.CONTINUE,
                description="应用历史成功模式",
                command="aceflow apply-pattern --auto",
                confidence=0.75,
                estimated_time="根据模式而定"
            ))
        
        # 智能并行执行建议
        if current_state.get('task_progress', 0) < 0.8:
            recommendations.append(NextAction(
                action_type=ActionType.PARALLEL,
                description="智能并行任务执行",
                command="aceflow parallel --smart",
                confidence=0.7,
                estimated_time="节省20-40%时间"
            ))
        
        return recommendations
    
    def _calculate_decision_confidence(
        self,
        intent_analysis: Dict[str, Any],
        context_decision: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> float:
        """计算决策置信度"""
        
        factors = {
            'intent_clarity': intent_analysis['confidence'],
            'context_alignment': self._calculate_context_alignment(context_decision['context_factors']),
            'risk_manageability': 1.0 - max(context_decision['risk_assessment'].values()),
            'historical_support': self._calculate_historical_support(intent_analysis, memories),
            'action_feasibility': self._assess_action_feasibility(context_decision['primary_action'])
        }
        
        weights = {
            'intent_clarity': 0.25,
            'context_alignment': 0.25,
            'risk_manageability': 0.2,
            'historical_support': 0.15,
            'action_feasibility': 0.15
        }
        
        confidence = sum(factors[key] * weights[key] for key in factors.keys())
        return min(1.0, max(0.3, confidence))
    
    def _generate_decision_reasoning_chain(
        self,
        intent_analysis: Dict[str, Any],
        context_decision: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> List[ReasoningStep]:
        """生成决策推理链"""
        
        reasoning_chain = []
        
        # 步骤1：意图识别
        reasoning_chain.append(ReasoningStep(
            step_id="intent_recognition",
            description="识别用户意图",
            input_factors=[intent_analysis['user_input']],
            logic=f"基于关键词分析识别主要意图: {intent_analysis['primary_intent']}",
            output=f"用户意图: {intent_analysis['primary_intent']} (置信度: {intent_analysis['confidence']:.2f})",
            confidence=intent_analysis['confidence']
        ))
        
        # 步骤2：上下文分析
        context_factors = context_decision['context_factors']
        reasoning_chain.append(ReasoningStep(
            step_id="context_analysis",
            description="分析项目上下文",
            input_factors=list(context_factors.keys()),
            logic="评估当前项目状态、进度和约束条件",
            output=f"上下文评估完成，关键因素: {', '.join([k for k, v in context_factors.items() if v > 0.6])}",
            confidence=0.85
        ))
        
        # 步骤3：风险评估
        risk_assessment = context_decision['risk_assessment']
        high_risks = [k for k, v in risk_assessment.items() if v > 0.6]
        reasoning_chain.append(ReasoningStep(
            step_id="risk_assessment",
            description="评估执行风险",
            input_factors=list(risk_assessment.keys()),
            logic="分析时间、质量、复杂度和依赖风险",
            output=f"风险评估: {'高风险因素: ' + ', '.join(high_risks) if high_risks else '风险可控'}",
            confidence=0.8
        ))
        
        # 步骤4：行动决策
        primary_action = context_decision['primary_action']
        reasoning_chain.append(ReasoningStep(
            step_id="action_decision",
            description="制定行动方案",
            input_factors=["意图分析", "上下文评估", "风险评估"],
            logic="综合考虑用户意图、项目状态和风险因素",
            output=f"推荐行动: {primary_action.description}",
            confidence=primary_action.confidence
        ))
        
        return reasoning_chain
    
    def _find_relevant_memories_for_intent(
        self,
        user_input: str,
        memories: List[MemoryFragment]
    ) -> List[MemoryFragment]:
        """为意图查找相关记忆"""
        
        relevant_memories = []
        input_keywords = user_input.lower().split()
        
        for memory in memories:
            # 计算关键词重叠度
            memory_keywords = memory.content.lower().split()
            overlap = len(set(input_keywords) & set(memory_keywords))
            
            if overlap > 0 or memory.importance > 0.8:
                relevant_memories.append(memory)
        
        # 按重要性和相关性排序
        relevant_memories.sort(key=lambda m: (m.importance, len(set(input_keywords) & set(m.content.lower().split()))), reverse=True)
        
        return relevant_memories[:5]  # 返回最相关的5个记忆
    
    def _assess_stage_appropriateness(self, intent: str, current_stage: str) -> float:
        """评估意图与当前阶段的适配性"""
        
        stage_intent_mapping = {
            'S1': ['start_project', 'check_status', 'continue_work'],
            'S2': ['continue_work', 'review', 'optimize'],
            'S3': ['continue_work', 'test', 'review'],
            'S4': ['continue_work', 'test', 'fix_issue'],
            'S5': ['test', 'fix_issue', 'review'],
            'S6': ['complete_stage', 'deploy', 'review']
        }
        
        appropriate_intents = stage_intent_mapping.get(current_stage, [])
        return 0.9 if intent in appropriate_intents else 0.3
    
    def _assess_progress_alignment(self, intent: str, progress: float) -> float:
        """评估意图与项目进度的对齐性"""
        
        if intent == 'start_project' and progress < 0.1:
            return 0.9
        elif intent == 'continue_work' and 0.1 <= progress <= 0.9:
            return 0.8
        elif intent == 'complete_stage' and progress > 0.8:
            return 0.9
        elif intent == 'fix_issue':
            return 0.7  # 任何阶段都可能需要修复问题
        else:
            return 0.5
    
    def _assess_resource_availability(self, current_state: Dict[str, Any]) -> float:
        """评估资源可用性"""
        
        available_time = current_state.get('available_dev_time', 0.8)
        team_capacity = current_state.get('team_capacity', 0.8)
        
        return (available_time + team_capacity) / 2.0
    
    def _analyze_historical_patterns(self, intent: str, memories: List[MemoryFragment]) -> float:
        """分析历史模式"""
        
        pattern_memories = [m for m in memories if m.category == MemoryCategory.PATTERN]
        relevant_patterns = [m for m in pattern_memories if intent.lower() in m.content.lower()]
        
        if not pattern_memories:
            return 0.5
        
        return len(relevant_patterns) / len(pattern_memories)
    
    def _analyze_project_constraints(self, project_context: Dict[str, Any]) -> float:
        """分析项目约束"""
        
        constraints = project_context.get('constraints', {})
        
        # 时间约束
        time_pressure = constraints.get('time_pressure', 0.5)
        # 质量要求
        quality_requirement = constraints.get('quality_requirement', 0.5)
        # 资源限制
        resource_limitation = constraints.get('resource_limitation', 0.5)
        
        # 约束越多，灵活性越低
        constraint_score = 1.0 - (time_pressure + quality_requirement + resource_limitation) / 3.0
        return max(0.1, constraint_score)
    
    def _assess_time_risk(self, intent_analysis: Dict[str, Any], current_state: Dict[str, Any]) -> float:
        """评估时间风险"""
        
        urgency = intent_analysis['emotional_context']['urgency']
        deadline_pressure = current_state.get('deadline_pressure', False)
        progress = current_state.get('task_progress', 0.0)
        elapsed_ratio = current_state.get('elapsed_time_ratio', 0.5)
        
        risk_factors = [
            0.3 if urgency else 0.0,
            0.3 if deadline_pressure else 0.0,
            0.2 if elapsed_ratio > progress else 0.0,
            0.2 if progress < 0.3 and elapsed_ratio > 0.5 else 0.0
        ]
        
        return sum(risk_factors)
    
    def _assess_quality_risk(self, intent_analysis: Dict[str, Any], memories: List[MemoryFragment]) -> float:
        """评估质量风险"""
        
        issue_memories = [m for m in memories if m.category == MemoryCategory.ISSUE]
        recent_issues = len([m for m in issue_memories if is_recent(m.created_at, hours=7*24)])
        
        risk_score = 0.0
        
        # 最近问题数量
        if recent_issues > 3:
            risk_score += 0.4
        elif recent_issues > 1:
            risk_score += 0.2
        
        # 用户表达的不确定性
        if intent_analysis['emotional_context']['uncertainty']:
            risk_score += 0.3
        
        # 历史问题密度
        if len(issue_memories) > len(memories) * 0.3:
            risk_score += 0.3
        
        return min(1.0, risk_score)
    
    def _assess_complexity_risk(self, intent_analysis: Dict[str, Any], project_context: Dict[str, Any]) -> float:
        """评估复杂度风险"""
        
        project_complexity = project_context.get('complexity', 'medium')
        team_experience = project_context.get('team_experience', 'medium')
        
        complexity_scores = {'low': 0.2, 'medium': 0.5, 'high': 0.8}
        experience_scores = {'junior': 0.8, 'medium': 0.5, 'senior': 0.2}
        
        complexity_risk = complexity_scores.get(project_complexity, 0.5)
        experience_risk = experience_scores.get(team_experience, 0.5)
        
        return (complexity_risk + experience_risk) / 2.0
    
    def _assess_dependency_risk(self, current_state: Dict[str, Any], memories: List[MemoryFragment]) -> float:
        """评估依赖风险"""
        
        pending_tasks = current_state.get('pending_tasks', [])
        blocked_tasks = current_state.get('blocked_tasks', [])
        
        dependency_memories = [m for m in memories if 'depend' in m.content.lower() or '依赖' in m.content]
        
        risk_score = 0.0
        
        if len(pending_tasks) > 5:
            risk_score += 0.3
        if len(blocked_tasks) > 0:
            risk_score += 0.4
        if len(dependency_memories) > 3:
            risk_score += 0.3
        
        return min(1.0, risk_score)
    
    def _generate_context_aware_action(
        self,
        intent_analysis: Dict[str, Any],
        context_factors: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        current_state: Dict[str, Any]
    ) -> NextAction:
        """生成上下文感知的行动"""
        
        primary_intent = intent_analysis['primary_intent']
        high_risk_areas = [k for k, v in risk_assessment.items() if v > 0.7]
        
        # 基于意图和风险调整行动
        if primary_intent == 'fix_issue' or 'quality_risk' in high_risk_areas:
            return NextAction(
                action_type=ActionType.OPTIMIZE,
                description="优先解决质量问题",
                command="aceflow fix --priority high",
                confidence=0.85,
                estimated_time="1-3小时"
            )
        
        elif primary_intent == 'optimize' or 'time_risk' in high_risk_areas:
            return NextAction(
                action_type=ActionType.OPTIMIZE,
                description="启用时间优化模式",
                command="aceflow optimize --time-critical",
                confidence=0.8,
                estimated_time="立即生效"
            )
        
        elif primary_intent == 'continue_work':
            if context_factors['stage_appropriateness'] > 0.7:
                return NextAction(
                    action_type=ActionType.CONTINUE,
                    description="继续当前阶段工作",
                    command="aceflow continue --smart",
                    confidence=0.8,
                    estimated_time="2-4小时"
                )
            else:
                return NextAction(
                    action_type=ActionType.CONTINUE,
                    description="调整工作流程后继续",
                    command="aceflow adjust-and-continue",
                    confidence=0.7,
                    estimated_time="30分钟调整 + 2-4小时工作"
                )
        
        else:
            # 默认行动
            return NextAction(
                action_type=ActionType.CONTINUE,
                description="基于当前状态继续工作",
                command="aceflow status && aceflow continue",
                confidence=0.6,
                estimated_time="根据具体情况而定"
            )
    
    def _generate_decision_rationale(
        self,
        intent_analysis: Dict[str, Any],
        context_factors: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> str:
        """生成决策理由"""
        
        rationale_parts = []
        
        # 意图相关理由
        rationale_parts.append(f"用户意图: {intent_analysis['primary_intent']}")
        
        # 上下文相关理由
        high_context_factors = [k for k, v in context_factors.items() if v > 0.7]
        if high_context_factors:
            rationale_parts.append(f"有利因素: {', '.join(high_context_factors)}")
        
        # 风险相关理由
        high_risks = [k for k, v in risk_assessment.items() if v > 0.7]
        if high_risks:
            rationale_parts.append(f"需要关注的风险: {', '.join(high_risks)}")
        
        # 情感上下文
        emotional_context = intent_analysis['emotional_context']
        if emotional_context['urgency']:
            rationale_parts.append("检测到紧急需求")
        if emotional_context['uncertainty']:
            rationale_parts.append("用户表达了不确定性")
        
        return "; ".join(rationale_parts)
    
    def _calculate_context_alignment(self, context_factors: Dict[str, Any]) -> float:
        """计算上下文对齐度"""
        return sum(context_factors.values()) / len(context_factors)
    
    def _calculate_historical_support(self, intent_analysis: Dict[str, Any], memories: List[MemoryFragment]) -> float:
        """计算历史支持度"""
        relevant_memories = intent_analysis['relevant_memories']
        if not memories:
            return 0.5
        
        support_score = len(relevant_memories) / min(len(memories), 10)  # 最多考虑10个记忆
        return min(1.0, support_score)
    
    def _assess_action_feasibility(self, action: NextAction) -> float:
        """评估行动可行性"""
        # 基于行动类型和置信度评估可行性
        feasibility_scores = {
            ActionType.CONTINUE: 0.8,
            ActionType.OPTIMIZE: 0.7,
            ActionType.PARALLEL: 0.6,
            ActionType.SKIP: 0.5,
            ActionType.ESCALATE: 0.9
        }
        
        base_feasibility = feasibility_scores.get(action.action_type, 0.6)
        confidence_adjustment = action.confidence * 0.3
        
        return min(1.0, base_feasibility + confidence_adjustment)
    
    def decide_next_action_with_intelligence(
        self,
        user_input: str,
        current_state: Dict[str, Any],
        memories: List[MemoryFragment],
        project_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """智能决策下一步行动"""
        
        # 1. 分析用户意图（增强版）
        intent_analysis = self._analyze_user_intent_enhanced(user_input, current_state, memories)
        
        # 2. 上下文感知决策
        context_aware_decision = self._make_context_aware_decision(
            intent_analysis, current_state, memories, project_context or {}
        )
        
        # 3. 生成智能推荐
        intelligent_recommendations = self._generate_intelligent_recommendations(
            context_aware_decision, current_state, memories
        )
        
        # 4. 计算决策置信度
        decision_confidence = self._calculate_decision_confidence(
            intent_analysis, context_aware_decision, memories
        )
        
        # 5. 生成推理链
        reasoning_chain = self._generate_decision_reasoning_chain(
            intent_analysis, context_aware_decision, memories
        )
        
        return {
            'primary_action': context_aware_decision['primary_action'],
            'alternative_actions': intelligent_recommendations,
            'confidence': decision_confidence,
            'reasoning_chain': reasoning_chain,
            'intent_analysis': intent_analysis,
            'context_factors': context_aware_decision['context_factors'],
            'risk_assessment': context_aware_decision['risk_assessment'],
            'success_probability': context_aware_decision['success_probability']
        }
    
    def _analyze_user_intent_enhanced(
        self,
        user_input: str,
        current_state: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """增强的用户意图分析"""
        
        text = user_input.lower()
        
        # 基础意图分类
        intent_keywords = {
            'start_project': ['开始', '启动', '新建', 'start', 'begin', 'create', '创建'],
            'continue_work': ['继续', '下一步', 'continue', 'next', '进行', '执行'],
            'check_status': ['状态', '进度', '如何', 'status', 'progress', 'how', '查看'],
            'fix_issue': ['问题', '错误', '修复', 'issue', 'error', 'fix', 'bug', '解决'],
            'optimize': ['优化', '改进', '提升', 'optimize', 'improve', 'enhance', '加速'],
            'complete_stage': ['完成', '结束', 'complete', 'finish', 'done', '结束'],
            'review': ['审查', '检查', '评估', 'review', 'check', 'evaluate', '验证'],
            'plan': ['计划', '安排', '规划', 'plan', 'schedule', '设计']
        }
        
        # 检测意图
        detected_intents = []
        intent_scores = {}
        
        for intent, keywords in intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            if score > 0:
                detected_intents.append(intent)
                intent_scores[intent] = score / len(keywords)
        
        # 确定主要意图
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0] if intent_scores else 'general_query'
        
        # 上下文增强
        context_enhancement = self._enhance_intent_with_context(
            primary_intent, current_state, memories
        )
        
        # 情感分析
        sentiment = self._analyze_sentiment(user_input)
        
        # 紧急程度分析
        urgency = self._detect_urgency_enhanced(user_input, current_state)
        
        return {
            'primary_intent': primary_intent,
            'all_intents': detected_intents,
            'intent_scores': intent_scores,
            'confidence': max(intent_scores.values()) if intent_scores else 0.3,
            'context_enhancement': context_enhancement,
            'sentiment': sentiment,
            'urgency': urgency,
            'user_input': user_input
        }
    
    def _enhance_intent_with_context(
        self,
        primary_intent: str,
        current_state: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """基于上下文增强意图理解"""
        
        enhancement = {
            'stage_relevance': 0.5,
            'historical_pattern': 0.5,
            'suggested_refinement': None
        }
        
        current_stage = current_state.get('current_stage', 'S1')
        
        # 基于当前阶段的相关性
        stage_intent_relevance = {
            'S1': {'start_project': 0.9, 'plan': 0.8, 'check_status': 0.7},
            'S2': {'plan': 0.9, 'review': 0.8, 'continue_work': 0.7},
            'S3': {'continue_work': 0.9, 'fix_issue': 0.8, 'check_status': 0.7},
            'S4': {'continue_work': 0.9, 'fix_issue': 0.8, 'optimize': 0.7},
            'S5': {'review': 0.9, 'complete_stage': 0.8, 'fix_issue': 0.7},
            'S6': {'complete_stage': 0.9, 'review': 0.8, 'optimize': 0.6}
        }
        
        if current_stage in stage_intent_relevance:
            enhancement['stage_relevance'] = stage_intent_relevance[current_stage].get(primary_intent, 0.5)
        
        # 基于历史模式
        recent_memories = [m for m in memories if is_recent(m.created_at, hours=24)]
        if recent_memories:
            recent_actions = [m.content for m in recent_memories if m.category == MemoryCategory.DECISION]
            if recent_actions:
                # 简化的模式检测
                if primary_intent == 'fix_issue' and any('问题' in action or 'issue' in action.lower() for action in recent_actions):
                    enhancement['historical_pattern'] = 0.8
                    enhancement['suggested_refinement'] = '基于最近的问题处理经验，建议优先解决类似问题'
        
        return enhancement
    
    def _analyze_sentiment(self, user_input: str) -> Dict[str, Any]:
        """分析用户情感"""
        text = user_input.lower()
        
        positive_words = ['好', '棒', '优秀', 'good', 'great', 'excellent', '满意', '成功']
        negative_words = ['差', '糟糕', '问题', 'bad', 'terrible', 'issue', 'problem', '失败', '困难']
        urgent_words = ['急', '紧急', 'urgent', 'emergency', '马上', 'immediately', '立即']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        urgent_count = sum(1 for word in urgent_words if word in text)
        
        if urgent_count > 0:
            sentiment = 'urgent'
            polarity = -0.3  # 紧急通常带有负面情绪
        elif positive_count > negative_count:
            sentiment = 'positive'
            polarity = 0.5
        elif negative_count > positive_count:
            sentiment = 'negative'
            polarity = -0.5
        else:
            sentiment = 'neutral'
            polarity = 0.0
        
        return {
            'sentiment': sentiment,
            'polarity': polarity,
            'confidence': max(positive_count, negative_count, urgent_count) / max(1, len(text.split()))
        }
    
    def _detect_urgency_enhanced(self, user_input: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """增强的紧急程度检测"""
        text = user_input.lower()
        
        urgency_indicators = {
            'emergency': ['紧急', '立即', '马上', 'urgent', 'emergency', 'critical', '故障', '线上'],
            'high': ['重要', '优先', 'important', 'priority', '尽快', 'asap', '今天'],
            'medium': ['需要', '应该', 'need', 'should', '计划', '安排'],
            'low': ['可以', '建议', 'can', 'suggest', '有空', '方便']
        }
        
        detected_level = 'normal'
        max_score = 0
        
        for level, keywords in urgency_indicators.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > max_score:
                max_score = score
                detected_level = level
        
        # 基于项目状态调整紧急程度
        project_urgency = current_state.get('urgency_level', 'normal')
        if project_urgency == 'high' and detected_level in ['medium', 'low']:
            detected_level = 'high'
        
        return {
            'level': detected_level,
            'score': max_score,
            'project_context_adjusted': project_urgency != 'normal'
        }
    
    def _make_context_aware_decision(
        self,
        intent_analysis: Dict[str, Any],
        current_state: Dict[str, Any],
        memories: List[MemoryFragment],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """基于上下文的智能决策"""
        
        primary_intent = intent_analysis['primary_intent']
        urgency = intent_analysis['urgency']['level']
        sentiment = intent_analysis['sentiment']['sentiment']
        
        # 基础行动推荐
        base_action = self._get_base_action_for_intent(primary_intent, current_state)
        
        # 上下文调整
        context_factors = self._analyze_context_factors(current_state, memories, project_context)
        
        # 风险评估
        risk_assessment = self._assess_decision_risks(base_action, context_factors, memories)
        
        # 成功概率计算
        success_probability = self._calculate_success_probability(
            base_action, context_factors, risk_assessment, memories
        )
        
        # 基于上下文调整行动
        adjusted_action = self._adjust_action_based_on_context(
            base_action, context_factors, urgency, sentiment
        )
        
        return {
            'primary_action': adjusted_action,
            'context_factors': context_factors,
            'risk_assessment': risk_assessment,
            'success_probability': success_probability,
            'adjustment_reasoning': self._explain_action_adjustment(base_action, adjusted_action, context_factors)
        }
    
    def _get_base_action_for_intent(self, intent: str, current_state: Dict[str, Any]) -> NextAction:
        """根据意图获取基础行动"""
        
        current_stage = current_state.get('current_stage', 'S1')
        
        action_mapping = {
            'start_project': NextAction(
                action_type=ActionType.CONTINUE,
                description="开始项目分析和需求收集",
                command="aceflow start --mode smart",
                confidence=0.9,
                estimated_time="2-4小时"
            ),
            'continue_work': NextAction(
                action_type=ActionType.CONTINUE,
                description=f"继续执行当前阶段 {current_stage}",
                command=f"aceflow run {current_stage}",
                confidence=0.85,
                estimated_time="1-3小时"
            ),
            'check_status': NextAction(
                action_type=ActionType.CONTINUE,
                description="查看项目状态和进度",
                command="aceflow status --verbose",
                confidence=0.95,
                estimated_time="5分钟"
            ),
            'fix_issue': NextAction(
                action_type=ActionType.OPTIMIZE,
                description="分析和修复当前问题",
                command="aceflow analyze --focus issues",
                confidence=0.8,
                estimated_time="30分钟-2小时"
            ),
            'optimize': NextAction(
                action_type=ActionType.OPTIMIZE,
                description="优化当前工作流程",
                command="aceflow optimize --current-stage",
                confidence=0.75,
                estimated_time="1-2小时"
            ),
            'complete_stage': NextAction(
                action_type=ActionType.CONTINUE,
                description=f"完成当前阶段 {current_stage}",
                command=f"aceflow complete {current_stage}",
                confidence=0.8,
                estimated_time="30分钟-1小时"
            ),
            'review': NextAction(
                action_type=ActionType.CONTINUE,
                description="执行质量审查",
                command="aceflow review --comprehensive",
                confidence=0.85,
                estimated_time="1-2小时"
            ),
            'plan': NextAction(
                action_type=ActionType.CONTINUE,
                description="制定详细计划",
                command="aceflow plan --detailed",
                confidence=0.8,
                estimated_time="1-3小时"
            )
        }
        
        return action_mapping.get(intent, NextAction(
            action_type=ActionType.CONTINUE,
            description="继续当前工作流程",
            command="aceflow status",
            confidence=0.6,
            estimated_time="未知"
        ))
    
    def _analyze_context_factors(
        self,
        current_state: Dict[str, Any],
        memories: List[MemoryFragment],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析上下文因素"""
        
        return {
            'project_progress': current_state.get('task_progress', 0.0),
            'current_stage': current_state.get('current_stage', 'S1'),
            'team_capacity': current_state.get('team_capacity', 0.8),
            'time_pressure': current_state.get('deadline_pressure', False),
            'recent_issues': len([m for m in memories if m.category == MemoryCategory.ISSUE and is_recent(m.created_at, hours=24)]),
            'recent_decisions': len([m for m in memories if m.category == MemoryCategory.DECISION and is_recent(m.created_at, hours=24)]),
            'learning_momentum': len([m for m in memories if m.category == MemoryCategory.LEARNING and is_recent(m.created_at, hours=48)]),
            'project_complexity': project_context.get('complexity', 'medium'),
            'team_experience': project_context.get('team_experience', 'medium')
        }
    
    def _assess_decision_risks(
        self,
        action: NextAction,
        context_factors: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """评估决策风险"""
        
        risks = []
        risk_score = 0.0
        
        # 基于行动类型的风险
        if action.action_type == ActionType.SKIP:
            risks.append("跳过阶段可能遗漏重要问题")
            risk_score += 0.3
        elif action.action_type == ActionType.PARALLEL:
            risks.append("并行执行可能增加协调复杂度")
            risk_score += 0.2
        
        # 基于上下文的风险
        if context_factors['time_pressure'] and action.estimated_time and '小时' in action.estimated_time:
            risks.append("时间压力下执行长时间任务风险较高")
            risk_score += 0.2
        
        if context_factors['recent_issues'] > 2:
            risks.append("最近问题频发，新行动可能遇到类似问题")
            risk_score += 0.15
        
        if context_factors['team_capacity'] < 0.7:
            risks.append("团队容量不足可能影响执行效果")
            risk_score += 0.1
        
        return {
            'risks': risks,
            'risk_score': min(1.0, risk_score),
            'risk_level': 'high' if risk_score > 0.6 else 'medium' if risk_score > 0.3 else 'low'
        }
    
    def _calculate_success_probability(
        self,
        action: NextAction,
        context_factors: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> float:
        """计算成功概率"""
        
        base_probability = action.confidence
        
        # 基于上下文调整
        if context_factors['project_progress'] > 0.7:
            base_probability += 0.1  # 项目后期经验积累
        
        if context_factors['learning_momentum'] > 2:
            base_probability += 0.05  # 学习势头良好
        
        if context_factors['recent_decisions'] > 3:
            base_probability += 0.05  # 决策活跃
        
        # 基于风险调整
        base_probability -= risk_assessment['risk_score'] * 0.2
        
        # 基于历史成功率调整
        similar_actions = [m for m in memories if action.action_type.value in m.content.lower()]
        if similar_actions:
            success_actions = [m for m in similar_actions if '成功' in m.content or 'success' in m.content.lower()]
            historical_success_rate = len(success_actions) / len(similar_actions)
            base_probability = base_probability * 0.7 + historical_success_rate * 0.3
        
        return max(0.1, min(0.95, base_probability))
    
    def _adjust_action_based_on_context(
        self,
        base_action: NextAction,
        context_factors: Dict[str, Any],
        urgency: str,
        sentiment: str
    ) -> NextAction:
        """基于上下文调整行动"""
        
        adjusted_action = NextAction(
            action_type=base_action.action_type,
            description=base_action.description,
            command=base_action.command,
            confidence=base_action.confidence,
            estimated_time=base_action.estimated_time
        )
        
        # 基于紧急程度调整
        if urgency == 'emergency':
            adjusted_action.description = f"[紧急] {adjusted_action.description}"
            adjusted_action.command = adjusted_action.command.replace('--mode smart', '--mode minimal')
            adjusted_action.estimated_time = "尽快完成"
        elif urgency == 'high':
            adjusted_action.description = f"[高优先级] {adjusted_action.description}"
        
        # 基于情感调整
        if sentiment == 'negative':
            adjusted_action.description = f"{adjusted_action.description}，并提供详细反馈"
            adjusted_action.command += " --verbose"
        
        # 基于上下文因素调整
        if context_factors['time_pressure']:
            if 'optimize' in adjusted_action.command:
                adjusted_action.command += " --quick"
                adjusted_action.estimated_time = "30分钟-1小时"
        
        if context_factors['recent_issues'] > 2:
            adjusted_action.description += "，注意问题预防"
            adjusted_action.command += " --careful"
        
        return adjusted_action
    
    def _explain_action_adjustment(
        self,
        base_action: NextAction,
        adjusted_action: NextAction,
        context_factors: Dict[str, Any]
    ) -> str:
        """解释行动调整的原因"""
        
        if base_action.description == adjusted_action.description:
            return "无需调整，基础行动适合当前上下文"
        
        reasons = []
        
        if "[紧急]" in adjusted_action.description:
            reasons.append("检测到紧急情况，优先处理")
        
        if "[高优先级]" in adjusted_action.description:
            reasons.append("识别为高优先级任务")
        
        if "详细反馈" in adjusted_action.description:
            reasons.append("考虑到用户情绪，提供更多支持")
        
        if context_factors['time_pressure']:
            reasons.append("考虑时间压力，采用快速模式")
        
        if context_factors['recent_issues'] > 2:
            reasons.append("基于最近问题频发，增加谨慎措施")
        
        return "; ".join(reasons) if reasons else "基于上下文进行了优化调整"
    
    def _generate_intelligent_recommendations(
        self,
        context_decision: Dict[str, Any],
        current_state: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> List[NextAction]:
        """生成智能推荐"""
        
        recommendations = []
        primary_action = context_decision['primary_action']
        context_factors = context_decision['context_factors']
        
        # 基于主要行动生成替代方案
        if primary_action.action_type == ActionType.CONTINUE:
            # 提供并行执行选项
            recommendations.append(NextAction(
                action_type=ActionType.PARALLEL,
                description="并行执行多个任务以提高效率",
                command=primary_action.command.replace('run', 'run --parallel'),
                confidence=0.7,
                estimated_time="节省20-30%时间"
            ))
            
            # 提供优化选项
            recommendations.append(NextAction(
                action_type=ActionType.OPTIMIZE,
                description="先优化当前流程再继续",
                command="aceflow optimize --before-continue",
                confidence=0.6,
                estimated_time="额外30分钟，长期节省时间"
            ))
        
        elif primary_action.action_type == ActionType.OPTIMIZE:
            # 提供快速修复选项
            recommendations.append(NextAction(
                action_type=ActionType.CONTINUE,
                description="快速修复后继续",
                command=primary_action.command.replace('analyze', 'quick-fix'),
                confidence=0.75,
                estimated_time="15-30分钟"
            ))
            
            # 提供深度分析选项
            recommendations.append(NextAction(
                action_type=ActionType.OPTIMIZE,
                description="深度分析根本原因",
                command=primary_action.command + " --deep",
                confidence=0.8,
                estimated_time="1-3小时"
            ))
        
        # 基于上下文因素添加特定推荐
        if context_factors['time_pressure']:
            recommendations.append(NextAction(
                action_type=ActionType.SKIP,
                description="跳过非关键步骤以节省时间",
                command="aceflow skip --non-critical",
                confidence=0.6,
                estimated_time="节省1-2小时"
            ))
        
        if context_factors['recent_issues'] > 2:
            recommendations.append(NextAction(
                action_type=ActionType.ESCALATE,
                description="请求专家协助解决复杂问题",
                command="aceflow escalate --expert-help",
                confidence=0.8,
                estimated_time="等待专家响应"
            ))
        
        if context_factors['learning_momentum'] > 2:
            recommendations.append(NextAction(
                action_type=ActionType.CONTINUE,
                description="利用学习势头加速执行",
                command=primary_action.command + " --accelerated",
                confidence=0.85,
                estimated_time="比预期快20-30%"
            ))
        
        # 基于历史模式添加推荐
        pattern_memories = [m for m in memories if m.category == MemoryCategory.PATTERN]
        if pattern_memories:
            recommendations.append(NextAction(
                action_type=ActionType.CONTINUE,
                description="应用已识别的成功模式",
                command="aceflow apply-pattern --auto",
                confidence=0.8,
                estimated_time="基于历史经验优化"
            ))
        
        return recommendations[:3]  # 返回最多3个推荐
    
    def _calculate_decision_confidence(
        self,
        intent_analysis: Dict[str, Any],
        context_decision: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> float:
        """计算决策置信度"""
        
        factors = {
            'intent_clarity': intent_analysis['confidence'],
            'context_completeness': self._assess_context_completeness(context_decision['context_factors']),
            'historical_support': self._assess_historical_support(context_decision['primary_action'], memories),
            'risk_level': 1.0 - context_decision['risk_assessment']['risk_score'],
            'success_probability': context_decision['success_probability']
        }
        
        weights = {
            'intent_clarity': 0.25,
            'context_completeness': 0.2,
            'historical_support': 0.2,
            'risk_level': 0.15,
            'success_probability': 0.2
        }
        
        confidence = sum(factors[key] * weights[key] for key in factors.keys())
        return max(0.3, min(0.95, confidence))
    
    def _assess_context_completeness(self, context_factors: Dict[str, Any]) -> float:
        """评估上下文完整性"""
        
        required_factors = ['project_progress', 'current_stage', 'team_capacity', 'project_complexity']
        available_factors = [factor for factor in required_factors if context_factors.get(factor) is not None]
        
        completeness = len(available_factors) / len(required_factors)
        
        # 额外加分项
        if context_factors.get('recent_issues') is not None:
            completeness += 0.1
        if context_factors.get('learning_momentum') is not None:
            completeness += 0.1
        
        return min(1.0, completeness)
    
    def _assess_historical_support(self, action: NextAction, memories: List[MemoryFragment]) -> float:
        """评估历史支持度"""
        
        # 查找类似的历史行动
        similar_memories = []
        action_keywords = action.description.lower().split()
        
        for memory in memories:
            memory_keywords = memory.content.lower().split()
            common_keywords = set(action_keywords) & set(memory_keywords)
            if len(common_keywords) >= 2:  # 至少2个共同关键词
                similar_memories.append(memory)
        
        if not similar_memories:
            return 0.5  # 没有历史数据，中等支持度
        
        # 评估历史成功率
        successful_memories = [
            m for m in similar_memories 
            if any(success_word in m.content.lower() for success_word in ['成功', 'success', '完成', 'completed', '解决', 'solved'])
        ]
        
        support_score = len(successful_memories) / len(similar_memories)
        
        # 考虑记忆的重要性
        importance_bonus = sum(m.importance for m in successful_memories) / max(1, len(successful_memories)) * 0.2
        
        return min(1.0, support_score + importance_bonus)
    
    def _generate_decision_reasoning_chain(
        self,
        intent_analysis: Dict[str, Any],
        context_decision: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> List[ReasoningStep]:
        """生成决策推理链"""
        
        reasoning_chain = []
        
        # 步骤1：意图理解
        reasoning_chain.append(ReasoningStep(
            step_id="intent_understanding",
            description="理解用户意图",
            input_factors=[intent_analysis['user_input']],
            logic=f"基于关键词分析和上下文增强，识别主要意图为: {intent_analysis['primary_intent']}",
            output=f"用户意图: {intent_analysis['primary_intent']} (置信度: {intent_analysis['confidence']:.2f})",
            confidence=intent_analysis['confidence']
        ))
        
        # 步骤2：上下文分析
        context_factors = context_decision['context_factors']
        reasoning_chain.append(ReasoningStep(
            step_id="context_analysis",
            description="分析项目上下文",
            input_factors=[
                f"项目进度: {context_factors['project_progress']:.1%}",
                f"当前阶段: {context_factors['current_stage']}",
                f"团队容量: {context_factors['team_capacity']:.1%}"
            ],
            logic="综合分析项目状态、团队情况和历史数据",
            output=f"上下文评估完成，识别关键因素 {len(context_factors)} 个",
            confidence=0.85
        ))
        
        # 步骤3：风险评估
        risk_assessment = context_decision['risk_assessment']
        reasoning_chain.append(ReasoningStep(
            step_id="risk_assessment",
            description="评估决策风险",
            input_factors=[f"识别风险 {len(risk_assessment['risks'])} 个"],
            logic="基于行动类型、上下文因素和历史经验评估风险",
            output=f"风险等级: {risk_assessment['risk_level']} (风险分数: {risk_assessment['risk_score']:.2f})",
            confidence=0.8
        ))
        
        # 步骤4：行动决策
        primary_action = context_decision['primary_action']
        reasoning_chain.append(ReasoningStep(
            step_id="action_decision",
            description="制定行动方案",
            input_factors=["用户意图", "上下文分析", "风险评估"],
            logic="综合考虑意图、上下文和风险，选择最优行动方案",
            output=f"推荐行动: {primary_action.description}",
            confidence=context_decision['success_probability']
        ))
        
        # 步骤5：置信度计算
        overall_confidence = self._calculate_decision_confidence(intent_analysis, context_decision, memories)
        reasoning_chain.append(ReasoningStep(
            step_id="confidence_calculation",
            description="计算决策置信度",
            input_factors=["意图清晰度", "上下文完整性", "历史支持度", "风险水平"],
            logic="基于多个因素的加权计算得出最终置信度",
            output=f"决策置信度: {overall_confidence:.2f}",
            confidence=overall_confidence
        ))
        
        return reasoning_chain