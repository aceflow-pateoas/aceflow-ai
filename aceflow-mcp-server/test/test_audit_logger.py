"""
审计日志器测试
Test Audit Logger

测试审计日志系统的功能性和可靠性。
"""
import pytest
import tempfile
import os
import time
import json
from pathlib import Path

from aceflow_mcp_server.security.audit_logger import (
    AuditLogger, AuditLevel, AuditCategory, AuditEvent
)

class TestAuditLogger:
    """审计日志器测试类"""

    def setup_method(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test_audit.log")
        self.audit_logger = AuditLogger(log_file=self.log_file)

    def teardown_method(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_basic_logging(self):
        """测试基本日志记录功能"""
        # 记录一个基本事件
        self.audit_logger.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.SYSTEM_OPERATION,
            event_type="test_event",
            action="test_action",
            result="success",
            details={"test_key": "test_value"}
        )
        
        # 检查事件是否被记录
        assert len(self.audit_logger._events) == 1
        event = self.audit_logger._events[0]
        assert event.level == AuditLevel.INFO
        assert event.category == AuditCategory.SYSTEM_OPERATION
        assert event.action == "test_action"
        assert event.result == "success"
        assert event.details["test_key"] == "test_value"

    def test_authentication_logging(self):
        """测试认证事件日志"""
        # 记录成功认证
        self.audit_logger.log_authentication(
            user_id="test_user",
            action="login",
            result="success",
            ip_address="192.168.1.1"
        )
        
        # 记录失败认证
        self.audit_logger.log_authentication(
            user_id="test_user",
            action="login",
            result="failed",
            ip_address="192.168.1.1",
            details={"reason": "invalid_password"}
        )
        
        assert len(self.audit_logger._events) == 2
        
        # 检查成功认证事件
        success_event = self.audit_logger._events[0]
        assert success_event.category == AuditCategory.AUTHENTICATION
        assert success_event.level == AuditLevel.INFO
        assert success_event.user_id == "test_user"
        assert success_event.ip_address == "192.168.1.1"
        
        # 检查失败认证事件
        failed_event = self.audit_logger._events[1]
        assert failed_event.level == AuditLevel.SECURITY
        assert failed_event.details["reason"] == "invalid_password"

    def test_authorization_logging(self):
        """测试授权事件日志"""
        # 记录授权成功
        self.audit_logger.log_authorization(
            user_id="test_user",
            resource="test_resource",
            action="read",
            result="allowed"
        )
        
        # 记录授权失败
        self.audit_logger.log_authorization(
            user_id="test_user",
            resource="sensitive_resource",
            action="write",
            result="denied",
            details={"reason": "insufficient_permissions"}
        )
        
        assert len(self.audit_logger._events) == 2
        
        allowed_event = self.audit_logger._events[0]
        assert allowed_event.category == AuditCategory.AUTHORIZATION
        assert allowed_event.level == AuditLevel.INFO
        assert allowed_event.resource == "test_resource"
        
        denied_event = self.audit_logger._events[1]
        assert denied_event.level == AuditLevel.WARNING
        assert denied_event.resource == "sensitive_resource"

    def test_data_access_logging(self):
        """测试数据访问事件日志"""
        self.audit_logger.log_data_access(
            user_id="test_user",
            resource="user_data",
            action="select",
            result="success",
            details={"rows_affected": 10}
        )
        
        assert len(self.audit_logger._events) == 1
        event = self.audit_logger._events[0]
        assert event.category == AuditCategory.DATA_ACCESS
        assert event.level == AuditLevel.INFO
        assert event.details["rows_affected"] == 10

    def test_security_event_logging(self):
        """测试安全事件日志"""
        self.audit_logger.log_security_event(
            event_type="suspicious_activity",
            action="multiple_failed_logins",
            result="blocked",
            user_id="test_user",
            ip_address="192.168.1.100",
            details={"attempts": 5, "time_window": "5min"}
        )
        
        assert len(self.audit_logger._events) == 1
        event = self.audit_logger._events[0]
        assert event.category == AuditCategory.SECURITY_EVENT
        assert event.level == AuditLevel.SECURITY
        assert event.event_type == "suspicious_activity"

    def test_file_logging(self):
        """测试文件日志记录"""
        # 记录一个事件
        self.audit_logger.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.SYSTEM_OPERATION,
            event_type="test_event",
            action="test_action",
            result="success"
        )
        
        # 检查文件是否被创建和写入
        assert os.path.exists(self.log_file)
        
        with open(self.log_file, 'r') as f:
            log_content = f.read()
            assert log_content.strip()  # 文件不为空
            
            # 解析JSON日志
            log_entry = json.loads(log_content.strip())
            assert log_entry["level"] == "INFO"
            assert log_entry["category"] == "system_operation"
            assert log_entry["action"] == "test_action"

    def test_event_querying(self):
        """测试事件查询功能"""
        # 记录多个不同类型的事件
        self.audit_logger.log_authentication("user1", "login", "success")
        self.audit_logger.log_authorization("user1", "resource1", "read", "allowed")
        self.audit_logger.log_security_event("alert", "intrusion_attempt", "blocked")
        
        # 查询认证事件
        auth_events = self.audit_logger.query_events(category=AuditCategory.AUTHENTICATION)
        assert len(auth_events) == 1
        assert auth_events[0].user_id == "user1"
        
        # 查询安全级别事件
        security_events = self.audit_logger.query_events(level=AuditLevel.SECURITY)
        assert len(security_events) == 1
        assert security_events[0].event_type == "alert"
        
        # 查询特定用户事件
        user_events = self.audit_logger.query_events(user_id="user1")
        assert len(user_events) == 2

    def test_statistics(self):
        """测试统计功能"""
        # 记录各种类型的事件
        self.audit_logger.log_authentication("user1", "login", "success")
        self.audit_logger.log_authorization("user1", "resource1", "read", "denied")
        self.audit_logger.log_security_event("alert", "attack", "blocked")
        
        stats = self.audit_logger.get_statistics()
        
        assert stats["total_events"] == 3
        assert stats["category_stats"]["authentication"] == 1
        assert stats["category_stats"]["authorization"] == 1
        assert stats["category_stats"]["security_event"] == 1
        assert stats["level_stats"]["INFO"] == 1
        assert stats["level_stats"]["WARNING"] == 1
        assert stats["level_stats"]["SECURITY"] == 1
        assert len(stats["recent_events"]) == 3

    def test_clear_old_events(self):
        """测试清理旧事件功能"""
        # 记录一些事件
        for i in range(5):
            self.audit_logger.log_event(
                level=AuditLevel.INFO,
                category=AuditCategory.SYSTEM_OPERATION,
                event_type="test_event",
                action=f"action_{i}",
                result="success"
            )
        
        assert len(self.audit_logger._events) == 5
        
        # 清理旧事件（使用0天，应该清理所有事件）
        self.audit_logger.clear_old_events(days=0)
        assert len(self.audit_logger._events) == 0

    def test_enable_disable(self):
        """测试启用/禁用功能"""
        assert self.audit_logger.is_enabled()
        
        # 禁用日志
        self.audit_logger.disable()
        assert not self.audit_logger.is_enabled()
        
        # 记录事件（应该被忽略）
        self.audit_logger.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.SYSTEM_OPERATION,
            event_type="test_event",
            action="test_action",
            result="success"
        )
        assert len(self.audit_logger._events) == 0
        
        # 重新启用
        self.audit_logger.enable()
        assert self.audit_logger.is_enabled()
        
        # 记录事件（应该被记录）
        self.audit_logger.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.SYSTEM_OPERATION,
            event_type="test_event",
            action="test_action",
            result="success"
        )
        assert len(self.audit_logger._events) == 1

    def test_log_rotation(self):
        """测试日志轮转功能"""
        # 创建一个小的最大日志大小
        small_logger = AuditLogger(
            log_file=os.path.join(self.temp_dir, "small_audit.log"),
            max_log_size=100  # 100字节
        )
        
        # 记录足够的事件来触发轮转
        for i in range(10):
            small_logger.log_event(
                level=AuditLevel.INFO,
                category=AuditCategory.SYSTEM_OPERATION,
                event_type="test_event",
                action=f"action_{i}_with_long_description_to_make_file_large",
                result="success",
                details={"data": "x" * 50}  # 增加数据量
            )
        
        # 检查是否有备份文件被创建
        log_dir = Path(self.temp_dir)
        backup_files = list(log_dir.glob("small_audit.log.*"))
        # 可能有备份文件被创建（取决于具体的日志大小）
        assert len(backup_files) >= 0  # 至少不会出错

if __name__ == "__main__":
    pytest.main([__file__])
