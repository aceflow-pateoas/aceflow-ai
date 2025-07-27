"""
智能决策门系统
实现基于上下文和历史数据的智能质量评估
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from .models import MemoryFragment, MemoryCategory
# 临时注释质量评估导入，使用简化版本
# from .quality_assessment import ContextAwareQualityAssessment, QualityDimension


class DecisionGateResult(Enum):
    """决策门结果枚举"""
    PASS = "pass"
    CONDITIONAL_PASS = "conditional_pass"
    WARNING = "warning"
    FAIL = "fail"


@dataclass
class DecisionGateEvaluation:
    """决策门评估结果"""
    result: DecisionGateResult
    confidence: float
    score: float
    criteria_scores: Dict[str, float]
    recommendations: List[str]
    risk_factors: List[str]
    next_actions: List[str]
    timestamp: datetime


class IntelligentDecisionGate(ABC):
    """智能决策门基类"""
    
    def __init__(self, gate_id: str, name: str, description: str):
        self.gate_id = gate_id
        self.name = name
        self.description = description
        self.evaluation_history = []
        self.performance_metrics = {
            'accuracy': 0.8,
            'total_evaluations': 0,
            'correct_predictions': 0
        }
    
    @abstractmethod
    def evaluate(self, current_state: Dict[str, Any], memories: List[MemoryFragment], 
                project_context: Dict[str, Any]) -> DecisionGateEvaluation:
        """评估决策门"""
        pass
    
    def _calculate_confidence(self, criteria_scores: Dict[str, float]) -> float:
        """计算置信度"""
        if not criteria_scores:
            return 0.5
        
        # 基于标准分数的一致性计算置信度
        scores = list(criteria_scores.values())
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        consistency = max(0.0, 1.0 - variance)
        
        return min(0.95, avg_score * 0.7 + consistency * 0.3)
    
    def _determine_result(self, overall_score: float, confidence: float) -> DecisionGateResult:
        """确定决策结果"""
        if overall_score >= 0.8 and confidence >= 0.7:
            return DecisionGateResult.PASS
        elif overall_score >= 0.6 and confidence >= 0.6:
            return DecisionGateResult.CONDITIONAL_PASS
        elif overall_score >= 0.4:
            return DecisionGateResult.WARNING
        else:
            return DecisionGateResult.FAIL
    
    def _is_recent(self, timestamp: datetime, hours: int = 24) -> bool:
        """判断时间戳是否是最近的"""
        return (datetime.now() - timestamp) <= timedelta(hours=hours)


class OptimizedDG1(IntelligentDecisionGate):
    """优化的DG1：开发前检查决策门"""
    
    def __init__(self):
        super().__init__(
            gate_id="DG1",
            name="开发前检查",
            description="评估需求分析和设计的完整性，确保开发准备就绪"
        )

    
    def evaluate(self, current_state: Dict[str, Any], memories: List[MemoryFragment], 
                project_context: Dict[str, Any]) -> DecisionGateEvaluation:
        """执行DG1评估"""
        
        # 1. 评估需求完整性
        requirements_score = self._evaluate_requirements(memories)
        
        # 2. 评估设计准确性
        design_score = self._evaluate_design(memories)
        
        # 3. 评估可行性
        feasibility_score = self._evaluate_feasibility(current_state, project_context)
        
        # 4. 评估团队准备度
        readiness_score = self._evaluate_team_readiness(memories, project_context)
        
        criteria_scores = {
            'requirements_completeness': requirements_score,
            'design_accuracy': design_score,
            'feasibility_assessment': feasibility_score,
            'team_readiness': readiness_score
        }
        
        # 计算总分
        overall_score = sum(criteria_scores.values()) / len(criteria_scores)
        confidence = self._calculate_confidence(criteria_scores)
        result = self._determine_result(overall_score, confidence)
        
        # 生成建议和风险
        recommendations = self._generate_recommendations(criteria_scores, result)
        risk_factors = self._identify_risks(criteria_scores, project_context)
        next_actions = self._suggest_next_actions(result, criteria_scores)
        
        return DecisionGateEvaluation(
            result=result,
            confidence=confidence,
            score=overall_score,
            criteria_scores=criteria_scores,
            recommendations=recommendations,
            risk_factors=risk_factors,
            next_actions=next_actions,
            timestamp=datetime.now()
        )
    
    def _determine_result_with_context(self, overall_score: float, confidence: float, 
                                     quality_assessment: Dict[str, Any]) -> DecisionGateResult:
        """基于上下文确定决策结果"""
        # 检查是否有严重的质量问题
        critical_failures = []
        for criteria, assessment in quality_assessment['quality_assessment'].items():
            if not assessment['meets_standard'] and assessment['gap'] > 0.2:
                critical_failures.append(criteria)
        
        # 基于严重问题数量和整体分数确定结果
        if len(critical_failures) == 0 and overall_score >= 0.85 and confidence >= 0.8:
            return DecisionGateResult.PASS
        elif len(critical_failures) > 2 or overall_score < 0.5:
            return DecisionGateResult.FAIL
        elif len(critical_failures) == 1 or overall_score < 0.7:
            return DecisionGateResult.WARNING
        else:
            return DecisionGateResult.CONDITIONAL_PASS
  
    def _evaluate_requirements(self, memories: List[MemoryFragment]) -> float:
        """评估需求完整性"""
        req_memories = [m for m in memories if m.category == MemoryCategory.REQUIREMENT]
        
        if not req_memories:
            return 0.2
        
        # 基于需求数量和质量评分
        count_score = min(1.0, len(req_memories) / 5.0)  # 至少5个需求
        
        # 检查需求的详细程度
        detail_score = 0.0
        for memory in req_memories:
            if len(memory.content) > 50:  # 详细需求
                detail_score += 0.2
        detail_score = min(1.0, detail_score)
        
        return (count_score * 0.6 + detail_score * 0.4)
    
    def _evaluate_design(self, memories: List[MemoryFragment]) -> float:
        """评估设计准确性"""
        design_memories = [m for m in memories if m.category == MemoryCategory.DECISION]
        
        if not design_memories:
            return 0.3
        
        # 基于设计决策的数量和质量
        count_score = min(1.0, len(design_memories) / 3.0)  # 至少3个设计决策
        
        # 检查是否有架构相关的设计
        arch_keywords = ['架构', 'architecture', 'api', 'database', '数据库']
        arch_score = 0.0
        for memory in design_memories:
            if any(keyword in memory.content.lower() for keyword in arch_keywords):
                arch_score = 1.0
                break
        
        return (count_score * 0.7 + arch_score * 0.3)
    
    def _evaluate_feasibility(self, current_state: Dict[str, Any], 
                            project_context: Dict[str, Any]) -> float:
        """评估可行性"""
        complexity = project_context.get('complexity', 'medium')
        team_exp = project_context.get('team_experience', 'medium')
        
        # 复杂度评分
        complexity_scores = {'low': 0.9, 'medium': 0.7, 'high': 0.5}
        complexity_score = complexity_scores.get(complexity, 0.7)
        
        # 团队经验评分
        experience_scores = {'senior': 0.9, 'medium': 0.7, 'junior': 0.5}
        experience_score = experience_scores.get(team_exp, 0.7)
        
        # 时间约束评分
        time_score = 0.8  # 简化实现
        
        return (complexity_score * 0.4 + experience_score * 0.4 + time_score * 0.2)
    
    def _evaluate_team_readiness(self, memories: List[MemoryFragment], 
                               project_context: Dict[str, Any]) -> float:
        """评估团队准备度"""
        learning_memories = [m for m in memories if m.category == MemoryCategory.LEARNING]
        
        # 学习活动评分
        learning_score = min(1.0, len(learning_memories) / 3.0)  # 至少3个学习记录
        
        # 团队经验评分
        team_exp = project_context.get('team_experience', 'medium')
        exp_scores = {'senior': 0.9, 'medium': 0.7, 'junior': 0.5}
        exp_score = exp_scores.get(team_exp, 0.7)
        
        return (learning_score * 0.6 + exp_score * 0.4)
    
    def _generate_recommendations(self, criteria_scores: Dict[str, float], 
                                result: DecisionGateResult) -> List[str]:
        """生成建议"""
        recommendations = []
        
        for criteria, score in criteria_scores.items():
            if score < 0.6:
                if criteria == 'requirements_completeness':
                    recommendations.append("需要补充和完善需求文档，确保覆盖所有功能点")
                elif criteria == 'design_accuracy':
                    recommendations.append("需要审查和优化设计决策，确保技术方案的准确性")
                elif criteria == 'feasibility_assessment':
                    recommendations.append("需要重新评估项目可行性，考虑调整范围或资源")
                elif criteria == 'team_readiness':
                    recommendations.append("需要加强团队培训和技术准备")
        
        if result == DecisionGateResult.PASS:
            recommendations.append("所有标准都达到要求，可以开始开发阶段")
        
        return recommendations
    
    def _identify_risks(self, criteria_scores: Dict[str, float], 
                       project_context: Dict[str, Any]) -> List[str]:
        """识别风险"""
        risks = []
        
        # 基于分数识别风险
        if criteria_scores.get('requirements_completeness', 0) < 0.6:
            risks.append("需求不完整可能导致开发返工")
        
        if criteria_scores.get('feasibility_assessment', 0) < 0.6:
            risks.append("可行性不足可能导致项目延期或失败")
        
        # 基于上下文识别风险
        if (project_context.get('team_experience') == 'junior' and 
            project_context.get('complexity') == 'high'):
            risks.append("高复杂度项目配新手团队存在交付风险")
        
        return risks
    
    def _suggest_next_actions(self, result: DecisionGateResult, 
                            criteria_scores: Dict[str, float]) -> List[str]:
        """建议下一步行动"""
        actions = []
        
        if result == DecisionGateResult.PASS:
            actions.extend([
                "制定开发计划和里程碑",
                "设置开发环境和工具链",
                "开始详细设计和开发准备"
            ])
        elif result == DecisionGateResult.FAIL:
            actions.extend([
                "暂停进入开发阶段",
                "重新进行需求分析和设计",
                "组织团队评审会议"
            ])
        elif result == DecisionGateResult.WARNING:
            actions.extend([
                "解决识别出的关键问题",
                "进行有限范围的开发试点",
                "增加监控和检查点"
            ])
        else:  # CONDITIONAL_PASS
            actions.extend([
                "在解决特定问题后开始开发",
                "建立更频繁的检查机制",
                "准备应急计划"
            ])
        
        return actions


class OptimizedDG2(IntelligentDecisionGate):
    """优化的DG2：任务完成检查决策门"""
    
    def __init__(self):
        super().__init__(
            gate_id="DG2",
            name="任务完成检查",
            description="评估任务完成质量和准备进入下一阶段的条件"
        )
    
    def evaluate(self, current_state: Dict[str, Any], memories: List[MemoryFragment], 
                project_context: Dict[str, Any]) -> DecisionGateEvaluation:
        """执行DG2评估"""
        
        # 1. 评估完成质量
        completion_score = self._evaluate_completion_quality(current_state, memories)
        
        # 2. 评估交付物准确性
        deliverable_score = self._evaluate_deliverable_accuracy(memories)
        
        # 3. 评估质量保证
        qa_score = self._evaluate_quality_assurance(memories)
        
        # 4. 评估进度符合度
        progress_score = self._evaluate_progress_alignment(current_state)
        
        criteria_scores = {
            'completion_quality': completion_score,
            'deliverable_accuracy': deliverable_score,
            'quality_assurance': qa_score,
            'progress_alignment': progress_score
        }
        
        # 计算总分
        overall_score = sum(criteria_scores.values()) / len(criteria_scores)
        confidence = self._calculate_confidence(criteria_scores)
        result = self._determine_result(overall_score, confidence)
        
        # 生成建议和风险
        recommendations = self._generate_dg2_recommendations(criteria_scores, result)
        risk_factors = self._identify_dg2_risks(criteria_scores, current_state)
        next_actions = self._suggest_dg2_next_actions(result, current_state)
        
        return DecisionGateEvaluation(
            result=result,
            confidence=confidence,
            score=overall_score,
            criteria_scores=criteria_scores,
            recommendations=recommendations,
            risk_factors=risk_factors,
            next_actions=next_actions,
            timestamp=datetime.now()
        )    

    def _evaluate_completion_quality(self, current_state: Dict[str, Any], 
                                   memories: List[MemoryFragment]) -> float:
        """评估完成质量"""
        task_progress = current_state.get('task_progress', 0.0)
        
        # 基础进度分数
        progress_score = min(1.0, task_progress)
        
        # 基于最近活动的质量
        recent_activities = [m for m in memories if self._is_recent(m.created_at, hours=24*7)]
        activity_quality = min(1.0, len(recent_activities) / 5.0)
        
        # 基于问题解决情况
        issue_memories = [m for m in memories if m.category == MemoryCategory.ISSUE]
        recent_issues = [m for m in issue_memories if self._is_recent(m.created_at, hours=24*7)]
        resolved_issues = [m for m in recent_issues if '解决' in m.content or 'resolved' in m.content.lower()]
        
        issue_resolution_rate = len(resolved_issues) / max(1, len(recent_issues))
        
        return (progress_score * 0.5 + activity_quality * 0.3 + issue_resolution_rate * 0.2)
    
    def _evaluate_deliverable_accuracy(self, memories: List[MemoryFragment]) -> float:
        """评估交付物准确性"""
        pattern_memories = [m for m in memories if m.category == MemoryCategory.PATTERN]
        
        if not pattern_memories:
            return 0.6
        
        # 基于模式识别的质量
        pattern_quality = min(1.0, len(pattern_memories) / 3.0)
        
        # 基于实现质量
        implementation_keywords = ['实现', 'implementation', '完成', 'completed']
        implementation_quality = 0.0
        for memory in pattern_memories:
            if any(keyword in memory.content.lower() for keyword in implementation_keywords):
                implementation_quality += 0.3
        implementation_quality = min(1.0, implementation_quality)
        
        return (pattern_quality * 0.6 + implementation_quality * 0.4)
    
    def _evaluate_quality_assurance(self, memories: List[MemoryFragment]) -> float:
        """评估质量保证"""
        qa_keywords = ['测试', 'test', '检查', 'check', '审查', 'review', '验证', 'validate', '质量', 'quality']
        qa_memories = [m for m in memories if any(keyword in m.content.lower() for keyword in qa_keywords)]
        
        # 至少3个质量保证活动
        qa_activity_score = min(1.0, len(qa_memories) / 3.0)
        
        # 检查问题发现和解决
        issue_memories = [m for m in memories if m.category == MemoryCategory.ISSUE]
        proactive_issues = len([m for m in issue_memories if any(keyword in m.content.lower() 
                                                               for keyword in ['发现', 'found', '识别', 'identified'])])
        proactive_ratio = proactive_issues / max(1, len(issue_memories))
        
        qa_score = (qa_activity_score * 0.6 + proactive_ratio * 0.4)
        return min(1.0, qa_score)
    
    def _evaluate_progress_alignment(self, current_state: Dict[str, Any]) -> float:
        """评估进度符合度"""
        task_progress = current_state.get('task_progress', 0.0)
        current_stage = current_state.get('current_stage', 'S1')
        
        # 基于阶段的期望进度
        stage_expectations = {
            'S1': 0.2, 'S2': 0.4, 'S3': 0.6, 'S4': 0.8, 'S5': 0.9, 'S6': 1.0
        }
        
        expected_progress = stage_expectations.get(current_stage, 0.5)
        alignment_score = min(1.0, task_progress / expected_progress) if expected_progress > 0 else 0.5
        
        return alignment_score
    
    def _generate_dg2_recommendations(self, criteria_scores: Dict[str, float], 
                                    result: DecisionGateResult) -> List[str]:
        """生成DG2建议"""
        recommendations = []
        
        for criteria, score in criteria_scores.items():
            if score < 0.7:
                if criteria == 'completion_quality':
                    recommendations.append("需要提高任务完成质量，解决未完成的任务")
                elif criteria == 'deliverable_accuracy':
                    recommendations.append("需要验证交付物的准确性，确保符合需求")
                elif criteria == 'quality_assurance':
                    recommendations.append("需要加强质量保证活动，增加审查和验证")
        
        if result == DecisionGateResult.PASS:
            recommendations.append("准备进入下一阶段")
        
        return recommendations
    
    def _identify_dg2_risks(self, criteria_scores: Dict[str, float], 
                          current_state: Dict[str, Any]) -> List[str]:
        """识别DG2风险"""
        risks = []
        
        # 基于进度的风险
        task_progress = current_state.get('task_progress', 0.0)
        current_stage = current_state.get('current_stage', 'S1')
        
        if task_progress < 0.8 and current_stage in ['S3', 'S4']:
            risks.append("任务进度滞后，可能导致项目延期")
        
        # 基于质量保证的风险
        if criteria_scores.get('quality_assurance', 0) < 0.6:
            risks.append("质量保证不足，可能在后续阶段发现更多问题")
        
        return risks
    
    def _suggest_dg2_next_actions(self, result: DecisionGateResult, 
                                current_state: Dict[str, Any]) -> List[str]:
        """建议DG2下一步行动"""
        actions = []
        current_stage = current_state.get('current_stage', 'S1')
        
        if result == DecisionGateResult.PASS:
            next_stage = self._get_next_stage(current_stage)
            actions.extend([
                f"继续完善{current_stage}阶段的工作",
                "更新项目状态和里程碑",
                "通知相关团队成员",
                f"准备进入{next_stage}阶段"
            ])
        elif result == DecisionGateResult.FAIL:
            actions.extend([
                "重点解决质量问题",
                "重新评估任务范围和时间安排",
                "准备风险应对措施"
            ])
        elif result == DecisionGateResult.WARNING:
            actions.extend([
                "解决识别出的关键问题",
                "增加质量检查频率",
                "准备备用风险应对措施"
            ])
        else:  # CONDITIONAL_PASS
            actions.extend([
                "在满足特定条件后进入下一阶段",
                "建立更严格的监控机制"
            ])
        
        return actions
    
    def _get_next_stage(self, current_stage: str) -> str:
        """获取下一阶段"""
        stage_sequence = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
        try:
            current_index = stage_sequence.index(current_stage)
            if current_index < len(stage_sequence) - 1:
                return stage_sequence[current_index + 1]
        except ValueError:
            pass
        return 'Unknown'


class DecisionGateManager:
    """决策门管理器"""
    
    def __init__(self):
        self.gates = {}
        self.evaluation_history = []
    
    def register_gate(self, gate: IntelligentDecisionGate):
        """注册决策门"""
        self.gates[gate.gate_id] = gate
    
    def evaluate_gate(self, gate_id: str, current_state: Dict[str, Any], 
                     memories: List[MemoryFragment], 
                     project_context: Dict[str, Any] = None) -> DecisionGateEvaluation:
        """评估指定决策门"""
        if gate_id not in self.gates:
            raise ValueError(f"Decision gate {gate_id} not registered")
        
        gate = self.gates[gate_id]
        evaluation = gate.evaluate(current_state, memories, project_context or {})
        
        # 记录评估历史
        self.evaluation_history.append({
            'gate_id': gate_id,
            'result': evaluation.result.value,
            'confidence': evaluation.confidence,
            'score': evaluation.score,
            'timestamp': evaluation.timestamp
        })
        
        return evaluation
    
    def evaluate_all_gates(self, current_state: Dict[str, Any], 
                          memories: List[MemoryFragment], 
                          project_context: Dict[str, Any] = None) -> Dict[str, DecisionGateEvaluation]:
        """评估所有注册的决策门"""
        evaluations = {}
        
        for gate_id in self.gates:
            evaluations[gate_id] = self.evaluate_gate(gate_id, current_state, memories, project_context)
        
        return evaluations
    
    def get_evaluation_history(self, gate_id: str = None) -> List[Dict[str, Any]]:
        """获取评估历史"""
        if gate_id:
            return [h for h in self.evaluation_history if h['gate_id'] == gate_id]
        return self.evaluation_history.copy()
    
    def get_gate_performance(self, gate_id: str) -> Dict[str, float]:
        """获取决策门性能指标"""
        if gate_id not in self.gates:
            raise ValueError(f"Decision gate {gate_id} not registered")
        
        return self.gates[gate_id].performance_metrics.copy()


class DecisionGateFactory:
    """决策门工厂"""
    
    @staticmethod
    def create_decision_gate(gate_id: str) -> IntelligentDecisionGate:
        """创建决策门实例"""
        if gate_id == "DG1":
            return OptimizedDG1()
        elif gate_id == "DG2":
            return OptimizedDG2()
        else:
            raise ValueError(f"Unknown decision gate ID: {gate_id}")
    
    @staticmethod
    def get_available_gates() -> List[str]:
        """获取可用的决策门列表"""
        return ["DG1", "DG2"]


def initialize_default_gates() -> DecisionGateManager:
    """初始化默认决策门"""
    manager = DecisionGateManager()
    
    # 注册优化的决策门
    manager.register_gate(OptimizedDG1())
    manager.register_gate(OptimizedDG2())
    
    return manager