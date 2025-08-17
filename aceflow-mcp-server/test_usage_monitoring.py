#!/usr/bin/env python3
"""
使用数据收集和监控系统测试
Usage Data Collection and Monitoring System Test
"""
import sys
import os
import asyncio
import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass, asdict
import threading
from datetime import datetime, timedelta
import uuid

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import logging

logger = logging.getLogger(__name__)

# 使用事件类型枚举
class UsageEventType(Enum):
    TOOL_CALL = "tool_call"
    RESOURCE_ACCESS = "resource_access"
    SERVER_START = "server_start"
    SERVER_STOP = "server_stop"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_METRIC = "performance_metric"

# 使用事件数据类
@dataclass
class UsageEvent:
    """使用事件数据结构"""
    event_id: str
    event_type: UsageEventType
    timestamp: float
    user_id: str
    session_id: str
    
    # 工具相关字段
    tool_name: Optional[str] = None
    tool_parameters: Optional[Dict[str, Any]] = None
    tool_success: Optional[bool] = None
    tool_execution_time: Optional[float] = None
    tool_error: Optional[str] = None
    
    # 资源相关字段
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_success: Optional[bool] = None
    resource_cache_hit: Optional[bool] = None
    resource_access_time: Optional[float] = None
    
    # 性能相关字段
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    response_time: Optional[float] = None
    
    # 通用字段
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageEvent':
        """从字典创建"""
        data = data.copy()
        data['event_type'] = UsageEventType(data['event_type'])
        return cls(**data)

# 数据持久化接口
class DataPersistence:
    """数据持久化抽象接口"""
    
    def save_event(self, event: UsageEvent):
        """保存事件"""
        raise NotImplementedError
    
    def get_events(self, start_time: Optional[float] = None, 
                   end_time: Optional[float] = None,
                   event_type: Optional[UsageEventType] = None,
                   user_id: Optional[str] = None,
                   limit: Optional[int] = None) -> List[UsageEvent]:
        """获取事件"""
        raise NotImplementedError
    
    def get_event_count(self, start_time: Optional[float] = None,
                       end_time: Optional[float] = None,
                       event_type: Optional[UsageEventType] = None) -> int:
        """获取事件数量"""
        raise NotImplementedError
    
    def cleanup_old_events(self, older_than_days: int = 30):
        """清理旧事件"""
        raise NotImplementedError

# SQLite数据持久化实现
class SQLiteDataPersistence(DataPersistence):
    """SQLite数据持久化实现"""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS usage_events (
                        event_id TEXT PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        user_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        tool_name TEXT,
                        tool_parameters TEXT,
                        tool_success INTEGER,
                        tool_execution_time REAL,
                        tool_error TEXT,
                        resource_type TEXT,
                        resource_id TEXT,
                        resource_success INTEGER,
                        resource_cache_hit INTEGER,
                        resource_access_time REAL,
                        cpu_usage REAL,
                        memory_usage REAL,
                        response_time REAL,
                        metadata TEXT
                    )
                ''')
                
                # 创建索引
                conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON usage_events(timestamp)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON usage_events(event_type)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON usage_events(user_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_tool_name ON usage_events(tool_name)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_resource_type ON usage_events(resource_type)')
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def save_event(self, event: UsageEvent):
        """保存事件到数据库"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO usage_events (
                        event_id, event_type, timestamp, user_id, session_id,
                        tool_name, tool_parameters, tool_success, tool_execution_time, tool_error,
                        resource_type, resource_id, resource_success, resource_cache_hit, resource_access_time,
                        cpu_usage, memory_usage, response_time, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.event_id, event.event_type.value, event.timestamp, event.user_id, event.session_id,
                    event.tool_name, 
                    json.dumps(event.tool_parameters) if event.tool_parameters else None,
                    event.tool_success,
                    event.tool_execution_time,
                    event.tool_error,
                    event.resource_type,
                    event.resource_id,
                    event.resource_success,
                    event.resource_cache_hit,
                    event.resource_access_time,
                    event.cpu_usage,
                    event.memory_usage,
                    event.response_time,
                    json.dumps(event.metadata) if event.metadata else None
                ))
    
    def get_events(self, start_time: Optional[float] = None, 
                   end_time: Optional[float] = None,
                   event_type: Optional[UsageEventType] = None,
                   user_id: Optional[str] = None,
                   limit: Optional[int] = None) -> List[UsageEvent]:
        """从数据库获取事件"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = "SELECT * FROM usage_events WHERE 1=1"
                params = []
                
                if start_time is not None:
                    query += " AND timestamp >= ?"
                    params.append(start_time)
                
                if end_time is not None:
                    query += " AND timestamp <= ?"
                    params.append(end_time)
                
                if event_type is not None:
                    query += " AND event_type = ?"
                    params.append(event_type.value)
                
                if user_id is not None:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                query += " ORDER BY timestamp DESC"
                
                if limit is not None:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event_data = dict(row)
                    
                    # 转换JSON字段
                    if event_data['tool_parameters']:
                        event_data['tool_parameters'] = json.loads(event_data['tool_parameters'])
                    if event_data['metadata']:
                        event_data['metadata'] = json.loads(event_data['metadata'])
                    
                    # 转换布尔字段
                    for bool_field in ['tool_success', 'resource_success', 'resource_cache_hit']:
                        if event_data[bool_field] is not None:
                            event_data[bool_field] = bool(event_data[bool_field])
                    
                    events.append(UsageEvent.from_dict(event_data))
                
                return events
    
    def get_event_count(self, start_time: Optional[float] = None,
                       end_time: Optional[float] = None,
                       event_type: Optional[UsageEventType] = None) -> int:
        """获取事件数量"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT COUNT(*) FROM usage_events WHERE 1=1"
                params = []
                
                if start_time is not None:
                    query += " AND timestamp >= ?"
                    params.append(start_time)
                
                if end_time is not None:
                    query += " AND timestamp <= ?"
                    params.append(end_time)
                
                if event_type is not None:
                    query += " AND event_type = ?"
                    params.append(event_type.value)
                
                cursor = conn.execute(query, params)
                return cursor.fetchone()[0]
    
    def cleanup_old_events(self, older_than_days: int = 30):
        """清理旧事件"""
        cutoff_time = time.time() - (older_than_days * 24 * 3600)
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM usage_events WHERE timestamp < ?", (cutoff_time,))
                deleted_count = cursor.rowcount
                logger.info(f"Cleaned up {deleted_count} old events")
                return deleted_count

# 使用监控器主类
class UsageMonitor:
    """使用数据收集和监控器"""
    
    def __init__(self, persistence: Optional[DataPersistence] = None, 
                 session_id: Optional[str] = None):
        self.persistence = persistence or SQLiteDataPersistence()
        self.session_id = session_id or str(uuid.uuid4())
        
        # 确保数据库已初始化
        if hasattr(self.persistence, '_init_database'):
            self.persistence._init_database()
        
        # 内存缓存用于快速访问
        self.memory_cache = []
        self.cache_size_limit = 1000
        
        # 统计计数器
        self.stats = {
            "total_events": 0,
            "tool_calls": 0,
            "resource_accesses": 0,
            "errors": 0,
            "session_start_time": time.time()
        }
        
        # 性能监控
        self.performance_data = {
            "avg_response_time": 0.0,
            "total_response_time": 0.0,
            "response_count": 0
        }
        
        logger.info(f"UsageMonitor initialized with session_id: {self.session_id}")
    
    def record_tool_call(self, tool_name: str, user_id: str = "anonymous",
                        parameters: Optional[Dict[str, Any]] = None,
                        success: bool = True, execution_time: Optional[float] = None,
                        error: Optional[str] = None, **metadata):
        """记录工具调用事件"""
        event = UsageEvent(
            event_id=str(uuid.uuid4()),
            event_type=UsageEventType.TOOL_CALL,
            timestamp=time.time(),
            user_id=user_id,
            session_id=self.session_id,
            tool_name=tool_name,
            tool_parameters=parameters,
            tool_success=success,
            tool_execution_time=execution_time,
            tool_error=error,
            metadata=metadata if metadata else None
        )
        
        self._record_event(event)
        self.stats["tool_calls"] += 1
        
        if execution_time is not None:
            self._update_performance_stats(execution_time)
    
    def record_resource_access(self, resource_type: str, resource_id: str = "default",
                             user_id: str = "anonymous", success: bool = True,
                             cache_hit: bool = False, access_time: Optional[float] = None,
                             **metadata):
        """记录资源访问事件"""
        event = UsageEvent(
            event_id=str(uuid.uuid4()),
            event_type=UsageEventType.RESOURCE_ACCESS,
            timestamp=time.time(),
            user_id=user_id,
            session_id=self.session_id,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_success=success,
            resource_cache_hit=cache_hit,
            resource_access_time=access_time,
            metadata=metadata if metadata else None
        )
        
        self._record_event(event)
        self.stats["resource_accesses"] += 1
        
        if access_time is not None:
            self._update_performance_stats(access_time)
    
    def record_error(self, error_type: str, error_message: str, user_id: str = "anonymous",
                    context: Optional[Dict[str, Any]] = None):
        """记录错误事件"""
        event = UsageEvent(
            event_id=str(uuid.uuid4()),
            event_type=UsageEventType.ERROR_OCCURRED,
            timestamp=time.time(),
            user_id=user_id,
            session_id=self.session_id,
            tool_error=error_message,
            metadata={
                "error_type": error_type,
                "context": context
            }
        )
        
        self._record_event(event)
        self.stats["errors"] += 1
    
    def record_performance_metric(self, cpu_usage: Optional[float] = None,
                                memory_usage: Optional[float] = None,
                                response_time: Optional[float] = None,
                                **metadata):
        """记录性能指标"""
        event = UsageEvent(
            event_id=str(uuid.uuid4()),
            event_type=UsageEventType.PERFORMANCE_METRIC,
            timestamp=time.time(),
            user_id="system",
            session_id=self.session_id,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            response_time=response_time,
            metadata=metadata if metadata else None
        )
        
        self._record_event(event)
    
    def _record_event(self, event: UsageEvent):
        """记录事件到持久化存储和内存缓存"""
        # 保存到持久化存储
        try:
            self.persistence.save_event(event)
        except Exception as e:
            logger.error(f"Failed to persist event: {e}")
        
        # 添加到内存缓存
        self.memory_cache.append(event)
        
        # 限制内存缓存大小
        if len(self.memory_cache) > self.cache_size_limit:
            self.memory_cache = self.memory_cache[-self.cache_size_limit:]
        
        self.stats["total_events"] += 1
    
    def _update_performance_stats(self, response_time: float):
        """更新性能统计"""
        self.performance_data["total_response_time"] += response_time
        self.performance_data["response_count"] += 1
        self.performance_data["avg_response_time"] = (
            self.performance_data["total_response_time"] / 
            self.performance_data["response_count"]
        )
    
    def get_recent_events(self, limit: int = 100, 
                         event_type: Optional[UsageEventType] = None) -> List[UsageEvent]:
        """获取最近的事件"""
        try:
            return self.persistence.get_events(
                event_type=event_type,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to get recent events: {e}")
            # 从内存缓存返回
            events = self.memory_cache
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            return events[-limit:]
    
    def get_events_by_timerange(self, start_time: float, end_time: float,
                               event_type: Optional[UsageEventType] = None) -> List[UsageEvent]:
        """按时间范围获取事件"""
        try:
            return self.persistence.get_events(
                start_time=start_time,
                end_time=end_time,
                event_type=event_type
            )
        except Exception as e:
            logger.error(f"Failed to get events by timerange: {e}")
            return []
    
    def get_user_activity(self, user_id: str, hours: int = 24) -> List[UsageEvent]:
        """获取用户活动"""
        start_time = time.time() - (hours * 3600)
        try:
            return self.persistence.get_events(
                start_time=start_time,
                user_id=user_id
            )
        except Exception as e:
            logger.error(f"Failed to get user activity: {e}")
            return []
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        current_time = time.time()
        session_duration = current_time - self.stats["session_start_time"]
        
        # 获取最近24小时的统计
        recent_start = current_time - 86400  # 24小时
        try:
            recent_tool_calls = self.persistence.get_event_count(
                start_time=recent_start,
                event_type=UsageEventType.TOOL_CALL
            )
            recent_resource_accesses = self.persistence.get_event_count(
                start_time=recent_start,
                event_type=UsageEventType.RESOURCE_ACCESS
            )
            recent_errors = self.persistence.get_event_count(
                start_time=recent_start,
                event_type=UsageEventType.ERROR_OCCURRED
            )
        except Exception as e:
            logger.error(f"Failed to get recent stats: {e}")
            recent_tool_calls = 0
            recent_resource_accesses = 0
            recent_errors = 0
        
        return {
            "session": {
                "session_id": self.session_id,
                "duration_seconds": session_duration,
                "total_events": self.stats["total_events"],
                "tool_calls": self.stats["tool_calls"],
                "resource_accesses": self.stats["resource_accesses"],
                "errors": self.stats["errors"]
            },
            "recent_24h": {
                "tool_calls": recent_tool_calls,
                "resource_accesses": recent_resource_accesses,
                "errors": recent_errors
            },
            "performance": self.performance_data.copy(),
            "cache": {
                "memory_cache_size": len(self.memory_cache),
                "cache_limit": self.cache_size_limit
            }
        }
    
    def get_tool_usage_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取工具使用摘要"""
        start_time = time.time() - (hours * 3600)
        
        try:
            events = self.persistence.get_events(
                start_time=start_time,
                event_type=UsageEventType.TOOL_CALL
            )
        except Exception as e:
            logger.error(f"Failed to get tool usage summary: {e}")
            events = []
        
        tool_stats = {}
        total_calls = 0
        total_execution_time = 0.0
        successful_calls = 0
        
        for event in events:
            tool_name = event.tool_name or "unknown"
            
            if tool_name not in tool_stats:
                tool_stats[tool_name] = {
                    "calls": 0,
                    "successful_calls": 0,
                    "total_execution_time": 0.0,
                    "avg_execution_time": 0.0,
                    "errors": 0
                }
            
            stats = tool_stats[tool_name]
            stats["calls"] += 1
            total_calls += 1
            
            if event.tool_success:
                stats["successful_calls"] += 1
                successful_calls += 1
            else:
                stats["errors"] += 1
            
            if event.tool_execution_time:
                stats["total_execution_time"] += event.tool_execution_time
                total_execution_time += event.tool_execution_time
        
        # 计算平均执行时间
        for tool_name, stats in tool_stats.items():
            if stats["successful_calls"] > 0:
                stats["avg_execution_time"] = stats["total_execution_time"] / stats["successful_calls"]
        
        return {
            "timeframe_hours": hours,
            "summary": {
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "success_rate": successful_calls / max(1, total_calls),
                "avg_execution_time": total_execution_time / max(1, successful_calls)
            },
            "by_tool": tool_stats
        }
    
    def cleanup_old_data(self, older_than_days: int = 30) -> int:
        """清理旧数据"""
        try:
            return self.persistence.cleanup_old_events(older_than_days)
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0

# 测试函数
async def test_usage_monitor_basic():
    """测试使用监控器基本功能"""
    print("🧪 Testing Usage Monitor Basic Functionality...")
    
    monitor = UsageMonitor()
    
    # 测试1: 记录工具调用
    print("  Testing tool call recording...")
    monitor.record_tool_call(
        tool_name="aceflow_init",
        user_id="test_user",
        parameters={"project_name": "test_project"},
        success=True,
        execution_time=0.5
    )
    
    monitor.record_tool_call(
        tool_name="aceflow_stage",
        user_id="test_user",
        parameters={"stage": "implementation"},
        success=False,
        error="Stage validation failed"
    )
    
    # 验证统计
    stats = monitor.get_usage_stats()
    assert stats["session"]["tool_calls"] == 2
    assert stats["session"]["total_events"] == 2
    print("  ✅ Tool call recording test passed")
    
    # 测试2: 记录资源访问
    print("  Testing resource access recording...")
    monitor.record_resource_access(
        resource_type="project_state",
        resource_id="test_project",
        user_id="test_user",
        success=True,
        cache_hit=False,
        access_time=0.1
    )
    
    monitor.record_resource_access(
        resource_type="workflow_config",
        resource_id="default",
        user_id="test_user",
        success=True,
        cache_hit=True,
        access_time=0.01
    )
    
    # 验证统计
    stats = monitor.get_usage_stats()
    assert stats["session"]["resource_accesses"] == 2
    assert stats["session"]["total_events"] == 4
    print("  ✅ Resource access recording test passed")
    
    # 测试3: 记录错误
    print("  Testing error recording...")
    monitor.record_error(
        error_type="ValidationError",
        error_message="Invalid project configuration",
        user_id="test_user",
        context={"project_id": "test_project"}
    )
    
    # 验证统计
    stats = monitor.get_usage_stats()
    assert stats["session"]["errors"] == 1
    assert stats["session"]["total_events"] == 5
    print("  ✅ Error recording test passed")
    
    # 测试4: 获取最近事件
    print("  Testing recent events retrieval...")
    recent_events = monitor.get_recent_events(limit=10)
    assert len(recent_events) == 5
    
    # 按类型获取事件
    tool_events = monitor.get_recent_events(event_type=UsageEventType.TOOL_CALL)
    assert len(tool_events) == 2
    print("  ✅ Recent events retrieval test passed")
    
    print("🎉 All Usage Monitor Basic tests passed!")
    return True

async def test_usage_monitor_persistence():
    """测试使用监控器持久化功能"""
    print("🧪 Testing Usage Monitor Persistence...")
    
    # 使用临时数据库
    persistence = SQLiteDataPersistence(":memory:")
    monitor = UsageMonitor(persistence=persistence)
    
    # 记录一些测试数据
    current_time = time.time()
    
    # 记录不同时间的事件
    for i in range(10):
        monitor.record_tool_call(
            tool_name=f"test_tool_{i % 3}",
            user_id=f"user_{i % 2}",
            success=i % 4 != 0,  # 75%成功率
            execution_time=0.1 + (i * 0.05)
        )
        
        monitor.record_resource_access(
            resource_type=f"resource_{i % 2}",
            resource_id=f"id_{i}",
            user_id=f"user_{i % 2}",
            cache_hit=i % 3 == 0  # 33%缓存命中率
        )
    
    # 测试按时间范围查询
    print("  Testing time range queries...")
    start_time = current_time - 60  # 1分钟前
    end_time = current_time + 60    # 1分钟后
    
    events = monitor.get_events_by_timerange(start_time, end_time)
    assert len(events) == 20  # 10个工具调用 + 10个资源访问
    print("  ✅ Time range queries test passed")
    
    # 测试用户活动查询
    print("  Testing user activity queries...")
    user0_activity = monitor.get_user_activity("user_0", hours=1)
    user1_activity = monitor.get_user_activity("user_1", hours=1)
    
    # user_0应该有索引0,2,4,6,8的事件 = 5个工具调用 + 5个资源访问 = 10个事件
    # user_1应该有索引1,3,5,7,9的事件 = 5个工具调用 + 5个资源访问 = 10个事件
    assert len(user0_activity) == 10
    assert len(user1_activity) == 10
    print("  ✅ User activity queries test passed")
    
    # 测试工具使用摘要
    print("  Testing tool usage summary...")
    tool_summary = monitor.get_tool_usage_summary(hours=1)
    
    assert tool_summary["summary"]["total_calls"] == 10
    assert len(tool_summary["by_tool"]) == 3  # test_tool_0, test_tool_1, test_tool_2
    print("  ✅ Tool usage summary test passed")
    
    # 测试数据清理
    print("  Testing data cleanup...")
    # 先记录一些"旧"数据（通过直接操作数据库）
    old_event = UsageEvent(
        event_id=str(uuid.uuid4()),
        event_type=UsageEventType.TOOL_CALL,
        timestamp=current_time - (40 * 24 * 3600),  # 40天前
        user_id="old_user",
        session_id="old_session",
        tool_name="old_tool"
    )
    persistence.save_event(old_event)
    
    # 清理30天前的数据
    cleaned_count = monitor.cleanup_old_data(older_than_days=30)
    assert cleaned_count == 1
    print("  ✅ Data cleanup test passed")
    
    print("🎉 All Usage Monitor Persistence tests passed!")
    return True

async def test_performance_monitoring():
    """测试性能监控功能"""
    print("🧪 Testing Performance Monitoring...")
    
    monitor = UsageMonitor()
    
    # 记录一些性能数据
    execution_times = [0.1, 0.2, 0.15, 0.3, 0.05]
    
    for i, exec_time in enumerate(execution_times):
        monitor.record_tool_call(
            tool_name=f"perf_tool_{i}",
            user_id="perf_user",
            execution_time=exec_time,
            success=True
        )
    
    # 记录性能指标
    monitor.record_performance_metric(
        cpu_usage=0.45,
        memory_usage=0.67,
        response_time=0.12
    )
    
    # 验证性能统计
    stats = monitor.get_usage_stats()
    expected_avg = sum(execution_times) / len(execution_times)
    
    assert abs(stats["performance"]["avg_response_time"] - expected_avg) < 0.001
    assert stats["performance"]["response_count"] == len(execution_times)
    print("  ✅ Performance statistics calculation test passed")
    
    # 获取性能事件
    perf_events = monitor.get_recent_events(event_type=UsageEventType.PERFORMANCE_METRIC)
    assert len(perf_events) == 1
    assert perf_events[0].cpu_usage == 0.45
    assert perf_events[0].memory_usage == 0.67
    print("  ✅ Performance metrics recording test passed")
    
    print("🎉 All Performance Monitoring tests passed!")
    return True

async def main():
    """运行所有测试"""
    print("🚀 Starting Usage Data Collection and Monitoring System tests...\n")
    
    try:
        await test_usage_monitor_basic()
        await test_usage_monitor_persistence()
        await test_performance_monitoring()
        
        print("\n🎉 All Usage Data Collection and Monitoring System tests passed!")
        print("\n📊 Usage Monitoring System Summary:")
        print("   ✅ Basic Event Recording - Working")
        print("   ✅ Data Persistence (SQLite) - Working")
        print("   ✅ Time Range Queries - Working")
        print("   ✅ User Activity Tracking - Working")
        print("   ✅ Tool Usage Analytics - Working")
        print("   ✅ Performance Monitoring - Working")
        print("   ✅ Data Cleanup - Working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Usage monitoring test failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🏗️ Task 6.1 - Usage Data Collection Implementation Complete!")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)