"""
工作流优化算法
实现基于项目状态、历史数据和上下文的智能工作流优化
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .models import MemoryFragment, MemoryCategory
from .utils import is_recent


class OptimizationStrategy(Enum):
    """优化策略枚举"""
    SPEED = "speed"
    QUALITY = "quality"
    BALANCED = "balanced"
    ADAPTIVE = "adaptive"


class WorkflowMode(Enum):
    """工作流模式枚举"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    SMART = "smart"


@dataclass
class OptimizationContext:
    """优化上下文"""
    current_stage: str
    project_progress: float
    time_constraints: Dict[str, Any]
    resource_availability: Dict[str, float]
    quality_requirements: Dict[str, float]
    historical_performance: Dict[str, Any]
    user_preferences: Dict[str, Any] = None


@dataclass
class WorkflowRecommendation:
    """工作流推荐"""
    recommended_mode: WorkflowMode
    optimization_strategy: OptimizationStrategy
    suggested_actions: List[Dict[str, Any]]
    estimated_time_saving: float
    quality_impact: float
    confidence: float
    reasoning: str


class WorkflowOptimizer:
    """工作流优化器"""
    
    def __init__(self):
        self.optimization_algorithms = {
            OptimizationStrategy.SPEED: self._optimize_for_speed,
            OptimizationStrategy.QUALITY: self._optimize_for_quality,
            OptimizationStrategy.BALANCED: self._optimize_balanced,
            OptimizationStrategy.ADAPTIVE: self._optimize_adaptive
        }
    
    def optimize_workflow(
        self,
        context: OptimizationContext,
        current_memories: List[MemoryFragment],
        current_workflow_mode: WorkflowMode = WorkflowMode.STANDARD
    ) -> WorkflowRecommendation:
        """优化工作流"""
        
        # 1. 分析当前状态
        state_analysis = self._analyze_current_state(context, current_memories)
        
        # 2. 确定最佳优化策略
        optimal_strategy = self._determine_optimization_strategy(context, state_analysis)
        
        # 3. 应用优化算法
        optimization_result = self.optimization_algorithms[optimal_strategy](
            context, state_analysis, current_memories
        )
        
        # 4. 生成推荐
        recommendation = self._generate_recommendation(
            optimal_strategy, optimization_result, context, current_workflow_mode
        )
        
        return recommendation
    
    def _analyze_current_state(
        self, 
        context: OptimizationContext, 
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """分析当前状态"""
        
        analysis = {
            'bottlenecks': self._identify_bottlenecks(context, memories),
            'efficiency_metrics': self._calculate_efficiency_metrics(context, memories),
            'risk_factors': self._identify_risk_factors(context, memories),
            'optimization_opportunities': self._identify_optimization_opportunities(memories),
            'quality_indicators': self._analyze_quality_indicators(memories)
        }
        
        return analysis
    
    def _determine_optimization_strategy(
        self, 
        context: OptimizationContext, 
        state_analysis: Dict[str, Any]
    ) -> OptimizationStrategy:
        """确定最佳优化策略"""
        
        # 计算各策略的适用性分数
        strategy_scores = {}
        
        # 速度优先策略评分
        speed_score = 0.0
        if context.time_constraints.get('urgent', False):
            speed_score += 0.4
        if context.project_progress < 0.3:
            speed_score += 0.2
        if len(state_analysis['bottlenecks']) > 2:
            speed_score += 0.3
        strategy_scores[OptimizationStrategy.SPEED] = speed_score
        
        # 质量优先策略评分
        quality_score = 0.0
        if context.quality_requirements.get('high_quality', False):
            quality_score += 0.4
        if context.project_progress > 0.7:
            quality_score += 0.3
        if len(state_analysis['quality_indicators']['issues']) == 0:
            quality_score += 0.2
        strategy_scores[OptimizationStrategy.QUALITY] = quality_score
        
        # 平衡策略评分
        balanced_score = 0.3  # 基础分数
        if 0.3 <= context.project_progress <= 0.7:
            balanced_score += 0.3
        if context.resource_availability.get('development_time', 0.5) > 0.5:
            balanced_score += 0.2
        strategy_scores[OptimizationStrategy.BALANCED] = balanced_score
        
        # 自适应策略评分
        adaptive_score = 0.2  # 基础分数
        if len(state_analysis['optimization_opportunities']) > 3:
            adaptive_score += 0.3
        if state_analysis['efficiency_metrics']['overall_efficiency'] < 0.6:
            adaptive_score += 0.4
        strategy_scores[OptimizationStrategy.ADAPTIVE] = adaptive_score
        
        # 返回得分最高的策略
        return max(strategy_scores.items(), key=lambda x: x[1])[0]
    
    def _optimize_for_speed(self, context, state_analysis, memories) -> Dict[str, Any]:
        """速度优化算法"""
        optimizations = {
            'workflow_mode': WorkflowMode.MINIMAL,
            'skip_stages': [],
            'parallel_tasks': [],
            'automation_opportunities': [],
            'time_saving_estimate': 0.0
        }
        
        # 识别可跳过的阶段
        if context.project_progress > 0.5:
            if context.current_stage in ['S1', 'S2']:
                optimizations['skip_stages'].append('detailed_analysis')
                optimizations['time_saving_estimate'] += 0.2
        
        # 识别并行任务机会
        bottlenecks = state_analysis['bottlenecks']
        if 'sequential_development' in bottlenecks:
            optimizations['parallel_tasks'].extend([
                {'task': 'frontend_development', 'parallel_with': 'backend_api'},
                {'task': 'testing_preparation', 'parallel_with': 'implementation'}
            ])
            optimizations['time_saving_estimate'] += 0.3
        
        # 自动化机会
        if any(m.category == MemoryCategory.PATTERN for m in memories):
            optimizations['automation_opportunities'].extend([
                'automated_testing',
                'code_generation',
                'deployment_automation'
            ])
            optimizations['time_saving_estimate'] += 0.25
        
        return optimizations
    
    def _optimize_for_quality(self, context, state_analysis, memories) -> Dict[str, Any]:
        """质量优化算法"""
        optimizations = {
            'workflow_mode': WorkflowMode.COMPREHENSIVE,
            'additional_stages': [],
            'quality_gates': [],
            'review_processes': [],
            'quality_improvement_estimate': 0.0
        }
        
        # 添加质量保证阶段
        if context.current_stage in ['S3', 'S4']:
            optimizations['additional_stages'].extend([
                'code_review',
                'architecture_review',
                'security_audit'
            ])
            optimizations['quality_improvement_estimate'] += 0.3
        
        # 质量门控
        optimizations['quality_gates'].extend([
            {'stage': 'S2', 'criteria': 'design_completeness > 0.9'},
            {'stage': 'S4', 'criteria': 'code_coverage > 0.8'},
            {'stage': 'S5', 'criteria': 'bug_density < 0.1'}
        ])
        
        # 基于历史问题的审查流程
        issue_memories = [m for m in memories if m.category == MemoryCategory.ISSUE]
        if len(issue_memories) > 3:
            optimizations['review_processes'].extend([
                'peer_review',
                'automated_quality_checks',
                'continuous_integration'
            ])
            optimizations['quality_improvement_estimate'] += 0.2
        
        return optimizations
    
    def _optimize_balanced(self, context, state_analysis, memories) -> Dict[str, Any]:
        """平衡优化算法"""
        optimizations = {
            'workflow_mode': WorkflowMode.STANDARD,
            'balanced_approach': [],
            'selective_optimizations': [],
            'risk_mitigation': [],
            'overall_improvement_estimate': 0.0
        }
        
        # 选择性优化
        efficiency = state_analysis['efficiency_metrics']['overall_efficiency']
        if efficiency < 0.7:
            optimizations['selective_optimizations'].extend([
                'optimize_critical_path',
                'improve_resource_allocation',
                'streamline_communication'
            ])
            optimizations['overall_improvement_estimate'] += 0.2
        
        # 风险缓解
        risk_factors = state_analysis['risk_factors']
        if len(risk_factors) > 1:
            optimizations['risk_mitigation'].extend([
                'add_buffer_time',
                'prepare_contingency_plans',
                'increase_monitoring'
            ])
        
        # 平衡方法
        optimizations['balanced_approach'].extend([
            {'focus': 'speed', 'weight': 0.4},
            {'focus': 'quality', 'weight': 0.4},
            {'focus': 'resource_efficiency', 'weight': 0.2}
        ])
        
        return optimizations
    
    def _optimize_adaptive(self, context, state_analysis, memories) -> Dict[str, Any]:
        """自适应优化算法"""
        optimizations = {
            'workflow_mode': WorkflowMode.SMART,
            'adaptive_rules': [],
            'dynamic_adjustments': [],
            'learning_based_optimizations': [],
            'adaptability_score': 0.0
        }
        
        # 基于历史学习的优化
        learning_memories = [m for m in memories if m.category == MemoryCategory.LEARNING]
        if learning_memories:
            optimizations['learning_based_optimizations'].extend([
                'apply_learned_patterns',
                'avoid_known_pitfalls',
                'leverage_successful_approaches'
            ])
            optimizations['adaptability_score'] += 0.3
        
        # 动态调整规则
        optimizations['adaptive_rules'].extend([
            {
                'condition': 'progress_rate < expected_rate',
                'action': 'switch_to_speed_mode',
                'threshold': 0.8
            },
            {
                'condition': 'quality_issues_detected',
                'action': 'increase_quality_checks',
                'threshold': 2
            },
            {
                'condition': 'resource_constraints_detected',
                'action': 'optimize_resource_allocation',
                'threshold': 0.7
            }
        ])
        
        # 动态调整机制
        optimizations['dynamic_adjustments'].extend([
            'real_time_progress_monitoring',
            'automatic_workflow_switching',
            'predictive_bottleneck_detection'
        ])
        optimizations['adaptability_score'] += 0.4
        
        return optimizations
    
    def _identify_bottlenecks(self, context, memories) -> List[str]:
        """识别瓶颈"""
        bottlenecks = []
        
        # 基于进度分析
        if context.project_progress < 0.3 and context.current_stage > 'S2':
            bottlenecks.append('slow_initial_progress')
        
        # 基于资源可用性
        if context.resource_availability.get('development_time', 1.0) < 0.5:
            bottlenecks.append('limited_development_time')
        
        # 基于历史问题
        issue_memories = [m for m in memories if m.category == MemoryCategory.ISSUE]
        if len(issue_memories) > 3:
            bottlenecks.append('recurring_issues')
        
        # 基于决策延迟
        decision_memories = [m for m in memories if m.category == MemoryCategory.DECISION]
        recent_decisions = [m for m in decision_memories if is_recent(m.created_at, hours=7*24)]
        if len(recent_decisions) < 2 and context.current_stage in ['S1', 'S2']:
            bottlenecks.append('decision_delays')
        
        return bottlenecks
    
    def _calculate_efficiency_metrics(self, context, memories) -> Dict[str, float]:
        """计算效率指标"""
        # 基于进度和时间的效率计算
        time_efficiency = context.project_progress / max(0.1, context.time_constraints.get('elapsed_ratio', 0.5))
        
        # 基于记忆质量的效率
        high_importance_memories = [m for m in memories if m.importance > 0.7]
        memory_efficiency = len(high_importance_memories) / max(1, len(memories))
        
        # 基于问题解决的效率
        issue_memories = [m for m in memories if m.category == MemoryCategory.ISSUE]
        resolved_issues = len([m for m in issue_memories if 'resolved' in m.content.lower() or '解决' in m.content])
        issue_resolution_efficiency = resolved_issues / max(1, len(issue_memories))
        
        overall_efficiency = (time_efficiency * 0.4 + memory_efficiency * 0.3 + issue_resolution_efficiency * 0.3)
        
        return {
            'time_efficiency': min(1.0, time_efficiency),
            'memory_efficiency': memory_efficiency,
            'issue_resolution_efficiency': issue_resolution_efficiency,
            'overall_efficiency': min(1.0, overall_efficiency)
        }
    
    def _identify_risk_factors(self, context, memories) -> List[str]:
        """识别风险因素"""
        risks = []
        
        # 时间风险
        if context.time_constraints.get('deadline_pressure', False):
            risks.append('tight_deadline')
        
        # 质量风险
        issue_memories = [m for m in memories if m.category == MemoryCategory.ISSUE]
        if len(issue_memories) > 5:
            risks.append('quality_concerns')
        
        # 资源风险
        if context.resource_availability.get('team_capacity', 1.0) < 0.7:
            risks.append('resource_constraints')
        
        # 技术风险
        learning_memories = [m for m in memories if m.category == MemoryCategory.LEARNING]
        if len(learning_memories) < 2 and context.current_stage > 'S2':
            risks.append('insufficient_technical_knowledge')
        
        return risks
    
    def _identify_optimization_opportunities(self, memories) -> List[str]:
        """识别优化机会"""
        opportunities = []
        
        # 基于模式记忆的优化机会
        pattern_memories = [m for m in memories if m.category == MemoryCategory.PATTERN]
        if pattern_memories:
            opportunities.extend([
                'leverage_identified_patterns',
                'automate_repetitive_tasks',
                'standardize_common_processes'
            ])
        
        # 基于学习记忆的优化机会
        learning_memories = [m for m in memories if m.category == MemoryCategory.LEARNING]
        if learning_memories:
            opportunities.extend([
                'apply_learned_best_practices',
                'share_knowledge_across_team',
                'create_reusable_components'
            ])
        
        # 基于决策记忆的优化机会
        decision_memories = [m for m in memories if m.category == MemoryCategory.DECISION]
        tech_decisions = [m for m in decision_memories if any(tech in m.content.lower() for tech in ['技术', 'technology', 'framework', '框架'])]
        if len(tech_decisions) > 2:
            opportunities.append('optimize_technology_stack')
        
        return opportunities
    
    def _analyze_quality_indicators(self, memories) -> Dict[str, Any]:
        """分析质量指标"""
        issue_memories = [m for m in memories if m.category == MemoryCategory.ISSUE]
        decision_memories = [m for m in memories if m.category == MemoryCategory.DECISION]
        
        return {
            'issues': issue_memories,
            'issue_count': len(issue_memories),
            'decision_quality': len([m for m in decision_memories if m.importance > 0.7]) / max(1, len(decision_memories)),
            'overall_quality_score': max(0.0, 1.0 - len(issue_memories) / 10.0)
        }
    
    def _generate_recommendation(
        self,
        strategy: OptimizationStrategy,
        optimization_result: Dict[str, Any],
        context: OptimizationContext,
        current_mode: WorkflowMode
    ) -> WorkflowRecommendation:
        """生成工作流推荐"""
        
        # 确定推荐的工作流模式
        recommended_mode = optimization_result.get('workflow_mode', current_mode)
        
        # 生成建议行动
        suggested_actions = self._generate_suggested_actions(strategy, optimization_result)
        
        # 估算时间节省和质量影响
        time_saving = optimization_result.get('time_saving_estimate', 0.0)
        quality_impact = optimization_result.get('quality_improvement_estimate', 0.0)
        
        # 计算置信度
        confidence = self._calculate_recommendation_confidence(strategy, optimization_result, context)
        
        # 生成推理说明
        reasoning = self._generate_reasoning(strategy, optimization_result, context)
        
        return WorkflowRecommendation(
            recommended_mode=recommended_mode,
            optimization_strategy=strategy,
            suggested_actions=suggested_actions,
            estimated_time_saving=time_saving,
            quality_impact=quality_impact,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _generate_suggested_actions(self, strategy, optimization_result) -> List[Dict[str, Any]]:
        """生成建议行动"""
        actions = []
        
        if strategy == OptimizationStrategy.SPEED:
            if optimization_result.get('skip_stages'):
                actions.append({
                    'type': 'skip_stage',
                    'description': '跳过非关键分析阶段',
                    'stages': optimization_result['skip_stages'],
                    'priority': 'high'
                })
            
            if optimization_result.get('parallel_tasks'):
                actions.append({
                    'type': 'parallel_execution',
                    'description': '并行执行独立任务',
                    'tasks': optimization_result['parallel_tasks'],
                    'priority': 'high'
                })
        
        elif strategy == OptimizationStrategy.QUALITY:
            if optimization_result.get('additional_stages'):
                actions.append({
                    'type': 'add_quality_stage',
                    'description': '添加质量保证阶段',
                    'stages': optimization_result['additional_stages'],
                    'priority': 'medium'
                })
            
            if optimization_result.get('quality_gates'):
                actions.append({
                    'type': 'implement_quality_gates',
                    'description': '实施质量门控',
                    'gates': optimization_result['quality_gates'],
                    'priority': 'high'
                })
        
        elif strategy == OptimizationStrategy.ADAPTIVE:
            if optimization_result.get('adaptive_rules'):
                actions.append({
                    'type': 'setup_adaptive_rules',
                    'description': '设置自适应规则',
                    'rules': optimization_result['adaptive_rules'],
                    'priority': 'medium'
                })
        
        return actions
    
    def _calculate_recommendation_confidence(self, strategy, optimization_result, context) -> float:
        """计算推荐置信度"""
        base_confidence = 0.7
        
        # 基于历史性能调整
        if context.historical_performance.get('success_rate', 0.5) > 0.8:
            base_confidence += 0.1
        
        # 基于优化结果的预期收益调整
        expected_benefit = optimization_result.get('time_saving_estimate', 0) + optimization_result.get('quality_improvement_estimate', 0)
        if expected_benefit > 0.3:
            base_confidence += 0.1
        elif expected_benefit < 0.1:
            base_confidence -= 0.1
        
        # 基于策略适用性调整
        if strategy == OptimizationStrategy.ADAPTIVE:
            base_confidence += 0.05  # 自适应策略通常更可靠
        
        return min(1.0, max(0.3, base_confidence))
    
    def _generate_reasoning(self, strategy, optimization_result, context) -> str:
        """生成推理说明"""
        reasons = []
        
        # 策略选择原因
        if strategy == OptimizationStrategy.SPEED:
            reasons.append("检测到时间压力，优先提升开发速度")
        elif strategy == OptimizationStrategy.QUALITY:
            reasons.append("项目处于后期阶段，重点关注质量保证")
        elif strategy == OptimizationStrategy.BALANCED:
            reasons.append("项目状态平衡，采用均衡优化策略")
        elif strategy == OptimizationStrategy.ADAPTIVE:
            reasons.append("项目复杂度较高，采用自适应优化策略")
        
        # 具体优化原因
        if optimization_result.get('time_saving_estimate', 0) > 0.2:
            reasons.append(f"预计可节省 {optimization_result['time_saving_estimate']*100:.0f}% 的时间")
        
        if optimization_result.get('quality_improvement_estimate', 0) > 0.2:
            reasons.append(f"预计可提升 {optimization_result['quality_improvement_estimate']*100:.0f}% 的质量")
        
        # 基于上下文的原因
        if context.project_progress < 0.3:
            reasons.append("项目初期，重点优化分析和设计流程")
        elif context.project_progress > 0.7:
            reasons.append("项目后期，重点优化测试和部署流程")
        
        return "; ".join(reasons) if reasons else "基于当前项目状态的综合分析"