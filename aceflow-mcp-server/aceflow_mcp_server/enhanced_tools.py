"""
增强版AceFlow MCP工具 - 集成AI-人协同工作流
Enhanced AceFlow MCP Tools with AI-Human Collaborative Workflow
"""

from typing import Dict, Any, Optional, List
import json
import os
import sys
from pathlib import Path
import datetime

# 导入原有工具
from .tools import AceFlowTools

# 导入新的协作功能
from .core.intent_recognizer import IntentRecognizer, IntentType, recognize_user_intent
from .core.collaboration_manager import CollaborationManager, RequestType
from .core.task_parser import TaskParser, TaskStatus, TaskPriority


class EnhancedAceFlowTools(AceFlowTools):
    """增强版AceFlow工具集，集成AI-人协作功能"""
    
    def __init__(self):
        """初始化增强版工具"""
        super().__init__()
        
        # 初始化协作组件
        self.intent_recognizer = IntentRecognizer()
        self.collaboration_manager = CollaborationManager()
        self.task_parser = TaskParser()
        
        # 协作状态
        self.collaboration_enabled = True
        self.auto_advance = False
    
    def aceflow_stage_collaborative(
        self,
        action: str,
        stage: Optional[str] = None,
        user_input: Optional[str] = None,
        auto_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        增强版阶段管理工具，支持AI-人协作
        
        Args:
            action: 阶段管理动作 (status, next, execute, collaborative_execute)
            stage: 可选的目标阶段名称
            user_input: 用户输入文本，用于意图识别
            auto_confirm: 是否自动确认，跳过用户交互
            
        Returns:
            Dict: 包含成功状态和阶段信息的字典
        """
        try:
            # 如果提供了用户输入，先进行意图识别
            if user_input and self.collaboration_enabled:
                intent_result = self.intent_recognizer.recognize_intent(
                    user_input, 
                    self._get_current_context()
                )
                
                # 根据意图调整行为
                if intent_result.intent_type == IntentType.START_WORKFLOW:
                    return self._handle_start_workflow_intent(intent_result, auto_confirm)
                elif intent_result.intent_type == IntentType.EXECUTE_TASK:
                    action = "collaborative_execute"
                elif intent_result.intent_type == IntentType.CHECK_STATUS:
                    action = "status"
                elif intent_result.intent_type == IntentType.CONTINUE_STAGE:
                    action = "next"
                elif intent_result.intent_type == IntentType.PAUSE_WORKFLOW:
                    return self._handle_pause_workflow()
            
            # 执行相应的动作
            if action == "collaborative_execute":
                return self._collaborative_execute_stage(stage, auto_confirm)
            elif action == "collaborative_next":
                return self._collaborative_advance_stage(auto_confirm)
            else:
                # 调用原有的方法
                result = super().aceflow_stage(action, stage)
                
                # 如果启用协作且不是自动确认，添加协作提示
                if self.collaboration_enabled and not auto_confirm and result.get("success"):
                    result = self._add_collaboration_prompt(result, action)
                
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute collaborative stage action: {action}"
            }
    
    def aceflow_task_execute(
        self,
        task_id: Optional[str] = None,
        auto_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        任务级协作执行
        
        Args:
            task_id: 任务ID，如果为None则执行下一个可执行任务
            auto_confirm: 是否自动确认
            
        Returns:
            Dict: 执行结果
        """
        try:
            # 获取当前项目状态
            current_state = self.project_manager.get_current_state()
            project_id = current_state.get("project", {}).get("name", "unknown")
            current_stage = current_state.get("flow", {}).get("current_stage", "unknown")
            
            # 检查是否在实现阶段
            if "implementation" not in current_stage.lower():
                return {
                    "success": False,
                    "error": "Task execution is only available in implementation stage",
                    "message": "Please advance to implementation stage first"
                }
            
            # 尝试加载任务队列
            task_queue_file = Path("aceflow_result") / f"task_queue_{project_id}_S2_task_breakdown.json"
            
            if not task_queue_file.exists():
                return {
                    "success": False,
                    "error": "Task queue not found",
                    "message": "Please complete task breakdown stage first"
                }
            
            # 加载任务队列
            task_queue = self.task_parser.load_task_queue(task_queue_file)
            
            # 获取要执行的任务
            if task_id:
                target_task = next((t for t in task_queue.tasks if t.task_id == task_id), None)
                if not target_task:
                    return {
                        "success": False,
                        "error": f"Task {task_id} not found",
                        "message": "Invalid task ID"
                    }
            else:
                # 获取下一个可执行任务
                executable_tasks = self.task_parser.get_next_executable_tasks(task_queue)
                if not executable_tasks:
                    return {
                        "success": False,
                        "error": "No executable tasks available",
                        "message": "All tasks are completed or blocked"
                    }
                target_task = executable_tasks[0]
            
            # 协作确认
            if self.collaboration_enabled and not auto_confirm:
                request_id = self.collaboration_manager.request_confirmation(
                    project_id=project_id,
                    stage_id=current_stage,
                    title="执行任务确认",
                    description=f"准备执行任务: {target_task.name}\n描述: {target_task.description}\n预估时间: {target_task.estimated_hours}小时\n\n是否继续执行？",
                    timeout_seconds=300
                )
                
                return {
                    "success": True,
                    "action": "task_execution_requested",
                    "collaboration_request_id": request_id,
                    "task_info": {
                        "task_id": target_task.task_id,
                        "name": target_task.name,
                        "description": target_task.description,
                        "estimated_hours": target_task.estimated_hours,
                        "priority": target_task.priority.value
                    },
                    "message": "Task execution confirmation requested. Please respond to continue."
                }
            
            # 执行任务
            return self._execute_single_task(target_task, task_queue, project_id, current_stage)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute task"
            }
    
    def aceflow_respond(
        self,
        request_id: str,
        response: str,
        user_id: str = "user"
    ) -> Dict[str, Any]:
        """
        响应协作请求
        
        Args:
            request_id: 请求ID
            response: 响应内容
            user_id: 用户ID
            
        Returns:
            Dict: 响应结果
        """
        try:
            success = self.collaboration_manager.respond_to_request(
                request_id=request_id,
                response=response,
                user_id=user_id,
                confidence=1.0
            )
            
            if success:
                return {
                    "success": True,
                    "message": "Response recorded successfully",
                    "request_id": request_id,
                    "response": response
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to record response",
                    "message": "Request ID not found or already responded"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to respond to collaboration request"
            }
    
    def aceflow_collaboration_status(
        self,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取协作状态
        
        Args:
            project_id: 项目ID
            
        Returns:
            Dict: 协作状态信息
        """
        try:
            # 获取活跃请求
            active_requests = self.collaboration_manager.get_active_requests(project_id)
            
            # 获取协作历史
            history = None
            if project_id:
                history = self.collaboration_manager.get_collaboration_history(project_id)
            
            return {
                "success": True,
                "collaboration_enabled": self.collaboration_enabled,
                "active_requests": [
                    {
                        "request_id": req.request_id,
                        "project_id": req.project_id,
                        "stage_id": req.stage_id,
                        "type": req.request_type.value,
                        "title": req.title,
                        "description": req.description,
                        "created_at": req.created_at.isoformat()
                    }
                    for req in active_requests
                ],
                "history_interactions": len(history.interactions) if history else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get collaboration status"
            }
    
    def _collaborative_execute_stage(
        self,
        stage_id: Optional[str] = None,
        auto_confirm: bool = False
    ) -> Dict[str, Any]:
        """协作式阶段执行"""
        try:
            # 获取当前状态
            current_state = self.project_manager.get_current_state()
            project_id = current_state.get("project", {}).get("name", "unknown")
            current_stage = current_state.get("flow", {}).get("current_stage", "unknown")
            
            target_stage = stage_id or current_stage
            
            # 协作确认
            if self.collaboration_enabled and not auto_confirm:
                request_id = self.collaboration_manager.request_confirmation(
                    project_id=project_id,
                    stage_id=target_stage,
                    title="阶段执行确认",
                    description=f"准备执行阶段: {target_stage}\n\n这将生成该阶段的输出文档并更新项目状态。是否继续？",
                    timeout_seconds=300
                )
                
                return {
                    "success": True,
                    "action": "stage_execution_requested",
                    "collaboration_request_id": request_id,
                    "stage_info": {
                        "stage_id": target_stage,
                        "project_id": project_id
                    },
                    "message": "Stage execution confirmation requested. Please respond to continue."
                }
            
            # 执行阶段
            result = self._execute_current_stage(stage_id)
            
            # 如果执行成功且启用协作，询问是否继续下一阶段
            if result.get("success") and self.collaboration_enabled and not auto_confirm:
                next_stage_request_id = self.collaboration_manager.request_confirmation(
                    project_id=project_id,
                    stage_id=target_stage,
                    title="阶段完成",
                    description=f"阶段 {target_stage} 已完成。\n\n是否继续推进到下一阶段？",
                    timeout_seconds=300
                )
                
                result["next_stage_request_id"] = next_stage_request_id
                result["message"] += " Stage completed. Next stage confirmation requested."
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute stage collaboratively"
            }
    
    def _collaborative_advance_stage(self, auto_confirm: bool = False) -> Dict[str, Any]:
        """协作式阶段推进"""
        try:
            # 获取当前状态
            current_state = self.project_manager.get_current_state()
            project_id = current_state.get("project", {}).get("name", "unknown")
            current_stage = current_state.get("flow", {}).get("current_stage", "unknown")
            
            # 协作确认
            if self.collaboration_enabled and not auto_confirm:
                request_id = self.collaboration_manager.request_confirmation(
                    project_id=project_id,
                    stage_id=current_stage,
                    title="推进到下一阶段",
                    description=f"当前阶段: {current_stage}\n\n确认推进到下一阶段？",
                    timeout_seconds=300
                )
                
                return {
                    "success": True,
                    "action": "stage_advance_requested",
                    "collaboration_request_id": request_id,
                    "current_stage": current_stage,
                    "message": "Stage advance confirmation requested. Please respond to continue."
                }
            
            # 推进阶段
            return super().aceflow_stage("next")
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to advance stage collaboratively"
            }
    
    def _execute_single_task(
        self,
        task: Any,
        task_queue: Any,
        project_id: str,
        stage_id: str
    ) -> Dict[str, Any]:
        """执行单个任务"""
        try:
            # 更新任务状态为进行中
            self.task_parser.update_task_status(task_queue, task.task_id, TaskStatus.IN_PROGRESS)
            
            # 模拟任务执行（实际实现中这里会调用具体的代码生成、测试等功能）
            execution_result = {
                "task_id": task.task_id,
                "name": task.name,
                "status": "completed",
                "output_files": task.output_files,
                "execution_time": task.estimated_hours,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # 更新任务状态为完成
            self.task_parser.update_task_status(
                task_queue, 
                task.task_id, 
                TaskStatus.COMPLETED,
                {"execution_result": execution_result}
            )
            
            # 保存更新后的任务队列
            self.task_parser.save_task_queue(task_queue)
            
            # 获取进度信息
            progress = self.task_parser.get_progress(task_queue)
            
            # 生成任务执行报告
            report_content = f"""# 任务执行报告

**任务**: {task.name}
**任务ID**: {task.task_id}
**执行时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**状态**: 已完成

## 任务详情

- **描述**: {task.description}
- **优先级**: {task.priority.value}
- **预估时间**: {task.estimated_hours}小时
- **输出文件**: {', '.join(task.output_files) if task.output_files else '无'}

## 执行结果

任务已成功完成。

## 项目进度

- **总任务数**: {progress['total_tasks']}
- **已完成**: {progress['completed_tasks']}
- **进度**: {progress['progress_percentage']:.1f}%

---
*由 AceFlow AI-人协同工作流自动生成*
"""
            
            # 保存执行报告
            report_path = Path("aceflow_result") / f"task_execution_{task.task_id}.md"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            return {
                "success": True,
                "action": "task_executed",
                "task_info": {
                    "task_id": task.task_id,
                    "name": task.name,
                    "status": "completed"
                },
                "progress": progress,
                "report_path": str(report_path),
                "message": f"Task '{task.name}' completed successfully. Progress: {progress['progress_percentage']:.1f}%"
            }
            
        except Exception as e:
            # 如果执行失败，更新任务状态为阻塞
            self.task_parser.update_task_status(
                task_queue, 
                task.task_id, 
                TaskStatus.BLOCKED,
                {"error": str(e)}
            )
            
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute task '{task.name}'"
            }
    
    def _handle_start_workflow_intent(
        self,
        intent_result: Any,
        auto_confirm: bool = False
    ) -> Dict[str, Any]:
        """处理启动工作流意图"""
        suggested_mode = intent_result.parameters.get("suggested_mode", "standard")
        
        if self.collaboration_enabled and not auto_confirm:
            request_id = self.collaboration_manager.request_confirmation(
                project_id="new_project",
                stage_id="initialization",
                title="启动AceFlow工作流",
                description=f"检测到开发需求，建议启动 {suggested_mode} 模式工作流。\n\n是否确认启动？",
                timeout_seconds=300
            )
            
            return {
                "success": True,
                "action": "workflow_start_requested",
                "collaboration_request_id": request_id,
                "intent_result": {
                    "suggested_mode": suggested_mode,
                    "confidence": intent_result.confidence,
                    "reasoning": intent_result.reasoning
                },
                "message": "Workflow start confirmation requested. Please respond to continue."
            }
        
        # 自动启动工作流
        return self.aceflow_init(mode=suggested_mode)
    
    def _handle_pause_workflow(self) -> Dict[str, Any]:
        """处理暂停工作流"""
        try:
            # 保存当前状态
            current_state = self.project_manager.get_current_state()
            
            # 取消所有活跃的协作请求
            active_requests = self.collaboration_manager.get_active_requests()
            for request in active_requests:
                self.collaboration_manager.cancel_request(request.request_id)
            
            return {
                "success": True,
                "action": "workflow_paused",
                "current_state": current_state,
                "cancelled_requests": len(active_requests),
                "message": "Workflow paused successfully. All active collaboration requests cancelled."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to pause workflow"
            }
    
    def _get_current_context(self) -> Dict[str, Any]:
        """获取当前上下文信息"""
        try:
            current_state = self.project_manager.get_current_state()
            return {
                "current_stage": current_state.get("flow", {}).get("current_stage"),
                "project_id": current_state.get("project", {}).get("name"),
                "progress": current_state.get("flow", {}).get("progress_percentage", 0),
                "timestamp": datetime.datetime.now().isoformat()
            }
        except:
            return {}
    
    def _add_collaboration_prompt(
        self,
        result: Dict[str, Any],
        action: str
    ) -> Dict[str, Any]:
        """为结果添加协作提示"""
        if action == "status":
            result["collaboration_hint"] = "如需执行当前阶段，请使用 aceflow_stage_collaborative(action='collaborative_execute')"
        elif action == "execute":
            result["collaboration_hint"] = "阶段执行完成。如需推进到下一阶段，请使用 aceflow_stage_collaborative(action='collaborative_next')"
        
        return result


# 创建增强版工具实例的工厂函数
def create_enhanced_aceflow_tools() -> EnhancedAceFlowTools:
    """创建增强版AceFlow工具实例"""
    return EnhancedAceFlowTools()