"""
PATEOAS 配置管理
管理 PATEOAS 功能的配置选项和参数
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class PATEOASConfig:
    """PATEOAS 配置类"""
    
    # 状态管理配置
    state_persistence_enabled: bool = True
    state_history_limit: int = 100
    state_cache_size: int = 1000
    
    # 记忆系统配置
    memory_enabled: bool = True
    memory_retention_days: int = 90
    memory_max_size_mb: int = 100
    memory_similarity_threshold: float = 0.7
    
    # 流程控制配置
    adaptive_flow_enabled: bool = True
    parallel_execution_enabled: bool = True
    auto_optimization_enabled: bool = True
    
    # 决策门配置
    intelligent_gates_enabled: bool = True
    adaptive_thresholds_enabled: bool = True
    context_aware_quality: bool = True
    
    # AI 配置
    ai_confidence_threshold: float = 0.8
    auto_execution_threshold: float = 0.9
    reasoning_chain_enabled: bool = True
    meta_cognition_enabled: bool = True
    
    # 性能配置
    async_processing_enabled: bool = True
    caching_enabled: bool = True
    vector_indexing_enabled: bool = False  # 需要额外依赖
    
    # 调试配置
    debug_mode: bool = False
    verbose_logging: bool = False
    performance_monitoring: bool = True
    
    # 文件路径配置
    state_storage_path: str = ".aceflow/pateoas/state"
    memory_storage_path: str = ".aceflow/pateoas/memory"
    config_file_path: str = ".aceflow/pateoas/config.yaml"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'state_management': {
                'persistence_enabled': self.state_persistence_enabled,
                'history_limit': self.state_history_limit,
                'cache_size': self.state_cache_size
            },
            'memory_system': {
                'enabled': self.memory_enabled,
                'retention_days': self.memory_retention_days,
                'max_size_mb': self.memory_max_size_mb,
                'similarity_threshold': self.memory_similarity_threshold
            },
            'flow_control': {
                'adaptive_flow_enabled': self.adaptive_flow_enabled,
                'parallel_execution_enabled': self.parallel_execution_enabled,
                'auto_optimization_enabled': self.auto_optimization_enabled
            },
            'decision_gates': {
                'intelligent_gates_enabled': self.intelligent_gates_enabled,
                'adaptive_thresholds_enabled': self.adaptive_thresholds_enabled,
                'context_aware_quality': self.context_aware_quality
            },
            'ai_settings': {
                'confidence_threshold': self.ai_confidence_threshold,
                'auto_execution_threshold': self.auto_execution_threshold,
                'reasoning_chain_enabled': self.reasoning_chain_enabled,
                'meta_cognition_enabled': self.meta_cognition_enabled
            },
            'performance': {
                'async_processing_enabled': self.async_processing_enabled,
                'caching_enabled': self.caching_enabled,
                'vector_indexing_enabled': self.vector_indexing_enabled
            },
            'debug': {
                'debug_mode': self.debug_mode,
                'verbose_logging': self.verbose_logging,
                'performance_monitoring': self.performance_monitoring
            },
            'paths': {
                'state_storage': self.state_storage_path,
                'memory_storage': self.memory_storage_path,
                'config_file': self.config_file_path
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PATEOASConfig':
        """从字典创建配置对象"""
        config = cls()
        
        # 状态管理配置
        if 'state_management' in data:
            sm = data['state_management']
            config.state_persistence_enabled = sm.get('persistence_enabled', True)
            config.state_history_limit = sm.get('history_limit', 100)
            config.state_cache_size = sm.get('cache_size', 1000)
        
        # 记忆系统配置
        if 'memory_system' in data:
            ms = data['memory_system']
            config.memory_enabled = ms.get('enabled', True)
            config.memory_retention_days = ms.get('retention_days', 90)
            config.memory_max_size_mb = ms.get('max_size_mb', 100)
            config.memory_similarity_threshold = ms.get('similarity_threshold', 0.7)
        
        # 流程控制配置
        if 'flow_control' in data:
            fc = data['flow_control']
            config.adaptive_flow_enabled = fc.get('adaptive_flow_enabled', True)
            config.parallel_execution_enabled = fc.get('parallel_execution_enabled', True)
            config.auto_optimization_enabled = fc.get('auto_optimization_enabled', True)
        
        # 决策门配置
        if 'decision_gates' in data:
            dg = data['decision_gates']
            config.intelligent_gates_enabled = dg.get('intelligent_gates_enabled', True)
            config.adaptive_thresholds_enabled = dg.get('adaptive_thresholds_enabled', True)
            config.context_aware_quality = dg.get('context_aware_quality', True)
        
        # AI 配置
        if 'ai_settings' in data:
            ai = data['ai_settings']
            config.ai_confidence_threshold = ai.get('confidence_threshold', 0.8)
            config.auto_execution_threshold = ai.get('auto_execution_threshold', 0.9)
            config.reasoning_chain_enabled = ai.get('reasoning_chain_enabled', True)
            config.meta_cognition_enabled = ai.get('meta_cognition_enabled', True)
        
        # 性能配置
        if 'performance' in data:
            perf = data['performance']
            config.async_processing_enabled = perf.get('async_processing_enabled', True)
            config.caching_enabled = perf.get('caching_enabled', True)
            config.vector_indexing_enabled = perf.get('vector_indexing_enabled', False)
        
        # 调试配置
        if 'debug' in data:
            debug = data['debug']
            config.debug_mode = debug.get('debug_mode', False)
            config.verbose_logging = debug.get('verbose_logging', False)
            config.performance_monitoring = debug.get('performance_monitoring', True)
        
        # 路径配置
        if 'paths' in data:
            paths = data['paths']
            config.state_storage_path = paths.get('state_storage', '.aceflow/pateoas/state')
            config.memory_storage_path = paths.get('memory_storage', '.aceflow/pateoas/memory')
            config.config_file_path = paths.get('config_file', '.aceflow/pateoas/config.yaml')
        
        return config
    
    def save_to_file(self, file_path: Optional[str] = None):
        """保存配置到文件"""
        if file_path is None:
            file_path = self.config_file_path
        
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)
    
    @classmethod
    def load_from_file(cls, file_path: Optional[str] = None) -> 'PATEOASConfig':
        """从文件加载配置"""
        if file_path is None:
            file_path = cls().config_file_path
        
        if not os.path.exists(file_path):
            # 如果配置文件不存在，返回默认配置
            return cls()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return cls.from_dict(data or {})
        except Exception as e:
            print(f"加载 PATEOAS 配置文件失败: {e}")
            return cls()
    
    def ensure_directories(self):
        """确保所需目录存在"""
        directories = [
            self.state_storage_path,
            self.memory_storage_path,
            Path(self.config_file_path).parent
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


# 全局配置实例
_global_config: Optional[PATEOASConfig] = None


def get_config() -> PATEOASConfig:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = PATEOASConfig.load_from_file()
        _global_config.ensure_directories()
    return _global_config


def set_config(config: PATEOASConfig):
    """设置全局配置实例"""
    global _global_config
    _global_config = config
    config.ensure_directories()


def reload_config():
    """重新加载配置"""
    global _global_config
    _global_config = None
    return get_config()