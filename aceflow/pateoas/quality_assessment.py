"""
上下文感知质量评估系统
基于项目上下文和历史模式动态调整质量标准
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from .models import MemoryFragment, MemoryCategory


class QualityDimension(Enum):
    """质量维度枚举"""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    FEASIBILITY = "feasibility"
    TESTABILITY = "testability"
    MAINTAINABILITY = "maintainability"


@dataclass
class QualityThreshold:
    """质量阈值配置"""
    criteria: QualityDimension
    minimum_score: float
    weight: float
    adaptive: bool = True
    context_factors: List[str] = None
    
    def __post_init__(self):
        if self.context_factors is None:
            self.context_factors = []


@dataclass
class QualityAssessmentResult:
    """质量评估结果"""
    dimension: QualityDimension
    score: float
    meets_standard: bool
    context_adjustment: float
    confidence: float
    recommendations: List[str]
    evidence: List[str]


class ContextAwareQualityAssessment:
    """上下文感知质量评估器"""
    
    def __init__(self):
        self.assessment_history = []
        self.context_patterns = {}
        self.adaptation_rules = self._initialize_adaptation_rules()
    
    def _initialize_adaptation_rules(self) -> Dict[str, Any]:
        """初始化自适应规则"""
        return {
            'team_experience': {
                'senior': {'score_boost': 0.1, 'threshold_relaxation': 0.05},
                'medium': {'score_boost': 0.0, 'threshold_relaxation': 0.0},
                'junior': {'score_boost': -0.1, 'threshold_relaxation': -0.05}
            },
            'project_complexity': {
                'low': {'score_boost': 0.05, 'threshold_relaxation': 0.02},
                'medium': {'score_boost': 0.0, 'threshold_relaxation': 0.0},
                'high': {'score_boost': -0.05, 'threshold_relaxation': -0.02}
            },
            'time_pressure': {
                'low': {'score_boost': 0.0, 'threshold_relaxation': 0.0},
                'medium': {'score_boost': -0.02, 'threshold_relaxation': -0.01},
                'high': {'score_boost': -0.05, 'threshold_relaxation': -0.03}
            }
        }
    
    def assess_quality_with_context(
        self,
        quality_scores: Dict[str, float],
        project_context: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """基于上下文进行质量评估"""
        
        # 1. 分析项目上下文
        context_analysis = self._analyze_project_context(project_context, memories)
        
        # 2. 调整质量标准
        adjusted_thresholds = self._adjust_quality_thresholds(context_analysis)
        
        # 3. 评估各个质量维度
        dimension_assessments = {}
        for criteria, score in quality_scores.items():
            assessment = self._assess_quality_dimension(
                criteria, score, adjusted_thresholds, context_analysis, memories
            )
            dimension_assessments[criteria] = assessment
        
        # 4. 计算整体质量评分
        overall_quality = self._calculate_overall_quality(dimension_assessments, context_analysis)
        
        # 5. 生成上下文感知的建议
        recommendations = self._generate_contextual_recommendations(
            dimension_assessments, context_analysis, memories
        )
        
        # 6. 识别风险因素
        risk_factors = self._identify_contextual_risks(
            dimension_assessments, context_analysis, memories
        )
        
        # 7. 记录评估历史
        self._record_assessment_history(dimension_assessments, context_analysis, overall_quality)
        
        return {
            'overall_quality': overall_quality,
            'quality_assessment': {
                criteria: {
                    'score': assessment.score,
                    'meets_standard': assessment.meets_standard,
                    'context_adjustment': assessment.context_adjustment,
                    'confidence': assessment.confidence,
                    'recommendations': assessment.recommendations
                }
                for criteria, assessment in dimension_assessments.items()
            },
            'context_analysis': context_analysis,
            'recommendations': recommendations,
            'risk_factors': risk_factors,
            'contextual_insights': self._generate_contextual_insights(
                dimension_assessments, context_analysis
            )
        }
    
    def _analyze_project_context(
        self, 
        project_context: Dict[str, Any], 
        memories: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """分析项目上下文"""
        
        context_analysis = {
            'team_experience': project_context.get('team_experience', 'medium'),
            'project_complexity': project_context.get('complexity', 'medium'),
            'time_pressure': self._assess_time_pressure(project_context, memories),
            'historical_performance': self._analyze_historical_performance(memories),
            'domain_familiarity': self._assess_domain_familiarity(memories),
            'technical_debt': self._assess_technical_debt(memories),
            'stakeholder_involvement': self._assess_stakeholder_involvement(memories)
        }
        
        return context_analysis
    
    def _assess_time_pressure(
        self, 
        project_context: Dict[str, Any], 
        memories: List[MemoryFragment]
    ) -> str:
        """评估时间压力"""
        
        # 检查是否有紧急时间约束的记忆
        time_keywords = ['紧急', 'urgent', '截止', 'deadline', '延期', 'delay']
        time_memories = [
            m for m in memories 
            if any(keyword in m.content.lower() for keyword in time_keywords)
        ]
        
        if len(time_memories) > 3:
            return 'high'
        elif len(time_memories) > 1:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_historical_performance(self, memories: List[MemoryFragment]) -> Dict[str, float]:
        """分析历史性能"""
        
        # 分析成功和失败的模式
        success_keywords = ['成功', 'success', '完成', 'completed', '解决', 'resolved']
        failure_keywords = ['失败', 'failed', '问题', 'issue', '错误', 'error']
        
        success_memories = [
            m for m in memories 
            if any(keyword in m.content.lower() for keyword in success_keywords)
        ]
        
        failure_memories = [
            m for m in memories 
            if any(keyword in m.content.lower() for keyword in failure_keywords)
        ]
        
        total_memories = len(success_memories) + len(failure_memories)
        if total_memories == 0:
            return {'success_rate': 0.5, 'confidence': 0.3}
        
        success_rate = len(success_memories) / total_memories
        confidence = min(1.0, total_memories / 10.0)  # 更多历史数据 = 更高置信度
        
        return {
            'success_rate': success_rate,
            'confidence': confidence,
            'total_experiences': total_memories
        }
    
    def _assess_domain_familiarity(self, memories: List[MemoryFragment]) -> float:
        """评估领域熟悉度"""
        
        # 基于学习记忆的数量和质量评估领域熟悉度
        learning_memories = [m for m in memories if m.category == MemoryCategory.LEARNING]
        
        if not learning_memories:
            return 0.5  # 中等熟悉度
        
        # 学习记忆越多，说明在学习新知识，可能熟悉度较低
        # 但如果学习记忆的重要性高，说明学习效果好
        avg_importance = sum(m.importance for m in learning_memories) / len(learning_memories)
        learning_intensity = len(learning_memories) / max(1, len(memories))
        
        # 平衡学习强度和学习效果
        familiarity = avg_importance * 0.7 - learning_intensity * 0.3
        return max(0.1, min(1.0, familiarity))
    
    def _assess_technical_debt(self, memories: List[MemoryFragment]) -> float:
        """评估技术债务"""
        
        debt_keywords = ['重构', 'refactor', '优化', 'optimize', '修复', 'fix', '改进', 'improve']
        debt_memories = [
            m for m in memories 
            if any(keyword in m.content.lower() for keyword in debt_keywords)
        ]
        
        # 技术债务相关记忆越多，债务越高
        debt_ratio = len(debt_memories) / max(1, len(memories))
        return min(1.0, debt_ratio * 2.0)  # 标准化到0-1
    
    def _assess_stakeholder_involvement(self, memories: List[MemoryFragment]) -> float:
        """评估利益相关者参与度"""
        
        stakeholder_keywords = ['客户', 'client', '用户', 'user', '需求', 'requirement', '反馈', 'feedback']
        stakeholder_memories = [
            m for m in memories 
            if any(keyword in m.content.lower() for keyword in stakeholder_keywords)
        ]
        
        involvement_ratio = len(stakeholder_memories) / max(1, len(memories))
        return min(1.0, involvement_ratio * 1.5)  # 标准化到0-1
    
    def _adjust_quality_thresholds(self, context_analysis: Dict[str, Any]) -> Dict[str, float]:
        """基于上下文调整质量阈值"""
        
        base_thresholds = {
            'completeness': 0.8,
            'accuracy': 0.75,
            'consistency': 0.7,
            'feasibility': 0.7,
            'testability': 0.65,
            'maintainability': 0.7
        }
        
        adjusted_thresholds = base_thresholds.copy()
        
        # 基于团队经验调整
        team_exp = context_analysis.get('team_experience', 'medium')
        if team_exp in self.adaptation_rules['team_experience']:
            adjustment = self.adaptation_rules['team_experience'][team_exp]['threshold_relaxation']
            for criteria in adjusted_thresholds:
                adjusted_thresholds[criteria] += adjustment
        
        # 基于项目复杂度调整
        complexity = context_analysis.get('project_complexity', 'medium')
        if complexity in self.adaptation_rules['project_complexity']:
            adjustment = self.adaptation_rules['project_complexity'][complexity]['threshold_relaxation']
            for criteria in adjusted_thresholds:
                adjusted_thresholds[criteria] += adjustment
        
        # 基于时间压力调整
        time_pressure = context_analysis.get('time_pressure', 'medium')
        if time_pressure in self.adaptation_rules['time_pressure']:
            adjustment = self.adaptation_rules['time_pressure'][time_pressure]['threshold_relaxation']
            for criteria in adjusted_thresholds:
                adjusted_thresholds[criteria] += adjustment
        
        # 确保阈值在合理范围内
        for criteria in adjusted_thresholds:
            adjusted_thresholds[criteria] = max(0.3, min(0.95, adjusted_thresholds[criteria]))
        
        return adjusted_thresholds
    
    def _assess_quality_dimension(
        self,
        criteria: str,
        score: float,
        thresholds: Dict[str, float],
        context_analysis: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> QualityAssessmentResult:
        """评估单个质量维度"""
        
        threshold = thresholds.get(criteria, 0.7)
        
        # 基于上下文调整分数
        context_adjustment = self._calculate_context_adjustment(criteria, context_analysis)
        adjusted_score = min(1.0, max(0.0, score + context_adjustment))
        
        # 判断是否达标
        meets_standard = adjusted_score >= threshold
        
        # 计算置信度
        confidence = self._calculate_assessment_confidence(criteria, memories, context_analysis)
        
        # 生成建议
        recommendations = self._generate_dimension_recommendations(
            criteria, adjusted_score, threshold, context_analysis
        )
        
        # 收集证据
        evidence = self._collect_quality_evidence(criteria, memories)
        
        return QualityAssessmentResult(
            dimension=QualityDimension(criteria) if criteria in [d.value for d in QualityDimension] else None,
            score=adjusted_score,
            meets_standard=meets_standard,
            context_adjustment=context_adjustment,
            confidence=confidence,
            recommendations=recommendations,
            evidence=evidence
        )
    
    def _calculate_context_adjustment(self, criteria: str, context_analysis: Dict[str, Any]) -> float:
        """计算上下文调整值"""
        
        adjustment = 0.0
        
        # 基于团队经验调整
        team_exp = context_analysis.get('team_experience', 'medium')
        if team_exp in self.adaptation_rules['team_experience']:
            adjustment += self.adaptation_rules['team_experience'][team_exp]['score_boost']
        
        # 基于历史性能调整
        historical_perf = context_analysis.get('historical_performance', {})
        success_rate = historical_perf.get('success_rate', 0.5)
        if success_rate > 0.7:
            adjustment += 0.05
        elif success_rate < 0.3:
            adjustment -= 0.05
        
        # 基于领域熟悉度调整
        domain_familiarity = context_analysis.get('domain_familiarity', 0.5)
        if domain_familiarity > 0.7:
            adjustment += 0.03
        elif domain_familiarity < 0.3:
            adjustment -= 0.03
        
        return adjustment
    
    def _calculate_assessment_confidence(
        self,
        criteria: str,
        memories: List[MemoryFragment],
        context_analysis: Dict[str, Any]
    ) -> float:
        """计算评估置信度"""
        
        base_confidence = 0.7
        
        # 基于记忆数量调整置信度
        memory_count_factor = min(1.0, len(memories) / 10.0)
        
        # 基于历史性能置信度调整
        historical_confidence = context_analysis.get('historical_performance', {}).get('confidence', 0.5)
        
        # 基于上下文完整性调整
        context_completeness = len([v for v in context_analysis.values() if v is not None]) / len(context_analysis)
        
        confidence = base_confidence * 0.5 + memory_count_factor * 0.2 + historical_confidence * 0.2 + context_completeness * 0.1
        
        return min(0.95, max(0.3, confidence))
    
    def _generate_dimension_recommendations(
        self,
        criteria: str,
        score: float,
        threshold: float,
        context_analysis: Dict[str, Any]
    ) -> List[str]:
        """为特定质量维度生成建议"""
        
        recommendations = []
        gap = threshold - score
        
        if gap > 0.2:  # 显著差距
            if criteria == 'completeness':
                recommendations.append("需要大幅提升完整性，补充缺失的关键要素")
            elif criteria == 'accuracy':
                recommendations.append("准确性存在重大问题，需要全面审查和修正")
            elif criteria == 'consistency':
                recommendations.append("一致性问题严重，需要统一标准和规范")
        elif gap > 0.1:  # 中等差距
            if criteria == 'completeness':
                recommendations.append("完整性需要改进，关注细节补充")
            elif criteria == 'accuracy':
                recommendations.append("准确性有待提升，建议增加验证步骤")
        elif gap > 0:  # 小差距
            recommendations.append(f"{criteria}接近标准，需要微调优化")
        
        # 基于上下文添加特定建议
        team_exp = context_analysis.get('team_experience', 'medium')
        if team_exp == 'junior' and gap > 0.1:
            recommendations.append("考虑增加高级开发者指导或代码审查")
        
        time_pressure = context_analysis.get('time_pressure', 'medium')
        if time_pressure == 'high' and gap > 0.1:
            recommendations.append("在时间压力下，优先解决最关键的质量问题")
        
        return recommendations
    
    def _collect_quality_evidence(self, criteria: str, memories: List[MemoryFragment]) -> List[str]:
        """收集质量证据"""
        
        evidence = []
        
        # 基于记忆内容收集相关证据
        relevant_memories = []
        if criteria == 'completeness':
            keywords = ['完整', 'complete', '缺少', 'missing', '补充', 'add']
        elif criteria == 'accuracy':
            keywords = ['准确', 'accurate', '错误', 'error', '正确', 'correct']
        elif criteria == 'consistency':
            keywords = ['一致', 'consistent', '统一', 'uniform', '标准', 'standard']
        else:
            keywords = [criteria]
        
        for memory in memories:
            if any(keyword in memory.content.lower() for keyword in keywords):
                relevant_memories.append(memory)
        
        # 从相关记忆中提取证据
        for memory in relevant_memories[:3]:  # 最多3个证据
            evidence.append(f"记忆证据: {memory.content[:100]}...")
        
        return evidence
    
    def _calculate_overall_quality(
        self,
        dimension_assessments: Dict[str, QualityAssessmentResult],
        context_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算整体质量评分"""
        
        # 基础权重
        weights = {
            'completeness': 0.25,
            'accuracy': 0.25,
            'consistency': 0.15,
            'feasibility': 0.15,
            'testability': 0.1,
            'maintainability': 0.1
        }
        
        # 基于上下文调整权重
        if context_analysis.get('time_pressure') == 'high':
            weights['completeness'] = 0.3  # 时间紧张时更重视完整性
            weights['accuracy'] = 0.3
        
        if context_analysis.get('team_experience') == 'junior':
            weights['consistency'] = 0.2  # 新手团队更需要一致性
            weights['testability'] = 0.15
        
        # 计算加权平均分
        total_score = 0.0
        total_weight = 0.0
        confidence_sum = 0.0
        
        for criteria, assessment in dimension_assessments.items():
            weight = weights.get(criteria, 0.1)
            total_score += assessment.score * weight
            total_weight += weight
            confidence_sum += assessment.confidence
        
        overall_score = total_score / total_weight if total_weight > 0 else 0.0
        overall_confidence = confidence_sum / len(dimension_assessments) if dimension_assessments else 0.5
        
        return {
            'score': overall_score,
            'confidence': overall_confidence,
            'meets_standard': overall_score >= 0.7,  # 整体标准
            'quality_level': self._determine_quality_level(overall_score)
        }
    
    def _determine_quality_level(self, score: float) -> str:
        """确定质量等级"""
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.8:
            return 'good'
        elif score >= 0.7:
            return 'acceptable'
        elif score >= 0.6:
            return 'needs_improvement'
        else:
            return 'poor'
    
    def _generate_contextual_recommendations(
        self,
        dimension_assessments: Dict[str, QualityAssessmentResult],
        context_analysis: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> List[str]:
        """生成上下文感知的建议"""
        
        recommendations = []
        
        # 收集所有维度的建议
        for assessment in dimension_assessments.values():
            recommendations.extend(assessment.recommendations)
        
        # 基于上下文添加特定建议
        team_exp = context_analysis.get('team_experience', 'medium')
        if team_exp == 'junior':
            recommendations.append("建议增加代码审查和结对编程")
            recommendations.append("考虑提供更多技术培训和指导")
        
        complexity = context_analysis.get('project_complexity', 'medium')
        if complexity == 'high':
            recommendations.append("高复杂度项目建议采用分阶段交付")
            recommendations.append("增加架构审查和技术风险评估")
        
        time_pressure = context_analysis.get('time_pressure', 'medium')
        if time_pressure == 'high':
            recommendations.append("时间紧张时优先保证核心功能质量")
            recommendations.append("考虑适当调整功能范围以确保质量")
        
        # 去重并限制数量
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:8]  # 最多8个建议
    
    def _identify_contextual_risks(
        self,
        dimension_assessments: Dict[str, QualityAssessmentResult],
        context_analysis: Dict[str, Any],
        memories: List[MemoryFragment]
    ) -> List[str]:
        """识别上下文相关的风险"""
        
        risks = []
        
        # 基于质量评估识别风险
        low_quality_dimensions = [
            criteria for criteria, assessment in dimension_assessments.items()
            if not assessment.meets_standard
        ]
        
        if len(low_quality_dimensions) > 2:
            risks.append("多个质量维度不达标，存在系统性质量风险")
        
        # 基于上下文识别风险
        team_exp = context_analysis.get('team_experience', 'medium')
        complexity = context_analysis.get('project_complexity', 'medium')
        
        if team_exp == 'junior' and complexity == 'high':
            risks.append("新手团队处理高复杂度项目存在交付风险")
        
        time_pressure = context_analysis.get('time_pressure', 'medium')
        if time_pressure == 'high':
            risks.append("时间压力可能导致质量妥协")
        
        technical_debt = context_analysis.get('technical_debt', 0.0)
        if technical_debt > 0.7:
            risks.append("技术债务过高，影响长期可维护性")
        
        historical_perf = context_analysis.get('historical_performance', {})
        if historical_perf.get('success_rate', 0.5) < 0.4:
            risks.append("历史成功率较低，需要关注项目执行风险")
        
        return risks
    
    def _generate_contextual_insights(
        self,
        dimension_assessments: Dict[str, QualityAssessmentResult],
        context_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成上下文洞察"""
        
        insights = {
            'quality_trends': self._analyze_quality_trends(dimension_assessments),
            'context_impact': self._analyze_context_impact(context_analysis),
            'adaptive_recommendations': self._generate_adaptive_recommendations(
                dimension_assessments, context_analysis
            ),
            'improvement_priorities': self._identify_improvement_priorities(
                dimension_assessments, context_analysis
            )
        }
        
        return insights
    
    def _analyze_quality_trends(self, dimension_assessments: Dict[str, QualityAssessmentResult]) -> Dict[str, Any]:
        """分析质量趋势"""
        
        scores = [assessment.score for assessment in dimension_assessments.values()]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # 分析分数分布
        high_scores = len([s for s in scores if s >= 0.8])
        low_scores = len([s for s in scores if s < 0.6])
        
        return {
            'average_quality': avg_score,
            'high_quality_dimensions': high_scores,
            'low_quality_dimensions': low_scores,
            'quality_consistency': 1.0 - (max(scores) - min(scores)) if scores else 0.0
        }
    
    def _analyze_context_impact(self, context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析上下文影响"""
        
        positive_factors = []
        negative_factors = []
        
        if context_analysis.get('team_experience') == 'senior':
            positive_factors.append('经验丰富的团队')
        elif context_analysis.get('team_experience') == 'junior':
            negative_factors.append('团队经验不足')
        
        if context_analysis.get('project_complexity') == 'low':
            positive_factors.append('项目复杂度较低')
        elif context_analysis.get('project_complexity') == 'high':
            negative_factors.append('项目复杂度较高')
        
        if context_analysis.get('time_pressure') == 'high':
            negative_factors.append('时间压力较大')
        
        return {
            'positive_factors': positive_factors,
            'negative_factors': negative_factors,
            'overall_context_favorability': len(positive_factors) / max(1, len(positive_factors) + len(negative_factors))
        }
    
    def _generate_adaptive_recommendations(
        self,
        dimension_assessments: Dict[str, QualityAssessmentResult],
        context_analysis: Dict[str, Any]
    ) -> List[str]:
        """生成自适应建议"""
        
        recommendations = []
        
        # 基于质量评估和上下文生成针对性建议
        low_quality_dims = [
            criteria for criteria, assessment in dimension_assessments.items()
            if assessment.score < 0.7
        ]
        
        if 'completeness' in low_quality_dims:
            if context_analysis.get('time_pressure') == 'high':
                recommendations.append("优先完善核心功能的完整性")
            else:
                recommendations.append("系统性地补充缺失的功能和文档")
        
        if 'accuracy' in low_quality_dims:
            if context_analysis.get('team_experience') == 'junior':
                recommendations.append("增加高级开发者的代码审查频率")
            else:
                recommendations.append("建立更严格的质量检查流程")
        
        return recommendations
    
    def _identify_improvement_priorities(
        self,
        dimension_assessments: Dict[str, QualityAssessmentResult],
        context_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """识别改进优先级"""
        
        priorities = []
        
        for criteria, assessment in dimension_assessments.items():
            if not assessment.meets_standard:
                # 计算改进优先级
                urgency = 1.0 - assessment.score  # 分数越低越紧急
                impact = self._calculate_improvement_impact(criteria, context_analysis)
                priority_score = urgency * 0.6 + impact * 0.4
                
                priorities.append({
                    'criteria': criteria,
                    'priority_score': priority_score,
                    'urgency': urgency,
                    'impact': impact,
                    'current_score': assessment.score
                })
        
        # 按优先级排序
        priorities.sort(key=lambda x: x['priority_score'], reverse=True)
        return priorities[:5]  # 返回前5个优先级
    
    def _calculate_improvement_impact(self, criteria: str, context_analysis: Dict[str, Any]) -> float:
        """计算改进影响"""
        
        base_impact = {
            'completeness': 0.9,
            'accuracy': 0.8,
            'consistency': 0.6,
            'feasibility': 0.7,
            'testability': 0.5,
            'maintainability': 0.6
        }
        
        impact = base_impact.get(criteria, 0.5)
        
        # 基于上下文调整影响
        if context_analysis.get('team_experience') == 'junior' and criteria == 'consistency':
            impact += 0.2  # 新手团队更需要一致性
        
        if context_analysis.get('project_complexity') == 'high' and criteria == 'accuracy':
            impact += 0.1  # 复杂项目更需要准确性
        
        return min(1.0, impact)
    
    def _record_assessment_history(
        self,
        dimension_assessments: Dict[str, QualityAssessmentResult],
        context_analysis: Dict[str, Any],
        overall_quality: Dict[str, Any]
    ):
        """记录评估历史"""
        
        history_entry = {
            'timestamp': datetime.now(),
            'dimension_scores': {
                criteria: assessment.score 
                for criteria, assessment in dimension_assessments.items()
            },
            'overall_score': overall_quality['score'],
            'context': context_analysis.copy(),
            'quality_level': overall_quality['quality_level']
        }
        
        self.assessment_history.append(history_entry)
        
        # 保持历史记录在合理范围内
        if len(self.assessment_history) > 100:
            self.assessment_history = self.assessment_history[-100:]
    
    def get_assessment_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取评估历史"""
        return self.assessment_history[-limit:]
    
    def get_quality_trends(self) -> Dict[str, Any]:
        """获取质量趋势分析"""
        
        if len(self.assessment_history) < 2:
            return {'trend': 'insufficient_data'}
        
        recent_scores = [entry['overall_score'] for entry in self.assessment_history[-5:]]
        older_scores = [entry['overall_score'] for entry in self.assessment_history[-10:-5]]
        
        if not older_scores:
            return {'trend': 'insufficient_data'}
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg > older_avg + 0.05:
            trend = 'improving'
        elif recent_avg < older_avg - 0.05:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'recent_average': recent_avg,
            'older_average': older_avg,
            'improvement_rate': recent_avg - older_avg
        }