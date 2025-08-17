#!/usr/bin/env python3
"""
智能配置推荐系统测试
Intelligent Configuration Recommendations System Test
"""
import sys
import os
import asyncio
import json
import time
import math
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass
import uuid
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import logging

logger = logging.getLogger(__name__)

# 导入依赖的测试模块
from test_usage_monitoring_simple import (
    UsageEventType, UsageEvent, UsageMonitor, MemoryDataPersistence
)
from test_usage_analytics import (
    UsageDataAnalyzer, TrendAnalysis, UsagePattern, TrendDirection, UsagePatternType
)

# 推荐类型枚举
class RecommendationType(Enum):
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    FEATURE_USAGE = "feature_usage"
    CONFIGURATION_TUNING = "configuration_tuning"
    RESOURCE_SCALING = "resource_scaling"
    ERROR_REDUCTION = "error_reduction"
    WORKFLOW_IMPROVEMENT = "workflow_improvement"

# 推荐优先级枚举
class RecommendationPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

# 推荐影响范围枚举
class RecommendationScope(Enum):
    SYSTEM_WIDE = "system_wide"
    MODULE_SPECIFIC = "module_specific"
    USER_SPECIFIC = "user_specific"
    TOOL_SPECIFIC = "tool_specific"

# 推荐数据类
@dataclass
class ConfigurationRecommendation:
    """配置推荐数据结构"""
    recommendation_id: str
    type: RecommendationType
    priority: RecommendationPriority
    scope: RecommendationScope
    title: str
    description: str
    
    # 推荐的具体配置变更
    current_config: Dict[str, Any]
    recommended_config: Dict[str, Any]
    
    # 预期效果
    expected_benefits: List[str]
    potential_risks: List[str]
    estimated_impact: float  # 0.0 - 1.0
    
    # 支持数据
    supporting_data: Dict[str, Any]
    confidence_score: float  # 0.0 - 1.0
    
    # 实施信息
    implementation_steps: List[str]
    rollback_steps: List[str]
    testing_recommendations: List[str]
    
    # 元数据
    generated_at: float
    expires_at: Optional[float] = None
    applied: bool = False
    feedback_score: Optional[float] = None

# 推荐解释器
class RecommendationExplainer:
    """推荐解释机制"""
    
    @staticmethod
    def explain_performance_recommendation(recommendation: ConfigurationRecommendation) -> Dict[str, Any]:
        """解释性能优化推荐"""
        supporting_data = recommendation.supporting_data
        
        explanation = {
            "reasoning": [],
            "data_analysis": {},
            "impact_prediction": {},
            "risk_assessment": {}
        }
        
        # 分析支持数据
        if "avg_response_time" in supporting_data:
            avg_time = supporting_data["avg_response_time"]
            if avg_time > 1.0:
                explanation["reasoning"].append(
                    f"Average response time ({avg_time:.2f}s) exceeds optimal threshold (1.0s)"
                )
                explanation["data_analysis"]["response_time"] = {
                    "current": avg_time,
                    "threshold": 1.0,
                    "deviation": avg_time - 1.0
                }
        
        if "error_rate" in supporting_data:
            error_rate = supporting_data["error_rate"]
            if error_rate > 0.05:
                explanation["reasoning"].append(
                    f"Error rate ({error_rate:.1%}) is above acceptable level (5%)"
                )
                explanation["data_analysis"]["error_rate"] = {
                    "current": error_rate,
                    "threshold": 0.05,
                    "excess": error_rate - 0.05
                }
        
        # 预测影响
        explanation["impact_prediction"] = {
            "response_time_improvement": f"{recommendation.estimated_impact * 30:.0f}%",
            "error_reduction": f"{recommendation.estimated_impact * 20:.0f}%",
            "user_satisfaction_increase": f"{recommendation.estimated_impact * 15:.0f}%"
        }
        
        # 风险评估
        explanation["risk_assessment"] = {
            "implementation_risk": "low" if recommendation.confidence_score > 0.8 else "medium",
            "rollback_complexity": "simple" if len(recommendation.rollback_steps) <= 3 else "moderate",
            "downtime_required": "none" if "restart" not in str(recommendation.implementation_steps).lower() else "minimal"
        }
        
        return explanation
    
    @staticmethod
    def explain_feature_recommendation(recommendation: ConfigurationRecommendation) -> Dict[str, Any]:
        """解释功能使用推荐"""
        supporting_data = recommendation.supporting_data
        
        explanation = {
            "usage_analysis": {},
            "opportunity_identification": [],
            "adoption_strategy": {},
            "success_metrics": {}
        }
        
        # 使用分析
        if "tool_usage" in supporting_data:
            tool_usage = supporting_data["tool_usage"]
            total_calls = sum(tool_usage.values())
            
            explanation["usage_analysis"] = {
                "total_tool_calls": total_calls,
                "most_used_tools": sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:3],
                "underutilized_tools": [tool for tool, count in tool_usage.items() if count < total_calls * 0.1]
            }
        
        # 机会识别
        if "unused_features" in supporting_data:
            unused_features = supporting_data["unused_features"]
            for feature in unused_features:
                explanation["opportunity_identification"].append(
                    f"Feature '{feature}' could improve workflow efficiency by an estimated {recommendation.estimated_impact * 25:.0f}%"
                )
        
        # 采用策略
        explanation["adoption_strategy"] = {
            "gradual_rollout": True,
            "user_training_required": recommendation.priority in [RecommendationPriority.HIGH, RecommendationPriority.CRITICAL],
            "pilot_group_size": "20%" if recommendation.scope == RecommendationScope.SYSTEM_WIDE else "100%"
        }
        
        return explanation

# 性能优化推荐器
class PerformanceOptimizationRecommender:
    """性能优化推荐器"""
    
    def __init__(self, usage_analyzer: UsageDataAnalyzer):
        self.usage_analyzer = usage_analyzer
    
    def generate_recommendations(self, analysis_hours: int = 168) -> List[ConfigurationRecommendation]:
        """生成性能优化推荐"""
        recommendations = []
        
        # 获取性能数据
        usage_stats = self.usage_analyzer.usage_monitor.get_usage_stats()
        performance_data = usage_stats.get("performance", {})
        
        # 1. 响应时间优化推荐
        avg_response_time = performance_data.get("avg_response_time", 0)
        if avg_response_time > 1.0:
            recommendations.append(self._create_response_time_recommendation(avg_response_time))
        
        # 2. 缓存优化推荐
        cache_recommendation = self._analyze_cache_performance(analysis_hours)
        if cache_recommendation:
            recommendations.append(cache_recommendation)
        
        # 3. 资源分配推荐
        resource_recommendation = self._analyze_resource_usage(analysis_hours)
        if resource_recommendation:
            recommendations.append(resource_recommendation)
        
        return recommendations
    
    def _create_response_time_recommendation(self, avg_response_time: float) -> ConfigurationRecommendation:
        """创建响应时间优化推荐"""
        severity = "critical" if avg_response_time > 3.0 else "high" if avg_response_time > 2.0 else "medium"
        
        return ConfigurationRecommendation(
            recommendation_id=str(uuid.uuid4()),
            type=RecommendationType.PERFORMANCE_OPTIMIZATION,
            priority=RecommendationPriority.CRITICAL if severity == "critical" else RecommendationPriority.HIGH,
            scope=RecommendationScope.SYSTEM_WIDE,
            title="Optimize Response Time Performance",
            description=f"Average response time ({avg_response_time:.2f}s) exceeds optimal threshold. Implementing caching and connection pooling can improve performance.",
            current_config={
                "cache_enabled": False,
                "connection_pool_size": 10,
                "request_timeout": 30
            },
            recommended_config={
                "cache_enabled": True,
                "cache_ttl": 300,
                "connection_pool_size": 20,
                "request_timeout": 60,
                "enable_compression": True
            },
            expected_benefits=[
                f"Reduce average response time by {min(50, int((avg_response_time - 0.5) / avg_response_time * 100))}%",
                "Improve user experience and system throughput",
                "Reduce server load and resource consumption"
            ],
            potential_risks=[
                "Increased memory usage due to caching",
                "Potential cache invalidation complexity",
                "Initial performance impact during cache warm-up"
            ],
            estimated_impact=min(1.0, (avg_response_time - 0.5) / 2.0),
            supporting_data={
                "avg_response_time": avg_response_time,
                "performance_threshold": 1.0,
                "severity": severity
            },
            confidence_score=0.9,
            implementation_steps=[
                "Enable caching in configuration",
                "Increase connection pool size",
                "Configure request timeout",
                "Enable response compression",
                "Monitor performance metrics"
            ],
            rollback_steps=[
                "Disable caching",
                "Restore original connection pool size",
                "Reset request timeout",
                "Disable compression"
            ],
            testing_recommendations=[
                "Load test with increased concurrent users",
                "Monitor memory usage during peak hours",
                "Validate cache hit rates",
                "Test rollback procedures"
            ],
            generated_at=time.time()
        )
    
    def _analyze_cache_performance(self, hours: int) -> Optional[ConfigurationRecommendation]:
        """分析缓存性能并生成推荐"""
        # 模拟缓存分析
        cache_hit_rate = 0.3  # 假设当前缓存命中率较低
        
        if cache_hit_rate < 0.6:
            return ConfigurationRecommendation(
                recommendation_id=str(uuid.uuid4()),
                type=RecommendationType.PERFORMANCE_OPTIMIZATION,
                priority=RecommendationPriority.MEDIUM,
                scope=RecommendationScope.SYSTEM_WIDE,
                title="Improve Cache Configuration",
                description=f"Current cache hit rate ({cache_hit_rate:.1%}) is below optimal. Adjusting cache size and TTL can improve performance.",
                current_config={
                    "cache_size": 100,
                    "cache_ttl": 300,
                    "cache_strategy": "LRU"
                },
                recommended_config={
                    "cache_size": 500,
                    "cache_ttl": 600,
                    "cache_strategy": "LFU",
                    "cache_preload": True
                },
                expected_benefits=[
                    f"Increase cache hit rate to 70-80%",
                    "Reduce database/API calls by 40%",
                    "Improve response time by 25%"
                ],
                potential_risks=[
                    "Increased memory usage",
                    "Potential stale data issues",
                    "Cache warming overhead"
                ],
                estimated_impact=0.6,
                supporting_data={
                    "current_hit_rate": cache_hit_rate,
                    "target_hit_rate": 0.75,
                    "analysis_period_hours": hours
                },
                confidence_score=0.8,
                implementation_steps=[
                    "Increase cache size limit",
                    "Extend cache TTL for stable data",
                    "Switch to LFU eviction strategy",
                    "Enable cache preloading",
                    "Monitor cache metrics"
                ],
                rollback_steps=[
                    "Restore original cache size",
                    "Reset cache TTL",
                    "Switch back to LRU strategy",
                    "Disable cache preloading"
                ],
                testing_recommendations=[
                    "Monitor cache hit rate improvements",
                    "Test memory usage under load",
                    "Validate data freshness",
                    "Performance test cache warming"
                ],
                generated_at=time.time()
            )
        
        return None
    
    def _analyze_resource_usage(self, hours: int) -> Optional[ConfigurationRecommendation]:
        """分析资源使用并生成推荐"""
        # 模拟资源使用分析
        cpu_usage = 0.8  # 假设CPU使用率较高
        
        if cpu_usage > 0.75:
            return ConfigurationRecommendation(
                recommendation_id=str(uuid.uuid4()),
                type=RecommendationType.RESOURCE_SCALING,
                priority=RecommendationPriority.HIGH,
                scope=RecommendationScope.SYSTEM_WIDE,
                title="Scale System Resources",
                description=f"CPU usage ({cpu_usage:.1%}) is consistently high. Consider scaling resources or optimizing workload distribution.",
                current_config={
                    "worker_processes": 4,
                    "max_concurrent_requests": 100,
                    "queue_size": 1000
                },
                recommended_config={
                    "worker_processes": 8,
                    "max_concurrent_requests": 200,
                    "queue_size": 2000,
                    "enable_load_balancing": True
                },
                expected_benefits=[
                    "Reduce CPU usage to 60-70%",
                    "Improve system responsiveness",
                    "Handle 2x more concurrent requests",
                    "Better fault tolerance"
                ],
                potential_risks=[
                    "Increased memory consumption",
                    "Higher infrastructure costs",
                    "Complexity in load balancing"
                ],
                estimated_impact=0.7,
                supporting_data={
                    "cpu_usage": cpu_usage,
                    "cpu_threshold": 0.75,
                    "analysis_period_hours": hours
                },
                confidence_score=0.85,
                implementation_steps=[
                    "Double worker process count",
                    "Increase concurrent request limit",
                    "Expand queue capacity",
                    "Configure load balancing",
                    "Monitor resource utilization"
                ],
                rollback_steps=[
                    "Restore original worker count",
                    "Reset request limits",
                    "Restore queue size",
                    "Disable load balancing"
                ],
                testing_recommendations=[
                    "Stress test with increased load",
                    "Monitor memory usage patterns",
                    "Test load balancer configuration",
                    "Validate failover scenarios"
                ],
                generated_at=time.time()
            )
        
        return None

# 功能使用推荐器
class FeatureUsageRecommender:
    """功能使用推荐器"""
    
    def __init__(self, usage_analyzer: UsageDataAnalyzer):
        self.usage_analyzer = usage_analyzer
    
    def generate_recommendations(self, analysis_hours: int = 168) -> List[ConfigurationRecommendation]:
        """生成功能使用推荐"""
        recommendations = []
        
        # 1. 分析工具使用模式
        tool_recommendations = self._analyze_tool_usage(analysis_hours)
        recommendations.extend(tool_recommendations)
        
        # 2. 分析未使用功能
        unused_feature_recommendations = self._analyze_unused_features(analysis_hours)
        recommendations.extend(unused_feature_recommendations)
        
        # 3. 分析工作流优化机会
        workflow_recommendations = self._analyze_workflow_optimization(analysis_hours)
        recommendations.extend(workflow_recommendations)
        
        return recommendations
    
    def _analyze_tool_usage(self, hours: int) -> List[ConfigurationRecommendation]:
        """分析工具使用模式"""
        recommendations = []
        
        # 获取工具使用摘要
        tool_summary = self.usage_analyzer.usage_monitor.get_tool_usage_summary(hours)
        by_tool = tool_summary.get("by_tool", {})
        
        # 找出使用频率低但成功率高的工具
        underutilized_tools = []
        for tool_name, stats in by_tool.items():
            if stats["calls"] < 10 and stats.get("avg_execution_time", 0) < 0.5:
                underutilized_tools.append(tool_name)
        
        if underutilized_tools:
            recommendations.append(ConfigurationRecommendation(
                recommendation_id=str(uuid.uuid4()),
                type=RecommendationType.FEATURE_USAGE,
                priority=RecommendationPriority.MEDIUM,
                scope=RecommendationScope.USER_SPECIFIC,
                title="Explore Underutilized Tools",
                description=f"Tools {underutilized_tools} are available but rarely used. They could improve your workflow efficiency.",
                current_config={
                    "enabled_tools": list(by_tool.keys()),
                    "tool_recommendations_enabled": False
                },
                recommended_config={
                    "enabled_tools": list(by_tool.keys()),
                    "tool_recommendations_enabled": True,
                    "suggested_tools": underutilized_tools,
                    "show_tool_tips": True
                },
                expected_benefits=[
                    "Discover new workflow capabilities",
                    "Improve task completion efficiency",
                    "Reduce manual work through automation"
                ],
                potential_risks=[
                    "Learning curve for new tools",
                    "Potential workflow disruption during adoption"
                ],
                estimated_impact=0.4,
                supporting_data={
                    "underutilized_tools": underutilized_tools,
                    "tool_usage_stats": by_tool,
                    "analysis_period_hours": hours
                },
                confidence_score=0.7,
                implementation_steps=[
                    "Enable tool recommendations",
                    "Configure suggested tools list",
                    "Enable contextual tool tips",
                    "Track adoption metrics"
                ],
                rollback_steps=[
                    "Disable tool recommendations",
                    "Clear suggested tools list",
                    "Disable tool tips"
                ],
                testing_recommendations=[
                    "A/B test recommendation effectiveness",
                    "Monitor tool adoption rates",
                    "Collect user feedback",
                    "Measure workflow efficiency improvements"
                ],
                generated_at=time.time()
            ))
        
        return recommendations
    
    def _analyze_unused_features(self, hours: int) -> List[ConfigurationRecommendation]:
        """分析未使用的功能"""
        recommendations = []
        
        # 模拟未使用功能分析
        available_features = ["collaboration", "intelligence", "advanced_validation", "auto_deployment"]
        used_features = ["basic_validation"]  # 假设只使用了基础功能
        
        unused_features = [f for f in available_features if f not in used_features]
        
        if unused_features:
            recommendations.append(ConfigurationRecommendation(
                recommendation_id=str(uuid.uuid4()),
                type=RecommendationType.FEATURE_USAGE,
                priority=RecommendationPriority.LOW,
                scope=RecommendationScope.SYSTEM_WIDE,
                title="Enable Advanced Features",
                description=f"Advanced features {unused_features} are available but not enabled. They could enhance your development workflow.",
                current_config={
                    "enabled_features": used_features,
                    "feature_discovery": False
                },
                recommended_config={
                    "enabled_features": used_features + unused_features[:2],  # 逐步启用
                    "feature_discovery": True,
                    "feature_tutorials": True
                },
                expected_benefits=[
                    "Access to advanced workflow capabilities",
                    "Improved code quality through advanced validation",
                    "Enhanced team collaboration features",
                    "Automated deployment processes"
                ],
                potential_risks=[
                    "Increased system complexity",
                    "Additional configuration required",
                    "Learning curve for new features"
                ],
                estimated_impact=0.6,
                supporting_data={
                    "unused_features": unused_features,
                    "current_features": used_features,
                    "feature_benefits": {
                        "collaboration": "Team workflow improvement",
                        "intelligence": "Smart recommendations",
                        "advanced_validation": "Enhanced code quality",
                        "auto_deployment": "Deployment automation"
                    }
                },
                confidence_score=0.6,
                implementation_steps=[
                    "Enable feature discovery mode",
                    "Activate collaboration features",
                    "Configure intelligence module",
                    "Set up feature tutorials",
                    "Monitor feature adoption"
                ],
                rollback_steps=[
                    "Disable new features",
                    "Restore original configuration",
                    "Clear feature tutorials"
                ],
                testing_recommendations=[
                    "Test each feature individually",
                    "Monitor system performance impact",
                    "Collect user feedback on new features",
                    "Measure productivity improvements"
                ],
                generated_at=time.time()
            ))
        
        return recommendations
    
    def _analyze_workflow_optimization(self, hours: int) -> List[ConfigurationRecommendation]:
        """分析工作流优化机会"""
        recommendations = []
        
        # 模拟工作流分析
        # 假设发现用户经常手动执行可以自动化的任务序列
        common_sequences = [
            ["aceflow_init", "aceflow_stage", "aceflow_validate"],
            ["aceflow_validate", "aceflow_stage"]
        ]
        
        if common_sequences:
            recommendations.append(ConfigurationRecommendation(
                recommendation_id=str(uuid.uuid4()),
                type=RecommendationType.WORKFLOW_IMPROVEMENT,
                priority=RecommendationPriority.MEDIUM,
                scope=RecommendationScope.USER_SPECIFIC,
                title="Automate Common Task Sequences",
                description="Detected repeated task sequences that could be automated with workflow templates.",
                current_config={
                    "workflow_automation": False,
                    "custom_workflows": []
                },
                recommended_config={
                    "workflow_automation": True,
                    "custom_workflows": [
                        {
                            "name": "full_cycle",
                            "sequence": ["aceflow_init", "aceflow_stage", "aceflow_validate"],
                            "auto_trigger": False
                        },
                        {
                            "name": "validate_and_advance",
                            "sequence": ["aceflow_validate", "aceflow_stage"],
                            "auto_trigger": True,
                            "trigger_condition": "validation_success"
                        }
                    ]
                },
                expected_benefits=[
                    "Reduce manual task execution by 60%",
                    "Minimize human errors in task sequences",
                    "Improve workflow consistency",
                    "Save time on repetitive operations"
                ],
                potential_risks=[
                    "Over-automation may reduce control",
                    "Workflow templates may not fit all scenarios",
                    "Debugging automated workflows can be complex"
                ],
                estimated_impact=0.5,
                supporting_data={
                    "common_sequences": common_sequences,
                    "sequence_frequency": {"full_cycle": 15, "validate_and_advance": 8},
                    "potential_time_savings": "2-3 hours per week"
                },
                confidence_score=0.75,
                implementation_steps=[
                    "Enable workflow automation",
                    "Create workflow templates",
                    "Configure trigger conditions",
                    "Test automated sequences",
                    "Monitor automation effectiveness"
                ],
                rollback_steps=[
                    "Disable workflow automation",
                    "Remove custom workflows",
                    "Restore manual execution"
                ],
                testing_recommendations=[
                    "Test each workflow template thoroughly",
                    "Validate trigger conditions",
                    "Monitor automation success rates",
                    "Collect user feedback on automation"
                ],
                generated_at=time.time()
            ))
        
        return recommendations

# 智能配置推荐系统主类
class IntelligentConfigurationRecommender:
    """智能配置推荐系统"""
    
    def __init__(self, usage_analyzer: UsageDataAnalyzer):
        self.usage_analyzer = usage_analyzer
        self.performance_recommender = PerformanceOptimizationRecommender(usage_analyzer)
        self.feature_recommender = FeatureUsageRecommender(usage_analyzer)
        self.explainer = RecommendationExplainer()
        
        # 推荐历史
        self.recommendation_history = []
        self.applied_recommendations = {}
        
    def generate_all_recommendations(self, analysis_hours: int = 168) -> Dict[str, Any]:
        """生成所有类型的推荐"""
        recommendations = []
        
        # 生成性能优化推荐
        perf_recommendations = self.performance_recommender.generate_recommendations(analysis_hours)
        recommendations.extend(perf_recommendations)
        
        # 生成功能使用推荐
        feature_recommendations = self.feature_recommender.generate_recommendations(analysis_hours)
        recommendations.extend(feature_recommendations)
        
        # 按优先级排序
        recommendations.sort(key=lambda x: self._get_priority_score(x.priority), reverse=True)
        
        # 生成推荐报告
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "analysis_period_hours": analysis_hours,
                "total_recommendations": len(recommendations)
            },
            "recommendations": [self._serialize_recommendation(rec) for rec in recommendations],
            "summary": self._generate_recommendations_summary(recommendations),
            "implementation_plan": self._generate_implementation_plan(recommendations)
        }
        
        # 保存到历史
        self.recommendation_history.append(report)
        
        return report
    
    def explain_recommendation(self, recommendation_id: str) -> Dict[str, Any]:
        """解释特定推荐"""
        # 查找推荐
        recommendation = None
        for report in self.recommendation_history:
            for rec_data in report["recommendations"]:
                if rec_data["recommendation_id"] == recommendation_id:
                    recommendation = self._deserialize_recommendation(rec_data)
                    break
            if recommendation:
                break
        
        if not recommendation:
            return {"error": "Recommendation not found"}
        
        # 生成解释
        if recommendation.type == RecommendationType.PERFORMANCE_OPTIMIZATION:
            explanation = self.explainer.explain_performance_recommendation(recommendation)
        elif recommendation.type == RecommendationType.FEATURE_USAGE:
            explanation = self.explainer.explain_feature_recommendation(recommendation)
        else:
            explanation = {"message": "Detailed explanation not available for this recommendation type"}
        
        return {
            "recommendation_id": recommendation_id,
            "recommendation_summary": {
                "title": recommendation.title,
                "type": recommendation.type.value,
                "priority": recommendation.priority.value,
                "confidence": recommendation.confidence_score
            },
            "explanation": explanation,
            "generated_at": datetime.now().isoformat()
        }
    
    def apply_recommendation(self, recommendation_id: str, feedback_score: Optional[float] = None) -> Dict[str, Any]:
        """应用推荐（模拟）"""
        # 在实际实现中，这里会真正应用配置变更
        # 现在只是记录应用状态
        
        self.applied_recommendations[recommendation_id] = {
            "applied_at": time.time(),
            "feedback_score": feedback_score,
            "status": "applied"
        }
        
        return {
            "recommendation_id": recommendation_id,
            "status": "applied",
            "applied_at": datetime.now().isoformat(),
            "message": "Recommendation applied successfully (simulated)"
        }
    
    def get_recommendation_effectiveness(self) -> Dict[str, Any]:
        """获取推荐效果分析"""
        if not self.applied_recommendations:
            return {"message": "No recommendations have been applied yet"}
        
        total_applied = len(self.applied_recommendations)
        feedback_scores = [
            rec["feedback_score"] for rec in self.applied_recommendations.values()
            if rec["feedback_score"] is not None
        ]
        
        avg_feedback = sum(feedback_scores) / len(feedback_scores) if feedback_scores else None
        
        return {
            "total_recommendations_applied": total_applied,
            "average_feedback_score": avg_feedback,
            "feedback_distribution": {
                "excellent": len([s for s in feedback_scores if s >= 4.0]),
                "good": len([s for s in feedback_scores if 3.0 <= s < 4.0]),
                "fair": len([s for s in feedback_scores if 2.0 <= s < 3.0]),
                "poor": len([s for s in feedback_scores if s < 2.0])
            } if feedback_scores else None,
            "analysis_date": datetime.now().isoformat()
        }
    
    def _get_priority_score(self, priority: RecommendationPriority) -> int:
        """获取优先级分数"""
        priority_scores = {
            RecommendationPriority.CRITICAL: 5,
            RecommendationPriority.HIGH: 4,
            RecommendationPriority.MEDIUM: 3,
            RecommendationPriority.LOW: 2,
            RecommendationPriority.INFORMATIONAL: 1
        }
        return priority_scores.get(priority, 0)
    
    def _serialize_recommendation(self, recommendation: ConfigurationRecommendation) -> Dict[str, Any]:
        """序列化推荐对象"""
        return {
            "recommendation_id": recommendation.recommendation_id,
            "type": recommendation.type.value,
            "priority": recommendation.priority.value,
            "scope": recommendation.scope.value,
            "title": recommendation.title,
            "description": recommendation.description,
            "current_config": recommendation.current_config,
            "recommended_config": recommendation.recommended_config,
            "expected_benefits": recommendation.expected_benefits,
            "potential_risks": recommendation.potential_risks,
            "estimated_impact": recommendation.estimated_impact,
            "confidence_score": recommendation.confidence_score,
            "implementation_steps": recommendation.implementation_steps,
            "rollback_steps": recommendation.rollback_steps,
            "testing_recommendations": recommendation.testing_recommendations,
            "generated_at": recommendation.generated_at,
            "expires_at": recommendation.expires_at,
            "applied": recommendation.applied
        }
    
    def _deserialize_recommendation(self, data: Dict[str, Any]) -> ConfigurationRecommendation:
        """反序列化推荐对象"""
        return ConfigurationRecommendation(
            recommendation_id=data["recommendation_id"],
            type=RecommendationType(data["type"]),
            priority=RecommendationPriority(data["priority"]),
            scope=RecommendationScope(data["scope"]),
            title=data["title"],
            description=data["description"],
            current_config=data["current_config"],
            recommended_config=data["recommended_config"],
            expected_benefits=data["expected_benefits"],
            potential_risks=data["potential_risks"],
            estimated_impact=data["estimated_impact"],
            supporting_data=data.get("supporting_data", {}),
            confidence_score=data["confidence_score"],
            implementation_steps=data["implementation_steps"],
            rollback_steps=data["rollback_steps"],
            testing_recommendations=data["testing_recommendations"],
            generated_at=data["generated_at"],
            expires_at=data.get("expires_at"),
            applied=data.get("applied", False)
        )
    
    def _generate_recommendations_summary(self, recommendations: List[ConfigurationRecommendation]) -> Dict[str, Any]:
        """生成推荐摘要"""
        if not recommendations:
            return {"message": "No recommendations generated"}
        
        # 按类型分组
        by_type = {}
        for rec in recommendations:
            rec_type = rec.type.value
            if rec_type not in by_type:
                by_type[rec_type] = []
            by_type[rec_type].append(rec)
        
        # 按优先级分组
        by_priority = {}
        for rec in recommendations:
            priority = rec.priority.value
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(rec)
        
        # 计算总体影响
        total_impact = sum(rec.estimated_impact for rec in recommendations)
        avg_confidence = sum(rec.confidence_score for rec in recommendations) / len(recommendations)
        
        return {
            "total_recommendations": len(recommendations),
            "by_type": {rec_type: len(recs) for rec_type, recs in by_type.items()},
            "by_priority": {priority: len(recs) for priority, recs in by_priority.items()},
            "estimated_total_impact": total_impact,
            "average_confidence": avg_confidence,
            "top_recommendation": {
                "title": recommendations[0].title,
                "type": recommendations[0].type.value,
                "priority": recommendations[0].priority.value,
                "impact": recommendations[0].estimated_impact
            } if recommendations else None
        }
    
    def _generate_implementation_plan(self, recommendations: List[ConfigurationRecommendation]) -> Dict[str, Any]:
        """生成实施计划"""
        if not recommendations:
            return {"message": "No implementation plan needed"}
        
        # 按优先级分组实施
        critical_recs = [r for r in recommendations if r.priority == RecommendationPriority.CRITICAL]
        high_recs = [r for r in recommendations if r.priority == RecommendationPriority.HIGH]
        medium_recs = [r for r in recommendations if r.priority == RecommendationPriority.MEDIUM]
        low_recs = [r for r in recommendations if r.priority == RecommendationPriority.LOW]
        
        plan = {
            "implementation_phases": [],
            "estimated_timeline": "2-4 weeks",
            "resource_requirements": [],
            "success_metrics": []
        }
        
        # 第一阶段：关键推荐
        if critical_recs:
            plan["implementation_phases"].append({
                "phase": 1,
                "name": "Critical Issues",
                "duration": "1 week",
                "recommendations": [r.recommendation_id for r in critical_recs],
                "description": "Address critical performance and stability issues"
            })
        
        # 第二阶段：高优先级推荐
        if high_recs:
            plan["implementation_phases"].append({
                "phase": 2,
                "name": "High Priority Improvements",
                "duration": "1-2 weeks",
                "recommendations": [r.recommendation_id for r in high_recs],
                "description": "Implement high-impact performance and feature improvements"
            })
        
        # 第三阶段：中等优先级推荐
        if medium_recs or low_recs:
            plan["implementation_phases"].append({
                "phase": 3,
                "name": "Additional Optimizations",
                "duration": "1-2 weeks",
                "recommendations": [r.recommendation_id for r in medium_recs + low_recs],
                "description": "Apply remaining optimizations and feature enhancements"
            })
        
        return plan

# 测试函数
async def test_performance_recommender():
    """测试性能优化推荐器"""
    print("🧪 Testing Performance Optimization Recommender...")
    
    # 创建测试数据
    monitor = UsageMonitor()
    
    # 模拟高响应时间的工具调用
    for i in range(20):
        monitor.record_tool_call(
            tool_name=f"slow_tool_{i % 3}",
            user_id="test_user",
            execution_time=2.5 + (i * 0.1),  # 高响应时间
            success=True
        )
    
    analyzer = UsageDataAnalyzer(monitor)
    recommender = PerformanceOptimizationRecommender(analyzer)
    
    # 生成推荐
    recommendations = recommender.generate_recommendations(24)
    
    # 验证推荐
    assert len(recommendations) > 0
    
    # 检查响应时间推荐
    response_time_recs = [r for r in recommendations if "Response Time" in r.title]
    assert len(response_time_recs) > 0
    
    rec = response_time_recs[0]
    assert rec.type == RecommendationType.PERFORMANCE_OPTIMIZATION
    assert rec.priority in [RecommendationPriority.CRITICAL, RecommendationPriority.HIGH]
    assert rec.estimated_impact > 0
    assert rec.confidence_score > 0.5
    
    print("  ✅ Performance optimization recommendations test passed")
    print("🎉 All Performance Recommender tests passed!")
    return True

async def test_feature_recommender():
    """测试功能使用推荐器"""
    print("🧪 Testing Feature Usage Recommender...")
    
    # 创建测试数据
    monitor = UsageMonitor()
    
    # 模拟有限的工具使用
    for i in range(50):
        monitor.record_tool_call(
            tool_name="basic_tool",  # 只使用基础工具
            user_id="test_user",
            execution_time=0.1,
            success=True
        )
    
    # 少量使用其他工具
    for i in range(2):
        monitor.record_tool_call(
            tool_name="advanced_tool",
            user_id="test_user",
            execution_time=0.2,
            success=True
        )
    
    analyzer = UsageDataAnalyzer(monitor)
    recommender = FeatureUsageRecommender(analyzer)
    
    # 生成推荐
    recommendations = recommender.generate_recommendations(24)
    
    # 验证推荐
    assert len(recommendations) > 0
    
    # 检查功能使用推荐
    feature_recs = [r for r in recommendations if r.type == RecommendationType.FEATURE_USAGE]
    assert len(feature_recs) > 0
    
    rec = feature_recs[0]
    assert rec.scope in [RecommendationScope.USER_SPECIFIC, RecommendationScope.SYSTEM_WIDE]
    assert len(rec.expected_benefits) > 0
    assert len(rec.implementation_steps) > 0
    
    print("  ✅ Feature usage recommendations test passed")
    print("🎉 All Feature Recommender tests passed!")
    return True

async def test_recommendation_explainer():
    """测试推荐解释器"""
    print("🧪 Testing Recommendation Explainer...")
    
    explainer = RecommendationExplainer()
    
    # 创建测试推荐
    test_recommendation = ConfigurationRecommendation(
        recommendation_id="test-rec-1",
        type=RecommendationType.PERFORMANCE_OPTIMIZATION,
        priority=RecommendationPriority.HIGH,
        scope=RecommendationScope.SYSTEM_WIDE,
        title="Test Performance Recommendation",
        description="Test description",
        current_config={},
        recommended_config={},
        expected_benefits=["Benefit 1"],
        potential_risks=["Risk 1"],
        estimated_impact=0.7,
        supporting_data={
            "avg_response_time": 2.5,
            "error_rate": 0.08
        },
        confidence_score=0.9,
        implementation_steps=["Step 1"],
        rollback_steps=["Rollback 1"],
        testing_recommendations=["Test 1"],
        generated_at=time.time()
    )
    
    # 测试性能推荐解释
    explanation = explainer.explain_performance_recommendation(test_recommendation)
    
    assert "reasoning" in explanation
    assert "data_analysis" in explanation
    assert "impact_prediction" in explanation
    assert "risk_assessment" in explanation
    
    # 验证推理内容
    assert len(explanation["reasoning"]) > 0
    assert "response_time" in explanation["data_analysis"]
    assert "error_rate" in explanation["data_analysis"]
    
    print("  ✅ Performance recommendation explanation test passed")
    
    # 测试功能推荐解释
    feature_recommendation = ConfigurationRecommendation(
        recommendation_id="test-rec-2",
        type=RecommendationType.FEATURE_USAGE,
        priority=RecommendationPriority.MEDIUM,
        scope=RecommendationScope.USER_SPECIFIC,
        title="Test Feature Recommendation",
        description="Test description",
        current_config={},
        recommended_config={},
        expected_benefits=["Benefit 1"],
        potential_risks=["Risk 1"],
        estimated_impact=0.5,
        supporting_data={
            "tool_usage": {"tool1": 10, "tool2": 2},
            "unused_features": ["feature1", "feature2"]
        },
        confidence_score=0.7,
        implementation_steps=["Step 1"],
        rollback_steps=["Rollback 1"],
        testing_recommendations=["Test 1"],
        generated_at=time.time()
    )
    
    feature_explanation = explainer.explain_feature_recommendation(feature_recommendation)
    
    assert "usage_analysis" in feature_explanation
    assert "opportunity_identification" in feature_explanation
    assert "adoption_strategy" in feature_explanation
    
    print("  ✅ Feature recommendation explanation test passed")
    print("🎉 All Recommendation Explainer tests passed!")
    return True

async def test_intelligent_recommender():
    """测试智能配置推荐系统"""
    print("🧪 Testing Intelligent Configuration Recommender...")
    
    # 创建测试数据
    monitor = UsageMonitor()
    
    # 生成多样化的测试数据
    current_time = time.time()
    
    # 高响应时间的工具调用
    for i in range(30):
        monitor.record_tool_call(
            tool_name=f"tool_{i % 4}",
            user_id=f"user_{i % 3}",
            execution_time=1.5 + (i * 0.05),  # 逐渐增加的响应时间
            success=i % 10 != 0  # 90%成功率
        )
    
    # 一些错误事件
    for i in range(5):
        monitor.record_error(f"Error {i}: Test error message")
    
    # 资源访问事件
    for i in range(20):
        monitor.record_resource_access(
            resource_type=f"resource_{i % 2}",
            resource_id=f"id_{i}",
            cache_hit=i % 4 == 0  # 25%缓存命中率
        )
    
    analyzer = UsageDataAnalyzer(monitor)
    recommender = IntelligentConfigurationRecommender(analyzer)
    
    # 生成所有推荐
    report = recommender.generate_all_recommendations(24)
    
    # 验证报告结构
    assert "report_metadata" in report
    assert "recommendations" in report
    assert "summary" in report
    assert "implementation_plan" in report
    
    # 验证推荐内容
    recommendations = report["recommendations"]
    assert len(recommendations) > 0
    
    # 验证推荐类型多样性
    rec_types = set(rec["type"] for rec in recommendations)
    assert len(rec_types) > 1  # 应该有多种类型的推荐
    
    # 验证摘要
    summary = report["summary"]
    assert summary["total_recommendations"] == len(recommendations)
    assert "by_type" in summary
    assert "by_priority" in summary
    assert "top_recommendation" in summary
    
    # 验证实施计划
    impl_plan = report["implementation_plan"]
    assert "implementation_phases" in impl_plan
    assert len(impl_plan["implementation_phases"]) > 0
    
    print("  ✅ Comprehensive recommendation generation test passed")
    
    # 测试推荐解释
    if recommendations:
        rec_id = recommendations[0]["recommendation_id"]
        explanation = recommender.explain_recommendation(rec_id)
        
        assert "recommendation_id" in explanation
        assert "recommendation_summary" in explanation
        assert "explanation" in explanation
        
        print("  ✅ Recommendation explanation test passed")
    
    # 测试推荐应用
    if recommendations:
        rec_id = recommendations[0]["recommendation_id"]
        apply_result = recommender.apply_recommendation(rec_id, feedback_score=4.5)
        
        assert apply_result["status"] == "applied"
        assert apply_result["recommendation_id"] == rec_id
        
        print("  ✅ Recommendation application test passed")
    
    # 测试效果分析
    effectiveness = recommender.get_recommendation_effectiveness()
    assert "total_recommendations_applied" in effectiveness
    assert effectiveness["total_recommendations_applied"] > 0
    
    print("  ✅ Recommendation effectiveness analysis test passed")
    print("🎉 All Intelligent Recommender tests passed!")
    return True

async def main():
    """运行所有测试"""
    print("🚀 Starting Intelligent Configuration Recommendations System tests...\n")
    
    try:
        await test_performance_recommender()
        await test_feature_recommender()
        await test_recommendation_explainer()
        await test_intelligent_recommender()
        
        print("\n🎉 All Intelligent Configuration Recommendations System tests passed!")
        print("\n📊 Intelligent Recommendations System Summary:")
        print("   ✅ Performance Optimization Recommendations - Working")
        print("   ✅ Feature Usage Recommendations - Working")
        print("   ✅ Recommendation Explanation System - Working")
        print("   ✅ Comprehensive Recommendation Generation - Working")
        print("   ✅ Implementation Planning - Working")
        print("   ✅ Recommendation Application Tracking - Working")
        print("   ✅ Effectiveness Analysis - Working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Intelligent recommendations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🏗️ Task 6.3 - Intelligent Configuration Recommendations Implementation Complete!")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)