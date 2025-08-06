"""
协作管理器 - AceFlow AI-人协同工作流
Collaboration Manager for AceFlow AI-Human Collaborative Workflow
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from datetime import datetime, timedelta
from pathlib import Path


class RequestType(Enum):
    """协作请求类型"""
    CONFIRMATION = "confirmation"
    INPUT = "input"
    REVIEW = "review"
    DECISION = "decision"
    APPROVAL = "approval"


class RequestStatus(Enum):
    """请求状态"""
    PENDING = "pending"
    RESPONDED = "responded"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class CollaborationRequest:
    """协作请求"""
    request_id: str
    project_id: str
    stage_id: str
    request_type: RequestType
    title: str
    description: str
    options: List[str] = field(default_factory=list)
    default_option: Optional[str] = None
    timeout_seconds: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationResponse:
    """协作响应"""
    request_id: str
    user_id: str
    response: str
    confidence: float
    additional_context: Optional[str] = None
    responded_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationHistory:
    """协作历史记录"""
    project_id: str
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class CollaborationManager:
    """协作管理器"""
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        """
        初始化协作管理器
        
        Args:
            workspace_dir: 工作空间目录
        """
        self.workspace_dir = workspace_dir or Path.cwd()
        self.collaboration_dir = self.workspace_dir / ".aceflow" / "collaboration"
        self.collaboration_dir.mkdir(parents=True, exist_ok=True)
        
        # 活跃的请求
        self.active_requests: Dict[str, CollaborationRequest] = {}
        
        # 协作历史
        self.collaboration_histories: Dict[str, CollaborationHistory] = {}
        
        # 用户响应回调
        self.response_callbacks: Dict[str, Callable] = {}
        
        # 加载现有的协作历史
        self._load_collaboration_histories()
    
    def request_confirmation(
        self,
        project_id: str,
        stage_id: str,
        title: str,
        description: str,
        default_option: str = "yes",
        timeout_seconds: Optional[int] = 300
    ) -> str:
        """
        请求用户确认
        
        Args:
            project_id: 项目ID
            stage_id: 阶段ID
            title: 确认标题
            description: 确认描述
            default_option: 默认选项
            timeout_seconds: 超时时间(秒)
            
        Returns:
            str: 请求ID
        """
        request_id = self._generate_request_id()
        
        request = CollaborationRequest(
            request_id=request_id,
            project_id=project_id,
            stage_id=stage_id,
            request_type=RequestType.CONFIRMATION,
            title=title,
            description=description,
            options=["yes", "no"],
            default_option=default_option,
            timeout_seconds=timeout_seconds
        )
        
        self.active_requests[request_id] = request
        self._save_request(request)
        
        # 记录到协作历史
        self._add_to_history(project_id, {
            "type": "confirmation_request",
            "request_id": request_id,
            "title": title,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
        
        return request_id
    
    def request_input(
        self,
        project_id: str,
        stage_id: str,
        title: str,
        description: str,
        input_type: str = "text",
        timeout_seconds: Optional[int] = 600
    ) -> str:
        """
        请求用户输入
        
        Args:
            project_id: 项目ID
            stage_id: 阶段ID
            title: 输入标题
            description: 输入描述
            input_type: 输入类型
            timeout_seconds: 超时时间(秒)
            
        Returns:
            str: 请求ID
        """
        request_id = self._generate_request_id()
        
        request = CollaborationRequest(
            request_id=request_id,
            project_id=project_id,
            stage_id=stage_id,
            request_type=RequestType.INPUT,
            title=title,
            description=description,
            timeout_seconds=timeout_seconds,
            metadata={"input_type": input_type}
        )
        
        self.active_requests[request_id] = request
        self._save_request(request)
        
        # 记录到协作历史
        self._add_to_history(project_id, {
            "type": "input_request",
            "request_id": request_id,
            "title": title,
            "description": description,
            "input_type": input_type,
            "timestamp": datetime.now().isoformat()
        })
        
        return request_id
    
    def request_review(
        self,
        project_id: str,
        stage_id: str,
        title: str,
        description: str,
        review_content: Dict[str, Any],
        timeout_seconds: Optional[int] = 900
    ) -> str:
        """
        请求用户审查
        
        Args:
            project_id: 项目ID
            stage_id: 阶段ID
            title: 审查标题
            description: 审查描述
            review_content: 审查内容
            timeout_seconds: 超时时间(秒)
            
        Returns:
            str: 请求ID
        """
        request_id = self._generate_request_id()
        
        request = CollaborationRequest(
            request_id=request_id,
            project_id=project_id,
            stage_id=stage_id,
            request_type=RequestType.REVIEW,
            title=title,
            description=description,
            options=["approve", "reject", "modify"],
            default_option="approve",
            timeout_seconds=timeout_seconds,
            metadata={"review_content": review_content}
        )
        
        self.active_requests[request_id] = request
        self._save_request(request)
        
        # 记录到协作历史
        self._add_to_history(project_id, {
            "type": "review_request",
            "request_id": request_id,
            "title": title,
            "description": description,
            "review_content": review_content,
            "timestamp": datetime.now().isoformat()
        })
        
        return request_id
    
    def request_decision(
        self,
        project_id: str,
        stage_id: str,
        title: str,
        description: str,
        options: List[str],
        default_option: Optional[str] = None,
        timeout_seconds: Optional[int] = 600
    ) -> str:
        """
        请求用户决策
        
        Args:
            project_id: 项目ID
            stage_id: 阶段ID
            title: 决策标题
            description: 决策描述
            options: 选项列表
            default_option: 默认选项
            timeout_seconds: 超时时间(秒)
            
        Returns:
            str: 请求ID
        """
        request_id = self._generate_request_id()
        
        request = CollaborationRequest(
            request_id=request_id,
            project_id=project_id,
            stage_id=stage_id,
            request_type=RequestType.DECISION,
            title=title,
            description=description,
            options=options,
            default_option=default_option,
            timeout_seconds=timeout_seconds
        )
        
        self.active_requests[request_id] = request
        self._save_request(request)
        
        # 记录到协作历史
        self._add_to_history(project_id, {
            "type": "decision_request",
            "request_id": request_id,
            "title": title,
            "description": description,
            "options": options,
            "default_option": default_option,
            "timestamp": datetime.now().isoformat()
        })
        
        return request_id
    
    def respond_to_request(
        self,
        request_id: str,
        response: str,
        user_id: str = "user",
        confidence: float = 1.0,
        additional_context: Optional[str] = None
    ) -> bool:
        """
        响应协作请求
        
        Args:
            request_id: 请求ID
            response: 响应内容
            user_id: 用户ID
            confidence: 置信度
            additional_context: 额外上下文
            
        Returns:
            bool: 是否成功响应
        """
        if request_id not in self.active_requests:
            return False
        
        request = self.active_requests[request_id]
        
        # 创建响应
        collaboration_response = CollaborationResponse(
            request_id=request_id,
            user_id=user_id,
            response=response,
            confidence=confidence,
            additional_context=additional_context
        )
        
        # 保存响应
        self._save_response(collaboration_response)
        
        # 记录到协作历史
        self._add_to_history(request.project_id, {
            "type": "response",
            "request_id": request_id,
            "response": response,
            "user_id": user_id,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        })
        
        # 移除活跃请求
        del self.active_requests[request_id]
        
        # 调用回调函数
        if request_id in self.response_callbacks:
            callback = self.response_callbacks[request_id]
            callback(collaboration_response)
            del self.response_callbacks[request_id]
        
        return True
    
    def wait_for_response(
        self,
        request_id: str,
        timeout_seconds: Optional[int] = None
    ) -> Optional[CollaborationResponse]:
        """
        等待用户响应
        
        Args:
            request_id: 请求ID
            timeout_seconds: 超时时间(秒)
            
        Returns:
            Optional[CollaborationResponse]: 用户响应，如果超时则返回None
        """
        if request_id not in self.active_requests:
            return None
        
        request = self.active_requests[request_id]
        timeout = timeout_seconds or request.timeout_seconds or 300
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 检查是否有响应文件
            response_file = self.collaboration_dir / f"response_{request_id}.json"
            if response_file.exists():
                try:
                    with open(response_file, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)
                    
                    response = CollaborationResponse(**response_data)
                    
                    # 清理文件
                    response_file.unlink()
                    
                    # 移除活跃请求
                    if request_id in self.active_requests:
                        del self.active_requests[request_id]
                    
                    return response
                    
                except Exception as e:
                    print(f"Error loading response: {e}")
            
            time.sleep(1)
        
        # 超时处理
        self._handle_timeout(request_id)
        return None
    
    def get_active_requests(self, project_id: Optional[str] = None) -> List[CollaborationRequest]:
        """
        获取活跃的协作请求
        
        Args:
            project_id: 项目ID，如果为None则返回所有请求
            
        Returns:
            List[CollaborationRequest]: 活跃请求列表
        """
        if project_id is None:
            return list(self.active_requests.values())
        
        return [req for req in self.active_requests.values() if req.project_id == project_id]
    
    def get_collaboration_history(self, project_id: str) -> Optional[CollaborationHistory]:
        """
        获取协作历史
        
        Args:
            project_id: 项目ID
            
        Returns:
            Optional[CollaborationHistory]: 协作历史
        """
        return self.collaboration_histories.get(project_id)
    
    def cancel_request(self, request_id: str) -> bool:
        """
        取消协作请求
        
        Args:
            request_id: 请求ID
            
        Returns:
            bool: 是否成功取消
        """
        if request_id not in self.active_requests:
            return False
        
        request = self.active_requests[request_id]
        
        # 记录到协作历史
        self._add_to_history(request.project_id, {
            "type": "request_cancelled",
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # 移除活跃请求
        del self.active_requests[request_id]
        
        # 清理相关文件
        request_file = self.collaboration_dir / f"request_{request_id}.json"
        if request_file.exists():
            request_file.unlink()
        
        return True
    
    def set_response_callback(self, request_id: str, callback: Callable):
        """
        设置响应回调函数
        
        Args:
            request_id: 请求ID
            callback: 回调函数
        """
        self.response_callbacks[request_id] = callback
    
    def _generate_request_id(self) -> str:
        """生成请求ID"""
        timestamp = int(time.time() * 1000)
        return f"req_{timestamp}"
    
    def _save_request(self, request: CollaborationRequest):
        """保存请求到文件"""
        request_file = self.collaboration_dir / f"request_{request.request_id}.json"
        
        request_data = {
            "request_id": request.request_id,
            "project_id": request.project_id,
            "stage_id": request.stage_id,
            "request_type": request.request_type.value,
            "title": request.title,
            "description": request.description,
            "options": request.options,
            "default_option": request.default_option,
            "timeout_seconds": request.timeout_seconds,
            "created_at": request.created_at.isoformat(),
            "metadata": request.metadata
        }
        
        with open(request_file, 'w', encoding='utf-8') as f:
            json.dump(request_data, f, indent=2, ensure_ascii=False)
    
    def _save_response(self, response: CollaborationResponse):
        """保存响应到文件"""
        response_file = self.collaboration_dir / f"response_{response.request_id}.json"
        
        response_data = {
            "request_id": response.request_id,
            "user_id": response.user_id,
            "response": response.response,
            "confidence": response.confidence,
            "additional_context": response.additional_context,
            "responded_at": response.responded_at.isoformat(),
            "metadata": response.metadata
        }
        
        with open(response_file, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
    
    def _add_to_history(self, project_id: str, interaction: Dict[str, Any]):
        """添加交互到历史记录"""
        if project_id not in self.collaboration_histories:
            self.collaboration_histories[project_id] = CollaborationHistory(project_id=project_id)
        
        history = self.collaboration_histories[project_id]
        history.interactions.append(interaction)
        history.updated_at = datetime.now()
        
        # 保存历史记录
        self._save_collaboration_history(history)
    
    def _save_collaboration_history(self, history: CollaborationHistory):
        """保存协作历史到文件"""
        history_file = self.collaboration_dir / f"history_{history.project_id}.json"
        
        history_data = {
            "project_id": history.project_id,
            "interactions": history.interactions,
            "created_at": history.created_at.isoformat(),
            "updated_at": history.updated_at.isoformat()
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)
    
    def _load_collaboration_histories(self):
        """加载现有的协作历史"""
        if not self.collaboration_dir.exists():
            return
        
        for history_file in self.collaboration_dir.glob("history_*.json"):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                
                history = CollaborationHistory(
                    project_id=history_data["project_id"],
                    interactions=history_data["interactions"],
                    created_at=datetime.fromisoformat(history_data["created_at"]),
                    updated_at=datetime.fromisoformat(history_data["updated_at"])
                )
                
                self.collaboration_histories[history.project_id] = history
                
            except Exception as e:
                print(f"Error loading collaboration history from {history_file}: {e}")
    
    def _handle_timeout(self, request_id: str):
        """处理请求超时"""
        if request_id not in self.active_requests:
            return
        
        request = self.active_requests[request_id]
        
        # 使用默认选项作为响应
        default_response = request.default_option or "timeout"
        
        # 创建超时响应
        timeout_response = CollaborationResponse(
            request_id=request_id,
            user_id="system",
            response=default_response,
            confidence=0.0,
            additional_context="Request timed out, using default option"
        )
        
        # 记录到协作历史
        self._add_to_history(request.project_id, {
            "type": "timeout",
            "request_id": request_id,
            "default_response": default_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # 移除活跃请求
        del self.active_requests[request_id]
        
        # 调用回调函数
        if request_id in self.response_callbacks:
            callback = self.response_callbacks[request_id]
            callback(timeout_response)
            del self.response_callbacks[request_id]


# 工厂函数
def create_collaboration_manager(workspace_dir: Optional[Path] = None) -> CollaborationManager:
    """创建协作管理器实例"""
    return CollaborationManager(workspace_dir)


# 便捷函数
def request_user_confirmation(
    title: str,
    description: str,
    project_id: str = "default",
    stage_id: str = "current",
    timeout_seconds: int = 300
) -> str:
    """
    便捷的用户确认请求函数
    
    Args:
        title: 确认标题
        description: 确认描述
        project_id: 项目ID
        stage_id: 阶段ID
        timeout_seconds: 超时时间
        
    Returns:
        str: 请求ID
    """
    manager = create_collaboration_manager()
    return manager.request_confirmation(
        project_id=project_id,
        stage_id=stage_id,
        title=title,
        description=description,
        timeout_seconds=timeout_seconds
    )