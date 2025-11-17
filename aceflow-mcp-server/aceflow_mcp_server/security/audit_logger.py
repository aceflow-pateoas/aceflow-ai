"""
审计日志器
Audit Logger

记录和监控系统操作，提供安全审计功能。
"""
from typing import Dict, Any, Optional, List
import logging
import json
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
import threading
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

class AuditLevel(Enum):
    """审计级别"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"

class AuditCategory(Enum):
    """审计类别"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    SYSTEM_OPERATION = "system_operation"
    SECURITY_EVENT = "security_event"
    PERFORMANCE = "performance"
    ERROR = "error"

@dataclass
class AuditEvent:
    """审计事件"""
    timestamp: float
    level: AuditLevel
    category: AuditCategory
    event_type: str
    user_id: Optional[str]
    resource: Optional[str]
    action: str
    result: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

class AuditLogger:
    """
    审计日志器
    - 记录系统操作
    - 安全事件跟踪
    - 合规性审计
    """
    
    def __init__(self, log_file: Optional[str] = None, max_log_size: int = 10 * 1024 * 1024):
        self._log_file = log_file or "audit.log"
        self._max_log_size = max_log_size
        self._events: List[AuditEvent] = []
        self._lock = threading.Lock()
        self._enabled = True
        
        # 确保日志目录存在
        log_path = Path(self._log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Audit logger initialized with log file: {self._log_file}")

    def log_event(self, 
                  level: AuditLevel,
                  category: AuditCategory,
                  event_type: str,
                  action: str,
                  result: str,
                  user_id: Optional[str] = None,
                  resource: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  session_id: Optional[str] = None):
        """记录审计事件"""
        if not self._enabled:
            return
            
        event = AuditEvent(
            timestamp=time.time(),
            level=level,
            category=category,
            event_type=event_type,
            user_id=user_id,
            resource=resource,
            action=action,
            result=result,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
        
        with self._lock:
            self._events.append(event)
            self._write_to_file(event)
            
        # 记录到标准日志
        log_msg = f"AUDIT: {category.value}:{event_type} - {action} -> {result}"
        if level == AuditLevel.CRITICAL or level == AuditLevel.SECURITY:
            logger.critical(log_msg)
        elif level == AuditLevel.ERROR:
            logger.error(log_msg)
        elif level == AuditLevel.WARNING:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

    def log_authentication(self, user_id: str, action: str, result: str, 
                          ip_address: Optional[str] = None, details: Optional[Dict] = None):
        """记录认证事件"""
        self.log_event(
            level=AuditLevel.SECURITY if result == "failed" else AuditLevel.INFO,
            category=AuditCategory.AUTHENTICATION,
            event_type="user_auth",
            action=action,
            result=result,
            user_id=user_id,
            ip_address=ip_address,
            details=details
        )

    def log_authorization(self, user_id: str, resource: str, action: str, 
                         result: str, details: Optional[Dict] = None):
        """记录授权事件"""
        self.log_event(
            level=AuditLevel.WARNING if result == "denied" else AuditLevel.INFO,
            category=AuditCategory.AUTHORIZATION,
            event_type="access_control",
            action=action,
            result=result,
            user_id=user_id,
            resource=resource,
            details=details
        )

    def log_data_access(self, user_id: str, resource: str, action: str, 
                       result: str, details: Optional[Dict] = None):
        """记录数据访问事件"""
        self.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.DATA_ACCESS,
            event_type="data_operation",
            action=action,
            result=result,
            user_id=user_id,
            resource=resource,
            details=details
        )

    def log_security_event(self, event_type: str, action: str, result: str,
                          user_id: Optional[str] = None, ip_address: Optional[str] = None,
                          details: Optional[Dict] = None):
        """记录安全事件"""
        self.log_event(
            level=AuditLevel.SECURITY,
            category=AuditCategory.SECURITY_EVENT,
            event_type=event_type,
            action=action,
            result=result,
            user_id=user_id,
            ip_address=ip_address,
            details=details
        )

    def log_system_operation(self, action: str, result: str, 
                           details: Optional[Dict] = None):
        """记录系统操作事件"""
        self.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.SYSTEM_OPERATION,
            event_type="system_op",
            action=action,
            result=result,
            details=details
        )

    def log_performance_event(self, action: str, result: str, 
                             details: Optional[Dict] = None):
        """记录性能事件"""
        self.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.PERFORMANCE,
            event_type="performance",
            action=action,
            result=result,
            details=details
        )

    def log_error_event(self, error_type: str, action: str, result: str,
                       details: Optional[Dict] = None):
        """记录错误事件"""
        self.log_event(
            level=AuditLevel.ERROR,
            category=AuditCategory.ERROR,
            event_type=error_type,
            action=action,
            result=result,
            details=details
        )

    def _write_to_file(self, event: AuditEvent):
        """写入日志文件"""
        try:
            # 检查文件大小，如果太大则轮转
            if Path(self._log_file).exists() and Path(self._log_file).stat().st_size > self._max_log_size:
                self._rotate_log_file()
            
            log_entry = {
                "timestamp": datetime.fromtimestamp(event.timestamp).isoformat(),
                "level": event.level.value,
                "category": event.category.value,
                "event_type": event.event_type,
                "user_id": event.user_id,
                "resource": event.resource,
                "action": event.action,
                "result": event.result,
                "details": event.details,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "session_id": event.session_id
            }
            
            with open(self._log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def _rotate_log_file(self):
        """轮转日志文件"""
        try:
            backup_file = f"{self._log_file}.{int(time.time())}"
            Path(self._log_file).rename(backup_file)
            logger.info(f"Rotated audit log to {backup_file}")
        except Exception as e:
            logger.error(f"Failed to rotate audit log: {e}")

    def query_events(self, 
                    category: Optional[AuditCategory] = None,
                    level: Optional[AuditLevel] = None,
                    user_id: Optional[str] = None,
                    start_time: Optional[float] = None,
                    end_time: Optional[float] = None,
                    limit: int = 100) -> List[AuditEvent]:
        """查询审计事件"""
        with self._lock:
            filtered_events = []
            
            for event in self._events:
                # 应用过滤条件
                if category and event.category != category:
                    continue
                if level and event.level != level:
                    continue
                if user_id and event.user_id != user_id:
                    continue
                if start_time and event.timestamp < start_time:
                    continue
                if end_time and event.timestamp > end_time:
                    continue
                    
                filtered_events.append(event)
                
                if len(filtered_events) >= limit:
                    break
            
            return filtered_events

    def get_statistics(self) -> Dict[str, Any]:
        """获取审计统计信息"""
        with self._lock:
            total_events = len(self._events)
            
            # 按类别统计
            category_stats = {}
            for category in AuditCategory:
                category_stats[category.value] = sum(
                    1 for event in self._events if event.category == category
                )
            
            # 按级别统计
            level_stats = {}
            for level in AuditLevel:
                level_stats[level.value] = sum(
                    1 for event in self._events if event.level == level
                )
            
            # 最近活动
            recent_events = []
            if self._events:
                recent_events = [
                    {
                        "timestamp": datetime.fromtimestamp(event.timestamp).isoformat(),
                        "category": event.category.value,
                        "action": event.action,
                        "result": event.result
                    }
                    for event in sorted(self._events, key=lambda x: x.timestamp, reverse=True)[:10]
                ]
            
            return {
                "total_events": total_events,
                "category_stats": category_stats,
                "level_stats": level_stats,
                "recent_events": recent_events,
                "log_file": self._log_file,
                "enabled": self._enabled
            }

    def clear_old_events(self, days: int = 30):
        """清理旧的审计事件"""
        cutoff_time = time.time() - (days * 24 * 3600)
        
        with self._lock:
            original_count = len(self._events)
            self._events = [event for event in self._events if event.timestamp > cutoff_time]
            removed_count = original_count - len(self._events)
            
            if removed_count > 0:
                logger.info(f"Cleared {removed_count} old audit events")

    def enable(self):
        """启用审计日志"""
        self._enabled = True
        logger.info("Audit logging enabled")

    def disable(self):
        """禁用审计日志"""
        self._enabled = False
        logger.info("Audit logging disabled")

    def is_enabled(self) -> bool:
        """检查审计日志是否启用"""
        return self._enabled

# 全局审计日志器实例
audit_logger = AuditLogger()
