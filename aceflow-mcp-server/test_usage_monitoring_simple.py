#!/usr/bin/env python3
"""
简化的使用数据收集和监控系统测试
Simplified Usage Data Collection and Monitoring System Test
"""
import sys
import os
import asyncio
import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
import uuid

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import logging
import datetime

logger = logging.getLogger(__name__)

# 使用事件类型枚举
class UsageEventType(Enum):
    TOOL_CALL = "tool_call"
    RESOURCE_ACCESS = "resource_access"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_METRIC = "performance_metric"

# 简化的使用事件数据类
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
    tool_success: Optional[bool] = None
    tool_execution_time: Optional[float] = None
    tool_error: Optional[str] = None
    
    # 资源相关字段
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_success: Optional[bool] = None
    resource_cache_hit: Optional[bool] = None
    
    # 性能相关字段
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    response_time: Optional[float] = None

# 内存数据持久化实现（用于测试）
class MemoryDataPersistence:
    """内存数据持久化实现"""
    
    def __init__(self):
        self.events = []
    
    def save_event(self, event: UsageEvent):
        """保存事件到内存"""
        self.events.append(event)
    
    def get_events(self, start_time: Optional[float] = None, 
                   end_time: Optional[float] = None,
                   event_type: Optional[UsageEventType] = None,
                   user_id: Optional[str] = None,
                   limit: Optional[int] = None) -> List[UsageEvent]:
        """从内存获取事件"""
        filtered_events = self.events
        
        # 应用过滤条件
        if start_time is not None:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
        
        if end_time is not None:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
        
        if event_type is not None:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if user_id is not None:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        # 按时间戳倒序排序
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 应用限制
        if limit is not None:
            filtered_events = filtered_events[:limit]
        
        return filtered_events
    
    def get_event_count(self, start_time: Optional[float] = None,
                       end_time: Optional[float] = None,
                       event_type: Optional[UsageEventType] = None) -> int:
        """获取事件数量"""
        return len(self.get_events(start_time, end_time, event_type))
    
    def cleanup_old_events(self, older_than_days: int = 30) -> int:
        """清理旧事件"""
        cutoff_time = time.time() - (older_than_days * 24 * 3600)
        old_events = [e for e in self.events if e.timestamp < cutoff_time]
        self.events = [e for e in self.events if e.timestamp >= cutoff_time]
        return len(old_events)

# 使用监控器主类
class UsageMonitor:
    """使用数据收集和监控器"""
    
    def __init__(self, persistence=None, session_id: Optional[str] = None):
        self.persistence = persistence or MemoryDataPersistence()
        self.session_id = session_id or str(uuid.uuid4())
        
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
                        success: bool = True, execution_time: Optional[float] = None,
                        error: Optional[str] = None):
        """记录工具调用事件"""
        event = UsageEvent(
            event_id=str(uuid.uuid4()),
            event_type=UsageEventType.TOOL_CALL,
            timestamp=time.time(),
            user_id=user_id,
            session_id=self.session_id,
            tool_name=tool_name,
            tool_success=success,
            tool_execution_time=execution_time,
            tool_error=error
        )
        
        self._record_event(event)
        self.stats["tool_calls"] += 1
        
        if execution_time is not None:
            self._update_performance_stats(execution_time)
    
    def record_resource_access(self, resource_type: str, resource_id: str = "default",
                             user_id: str = "anonymous", success: bool = True,
                             cache_hit: bool = False):
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
            resource_cache_hit=cache_hit
        )
        
        self._record_event(event)
        self.stats["resource_accesses"] += 1
    
    def record_error(self, error_message: str, user_id: str = "anonymous"):
        """记录错误事件"""
        event = UsageEvent(
            event_id=str(uuid.uuid4()),
            event_type=UsageEventType.ERROR_OCCURRED,
            timestamp=time.time(),
            user_id=user_id,
            session_id=self.session_id,
            tool_error=error_message
        )
        
        self._record_event(event)
        self.stats["errors"] += 1
    
    def record_performance_metric(self, cpu_usage: Optional[float] = None,
                                memory_usage: Optional[float] = None,
                                response_time: Optional[float] = None):
        """记录性能指标"""
        event = UsageEvent(
            event_id=str(uuid.uuid4()),
            event_type=UsageEventType.PERFORMANCE_METRIC,
            timestamp=time.time(),
            user_id="system",
            session_id=self.session_id,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            response_time=response_time
        )
        
        self._record_event(event)
    
    def _record_event(self, event: UsageEvent):
        """记录事件"""
        try:
            self.persistence.save_event(event)
            self.stats["total_events"] += 1
        except Exception as e:
            logger.error(f"Failed to persist event: {e}")
    
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
            return self.persistence.get_events(event_type=event_type, limit=limit)
        except Exception as e:
            logger.error(f"Failed to get recent events: {e}")
            return []
    
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
            return self.persistence.get_events(start_time=start_time, user_id=user_id)
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
            recent_tool_calls = self.stats["tool_calls"]
            recent_resource_accesses = self.stats["resource_accesses"]
            recent_errors = self.stats["errors"]
        
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
            "performance": self.performance_data.copy()
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
        success=True,
        execution_time=0.5
    )
    
    monitor.record_tool_call(
        tool_name="aceflow_stage",
        user_id="test_user",
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
        cache_hit=False
    )
    
    monitor.record_resource_access(
        resource_type="workflow_config",
        resource_id="default",
        user_id="test_user",
        success=True,
        cache_hit=True
    )
    
    # 验证统计
    stats = monitor.get_usage_stats()
    assert stats["session"]["resource_accesses"] == 2
    assert stats["session"]["total_events"] == 4
    print("  ✅ Resource access recording test passed")
    
    # 测试3: 记录错误
    print("  Testing error recording...")
    monitor.record_error(
        error_message="Invalid project configuration",
        user_id="test_user"
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

async def test_usage_monitor_analytics():
    """测试使用监控器分析功能"""
    print("🧪 Testing Usage Monitor Analytics...")
    
    monitor = UsageMonitor()
    
    # 记录一些测试数据
    current_time = time.time()
    
    # 记录不同工具的调用
    tools_data = [
        ("aceflow_init", True, 0.5),
        ("aceflow_stage", True, 0.3),
        ("aceflow_validate", False, 0.8),
        ("aceflow_init", True, 0.4),
        ("aceflow_stage", True, 0.2)
    ]
    
    for tool_name, success, exec_time in tools_data:
        monitor.record_tool_call(
            tool_name=tool_name,
            user_id="analytics_user",
            success=success,
            execution_time=exec_time
        )
    
    # 记录资源访问
    for i in range(3):
        monitor.record_resource_access(
            resource_type="project_state",
            resource_id=f"project_{i}",
            user_id="analytics_user",
            cache_hit=i % 2 == 0
        )
    
    # 测试工具使用摘要
    print("  Testing tool usage summary...")
    tool_summary = monitor.get_tool_usage_summary(hours=1)
    
    assert tool_summary["summary"]["total_calls"] == 5
    assert tool_summary["summary"]["successful_calls"] == 4
    assert tool_summary["summary"]["success_rate"] == 0.8
    
    # 验证各工具统计
    by_tool = tool_summary["by_tool"]
    assert by_tool["aceflow_init"]["calls"] == 2
    assert by_tool["aceflow_init"]["successful_calls"] == 2
    assert by_tool["aceflow_stage"]["calls"] == 2
    assert by_tool["aceflow_validate"]["calls"] == 1
    assert by_tool["aceflow_validate"]["successful_calls"] == 0
    print("  ✅ Tool usage summary test passed")
    
    # 测试用户活动
    print("  Testing user activity tracking...")
    user_activity = monitor.get_user_activity("analytics_user", hours=1)
    assert len(user_activity) == 8  # 5个工具调用 + 3个资源访问
    print("  ✅ User activity tracking test passed")
    
    # 测试时间范围查询
    print("  Testing time range queries...")
    start_time = current_time - 60
    end_time = current_time + 60
    
    events = monitor.get_events_by_timerange(start_time, end_time)
    assert len(events) == 8
    
    # 只获取工具调用事件
    tool_events = monitor.get_events_by_timerange(
        start_time, end_time, 
        event_type=UsageEventType.TOOL_CALL
    )
    assert len(tool_events) == 5
    print("  ✅ Time range queries test passed")
    
    print("🎉 All Usage Monitor Analytics tests passed!")
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

async def test_data_cleanup():
    """测试数据清理功能"""
    print("🧪 Testing Data Cleanup...")
    
    persistence = MemoryDataPersistence()
    monitor = UsageMonitor(persistence=persistence)
    
    current_time = time.time()
    
    # 创建一些"旧"事件
    old_event = UsageEvent(
        event_id=str(uuid.uuid4()),
        event_type=UsageEventType.TOOL_CALL,
        timestamp=current_time - (40 * 24 * 3600),  # 40天前
        user_id="old_user",
        session_id="old_session",
        tool_name="old_tool"
    )
    persistence.save_event(old_event)
    
    # 创建一些"新"事件
    for i in range(3):
        monitor.record_tool_call(
            tool_name=f"new_tool_{i}",
            user_id="new_user"
        )
    
    # 验证总事件数
    all_events = monitor.get_recent_events(limit=100)
    assert len(all_events) == 4  # 1个旧事件 + 3个新事件
    
    # 清理30天前的数据
    cleaned_count = monitor.cleanup_old_data(older_than_days=30)
    assert cleaned_count == 1
    
    # 验证清理后的事件数
    remaining_events = monitor.get_recent_events(limit=100)
    assert len(remaining_events) == 3  # 只剩下3个新事件
    
    print("  ✅ Data cleanup test passed")
    print("🎉 All Data Cleanup tests passed!")
    return True

async def main():
    """运行所有测试"""
    print("🚀 Starting Usage Data Collection and Monitoring System tests...\n")
    
    try:
        await test_usage_monitor_basic()
        await test_usage_monitor_analytics()
        await test_performance_monitoring()
        await test_data_cleanup()
        
        print("\n🎉 All Usage Data Collection and Monitoring System tests passed!")
        print("\n📊 Usage Monitoring System Summary:")
        print("   ✅ Basic Event Recording - Working")
        print("   ✅ Tool Usage Analytics - Working")
        print("   ✅ Resource Access Tracking - Working")
        print("   ✅ User Activity Monitoring - Working")
        print("   ✅ Performance Monitoring - Working")
        print("   ✅ Time Range Queries - Working")
        print("   ✅ Data Cleanup - Working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Usage monitoring test failed: {e}")
        import traceback
        traceback.print_exc()
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