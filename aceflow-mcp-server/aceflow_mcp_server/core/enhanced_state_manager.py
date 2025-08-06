"""
增强版状态管理器 - AceFlow AI-人协同工作流
Enhanced State Manager for AceFlow AI-Human Collaborative Workflow
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


class StateChangeType(Enum):
    """状态变更类型"""
    STAGE_ADVANCE = "stage_advance"
    TASK_UPDATE = "task_update"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    VALIDATION_RESULT = "validation_result"
    PROJECT_INIT = "project_init"
    PROJECT_PAUSE = "project_pause"
    PROJECT_RESUME = "project_resume"


@dataclass
class StateSnapshot:
    """状态快照"""
    snapshot_id: str
    project_id: str
    timestamp: datetime
    state_data: Dict[str, Any]
    change_type: StateChangeType
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateChangeEvent:
    """状态变更事件"""
    event_id: str
    project_id: str
    change_type: StateChangeType
    old_state: Dict[str, Any]
    new_state: Dict[str, Any]
    timestamp: datetime
    description: str
    triggered_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateNotificationCallback:
    """状态通知回调"""
    
    def __init__(self, callback_id: str, callback_func, filter_types: Optional[List[StateChangeType]] = None):
        self.callback_id = callback_id
        self.callback_func = callback_func
        self.filter_types = filter_types or []
        self.created_at = datetime.now()
    
    def should_notify(self, change_type: StateChangeType) -> bool:
        """判断是否应该通知"""
        return not self.filter_types or change_type in self.filter_types


class EnhancedStateManager:
    """增强版状态管理器"""
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        """
        初始化增强版状态管理器
        
        Args:
            workspace_dir: 工作空间目录
        """
        self.workspace_dir = workspace_dir or Path.cwd()
        self.aceflow_dir = self.workspace_dir / ".aceflow"
        self.state_dir = self.aceflow_dir / "state"
        self.snapshots_dir = self.state_dir / "snapshots"
        self.events_dir = self.state_dir / "events"
        
        # 创建目录
        for dir_path in [self.aceflow_dir, self.state_dir, self.snapshots_dir, self.events_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 状态文件路径
        self.current_state_file = self.aceflow_dir / "current_state.json"
        self.collaboration_state_file = self.state_dir / "collaboration_state.json"
        self.task_state_file = self.state_dir / "task_state.json"
        
        # 内存状态缓存
        self._state_cache = {}
        self._cache_lock = threading.RLock()
        
        # 状态变更历史
        self._state_history = []
        self._snapshots = {}
        
        # 通知回调
        self._notification_callbacks = {}
        
        # 加载现有状态
        self._load_existing_states()
    
    def get_current_state(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取当前项目状态
        
        Args:
            project_id: 项目ID
            
        Returns:
            Dict: 当前状态
        """
        with self._cache_lock:
            try:
                if self.current_state_file.exists():
                    with open(self.current_state_file, 'r', encoding='utf-8') as f:
                        state_data = json.load(f)
                    
                    # 添加增强信息
                    enhanced_state = self._enhance_state_data(state_data, project_id)
                    
                    # 更新缓存
                    cache_key = project_id or "default"
                    self._state_cache[cache_key] = enhanced_state
                    
                    return enhanced_state
                else:
                    return self._create_default_state(project_id)
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to get current state"
                }
    
    def update_state(
        self,
        state_updates: Dict[str, Any],
        change_type: StateChangeType,
        description: str,
        project_id: Optional[str] = None,
        triggered_by: str = "system",
        create_snapshot: bool = True
    ) -> bool:
        """
        更新项目状态
        
        Args:
            state_updates: 状态更新数据
            change_type: 变更类型
            description: 变更描述
            project_id: 项目ID
            triggered_by: 触发者
            create_snapshot: 是否创建快照
            
        Returns:
            bool: 是否成功更新
        """
        with self._cache_lock:
            try:
                # 获取当前状态
                current_state = self.get_current_state(project_id)
                if not current_state.get("success", True):
                    return False
                
                # 创建状态快照（如果需要）
                if create_snapshot:
                    self._create_state_snapshot(current_state, change_type, description, project_id)
                
                # 应用状态更新
                old_state = current_state.copy()
                new_state = self._apply_state_updates(current_state, state_updates)
                
                # 保存新状态
                success = self._save_state(new_state, project_id)
                
                if success:
                    # 记录状态变更事件
                    self._record_state_change_event(
                        old_state, new_state, change_type, description, triggered_by, project_id
                    )
                    
                    # 触发通知回调
                    self._trigger_notifications(change_type, old_state, new_state, project_id)
                    
                    # 更新缓存
                    cache_key = project_id or "default"
                    self._state_cache[cache_key] = new_state
                
                return success
                
            except Exception as e:
                print(f"Error updating state: {e}")
                return False
    
    def get_collaboration_state(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取协作状态
        
        Args:
            project_id: 项目ID
            
        Returns:
            Dict: 协作状态
        """
        try:
            if self.collaboration_state_file.exists():
                with open(self.collaboration_state_file, 'r', encoding='utf-8') as f:
                    collaboration_data = json.load(f)
                
                # 过滤项目相关的协作状态
                if project_id:
                    project_collaboration = collaboration_data.get(project_id, {})
                else:
                    project_collaboration = collaboration_data
                
                return {
                    "success": True,
                    "collaboration_state": project_collaboration,
                    "last_updated": collaboration_data.get("last_updated", datetime.now().isoformat())
                }
            else:
                return {
                    "success": True,
                    "collaboration_state": {},
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get collaboration state"
            }
    
    def update_collaboration_state(
        self,
        collaboration_updates: Dict[str, Any],
        project_id: Optional[str] = None
    ) -> bool:
        """
        更新协作状态
        
        Args:
            collaboration_updates: 协作状态更新
            project_id: 项目ID
            
        Returns:
            bool: 是否成功更新
        """
        try:
            # 获取现有协作状态
            current_collaboration = self.get_collaboration_state(project_id)
            
            if not current_collaboration.get("success"):
                return False
            
            collaboration_data = current_collaboration["collaboration_state"]
            
            # 应用更新
            if project_id:
                if project_id not in collaboration_data:
                    collaboration_data[project_id] = {}
                collaboration_data[project_id].update(collaboration_updates)
            else:
                collaboration_data.update(collaboration_updates)
            
            # 添加时间戳
            collaboration_data["last_updated"] = datetime.now().isoformat()
            
            # 保存协作状态
            with open(self.collaboration_state_file, 'w', encoding='utf-8') as f:
                json.dump(collaboration_data, f, indent=2, ensure_ascii=False)
            
            # 触发状态更新通知
            self.update_state(
                {"collaboration": collaboration_updates},
                StateChangeType.COLLABORATION_REQUEST,
                "Collaboration state updated",
                project_id,
                create_snapshot=False
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating collaboration state: {e}")
            return False
    
    def get_task_state(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            project_id: 项目ID
            
        Returns:
            Dict: 任务状态
        """
        try:
            if self.task_state_file.exists():
                with open(self.task_state_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                
                # 过滤项目相关的任务状态
                if project_id:
                    project_tasks = task_data.get(project_id, {})
                else:
                    project_tasks = task_data
                
                return {
                    "success": True,
                    "task_state": project_tasks,
                    "last_updated": task_data.get("last_updated", datetime.now().isoformat())
                }
            else:
                return {
                    "success": True,
                    "task_state": {},
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get task state"
            }
    
    def update_task_state(
        self,
        task_updates: Dict[str, Any],
        project_id: Optional[str] = None
    ) -> bool:
        """
        更新任务状态
        
        Args:
            task_updates: 任务状态更新
            project_id: 项目ID
            
        Returns:
            bool: 是否成功更新
        """
        try:
            # 获取现有任务状态
            current_tasks = self.get_task_state(project_id)
            
            if not current_tasks.get("success"):
                return False
            
            task_data = current_tasks["task_state"]
            
            # 应用更新
            if project_id:
                if project_id not in task_data:
                    task_data[project_id] = {}
                task_data[project_id].update(task_updates)
            else:
                task_data.update(task_updates)
            
            # 添加时间戳
            task_data["last_updated"] = datetime.now().isoformat()
            
            # 保存任务状态
            with open(self.task_state_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2, ensure_ascii=False)
            
            # 触发状态更新通知
            self.update_state(
                {"tasks": task_updates},
                StateChangeType.TASK_UPDATE,
                "Task state updated",
                project_id,
                create_snapshot=False
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating task state: {e}")
            return False
    
    def create_state_snapshot(
        self,
        description: str,
        project_id: Optional[str] = None,
        change_type: StateChangeType = StateChangeType.PROJECT_INIT
    ) -> str:
        """
        创建状态快照
        
        Args:
            description: 快照描述
            project_id: 项目ID
            change_type: 变更类型
            
        Returns:
            str: 快照ID
        """
        current_state = self.get_current_state(project_id)
        return self._create_state_snapshot(current_state, change_type, description, project_id)
    
    def restore_from_snapshot(self, snapshot_id: str, project_id: Optional[str] = None) -> bool:
        """
        从快照恢复状态
        
        Args:
            snapshot_id: 快照ID
            project_id: 项目ID
            
        Returns:
            bool: 是否成功恢复
        """
        try:
            snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
            
            if not snapshot_file.exists():
                return False
            
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                snapshot_data = json.load(f)
            
            # 恢复状态
            success = self._save_state(snapshot_data["state_data"], project_id)
            
            if success:
                # 记录恢复事件
                self.update_state(
                    {"restored_from": snapshot_id},
                    StateChangeType.PROJECT_RESUME,
                    f"Restored from snapshot {snapshot_id}",
                    project_id,
                    create_snapshot=False
                )
            
            return success
            
        except Exception as e:
            print(f"Error restoring from snapshot: {e}")
            return False
    
    def get_state_history(
        self,
        project_id: Optional[str] = None,
        limit: int = 50,
        change_types: Optional[List[StateChangeType]] = None
    ) -> List[StateChangeEvent]:
        """
        获取状态变更历史
        
        Args:
            project_id: 项目ID
            limit: 返回数量限制
            change_types: 过滤的变更类型
            
        Returns:
            List[StateChangeEvent]: 状态变更历史
        """
        try:
            history = []
            
            # 从事件文件中加载历史
            for event_file in sorted(self.events_dir.glob("*.json"), reverse=True):
                if len(history) >= limit:
                    break
                
                try:
                    with open(event_file, 'r', encoding='utf-8') as f:
                        event_data = json.load(f)
                    
                    # 过滤项目和变更类型
                    if project_id and event_data.get("project_id") != project_id:
                        continue
                    
                    event_change_type = StateChangeType(event_data["change_type"])
                    if change_types and event_change_type not in change_types:
                        continue
                    
                    # 创建事件对象
                    event = StateChangeEvent(
                        event_id=event_data["event_id"],
                        project_id=event_data["project_id"],
                        change_type=event_change_type,
                        old_state=event_data["old_state"],
                        new_state=event_data["new_state"],
                        timestamp=datetime.fromisoformat(event_data["timestamp"]),
                        description=event_data["description"],
                        triggered_by=event_data.get("triggered_by", "system"),
                        metadata=event_data.get("metadata", {})
                    )
                    
                    history.append(event)
                    
                except Exception as e:
                    print(f"Error loading event file {event_file}: {e}")
                    continue
            
            return history[:limit]
            
        except Exception as e:
            print(f"Error getting state history: {e}")
            return []
    
    def register_notification_callback(
        self,
        callback_id: str,
        callback_func,
        filter_types: Optional[List[StateChangeType]] = None
    ) -> bool:
        """
        注册状态变更通知回调
        
        Args:
            callback_id: 回调ID
            callback_func: 回调函数
            filter_types: 过滤的变更类型
            
        Returns:
            bool: 是否成功注册
        """
        try:
            callback = StateNotificationCallback(callback_id, callback_func, filter_types)
            self._notification_callbacks[callback_id] = callback
            return True
        except Exception as e:
            print(f"Error registering notification callback: {e}")
            return False
    
    def unregister_notification_callback(self, callback_id: str) -> bool:
        """
        取消注册状态变更通知回调
        
        Args:
            callback_id: 回调ID
            
        Returns:
            bool: 是否成功取消注册
        """
        try:
            if callback_id in self._notification_callbacks:
                del self._notification_callbacks[callback_id]
                return True
            return False
        except Exception as e:
            print(f"Error unregistering notification callback: {e}")
            return False
    
    def get_state_analytics(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取状态分析数据
        
        Args:
            project_id: 项目ID
            
        Returns:
            Dict: 状态分析数据
        """
        try:
            history = self.get_state_history(project_id, limit=100)
            
            # 统计变更类型
            change_type_counts = defaultdict(int)
            for event in history:
                change_type_counts[event.change_type.value] += 1
            
            # 计算活跃度
            recent_events = [e for e in history if e.timestamp > datetime.now() - timedelta(days=7)]
            activity_score = len(recent_events) / 7.0  # 每天平均事件数
            
            # 分析协作频率
            collaboration_events = [
                e for e in history 
                if e.change_type in [StateChangeType.COLLABORATION_REQUEST, StateChangeType.COLLABORATION_RESPONSE]
            ]
            
            return {
                "success": True,
                "analytics": {
                    "total_events": len(history),
                    "change_type_distribution": dict(change_type_counts),
                    "recent_activity_score": round(activity_score, 2),
                    "collaboration_frequency": len(collaboration_events),
                    "most_common_change_type": max(change_type_counts.items(), key=lambda x: x[1])[0] if change_type_counts else "none",
                    "analysis_period": "last_100_events",
                    "generated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get state analytics"
            }
    
    def _enhance_state_data(self, state_data: Dict[str, Any], project_id: Optional[str]) -> Dict[str, Any]:
        """增强状态数据"""
        enhanced_state = state_data.copy()
        
        # 添加协作状态
        collaboration_state = self.get_collaboration_state(project_id)
        if collaboration_state.get("success"):
            enhanced_state["collaboration"] = collaboration_state["collaboration_state"]
        
        # 添加任务状态
        task_state = self.get_task_state(project_id)
        if task_state.get("success"):
            enhanced_state["tasks"] = task_state["task_state"]
        
        # 添加状态元数据
        enhanced_state["state_metadata"] = {
            "last_accessed": datetime.now().isoformat(),
            "cache_status": "enhanced",
            "project_id": project_id or "default"
        }
        
        return enhanced_state
    
    def _create_default_state(self, project_id: Optional[str]) -> Dict[str, Any]:
        """创建默认状态"""
        return {
            "success": True,
            "project": {
                "name": project_id or "default",
                "mode": "STANDARD",
                "created_at": datetime.now().isoformat(),
                "version": "3.0"
            },
            "flow": {
                "current_stage": "S1_user_stories",
                "completed_stages": [],
                "progress_percentage": 0
            },
            "metadata": {
                "total_stages": 8,
                "last_updated": datetime.now().isoformat()
            },
            "collaboration": {},
            "tasks": {},
            "state_metadata": {
                "created": datetime.now().isoformat(),
                "cache_status": "default",
                "project_id": project_id or "default"
            }
        }
    
    def _apply_state_updates(self, current_state: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """应用状态更新"""
        new_state = current_state.copy()
        
        # 深度合并更新
        def deep_merge(target, source):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_merge(target[key], value)
                else:
                    target[key] = value
        
        deep_merge(new_state, updates)
        
        # 更新时间戳
        if "metadata" not in new_state:
            new_state["metadata"] = {}
        new_state["metadata"]["last_updated"] = datetime.now().isoformat()
        
        return new_state
    
    def _save_state(self, state_data: Dict[str, Any], project_id: Optional[str]) -> bool:
        """保存状态"""
        try:
            with open(self.current_state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    def _create_state_snapshot(
        self,
        state_data: Dict[str, Any],
        change_type: StateChangeType,
        description: str,
        project_id: Optional[str]
    ) -> str:
        """创建状态快照"""
        try:
            snapshot_id = f"snapshot_{int(datetime.now().timestamp() * 1000)}"
            
            snapshot = StateSnapshot(
                snapshot_id=snapshot_id,
                project_id=project_id or "default",
                timestamp=datetime.now(),
                state_data=state_data,
                change_type=change_type,
                description=description
            )
            
            # 保存快照
            snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
            snapshot_data = {
                "snapshot_id": snapshot.snapshot_id,
                "project_id": snapshot.project_id,
                "timestamp": snapshot.timestamp.isoformat(),
                "state_data": snapshot.state_data,
                "change_type": snapshot.change_type.value,
                "description": snapshot.description,
                "metadata": snapshot.metadata
            }
            
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
            
            # 缓存快照
            self._snapshots[snapshot_id] = snapshot
            
            return snapshot_id
            
        except Exception as e:
            print(f"Error creating state snapshot: {e}")
            return ""
    
    def _record_state_change_event(
        self,
        old_state: Dict[str, Any],
        new_state: Dict[str, Any],
        change_type: StateChangeType,
        description: str,
        triggered_by: str,
        project_id: Optional[str]
    ):
        """记录状态变更事件"""
        try:
            event_id = f"event_{int(datetime.now().timestamp() * 1000)}"
            
            event = StateChangeEvent(
                event_id=event_id,
                project_id=project_id or "default",
                change_type=change_type,
                old_state=old_state,
                new_state=new_state,
                timestamp=datetime.now(),
                description=description,
                triggered_by=triggered_by
            )
            
            # 保存事件
            event_file = self.events_dir / f"{event_id}.json"
            event_data = {
                "event_id": event.event_id,
                "project_id": event.project_id,
                "change_type": event.change_type.value,
                "old_state": event.old_state,
                "new_state": event.new_state,
                "timestamp": event.timestamp.isoformat(),
                "description": event.description,
                "triggered_by": event.triggered_by,
                "metadata": event.metadata
            }
            
            with open(event_file, 'w', encoding='utf-8') as f:
                json.dump(event_data, f, indent=2, ensure_ascii=False)
            
            # 缓存事件
            self._state_history.append(event)
            
            # 保持历史记录在合理范围内
            if len(self._state_history) > 1000:
                self._state_history = self._state_history[-500:]
            
        except Exception as e:
            print(f"Error recording state change event: {e}")
    
    def _trigger_notifications(
        self,
        change_type: StateChangeType,
        old_state: Dict[str, Any],
        new_state: Dict[str, Any],
        project_id: Optional[str]
    ):
        """触发通知回调"""
        for callback_id, callback in self._notification_callbacks.items():
            try:
                if callback.should_notify(change_type):
                    callback.callback_func(change_type, old_state, new_state, project_id)
            except Exception as e:
                print(f"Error in notification callback {callback_id}: {e}")
    
    def _load_existing_states(self):
        """加载现有状态"""
        try:
            # 加载快照
            for snapshot_file in self.snapshots_dir.glob("*.json"):
                try:
                    with open(snapshot_file, 'r', encoding='utf-8') as f:
                        snapshot_data = json.load(f)
                    
                    snapshot = StateSnapshot(
                        snapshot_id=snapshot_data["snapshot_id"],
                        project_id=snapshot_data["project_id"],
                        timestamp=datetime.fromisoformat(snapshot_data["timestamp"]),
                        state_data=snapshot_data["state_data"],
                        change_type=StateChangeType(snapshot_data["change_type"]),
                        description=snapshot_data["description"],
                        metadata=snapshot_data.get("metadata", {})
                    )
                    
                    self._snapshots[snapshot.snapshot_id] = snapshot
                    
                except Exception as e:
                    print(f"Error loading snapshot {snapshot_file}: {e}")
            
            # 加载最近的事件历史
            event_files = sorted(self.events_dir.glob("*.json"), reverse=True)[:100]
            
            for event_file in event_files:
                try:
                    with open(event_file, 'r', encoding='utf-8') as f:
                        event_data = json.load(f)
                    
                    event = StateChangeEvent(
                        event_id=event_data["event_id"],
                        project_id=event_data["project_id"],
                        change_type=StateChangeType(event_data["change_type"]),
                        old_state=event_data["old_state"],
                        new_state=event_data["new_state"],
                        timestamp=datetime.fromisoformat(event_data["timestamp"]),
                        description=event_data["description"],
                        triggered_by=event_data.get("triggered_by", "system"),
                        metadata=event_data.get("metadata", {})
                    )
                    
                    self._state_history.append(event)
                    
                except Exception as e:
                    print(f"Error loading event {event_file}: {e}")
            
            # 按时间排序
            self._state_history.sort(key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            print(f"Error loading existing states: {e}")


# 工厂函数
def create_enhanced_state_manager(workspace_dir: Optional[Path] = None) -> EnhancedStateManager:
    """创建增强版状态管理器实例"""
    return EnhancedStateManager(workspace_dir)


# 便捷函数
def get_project_state_with_history(project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    便捷函数：获取包含历史的项目状态
    
    Args:
        project_id: 项目ID
        
    Returns:
        Dict: 包含历史的项目状态
    """
    state_manager = create_enhanced_state_manager()
    current_state = state_manager.get_current_state(project_id)
    history = state_manager.get_state_history(project_id, limit=10)
    
    return {
        "current_state": current_state,
        "recent_history": [
            {
                "change_type": event.change_type.value,
                "description": event.description,
                "timestamp": event.timestamp.isoformat(),
                "triggered_by": event.triggered_by
            }
            for event in history
        ]
    }