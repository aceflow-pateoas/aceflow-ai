"""
安全系统综合测试
Test Security System

测试完整的安全控制系统，包括输入验证、访问控制、数据保护和审计日志。
"""
import pytest
import tempfile
import os
import time
from unittest.mock import Mock, patch

from aceflow_mcp_server.security import (
    InputValidator, ValidationRule, ValidationResult,
    AccessController, DataProtector, SensitiveDataType, ProtectionLevel,
    AuditLogger, AuditLevel, AuditCategory
)

class TestSecuritySystemIntegration:
    """安全系统集成测试类"""

    def setup_method(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "security_test.log")
        
        # 初始化安全组件
        self.input_validator = InputValidator()
        self.access_controller = AccessController()
        self.data_protector = DataProtector()
        self.audit_logger = AuditLogger(log_file=self.log_file)

    def teardown_method(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_security_workflow(self):
        """测试完整的安全工作流"""
        user_id = "test_user"
        resource = "sensitive_data"
        
        # 1. 设置用户角色和资源权限
        self.access_controller.set_user_roles(user_id, {"user", "reader"})
        self.access_controller.set_resource_permissions(resource, {"reader", "admin"})
        
        # 2. 验证输入数据
        test_data = {
            "query": "SELECT * FROM users WHERE id = 123",
            "file_path": "/safe/path/file.txt",
            "content": "Normal content without sensitive data"
        }
        
        # 验证SQL查询
        sql_result = self.input_validator.validate_sql_injection(test_data["query"])
        assert sql_result.is_valid
        
        # 验证路径遍历
        path_result = self.input_validator.validate_path_traversal(test_data["file_path"])
        assert path_result.is_valid
        
        # 3. 检查访问权限
        has_permission = self.access_controller.check_permission(user_id, resource)
        assert has_permission
        
        # 4. 检查速率限制
        within_limit = self.access_controller.enforce_rate_limiting(user_id, max_requests=10)
        assert within_limit
        
        # 5. 保护敏感数据
        protected_data = self.data_protector.protect_data(
            "User SSN: 123-45-6789",
            ProtectionLevel.STRICT
        )
        assert "123-45-6789" not in protected_data
        
        # 6. 记录安全事件
        self.audit_logger.log_data_access(
            user_id=user_id,
            resource=resource,
            action="read",
            result="success",
            details={"data_size": len(test_data["content"])}
        )
        
        # 验证审计日志
        events = self.audit_logger.query_events(user_id=user_id)
        assert len(events) == 1
        assert events[0].action == "read"
        assert events[0].result == "success"

    def test_security_violation_detection(self):
        """测试安全违规检测"""
        user_id = "malicious_user"
        
        # 1. SQL注入尝试
        malicious_sql = "SELECT * FROM users WHERE id = 1; DROP TABLE users; --"
        sql_result = self.input_validator.validate_sql_injection(malicious_sql)
        assert not sql_result.is_valid
        assert "SQL injection" in sql_result.error_message
        
        # 记录安全事件
        self.audit_logger.log_security_event(
            event_type="sql_injection_attempt",
            action="validate_input",
            result="blocked",
            user_id=user_id,
            details={"query": malicious_sql}
        )
        
        # 2. 路径遍历尝试
        malicious_path = "../../../etc/passwd"
        path_result = self.input_validator.validate_path_traversal(malicious_path)
        assert not path_result.is_valid
        assert "path traversal" in path_result.error_message
        
        # 3. XSS尝试
        xss_input = "<script>alert('XSS')</script>"
        xss_result = self.input_validator.validate_xss(xss_input)
        assert not xss_result.is_valid
        assert "XSS" in xss_result.error_message
        
        # 4. 访问被拒绝
        restricted_resource = "admin_panel"
        self.access_controller.set_resource_permissions(restricted_resource, {"admin"})
        self.access_controller.set_user_roles(user_id, {"user"})
        
        has_permission = self.access_controller.check_permission(user_id, restricted_resource)
        assert not has_permission
        
        # 记录授权失败
        self.audit_logger.log_authorization(
            user_id=user_id,
            resource=restricted_resource,
            action="access",
            result="denied",
            details={"reason": "insufficient_privileges"}
        )
        
        # 验证安全事件被记录
        security_events = self.audit_logger.query_events(
            category=AuditCategory.SECURITY_EVENT,
            user_id=user_id
        )
        assert len(security_events) > 0

    def test_rate_limiting_enforcement(self):
        """测试速率限制执行"""
        user_id = "frequent_user"
        max_requests = 5
        
        # 在限制内的请求应该通过
        for i in range(max_requests):
            within_limit = self.access_controller.enforce_rate_limiting(
                user_id, max_requests=max_requests
            )
            assert within_limit
            
            # 记录每次访问
            self.audit_logger.log_data_access(
                user_id=user_id,
                resource="api_endpoint",
                action="request",
                result="success",
                details={"request_number": i + 1}
            )
        
        # 超过限制的请求应该被拒绝
        exceeded = self.access_controller.enforce_rate_limiting(
            user_id, max_requests=max_requests
        )
        assert not exceeded
        
        # 记录速率限制违规
        self.audit_logger.log_security_event(
            event_type="rate_limit_exceeded",
            action="rate_check",
            result="blocked",
            user_id=user_id,
            details={"max_requests": max_requests}
        )
        
        # 验证事件记录
        rate_limit_events = self.audit_logger.query_events(
            event_type="rate_limit_exceeded"
        )
        assert len(rate_limit_events) > 0

    def test_sensitive_data_protection(self):
        """测试敏感数据保护"""
        # 测试不同级别的数据保护
        test_data = "User credit card: 4532-1234-5678-9012, SSN: 123-45-6789, Email: user@example.com"
        
        # 基本保护级别
        basic_protected = self.data_protector.protect_data(test_data, ProtectionLevel.BASIC)
        assert "4532-1234-5678-9012" not in basic_protected  # 信用卡号应被保护
        assert "user@example.com" in basic_protected  # 邮箱在基本级别可能不被保护
        
        # 严格保护级别
        strict_protected = self.data_protector.protect_data(test_data, ProtectionLevel.STRICT)
        assert "4532-1234-5678-9012" not in strict_protected
        assert "123-45-6789" not in strict_protected
        assert "user@example.com" not in strict_protected  # 在严格级别邮箱也应被保护
        
        # 记录数据保护事件
        self.audit_logger.log_system_operation(
            action="data_protection",
            result="success",
            details={
                "protection_level": "strict",
                "data_types_found": ["credit_card", "ssn", "email"]
            }
        )

    def test_validation_rules_customization(self):
        """测试自定义验证规则"""
        # 添加自定义验证规则
        def validate_phone_number(value):
            import re
            phone_pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
            if re.match(phone_pattern, value):
                return ValidationResult(True, "Valid phone number")
            else:
                return ValidationResult(False, "Invalid phone number format", "INVALID_PHONE")
        
        rule = ValidationRule(
            name="phone_number",
            validator=validate_phone_number,
            error_message="Phone number format is invalid"
        )
        
        self.input_validator.add_rule(rule)
        
        # 测试有效电话号码
        valid_result = self.input_validator.validate_custom("phone_number", "+1-555-123-4567")
        assert valid_result.is_valid
        
        # 测试无效电话号码
        invalid_result = self.input_validator.validate_custom("phone_number", "invalid-phone")
        assert not invalid_result.is_valid
        assert invalid_result.error_code == "INVALID_PHONE"

    def test_data_encryption_decryption(self):
        """测试数据加密解密"""
        original_data = "Sensitive information that needs protection"
        
        # 加密数据
        encrypted_data = self.data_protector.encrypt_data(original_data)
        assert encrypted_data != original_data
        assert len(encrypted_data) > len(original_data)  # 加密后数据通常更长
        
        # 解密数据
        decrypted_data = self.data_protector.decrypt_data(encrypted_data)
        assert decrypted_data == original_data
        
        # 记录加密操作
        self.audit_logger.log_system_operation(
            action="data_encryption",
            result="success",
            details={
                "original_length": len(original_data),
                "encrypted_length": len(encrypted_data)
            }
        )

    def test_audit_log_analysis(self):
        """测试审计日志分析"""
        # 生成一系列测试事件
        test_events = [
            ("user1", "login", "success"),
            ("user1", "data_access", "success"),
            ("user2", "login", "failed"),
            ("user2", "login", "failed"),
            ("user2", "login", "success"),
            ("user1", "admin_access", "denied")
        ]
        
        for user, action, result in test_events:
            if action == "login":
                self.audit_logger.log_authentication(user, action, result)
            elif action == "data_access":
                self.audit_logger.log_data_access(user, "database", action, result)
            elif action == "admin_access":
                self.audit_logger.log_authorization(user, "admin_panel", action, result)
        
        # 分析审计日志
        stats = self.audit_logger.get_statistics()
        
        assert stats["total_events"] == len(test_events)
        assert stats["category_stats"]["authentication"] >= 3  # 至少3个认证事件
        assert stats["level_stats"]["WARNING"] >= 1  # 至少1个警告（授权失败）
        
        # 查询特定用户的事件
        user1_events = self.audit_logger.query_events(user_id="user1")
        user2_events = self.audit_logger.query_events(user_id="user2")
        
        assert len(user1_events) >= 2
        assert len(user2_events) >= 3

if __name__ == "__main__":
    pytest.main([__file__])
