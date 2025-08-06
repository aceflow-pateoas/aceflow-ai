"""
增强版MCP Resources - 支持AI-人协同工作流的动态资源管理
Enhanced MCP Resources for AI-Human Collaborative Workflow
"""

from typing import Dict, Any, Optional, List
import json
from pathlib import Path
from datetime import datetime

# 导入原有资源
from .resources import AceFlowResources

# 导入协作组件
from .core.intent_recognizer import IntentType, WorkflowMode
from .core.collaboration_manager import CollaborationManager
from .core.task_parser import TaskParser, TaskStatus


class EnhancedAceFlowResources(AceFlowResources):
    """增强版AceFlow资源管理器，支持动态资源利用和智能决策"""
    
    def __init__(self):
        """初始化增强版资源管理器"""
        super().__init__()
        
        # 初始化协作组件
        self.collaboration_manager = CollaborationManager()
        self.task_parser = TaskParser()
        
        # 资源缓存
        self._resource_cache = {}
        self._cache_timestamp = {}
        
        # 智能推荐配置
        self.recommendation_config = {
            "stage_transition_threshold": 0.8,
            "task_completion_threshold": 0.9,
            "collaboration_timeout": 300,
            "auto_advance_modes": ["minimal"]
        }
    
    def get_intelligent_project_state(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取智能项目状态，包含协作信息和推荐操作
        
        Args:
            project_id: 项目ID
            
        Returns:
            Dict: 增强的项目状态信息
        """
        try:
            # 获取基础项目状态
            base_state = self.get_project_state()
            
            if not base_state.get("success"):
                return base_state
            
            project_data = base_state["project_state"]
            current_stage = project_data.get("flow", {}).get("current_stage", "unknown")
            
            # 获取协作状态
            collaboration_status = self.collaboration_manager.get_active_requests(project_id)
            collaboration_history = self.collaboration_manager.get_collaboration_history(project_id or "default")
            
            # 获取任务状态（如果在实现阶段）
            task_status = None
            if "implementation" in current_stage.lower():
                task_status = self._get_task_status(project_id or project_data.get("project", {}).get("name", "default"))
            
            # 生成智能推荐
            recommendations = self._generate_intelligent_recommendations(
                project_data, collaboration_status, task_status
            )
            
            # 构建增强状态
            enhanced_state = {
                **base_state,
                "collaboration": {
                    "active_requests": len(collaboration_status),
                    "total_interactions": len(collaboration_history.interactions) if collaboration_history else 0,
                    "last_interaction": collaboration_history.updated_at.isoformat() if collaboration_history else None
                },
                "task_progress": task_status,
                "intelligent_recommendations": recommendations,
                "context": {
                    "timestamp": datetime.now().isoformat(),
                    "stage_readiness": self._assess_stage_readiness(project_data),
                    "next_actions": self._suggest_next_actions(project_data, collaboration_status)
                }
            }
            
            return enhanced_state
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get intelligent project state"
            }
    
    def get_adaptive_stage_guide(self, stage_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取自适应阶段指导，根据项目状态和用户行为调整指导内容
        
        Args:
            stage_id: 阶段ID
            context: 上下文信息
            
        Returns:
            Dict: 自适应的阶段指导
        """
        try:
            # 获取基础阶段指导
            base_guide = self.get_stage_guide(stage_id)
            
            if not base_guide.get("success"):
                return base_guide
            
            # 获取项目上下文
            project_state = self.get_project_state()
            project_data = project_state.get("project_state", {}) if project_state.get("success") else {}
            
            # 获取协作历史
            project_id = project_data.get("project", {}).get("name", "default")
            collaboration_history = self.collaboration_manager.get_collaboration_history(project_id)
            
            # 分析用户行为模式
            user_patterns = self._analyze_user_patterns(collaboration_history)
            
            # 生成自适应指导
            adaptive_guide = self._create_adaptive_guide(
                base_guide["stage_guide"],
                stage_id,
                project_data,
                user_patterns,
                context or {}
            )
            
            return {
                "success": True,
                "stage_id": stage_id,
                "adaptive_guide": adaptive_guide,
                "personalization": user_patterns,
                "context_applied": context or {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get adaptive stage guide for {stage_id}"
            }
    
    def get_collaboration_insights(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取协作洞察，分析协作效果和改进建议
        
        Args:
            project_id: 项目ID
            
        Returns:
            Dict: 协作洞察信息
        """
        try:
            # 获取协作历史
            history = self.collaboration_manager.get_collaboration_history(project_id or "default")
            active_requests = self.collaboration_manager.get_active_requests(project_id)
            
            if not history:
                return {
                    "success": True,
                    "insights": {
                        "total_interactions": 0,
                        "collaboration_effectiveness": "No data",
                        "recommendations": ["Start collaborating to generate insights"]
                    }
                }
            
            # 分析协作模式
            interaction_analysis = self._analyze_collaboration_patterns(history.interactions)
            
            # 计算协作效果
            effectiveness_score = self._calculate_collaboration_effectiveness(history.interactions)
            
            # 生成改进建议
            improvement_suggestions = self._generate_collaboration_improvements(
                interaction_analysis, effectiveness_score
            )
            
            return {
                "success": True,
                "project_id": project_id or "default",
                "insights": {
                    "total_interactions": len(history.interactions),
                    "collaboration_effectiveness": effectiveness_score,
                    "interaction_patterns": interaction_analysis,
                    "active_requests": len(active_requests),
                    "improvement_suggestions": improvement_suggestions,
                    "last_updated": history.updated_at.isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get collaboration insights"
            }
    
    def get_dynamic_workflow_config(self, mode: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取动态工作流配置，根据项目特征和用户偏好调整工作流
        
        Args:
            mode: 工作流模式
            context: 上下文信息
            
        Returns:
            Dict: 动态工作流配置
        """
        try:
            # 获取基础工作流配置
            base_config = self.get_workflow_config()
            
            if not base_config.get("success"):
                return base_config
            
            # 分析项目特征
            project_features = self._analyze_project_features(context or {})
            
            # 获取用户偏好
            user_preferences = self._get_user_preferences()
            
            # 生成动态配置
            dynamic_config = self._create_dynamic_workflow_config(
                base_config["workflow_config"],
                mode,
                project_features,
                user_preferences
            )
            
            return {
                "success": True,
                "mode": mode,
                "dynamic_config": dynamic_config,
                "project_features": project_features,
                "user_preferences": user_preferences,
                "optimization_applied": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get dynamic workflow config for mode {mode}"
            }
    
    def _get_task_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        try:
            task_queue_file = Path("aceflow_result") / f"task_queue_{project_id}_S2_task_breakdown.json"
            
            if not task_queue_file.exists():
                return None
            
            task_queue = self.task_parser.load_task_queue(task_queue_file)
            progress = self.task_parser.get_task_progress(task_queue)
            
            return {
                "total_tasks": progress["total_tasks"],
                "completed_tasks": progress["completed_tasks"],
                "progress_percentage": progress["progress_percentage"],
                "next_executable_tasks": len(self.task_parser.get_next_executable_tasks(task_queue))
            }
            
        except Exception:
            return None
    
    def _generate_intelligent_recommendations(
        self,
        project_data: Dict[str, Any],
        collaboration_status: List,
        task_status: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """生成智能推荐"""
        recommendations = []
        
        current_stage = project_data.get("flow", {}).get("current_stage", "unknown")
        progress = project_data.get("flow", {}).get("progress_percentage", 0)
        
        # 基于进度的推荐
        if progress >= 80:
            recommendations.append({
                "type": "stage_advancement",
                "priority": "high",
                "title": "准备推进到下一阶段",
                "description": f"当前阶段 {current_stage} 进度已达 {progress}%，建议推进到下一阶段",
                "suggested_action": "aceflow_stage_collaborative(action='collaborative_next')"
            })
        
        # 基于协作状态的推荐
        if len(collaboration_status) > 0:
            recommendations.append({
                "type": "collaboration_pending",
                "priority": "urgent",
                "title": "待处理的协作请求",
                "description": f"有 {len(collaboration_status)} 个协作请求等待响应",
                "suggested_action": "aceflow_collaboration_status()"
            })
        
        # 基于任务状态的推荐
        if task_status and task_status["next_executable_tasks"] > 0:
            recommendations.append({
                "type": "task_execution",
                "priority": "medium",
                "title": "可执行任务可用",
                "description": f"有 {task_status['next_executable_tasks']} 个任务可以执行",
                "suggested_action": "aceflow_task_execute()"
            })
        
        return recommendations
    
    def _assess_stage_readiness(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估阶段准备情况"""
        current_stage = project_data.get("flow", {}).get("current_stage", "unknown")
        progress = project_data.get("flow", {}).get("progress_percentage", 0)
        
        readiness_score = min(progress / 100.0, 1.0)
        
        return {
            "current_stage": current_stage,
            "readiness_score": readiness_score,
            "ready_for_next": readiness_score >= self.recommendation_config["stage_transition_threshold"],
            "completion_estimate": f"{100 - progress:.1f}% remaining"
        }
    
    def _suggest_next_actions(
        self,
        project_data: Dict[str, Any],
        collaboration_status: List
    ) -> List[str]:
        """建议下一步操作"""
        actions = []
        
        # 如果有待处理的协作请求
        if collaboration_status:
            actions.append("处理待处理的协作请求")
        
        current_stage = project_data.get("flow", {}).get("current_stage", "unknown")
        progress = project_data.get("flow", {}).get("progress_percentage", 0)
        
        # 基于当前阶段建议操作
        if progress < 50:
            actions.append(f"继续执行当前阶段 {current_stage}")
        elif progress >= 80:
            actions.append("准备推进到下一阶段")
        else:
            actions.append("完成当前阶段的剩余工作")
        
        return actions
    
    def _analyze_user_patterns(self, history) -> Dict[str, Any]:
        """分析用户行为模式"""
        if not history or not history.interactions:
            return {
                "response_time_avg": 0,
                "confirmation_rate": 0,
                "preferred_interaction_type": "unknown",
                "activity_pattern": "no_data"
            }
        
        interactions = history.interactions
        
        # 分析响应时间
        response_times = []
        confirmations = 0
        total_requests = 0
        
        for interaction in interactions:
            if interaction.get("type") == "response":
                # 简化的响应时间分析
                response_times.append(60)  # 假设平均60秒响应时间
                if interaction.get("response", "").lower() in ["yes", "是", "确认", "继续"]:
                    confirmations += 1
            elif interaction.get("type") in ["confirmation_request", "input_request", "review_request"]:
                total_requests += 1
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        confirmation_rate = confirmations / total_requests if total_requests > 0 else 0
        
        return {
            "response_time_avg": avg_response_time,
            "confirmation_rate": confirmation_rate,
            "preferred_interaction_type": "confirmation",  # 简化
            "activity_pattern": "active" if len(interactions) > 5 else "moderate"
        }
    
    def _create_adaptive_guide(
        self,
        base_guide: Dict[str, Any],
        stage_id: str,
        project_data: Dict[str, Any],
        user_patterns: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建自适应指导"""
        adaptive_guide = base_guide.copy()
        
        # 根据用户模式调整
        if user_patterns["confirmation_rate"] > 0.8:
            adaptive_guide["collaboration_style"] = "high_trust"
            adaptive_guide["auto_advance_suggestion"] = True
        else:
            adaptive_guide["collaboration_style"] = "careful_confirmation"
            adaptive_guide["auto_advance_suggestion"] = False
        
        # 根据项目进度调整
        progress = project_data.get("flow", {}).get("progress_percentage", 0)
        if progress > 75:
            adaptive_guide["urgency_level"] = "high"
            adaptive_guide["focus_areas"] = ["completion", "quality_check"]
        else:
            adaptive_guide["urgency_level"] = "normal"
            adaptive_guide["focus_areas"] = ["implementation", "testing"]
        
        # 添加个性化建议
        adaptive_guide["personalized_tips"] = self._generate_personalized_tips(
            stage_id, user_patterns, context
        )
        
        return adaptive_guide
    
    def _analyze_collaboration_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析协作模式"""
        if not interactions:
            return {"pattern": "no_data"}
        
        # 统计交互类型
        interaction_types = {}
        for interaction in interactions:
            interaction_type = interaction.get("type", "unknown")
            interaction_types[interaction_type] = interaction_types.get(interaction_type, 0) + 1
        
        # 分析最常见的交互类型
        most_common_type = max(interaction_types.items(), key=lambda x: x[1])[0] if interaction_types else "unknown"
        
        return {
            "pattern": "collaborative" if len(interaction_types) > 2 else "simple",
            "most_common_interaction": most_common_type,
            "interaction_diversity": len(interaction_types),
            "total_interactions": len(interactions)
        }
    
    def _calculate_collaboration_effectiveness(self, interactions: List[Dict[str, Any]]) -> float:
        """计算协作效果"""
        if not interactions:
            return 0.0
        
        # 简化的效果计算
        successful_interactions = 0
        total_interactions = len(interactions)
        
        for interaction in interactions:
            if interaction.get("type") == "response":
                # 假设所有响应都是成功的
                successful_interactions += 1
        
        return successful_interactions / total_interactions if total_interactions > 0 else 0.0
    
    def _generate_collaboration_improvements(
        self,
        analysis: Dict[str, Any],
        effectiveness: float
    ) -> List[str]:
        """生成协作改进建议"""
        suggestions = []
        
        if effectiveness < 0.7:
            suggestions.append("考虑简化协作流程，减少不必要的确认步骤")
        
        if analysis.get("interaction_diversity", 0) < 2:
            suggestions.append("尝试使用更多样化的协作方式")
        
        if analysis.get("total_interactions", 0) < 5:
            suggestions.append("增加协作频率，保持更好的沟通")
        
        if not suggestions:
            suggestions.append("协作效果良好，继续保持当前模式")
        
        return suggestions
    
    def _analyze_project_features(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析项目特征"""
        return {
            "complexity": context.get("complexity", "medium"),
            "team_size": context.get("team_size", 1),
            "timeline": context.get("timeline", "normal"),
            "domain": context.get("domain", "general")
        }
    
    def _get_user_preferences(self) -> Dict[str, Any]:
        """获取用户偏好"""
        # 简化实现，实际中可以从配置文件或历史行为中学习
        return {
            "collaboration_frequency": "moderate",
            "auto_advance": False,
            "notification_style": "detailed",
            "preferred_confirmation_timeout": 300
        }
    
    def _create_dynamic_workflow_config(
        self,
        base_config: Dict[str, Any],
        mode: str,
        features: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建动态工作流配置"""
        dynamic_config = base_config.copy()
        
        # 根据项目复杂度调整
        if features["complexity"] == "high":
            dynamic_config["quality_gates"] = "strict"
            dynamic_config["review_frequency"] = "high"
        else:
            dynamic_config["quality_gates"] = "standard"
            dynamic_config["review_frequency"] = "normal"
        
        # 根据用户偏好调整
        if preferences["auto_advance"]:
            dynamic_config["auto_advance_enabled"] = True
            dynamic_config["confirmation_timeout"] = preferences["preferred_confirmation_timeout"]
        
        return dynamic_config
    
    def _generate_personalized_tips(
        self,
        stage_id: str,
        user_patterns: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """生成个性化提示"""
        tips = []
        
        if user_patterns["response_time_avg"] > 120:
            tips.append("建议设置更长的确认超时时间以适应您的工作节奏")
        
        if user_patterns["confirmation_rate"] > 0.9:
            tips.append("您的确认率很高，可以考虑启用自动推进功能")
        
        if stage_id == "implementation" and context.get("complexity") == "high":
            tips.append("复杂项目建议分阶段实现，每完成一个模块就进行测试")
        
        return tips


# 工厂函数
def create_enhanced_aceflow_resources() -> EnhancedAceFlowResources:
    """创建增强版AceFlow资源管理器实例"""
    return EnhancedAceFlowResources()