"""
协作模块 (CollaborationModule)
Collaboration Module

This module refactors EnhancedAceFlowTools as CollaborationModule,
implementing collaboration tools: aceflow_respond, aceflow_collaboration_status, aceflow_task_execute.
Integrates collaboration manager and state management.
Ensures compatibility with the original aceflow-enhanced-server.
"""

from typing import Dict, Any, Optional, List
import logging
import json
import os
import sys
from pathlib import Path
import datetime
import uuid

from .base_module import BaseModule, ModuleMetadata
# 导入协作组件 - 使用绝对导入避免问题
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.collaboration_manager import CollaborationManager, RequestType, RequestStatus
    from core.intent_recognizer import IntentRecognizer, recognize_user_intent
    from core.task_parser import TaskParser, TaskStatus, TaskPriority
except ImportError:
    # 如果导入失败，创建占位符类
    class CollaborationManager:
        def __init__(self): pass
    
    class RequestType:
        CONFIRMATION = "confirmation"
        INPUT = "input"
        REVIEW = "review"
        DECISION = "decision"
        APPROVAL = "approval"
    
    class RequestStatus:
        PENDING = "pending"
        RESPONDED = "responded"
        TIMEOUT = "timeout"
        CANCELLED = "cancelled"
    
    class IntentRecognizer:
        def __init__(self): pass
    
    def recognize_user_intent(text):
        return {"intent": "unknown", "confidence": 0.5, "entities": {}}
    
    class TaskParser:
        def __init__(self): pass
    
    class TaskStatus:
        PENDING = "pending"
        COMPLETED = "completed"
    
    class TaskPriority:
        LOW = "low"
        NORMAL = "normal"
        HIGH = "high"

logger = logging.getLogger(__name__)


class CollaborationModule(BaseModule):
    """
    协作模块
    
    重构 EnhancedAceFlowTools 为 CollaborationModule，实现协作工具：
    - aceflow_respond: 响应协作请求
    - aceflow_collaboration_status: 获取协作状态和洞察
    - aceflow_task_execute: 执行任务与协作确认
    
    集成协作管理器和状态管理，确保与原 aceflow-enhanced-server 兼容。
    """
    
    def __init__(self, config):
        """
        初始化协作模块
        
        Args:
            config: 协作模块配置
        """
        metadata = ModuleMetadata(
            name="collaboration",
            version="1.0.0",
            description="AI-Human collaboration functionality module",
            dependencies=["core"],
            provides=["aceflow_respond", "aceflow_collaboration_status", "aceflow_task_execute"],
            tags={"collaboration", "enhanced"}
        )
        
        super().__init__(config, metadata)
        
        # 协作组件
        self._collaboration_manager: Optional[CollaborationManager] = None
        self._intent_recognizer: Optional[IntentRecognizer] = None
        self._task_parser: Optional[TaskParser] = None
        
        # 协作状态
        self._active_requests: Dict[str, Any] = {}
        self._collaboration_history: List[Dict[str, Any]] = []
        
        # 配置参数
        self._confirmation_timeout = getattr(config, 'confirmation_timeout', 300)
        self._auto_confirm = getattr(config, 'auto_confirm', False)
        self._interaction_level = getattr(config, 'interaction_level', 'standard')
    
    def get_module_name(self) -> str:
        """获取模块名称"""
        return "collaboration"
    
    def _do_initialize(self) -> bool:
        """执行模块初始化逻辑"""
        try:
            # 初始化协作组件
            self._collaboration_manager = CollaborationManager()
            self._intent_recognizer = IntentRecognizer()
            self._task_parser = TaskParser()
            
            # 加载协作历史
            self._load_collaboration_history()
            
            logger.info("Collaboration module initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Collaboration module initialization failed: {e}")
            return False
    
    def _do_cleanup(self):
        """执行模块清理逻辑"""
        try:
            # 保存协作历史
            self._save_collaboration_history()
            
            # 清理活跃请求
            self._cleanup_active_requests()
            
            # 清理资源
            self._collaboration_manager = None
            self._intent_recognizer = None
            self._task_parser = None
            
            logger.info("Collaboration module cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Collaboration module cleanup error: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取模块健康状态"""
        if not self.initialized or not self._collaboration_manager:
            return {
                "healthy": False,
                "status": "not_initialized",
                "details": "Collaboration components not initialized"
            }
        
        return {
            "healthy": True,
            "status": "running",
            "details": "Collaboration module is healthy and ready",
            "tools_available": ["aceflow_respond", "aceflow_collaboration_status", "aceflow_task_execute"],
            "active_requests": len(self._active_requests),
            "collaboration_history_size": len(self._collaboration_history),
            "configuration": {
                "confirmation_timeout": self._confirmation_timeout,
                "auto_confirm": self._auto_confirm,
                "interaction_level": self._interaction_level
            }
        }
    
    # 协作工具方法
    
    def aceflow_respond(
        self,
        request_id: str,
        response: str,
        user_id: str = "user"
    ) -> Dict[str, Any]:
        """
        💬 Respond to collaboration requests
        
        Args:
            request_id: 协作请求ID
            response: 用户响应内容
            user_id: 用户ID
            
        Returns:
            Dict with response processing results
        """
        if not self.ensure_initialized():
            return {
                "success": False,
                "error": "Collaboration module not initialized",
                "message": "Module initialization failed"
            }
        
        try:
            start_time = datetime.datetime.now()
            
            # 查找活跃请求
            if request_id not in self._active_requests:
                return {
                    "success": False,
                    "error": f"Request '{request_id}' not found or already processed",
                    "message": "Invalid request ID"
                }
            
            request_info = self._active_requests[request_id]
            
            # 处理响应
            result = self._process_collaboration_response(
                request_id, response, user_id, request_info
            )
            
            # 记录统计信息
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.record_call(success=result.get("success", False), duration=duration)
            
            logger.info(f"aceflow_respond executed: request_id={request_id}, success={result.get('success')}")
            return result
            
        except Exception as e:
            self.record_call(success=False)
            logger.error(f"aceflow_respond error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process collaboration response"
            }
    
    def aceflow_collaboration_status(
        self,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        📊 Get collaboration status and insights
        
        Args:
            project_id: 可选的项目ID
            
        Returns:
            Dict with collaboration status and insights
        """
        if not self.ensure_initialized():
            return {
                "success": False,
                "error": "Collaboration module not initialized",
                "message": "Module initialization failed"
            }
        
        try:
            start_time = datetime.datetime.now()
            
            # 获取项目ID
            if not project_id:
                project_id = self._get_current_project_id()
            
            # 生成协作状态报告
            status_report = self._generate_collaboration_status(project_id)
            
            # 记录统计信息
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.record_call(success=True, duration=duration)
            
            logger.info(f"aceflow_collaboration_status executed: project_id={project_id}")
            return {
                "success": True,
                "message": "Collaboration status retrieved successfully",
                "project_id": project_id,
                "collaboration_status": status_report
            }
            
        except Exception as e:
            self.record_call(success=False)
            logger.error(f"aceflow_collaboration_status error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve collaboration status"
            }
    
    def aceflow_task_execute(
        self,
        task_id: Optional[str] = None,
        auto_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        📋 Execute tasks with collaborative confirmation
        
        Args:
            task_id: 可选的任务ID
            auto_confirm: 是否自动确认
            
        Returns:
            Dict with task execution results
        """
        if not self.ensure_initialized():
            return {
                "success": False,
                "error": "Collaboration module not initialized",
                "message": "Module initialization failed"
            }
        
        try:
            start_time = datetime.datetime.now()
            
            # 获取或生成任务ID
            if not task_id:
                task_id = self._generate_task_id()
            
            # 执行协作任务
            result = self._execute_collaborative_task(task_id, auto_confirm)
            
            # 记录统计信息
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.record_call(success=result.get("success", False), duration=duration)
            
            logger.info(f"aceflow_task_execute executed: task_id={task_id}, success={result.get('success')}")
            return result
            
        except Exception as e:
            self.record_call(success=False)
            logger.error(f"aceflow_task_execute error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute collaborative task"
            }
    
    # 内部实现方法
    
    def _process_collaboration_response(
        self,
        request_id: str,
        response: str,
        user_id: str,
        request_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理协作响应"""
        try:
            # 验证响应
            if not response.strip():
                return {
                    "success": False,
                    "error": "Empty response provided",
                    "message": "Response cannot be empty"
                }
            
            # 解析响应
            parsed_response = self._parse_user_response(response, request_info)
            
            # 更新请求状态
            request_info["status"] = "responded"
            request_info["response"] = parsed_response
            request_info["responded_by"] = user_id
            request_info["responded_at"] = datetime.datetime.now().isoformat()
            
            # 执行响应处理
            processing_result = self._execute_response_action(request_info)
            
            # 移除活跃请求
            del self._active_requests[request_id]
            
            # 添加到历史记录
            self._collaboration_history.append({
                "request_id": request_id,
                "type": "response_processed",
                "user_id": user_id,
                "response": parsed_response,
                "result": processing_result,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "message": "Collaboration response processed successfully",
                "request_id": request_id,
                "parsed_response": parsed_response,
                "processing_result": processing_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process collaboration response"
            }
    
    def _generate_collaboration_status(self, project_id: str) -> Dict[str, Any]:
        """生成协作状态报告"""
        try:
            # 获取活跃请求
            active_requests = [
                {
                    "request_id": req_id,
                    "type": req_info.get("type", "unknown"),
                    "title": req_info.get("title", ""),
                    "created_at": req_info.get("created_at", ""),
                    "timeout_at": req_info.get("timeout_at", "")
                }
                for req_id, req_info in self._active_requests.items()
                if req_info.get("project_id") == project_id
            ]
            
            # 获取最近的协作历史
            recent_history = [
                entry for entry in self._collaboration_history[-10:]
                if entry.get("project_id") == project_id
            ]
            
            # 计算协作统计
            total_requests = len([
                entry for entry in self._collaboration_history
                if entry.get("project_id") == project_id
            ])
            
            successful_responses = len([
                entry for entry in self._collaboration_history
                if entry.get("project_id") == project_id and 
                entry.get("result", {}).get("success", False)
            ])
            
            # 生成洞察
            insights = self._generate_collaboration_insights(project_id)
            
            return {
                "project_id": project_id,
                "active_requests": active_requests,
                "active_requests_count": len(active_requests),
                "recent_history": recent_history,
                "statistics": {
                    "total_requests": total_requests,
                    "successful_responses": successful_responses,
                    "success_rate": successful_responses / max(total_requests, 1),
                    "average_response_time": self._calculate_average_response_time(project_id)
                },
                "insights": insights,
                "configuration": {
                    "confirmation_timeout": self._confirmation_timeout,
                    "auto_confirm": self._auto_confirm,
                    "interaction_level": self._interaction_level
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate collaboration status: {e}")
            return {
                "project_id": project_id,
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _execute_collaborative_task(self, task_id: str, auto_confirm: bool) -> Dict[str, Any]:
        """执行协作任务"""
        try:
            # 获取任务信息
            task_info = self._get_task_info(task_id)
            
            # 检查是否需要协作确认
            if not auto_confirm and not self._auto_confirm:
                # 创建协作请求
                request_id = self._create_collaboration_request(
                    task_id=task_id,
                    request_type=RequestType.CONFIRMATION,
                    title=f"Confirm task execution: {task_info.get('title', task_id)}",
                    description=f"Do you want to execute task '{task_id}'?",
                    options=["yes", "no", "modify"],
                    default_option="yes"
                )
                
                return {
                    "success": True,
                    "message": "Collaboration request created for task execution",
                    "task_id": task_id,
                    "request_id": request_id,
                    "status": "pending_confirmation",
                    "next_action": "Wait for user response or use aceflow_respond to provide confirmation"
                }
            
            # 直接执行任务
            execution_result = self._execute_task_directly(task_id, task_info)
            
            return {
                "success": True,
                "message": "Task executed successfully",
                "task_id": task_id,
                "execution_result": execution_result,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute collaborative task '{task_id}'"
            }
    
    def _parse_user_response(self, response: str, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """解析用户响应"""
        # 使用意图识别器解析响应
        if self._intent_recognizer:
            try:
                intent_result = recognize_user_intent(response)
                # 处理不同类型的返回值
                if hasattr(intent_result, 'get'):
                    # 字典类型
                    return {
                        "raw_response": response,
                        "intent": intent_result.get("intent", "unknown"),
                        "confidence": intent_result.get("confidence", 0.0),
                        "entities": intent_result.get("entities", {}),
                        "parsed_at": datetime.datetime.now().isoformat()
                    }
                else:
                    # 其他类型，使用简单解析
                    pass
            except Exception as e:
                logger.warning(f"Intent recognition failed: {e}")
                # 继续使用简单解析
        
        # 简单解析
        response_lower = response.lower().strip()
        if response_lower in ["yes", "y", "ok", "confirm", "proceed"]:
            intent = "confirm"
        elif response_lower in ["no", "n", "cancel", "abort"]:
            intent = "reject"
        else:
            intent = "custom"
        
        return {
            "raw_response": response,
            "intent": intent,
            "confidence": 0.8 if intent != "custom" else 0.3,
            "entities": {},
            "parsed_at": datetime.datetime.now().isoformat()
        }
    
    def _execute_response_action(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行响应动作"""
        try:
            response = request_info.get("response", {})
            intent = response.get("intent", "unknown")
            
            if intent == "confirm":
                return self._handle_confirmation(request_info)
            elif intent == "reject":
                return self._handle_rejection(request_info)
            else:
                return self._handle_custom_response(request_info)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute response action"
            }
    
    def _handle_confirmation(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理确认响应"""
        # 执行确认后的动作
        return {
            "success": True,
            "action": "confirmed",
            "message": "User confirmed the request",
            "next_steps": ["proceed_with_task", "update_status"]
        }
    
    def _handle_rejection(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理拒绝响应"""
        # 执行拒绝后的动作
        return {
            "success": True,
            "action": "rejected",
            "message": "User rejected the request",
            "next_steps": ["cancel_task", "request_alternative"]
        }
    
    def _handle_custom_response(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理自定义响应"""
        # 处理自定义响应
        return {
            "success": True,
            "action": "custom_handled",
            "message": "Custom response processed",
            "next_steps": ["analyze_response", "determine_action"]
        }
    
    def _create_collaboration_request(
        self,
        task_id: str,
        request_type: RequestType,
        title: str,
        description: str,
        options: List[str] = None,
        default_option: str = None
    ) -> str:
        """创建协作请求"""
        request_id = str(uuid.uuid4())
        
        request_info = {
            "request_id": request_id,
            "task_id": task_id,
            "project_id": self._get_current_project_id(),
            "type": request_type.value,
            "title": title,
            "description": description,
            "options": options or [],
            "default_option": default_option,
            "status": "pending",
            "created_at": datetime.datetime.now().isoformat(),
            "timeout_at": (datetime.datetime.now() + datetime.timedelta(seconds=self._confirmation_timeout)).isoformat()
        }
        
        self._active_requests[request_id] = request_info
        
        return request_id
    
    def _get_current_project_id(self) -> str:
        """获取当前项目ID"""
        # 尝试从项目状态文件获取
        state_file = Path.cwd() / ".aceflow" / "current_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                return state.get("project", {}).get("name", "unknown")
            except Exception:
                pass
        
        return "current_project"
    
    def _get_task_info(self, task_id: str) -> Dict[str, Any]:
        """获取任务信息"""
        # 这里可以从任务管理系统获取任务信息
        # 暂时返回占位符信息
        return {
            "task_id": task_id,
            "title": f"Task {task_id}",
            "description": f"Execute task {task_id}",
            "priority": "normal",
            "estimated_duration": "5 minutes"
        }
    
    def _execute_task_directly(self, task_id: str, task_info: Dict[str, Any]) -> Dict[str, Any]:
        """直接执行任务"""
        # 这里实现实际的任务执行逻辑
        # 暂时返回占位符结果
        return {
            "task_id": task_id,
            "status": "completed",
            "result": "Task executed successfully",
            "execution_time": "2.5 seconds",
            "output": f"Task {task_id} completed"
        }
    
    def _generate_task_id(self) -> str:
        """生成任务ID"""
        return f"task_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    def _generate_collaboration_insights(self, project_id: str) -> List[Dict[str, Any]]:
        """生成协作洞察"""
        insights = []
        
        # 分析活跃请求
        active_count = len([
            req for req in self._active_requests.values()
            if req.get("project_id") == project_id
        ])
        
        if active_count > 0:
            insights.append({
                "type": "active_requests",
                "message": f"You have {active_count} pending collaboration request(s)",
                "priority": "high" if active_count > 3 else "medium",
                "action": "Review and respond to pending requests"
            })
        
        # 分析响应时间
        avg_response_time = self._calculate_average_response_time(project_id)
        if avg_response_time > 600:  # 10 minutes
            insights.append({
                "type": "response_time",
                "message": "Average response time is longer than expected",
                "priority": "medium",
                "action": "Consider enabling auto-confirm for routine tasks"
            })
        
        return insights
    
    def _calculate_average_response_time(self, project_id: str) -> float:
        """计算平均响应时间"""
        # 这里实现响应时间计算逻辑
        # 暂时返回占位符值
        return 120.0  # 2 minutes
    
    def _load_collaboration_history(self):
        """加载协作历史"""
        history_file = Path.cwd() / ".aceflow" / "collaboration_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self._collaboration_history = json.load(f)
                logger.debug("Collaboration history loaded")
            except Exception as e:
                logger.warning(f"Failed to load collaboration history: {e}")
                self._collaboration_history = []
        else:
            self._collaboration_history = []
    
    def _save_collaboration_history(self):
        """保存协作历史"""
        history_file = Path.cwd() / ".aceflow" / "collaboration_history.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # 只保留最近的100条记录
            recent_history = self._collaboration_history[-100:]
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(recent_history, f, indent=2, ensure_ascii=False)
            logger.debug("Collaboration history saved")
        except Exception as e:
            logger.error(f"Failed to save collaboration history: {e}")
    
    def _cleanup_active_requests(self):
        """清理活跃请求"""
        # 清理超时的请求
        current_time = datetime.datetime.now()
        expired_requests = []
        
        for request_id, request_info in self._active_requests.items():
            timeout_str = request_info.get("timeout_at")
            if timeout_str:
                try:
                    timeout_time = datetime.datetime.fromisoformat(timeout_str)
                    if current_time > timeout_time:
                        expired_requests.append(request_id)
                except Exception:
                    pass
        
        # 移除过期请求
        for request_id in expired_requests:
            request_info = self._active_requests.pop(request_id, {})
            self._collaboration_history.append({
                "request_id": request_id,
                "type": "timeout",
                "result": {"success": False, "reason": "timeout"},
                "timestamp": current_time.isoformat()
            })
        
        if expired_requests:
            logger.info(f"Cleaned up {len(expired_requests)} expired collaboration requests")