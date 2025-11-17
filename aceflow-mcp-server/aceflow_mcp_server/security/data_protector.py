"""
数据保护器
Data Protector

提供敏感信息保护、数据加密和脱敏功能。
"""

import hashlib
import base64
import re
from typing import Dict, Any, Optional, List
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class SensitivityLevel(Enum):
    """敏感度级别"""
    PUBLIC = "public"           # 公开信息
    INTERNAL = "internal"       # 内部信息
    CONFIDENTIAL = "confidential"  # 机密信息
    RESTRICTED = "restricted"   # 限制信息
    SECRET = "secret"           # 秘密信息


class ProtectionLevel(Enum):
    """保护级别"""
    BASIC = "basic"         # 基本保护
    STANDARD = "standard"   # 标准保护
    STRICT = "strict"       # 严格保护


class SensitiveDataType(Enum):
    """敏感数据类型"""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"


class DataProtector:
    """
    数据保护器
    
    提供数据保护功能：
    - 敏感信息检测和脱敏
    - 数据加密和解密
    - 个人信息保护
    - 安全日志记录
    """
    
    def __init__(self):
        # 敏感信息模式
        self._sensitive_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'api_key': r'\b[A-Za-z0-9]{32,}\b',
            'password': r'(password|passwd|pwd)\s*[:=]\s*[\'"]?([^\s\'"]+)',
            'token': r'(token|auth|bearer)\s*[:=]\s*[\'"]?([A-Za-z0-9._-]+)',
        }
        
        # 脱敏规则
        self._masking_rules = {
            'email': lambda m: f"{m.group()[:3]}***@{m.group().split('@')[1]}",
            'phone': lambda m: f"***-***-{m.group()[-4:]}",
            'ssn': lambda m: "***-**-****",
            'credit_card': lambda m: f"****-****-****-{m.group()[-4:]}",
            'ip_address': lambda m: f"{m.group().split('.')[0]}.***.***.***",
            'api_key': lambda m: f"{m.group()[:8]}{'*' * (len(m.group()) - 8)}",
            'password': lambda m: f"{m.group(1)}=***",
            'token': lambda m: f"{m.group(1)}={m.group(2)[:8]}***",
        }
        
        logger.info("Data protector initialized")
    
    def encrypt_sensitive_data(self, data: str, key: Optional[str] = None) -> str:
        """
        加密敏感数据
        
        Args:
            data: 要加密的数据
            key: 加密密钥（可选）
            
        Returns:
            加密后的数据（Base64编码）
        """
        if not isinstance(data, str):
            data = str(data)
        
        try:
            # 使用简单的Base64编码（生产环境应使用更强的加密）
            encoded_data = base64.b64encode(data.encode('utf-8')).decode('utf-8')
            
            # 添加校验和
            checksum = hashlib.md5(data.encode('utf-8')).hexdigest()[:8]
            encrypted_data = f"{encoded_data}.{checksum}"
            
            logger.debug(f"Data encrypted successfully, length: {len(encrypted_data)}")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data
    
    def decrypt_sensitive_data(self, encrypted_data: str, key: Optional[str] = None) -> str:
        """
        解密敏感数据
        
        Args:
            encrypted_data: 加密的数据
            key: 解密密钥（可选）
            
        Returns:
            解密后的数据
        """
        try:
            # 分离数据和校验和
            if '.' not in encrypted_data:
                raise ValueError("Invalid encrypted data format")
            
            encoded_data, checksum = encrypted_data.rsplit('.', 1)
            
            # 解码数据
            decoded_data = base64.b64decode(encoded_data.encode('utf-8')).decode('utf-8')
            
            # 验证校验和
            expected_checksum = hashlib.md5(decoded_data.encode('utf-8')).hexdigest()[:8]
            if checksum != expected_checksum:
                raise ValueError("Data integrity check failed")
            
            logger.debug("Data decrypted successfully")
            return decoded_data
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data
    
    def mask_confidential_info(self, text: str, sensitivity_level: SensitivityLevel = SensitivityLevel.CONFIDENTIAL) -> str:
        """
        脱敏机密信息
        
        Args:
            text: 要脱敏的文本
            sensitivity_level: 敏感度级别
            
        Returns:
            脱敏后的文本
        """
        if not isinstance(text, str):
            text = str(text)
        
        if sensitivity_level == SensitivityLevel.PUBLIC:
            return text
        
        masked_text = text
        
        # 根据敏感度级别应用不同的脱敏策略
        patterns_to_apply = self._get_patterns_for_level(sensitivity_level)
        
        for pattern_name in patterns_to_apply:
            if pattern_name in self._sensitive_patterns:
                pattern = self._sensitive_patterns[pattern_name]
                masking_func = self._masking_rules.get(pattern_name, self._default_mask)
                
                def replacer(match):
                    original = match.group()
                    try:
                        return masking_func(match)
                    except Exception:
                        return self._default_mask(match)
                
                masked_text = re.sub(pattern, replacer, masked_text)
        
        if masked_text != text:
            logger.debug(f"Applied masking for sensitivity level: {sensitivity_level.value}")
        
        return masked_text
    
    def mask_sensitive_data(self, text: str, protection_level: ProtectionLevel = ProtectionLevel.STANDARD) -> str:
        """
        屏蔽敏感数据（别名方法，用于向后兼容）
        
        Args:
            text: 要脱敏的文本
            protection_level: 保护级别
            
        Returns:
            脱敏后的文本
        """
        # 将ProtectionLevel映射到SensitivityLevel
        level_mapping = {
            ProtectionLevel.BASIC: SensitivityLevel.INTERNAL,
            ProtectionLevel.STANDARD: SensitivityLevel.CONFIDENTIAL,
            ProtectionLevel.STRICT: SensitivityLevel.RESTRICTED
        }
        
        sensitivity_level = level_mapping.get(protection_level, SensitivityLevel.CONFIDENTIAL)
        return self.mask_confidential_info(text, sensitivity_level)

    def detect_sensitive_info(self, text: str) -> Dict[str, List[str]]:
        """
        检测敏感信息
        
        Args:
            text: 要检测的文本
            
        Returns:
            检测到的敏感信息字典
        """
        if not isinstance(text, str):
            return {}
        
        detected_info = {}
        
        for info_type, pattern in self._sensitive_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # 对于元组匹配，只取完整匹配
                if isinstance(matches[0], tuple):
                    matches = [match[0] if len(match) > 1 else str(match) for match in matches]
                
                detected_info[info_type] = matches
        
        if detected_info:
            logger.info(f"Detected sensitive information types: {list(detected_info.keys())}")
        
        return detected_info
    
    def sanitize_for_logging(self, data: Any, max_length: int = 1000) -> str:
        """
        为日志记录清理数据
        
        Args:
            data: 要清理的数据
            max_length: 最大长度
            
        Returns:
            清理后的字符串
        """
        if data is None:
            return "None"
        
        # 转换为字符串
        if isinstance(data, dict):
            # 对字典进行特殊处理，避免暴露敏感键
            sanitized_dict = {}
            for key, value in data.items():
                if self._is_sensitive_key(key):
                    sanitized_dict[key] = "***"
                else:
                    sanitized_dict[key] = self._truncate_value(value)
            text = str(sanitized_dict)
        else:
            text = str(data)
        
        # 脱敏敏感信息
        masked_text = self.mask_confidential_info(text, SensitivityLevel.INTERNAL)
        
        # 长度限制
        if len(masked_text) > max_length:
            masked_text = masked_text[:max_length] + "..."
        
        return masked_text
    
    def hash_for_tracking(self, data: str) -> str:
        """
        为跟踪目的生成哈希
        
        Args:
            data: 要哈希的数据
            
        Returns:
            SHA256哈希值
        """
        if not isinstance(data, str):
            data = str(data)
        
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _get_patterns_for_level(self, level: SensitivityLevel) -> List[str]:
        """根据敏感度级别获取需要应用的模式"""
        if level == SensitivityLevel.SECRET:
            return list(self._sensitive_patterns.keys())
        elif level == SensitivityLevel.CONFIDENTIAL:
            return ['email', 'phone', 'ssn', 'credit_card', 'api_key', 'password', 'token']
        elif level == SensitivityLevel.INTERNAL:
            return ['email', 'phone', 'password', 'token']
        else:  # PUBLIC
            return []
    
    def _default_mask(self, match) -> str:
        """默认脱敏函数"""
        original = match.group()
        if len(original) <= 4:
            return "*" * len(original)
        else:
            return original[:2] + "*" * (len(original) - 4) + original[-2:]
    
    def _is_sensitive_key(self, key: str) -> bool:
        """检查键名是否敏感"""
        sensitive_keys = {
            'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'auth',
            'authorization', 'credential', 'private', 'confidential'
        }
        return any(sensitive_word in key.lower() for sensitive_word in sensitive_keys)
    
    def _truncate_value(self, value: Any) -> str:
        """截断值以适合日志记录"""
        if value is None:
            return "None"
        
        text = str(value)
        if len(text) > 100:
            return text[:100] + "..."
        return text


# 全局数据保护器实例
_global_data_protector: Optional[DataProtector] = None


def get_data_protector() -> DataProtector:
    """获取全局数据保护器实例"""
    global _global_data_protector
    if _global_data_protector is None:
        _global_data_protector = DataProtector()
    return _global_data_protector


def protect_sensitive_data(func):
    """敏感数据保护装饰器"""
    def wrapper(*args, **kwargs):
        protector = get_data_protector()
        
        # 检查参数中的敏感信息
        for key, value in kwargs.items():
            if isinstance(value, str):
                sensitive_info = protector.detect_sensitive_info(value)
                if sensitive_info:
                    logger.warning(f"Sensitive information detected in parameter {key}: {list(sensitive_info.keys())}")
        
        return func(*args, **kwargs)
    return wrapper
