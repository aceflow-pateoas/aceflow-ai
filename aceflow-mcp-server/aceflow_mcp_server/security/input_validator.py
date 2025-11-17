"""
输入验证器
Input Validator

提供统一的输入验证机制，防止注入攻击和恶意输入。
"""

import re
import json
import html
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """验证级别"""
    STRICT = "strict"      # 严格验证，拒绝任何可疑输入
    STANDARD = "standard"  # 标准验证，基本安全检查
    RELAXED = "relaxed"    # 宽松验证，仅检查明显恶意输入


class InputType(Enum):
    """输入类型"""
    STRING = "string"
    JSON = "json"
    PATH = "path"
    COMMAND = "command"
    EMAIL = "email"
    URL = "url"
    FILENAME = "filename"


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    error_message: str = ""
    error_code: Optional[str] = None
    sanitized_value: Optional[str] = None


@dataclass
class ValidationRule:
    """验证规则"""
    name: str
    pattern: str
    error_message: str
    severity: str = "high"


class InputValidator:
    """
    输入验证器
    
    提供多层次的输入验证和清理功能，包括：
    - SQL注入检测
    - XSS攻击防护
    - 路径遍历检测
    - 命令注入防护
    - 数据格式验证
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.validation_level = validation_level
        
        # 恶意模式检测规则
        self._injection_patterns = {
            'sql_injection': [
                r"(\bunion\b|\bselect\b|\binsert\b|\bdelete\b|\bdrop\b|\btable\b)",
                r"(--|#|/\*|\*/)",
                r"(\bor\b|\band\b)\s+[0-9]+=\s*[0-9]+",
                r"(\'\s*or\s*\'\s*=\s*\'|\"\s*or\s*\"\s*=\s*\")",
            ],
            'xss_injection': [
                r"<\s*script[^>]*>",
                r"javascript\s*:",
                r"on\w+\s*=",
                r"<\s*iframe[^>]*>",
                r"<\s*object[^>]*>",
                r"<\s*embed[^>]*>",
            ],
            'command_injection': [
                r"[;&|`$(){}\[\]]",
                r"(\.\./|\.\.\\)",
                r"(cat|ls|pwd|whoami|id|uname)\s",
                r"(rm|del|format|shutdown)\s",
            ],
            'path_traversal': [
                r"\.\.[\\/]",
                r"[\\/]\.\.[\\/]",
                r"~[\\/]",
                r"[\\/]etc[\\/]",
                r"[\\/]proc[\\/]",
            ]
        }
        
        # 允许的字符集
        self._allowed_chars = {
            InputType.STRING: r"[a-zA-Z0-9\s\-_.,!?@#$%^&*()+={}[\]:;\"'<>/\\|`~]",
            InputType.FILENAME: r"[a-zA-Z0-9\-_.]",
            InputType.PATH: r"[a-zA-Z0-9\-_./\\:]",
            InputType.EMAIL: r"[a-zA-Z0-9@._-]",
            InputType.URL: r"[a-zA-Z0-9:/?#\[\]@!$&'()*+,;=._~-]",
        }
        
        # 长度限制
        self._length_limits = {
            InputType.STRING: 10000,
            InputType.FILENAME: 255,
            InputType.PATH: 4096,
            InputType.EMAIL: 254,
            InputType.URL: 2048,
            InputType.COMMAND: 1000,
        }
        
        logger.info(f"Input validator initialized with level: {validation_level.value}")
    
    def validate_tool_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证工具参数
        
        Args:
            params: 工具参数字典
            
        Returns:
            验证和清理后的参数字典
        """
        validated_params = {}
        
        for key, value in params.items():
            try:
                # 验证参数名
                if not self._is_valid_param_name(key):
                    logger.warning(f"Invalid parameter name: {key}")
                    continue
                
                # 验证参数值
                validated_value = self._validate_param_value(key, value)
                if validated_value is not None:
                    validated_params[key] = validated_value
                else:
                    logger.warning(f"Parameter {key} failed validation")
                    
            except Exception as e:
                logger.error(f"Error validating parameter {key}: {e}")
                continue
        
        return validated_params
    
    def sanitize_input(self, data: Any, input_type: InputType = InputType.STRING) -> Any:
        """
        清理输入数据
        
        Args:
            data: 输入数据
            input_type: 输入类型
            
        Returns:
            清理后的数据
        """
        if data is None:
            return None
        
        if isinstance(data, str):
            return self._sanitize_string(data, input_type)
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v, input_type) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item, input_type) for item in data]
        else:
            return data
    
    def check_injection_patterns(self, text: str) -> Dict[str, List[str]]:
        """
        检查注入攻击模式
        
        Args:
            text: 要检查的文本
            
        Returns:
            检测到的攻击模式字典
        """
        if not isinstance(text, str):
            return {}
        
        detected_patterns = {}
        text_lower = text.lower()
        
        for attack_type, patterns in self._injection_patterns.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matches.append(pattern)
            
            if matches:
                detected_patterns[attack_type] = matches
        
        return detected_patterns
    
    def validate_json(self, json_str: str, max_depth: int = 10) -> Optional[Dict]:
        """
        验证JSON字符串
        
        Args:
            json_str: JSON字符串
            max_depth: 最大嵌套深度
            
        Returns:
            解析后的JSON对象或None
        """
        try:
            # 长度检查
            if len(json_str) > self._length_limits.get(InputType.JSON, 100000):
                logger.warning("JSON string too long")
                return None
            
            # 解析JSON
            data = json.loads(json_str)
            
            # 深度检查
            if self._get_dict_depth(data) > max_depth:
                logger.warning("JSON nesting too deep")
                return None
            
            return data
            
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON: {e}")
            return None
    
    def validate_file_path(self, path: str) -> bool:
        """
        验证文件路径
        
        Args:
            path: 文件路径
            
        Returns:
            路径是否有效
        """
        if not isinstance(path, str):
            return False
        
        # 长度检查
        if len(path) > self._length_limits[InputType.PATH]:
            return False
        
        # 路径遍历检查
        traversal_patterns = self._injection_patterns['path_traversal']
        for pattern in traversal_patterns:
            if re.search(pattern, path):
                logger.warning(f"Path traversal attempt detected: {path}")
                return False
        
        # 字符检查
        allowed_pattern = self._allowed_chars[InputType.PATH]
        if not re.match(f"^{allowed_pattern}+$", path):
            return False
        
        return True
    
    def _is_valid_param_name(self, name: str) -> bool:
        """验证参数名是否有效"""
        if not isinstance(name, str):
            return False
        
        # 参数名只能包含字母、数字、下划线
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
            return False
        
        # 长度限制
        if len(name) > 64:
            return False
        
        return True
    
    def _validate_param_value(self, param_name: str, value: Any) -> Any:
        """验证参数值"""
        if value is None:
            return None
        
        # 字符串类型验证
        if isinstance(value, str):
            # 注入攻击检查
            if self.validation_level in [ValidationLevel.STRICT, ValidationLevel.STANDARD]:
                injection_patterns = self.check_injection_patterns(value)
                if injection_patterns:
                    logger.warning(f"Injection patterns detected in {param_name}: {injection_patterns}")
                    if self.validation_level == ValidationLevel.STRICT:
                        return None
            
            # 长度检查
            if len(value) > self._length_limits[InputType.STRING]:
                logger.warning(f"Parameter {param_name} too long")
                return None
            
            # 清理字符串
            return self._sanitize_string(value, InputType.STRING)
        
        # 数字类型验证
        elif isinstance(value, (int, float)):
            # 范围检查
            if abs(value) > 1e10:
                logger.warning(f"Parameter {param_name} value too large")
                return None
            return value
        
        # 布尔类型验证
        elif isinstance(value, bool):
            return value
        
        # 列表类型验证
        elif isinstance(value, list):
            if len(value) > 1000:
                logger.warning(f"Parameter {param_name} list too long")
                return None
            return [self._validate_param_value(f"{param_name}[{i}]", item) for i, item in enumerate(value)]
        
        # 字典类型验证
        elif isinstance(value, dict):
            if len(value) > 100:
                logger.warning(f"Parameter {param_name} dict too large")
                return None
            return {k: self._validate_param_value(f"{param_name}.{k}", v) for k, v in value.items()}
        
        else:
            logger.warning(f"Unsupported parameter type for {param_name}: {type(value)}")
            return None
    
    def _sanitize_string(self, text: str, input_type: InputType) -> str:
        """清理字符串"""
        if not isinstance(text, str):
            return str(text)
        
        # HTML编码特殊字符
        if input_type in [InputType.STRING]:
            text = html.escape(text)
        
        # 移除控制字符
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
        
        # 长度限制
        max_length = self._length_limits.get(input_type, 1000)
        if len(text) > max_length:
            text = text[:max_length]
            logger.warning(f"Text truncated to {max_length} characters")
        
        return text
    
    def _get_dict_depth(self, data: Any, current_depth: int = 0) -> int:
        """获取字典/列表的嵌套深度"""
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(self._get_dict_depth(value, current_depth + 1) for value in data.values())
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(self._get_dict_depth(item, current_depth + 1) for item in data)
        else:
            return current_depth


# 全局输入验证器实例
_global_input_validator: Optional[InputValidator] = None


def get_input_validator() -> InputValidator:
    """获取全局输入验证器实例"""
    global _global_input_validator
    if _global_input_validator is None:
        _global_input_validator = InputValidator()
    return _global_input_validator


def validate_input_decorator(input_type: InputType = InputType.STRING):
    """输入验证装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            validator = get_input_validator()
            
            # 验证关键字参数
            validated_kwargs = validator.validate_tool_params(kwargs)
            
            return func(*args, **validated_kwargs)
        return wrapper
    return decorator
