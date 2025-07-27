"""
PATEOAS配置管理系统
提供功能开关、配置选项和渐进式部署支持
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from .config import get_config
from .utils import ensure_directory


class FeatureFlag(Enum):
    """功能开关枚举"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


class DeploymentStage(Enum):
    """部署阶段枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class FeatureConfig:
    """功能配置"""
    name: str
    enabled: bool = True
    flag: FeatureFlag = FeatureFlag.ENABLED
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    min_version: Optional[str] = None
    max_version: Optional[str] = None
    deployment_stages: List[DeploymentStage] = field(default_factory=lambda: [DeploymentStage.DEVELOPMENT])
    rollout_percentage: float = 100.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def is_available_for_stage(self, stage: DeploymentStage) -> bool:
        """检查功能是否在指定阶段可用"""
        return stage in self.deployment_stages
    
    def is_enabled_for_rollout(self, user_id: Optional[str] = None) -> bool:
        """检查功能是否在渐进式部署中启用"""
        if not self.enabled or self.flag == FeatureFlag.DISABLED:
            return False
        
        if self.rollout_percentage >= 100.0:
            return True
        
        if user_id:
            # 基于用户ID的一致性哈希来决定是否启用
            import hashlib
            hash_value = int(hashlib.md5(f"{self.name}_{user_id}".encode()).hexdigest(), 16)
            return (hash_value % 100) < self.rollout_percentage
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'flag': self.flag.value,
            'description': self.description,
            'dependencies': self.dependencies,
            'min_version': self.min_version,
            'max_version': self.max_version,
            'deployment_stages': [stage.value for stage in self.deployment_stages],
            'rollout_percentage': self.rollout_percentage,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeatureConfig':
        """从字典创建"""
        return cls(
            name=data['name'],
            enabled=data.get('enabled', True),
            flag=FeatureFlag(data.get('flag', 'enabled')),
            description=data.get('description', ''),
            dependencies=data.get('dependencies', []),
            min_version=data.get('min_version'),
            max_version=data.get('max_version'),
            deployment_stages=[DeploymentStage(stage) for stage in data.get('deployment_stages', ['development'])],
            rollout_percentage=data.get('rollout_percentage', 100.0),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )


@dataclass
class PATEOASConfig:
    """PATEOAS主配置"""
    # 核心功能开关
    enable_state_continuity: bool = True
    enable_memory_system: bool = True
    enable_adaptive_flow: bool = True
    enable_decision_gates: bool = True
    enable_performance_monitoring: bool = True
    enable_exception_handling: bool = True
    
    # 性能配置
    state_cache_size: int = 1000
    memory_cache_size: int = 1000
    vector_dimension: int = 384
    max_memory_fragments: int = 10000
    
    # 决策门配置
    decision_gate_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'DG1_confidence_threshold': 0.7,
        'DG2_confidence_threshold': 0.8,
        'quality_threshold': 0.6
    })
    
    # 记忆系统配置
    memory_categories: List[str] = field(default_factory=lambda: [
        'requirement', 'decision', 'pattern', 'issue', 'learning', 'context'
    ])
    memory_retention_days: int = 90
    memory_importance_threshold: float = 0.3
    
    # 性能监控配置
    performance_metrics_enabled: bool = True
    performance_alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'response_time_warning': 2.0,
        'response_time_critical': 5.0,
        'success_rate_warning': 0.8,
        'success_rate_critical': 0.6
    })
    
    # 部署配置
    deployment_stage: DeploymentStage = DeploymentStage.DEVELOPMENT
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # 版本信息
    pateoas_version: str = "2.0.0"
    config_version: str = "1.0.0"
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'enable_state_continuity': self.enable_state_continuity,
            'enable_memory_system': self.enable_memory_system,
            'enable_adaptive_flow': self.enable_adaptive_flow,
            'enable_decision_gates': self.enable_decision_gates,
            'enable_performance_monitoring': self.enable_performance_monitoring,
            'enable_exception_handling': self.enable_exception_handling,
            'state_cache_size': self.state_cache_size,
            'memory_cache_size': self.memory_cache_size,
            'vector_dimension': self.vector_dimension,
            'max_memory_fragments': self.max_memory_fragments,
            'decision_gate_thresholds': self.decision_gate_thresholds,
            'memory_categories': self.memory_categories,
            'memory_retention_days': self.memory_retention_days,
            'memory_importance_threshold': self.memory_importance_threshold,
            'performance_metrics_enabled': self.performance_metrics_enabled,
            'performance_alert_thresholds': self.performance_alert_thresholds,
            'deployment_stage': self.deployment_stage.value,
            'debug_mode': self.debug_mode,
            'log_level': self.log_level,
            'pateoas_version': self.pateoas_version,
            'config_version': self.config_version,
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PATEOASConfig':
        """从字典创建"""
        return cls(
            enable_state_continuity=data.get('enable_state_continuity', True),
            enable_memory_system=data.get('enable_memory_system', True),
            enable_adaptive_flow=data.get('enable_adaptive_flow', True),
            enable_decision_gates=data.get('enable_decision_gates', True),
            enable_performance_monitoring=data.get('enable_performance_monitoring', True),
            enable_exception_handling=data.get('enable_exception_handling', True),
            state_cache_size=data.get('state_cache_size', 1000),
            memory_cache_size=data.get('memory_cache_size', 1000),
            vector_dimension=data.get('vector_dimension', 384),
            max_memory_fragments=data.get('max_memory_fragments', 10000),
            decision_gate_thresholds=data.get('decision_gate_thresholds', {
                'DG1_confidence_threshold': 0.7,
                'DG2_confidence_threshold': 0.8,
                'quality_threshold': 0.6
            }),
            memory_categories=data.get('memory_categories', [
                'requirement', 'decision', 'pattern', 'issue', 'learning', 'context'
            ]),
            memory_retention_days=data.get('memory_retention_days', 90),
            memory_importance_threshold=data.get('memory_importance_threshold', 0.3),
            performance_metrics_enabled=data.get('performance_metrics_enabled', True),
            performance_alert_thresholds=data.get('performance_alert_thresholds', {
                'response_time_warning': 2.0,
                'response_time_critical': 5.0,
                'success_rate_warning': 0.8,
                'success_rate_critical': 0.6
            }),
            deployment_stage=DeploymentStage(data.get('deployment_stage', 'development')),
            debug_mode=data.get('debug_mode', False),
            log_level=data.get('log_level', 'INFO'),
            pateoas_version=data.get('pateoas_version', '2.0.0'),
            config_version=data.get('config_version', '1.0.0'),
            last_updated=datetime.fromisoformat(data.get('last_updated', datetime.now().isoformat()))
        )


class PATEOASConfigManager:
    """PATEOAS配置管理器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.base_config = get_config()
        if config_dir:
            self.config_dir = ensure_directory(config_dir)
        else:
            self.config_dir = ensure_directory(Path(self.base_config.config_path) / "pateoas")
        
        # 配置文件路径
        self.main_config_file = self.config_dir / "pateoas_config.json"
        self.features_config_file = self.config_dir / "features_config.json"
        self.user_config_file = self.config_dir / "user_config.json"
        
        # 配置实例
        self.main_config: PATEOASConfig = PATEOASConfig()
        self.feature_configs: Dict[str, FeatureConfig] = {}
        self.user_config: Dict[str, Any] = {}
        
        # 当前用户和部署阶段
        self.current_user_id: Optional[str] = None
        self.current_deployment_stage: DeploymentStage = DeploymentStage.DEVELOPMENT
        
        # 加载配置
        self._load_all_configs()
        
        # 初始化默认功能配置
        self._initialize_default_features()
        
        print(f"✓ PATEOAS配置管理器已初始化 (配置目录: {self.config_dir})")
    
    def _initialize_default_features(self):
        """初始化默认功能配置"""
        default_features = [
            {
                'name': 'state_continuity',
                'description': '状态连续性管理功能',
                'enabled': True,
                'flag': FeatureFlag.ENABLED,
                'deployment_stages': [DeploymentStage.DEVELOPMENT, DeploymentStage.TESTING, DeploymentStage.PRODUCTION],
                'rollout_percentage': 100.0
            },
            {
                'name': 'memory_system',
                'description': '上下文记忆系统',
                'enabled': True,
                'flag': FeatureFlag.ENABLED,
                'deployment_stages': [DeploymentStage.DEVELOPMENT, DeploymentStage.TESTING, DeploymentStage.PRODUCTION],
                'rollout_percentage': 100.0
            },
            {
                'name': 'adaptive_flow',
                'description': '自适应流程控制',
                'enabled': True,
                'flag': FeatureFlag.ENABLED,
                'deployment_stages': [DeploymentStage.DEVELOPMENT, DeploymentStage.TESTING, DeploymentStage.PRODUCTION],
                'rollout_percentage': 100.0
            },
            {
                'name': 'decision_gates',
                'description': '智能决策门系统',
                'enabled': True,
                'flag': FeatureFlag.ENABLED,
                'deployment_stages': [DeploymentStage.DEVELOPMENT, DeploymentStage.TESTING, DeploymentStage.PRODUCTION],
                'rollout_percentage': 100.0
            },
            {
                'name': 'performance_monitoring',
                'description': '性能监控和指标',
                'enabled': True,
                'flag': FeatureFlag.ENABLED,
                'deployment_stages': [DeploymentStage.DEVELOPMENT, DeploymentStage.TESTING, DeploymentStage.PRODUCTION],
                'rollout_percentage': 100.0
            },
            {
                'name': 'exception_handling',
                'description': '智能异常处理和恢复',
                'enabled': True,
                'flag': FeatureFlag.ENABLED,
                'deployment_stages': [DeploymentStage.DEVELOPMENT, DeploymentStage.TESTING, DeploymentStage.PRODUCTION],
                'rollout_percentage': 100.0
            },
            {
                'name': 'optimized_state_manager',
                'description': '优化状态管理器',
                'enabled': True,
                'flag': FeatureFlag.ENABLED,
                'deployment_stages': [DeploymentStage.DEVELOPMENT, DeploymentStage.TESTING],
                'rollout_percentage': 80.0
            },
            {
                'name': 'optimized_memory_retrieval',
                'description': '优化记忆检索系统',
                'enabled': True,
                'flag': FeatureFlag.ENABLED,
                'deployment_stages': [DeploymentStage.DEVELOPMENT, DeploymentStage.TESTING],
                'rollout_percentage': 80.0
            },
            {
                'name': 'advanced_analytics',
                'description': '高级分析和洞察',
                'enabled': False,
                'flag': FeatureFlag.EXPERIMENTAL,
                'deployment_stages': [DeploymentStage.DEVELOPMENT],
                'rollout_percentage': 10.0
            },
            {
                'name': 'ai_assisted_debugging',
                'description': 'AI辅助调试功能',
                'enabled': False,
                'flag': FeatureFlag.EXPERIMENTAL,
                'deployment_stages': [DeploymentStage.DEVELOPMENT],
                'rollout_percentage': 5.0
            }
        ]
        
        for feature_data in default_features:
            if feature_data['name'] not in self.feature_configs:
                feature_config = FeatureConfig(
                    name=feature_data['name'],
                    enabled=feature_data['enabled'],
                    flag=feature_data['flag'],
                    description=feature_data['description'],
                    deployment_stages=feature_data['deployment_stages'],
                    rollout_percentage=feature_data['rollout_percentage']
                )
                self.feature_configs[feature_data['name']] = feature_config
    
    def is_feature_enabled(self, feature_name: str, user_id: Optional[str] = None) -> bool:
        """检查功能是否启用"""
        if feature_name not in self.feature_configs:
            return False
        
        feature = self.feature_configs[feature_name]
        
        # 检查部署阶段
        if not feature.is_available_for_stage(self.current_deployment_stage):
            return False
        
        # 检查渐进式部署
        return feature.is_enabled_for_rollout(user_id or self.current_user_id)
    
    def get_feature_config(self, feature_name: str) -> Optional[FeatureConfig]:
        """获取功能配置"""
        return self.feature_configs.get(feature_name)
    
    def update_feature_config(self, feature_name: str, **kwargs) -> bool:
        """更新功能配置"""
        if feature_name not in self.feature_configs:
            return False
        
        feature = self.feature_configs[feature_name]
        
        # 更新配置
        for key, value in kwargs.items():
            if hasattr(feature, key):
                setattr(feature, key, value)
        
        feature.updated_at = datetime.now()
        
        # 保存配置
        self._save_features_config()
        return True
    
    def add_feature_config(self, feature_config: FeatureConfig) -> bool:
        """添加功能配置"""
        self.feature_configs[feature_config.name] = feature_config
        self._save_features_config()
        return True
    
    def remove_feature_config(self, feature_name: str) -> bool:
        """移除功能配置"""
        if feature_name in self.feature_configs:
            del self.feature_configs[feature_name]
            self._save_features_config()
            return True
        return False
    
    def get_main_config(self) -> PATEOASConfig:
        """获取主配置"""
        return self.main_config
    
    def update_main_config(self, **kwargs) -> bool:
        """更新主配置"""
        for key, value in kwargs.items():
            if hasattr(self.main_config, key):
                setattr(self.main_config, key, value)
        
        self.main_config.last_updated = datetime.now()
        self._save_main_config()
        return True
    
    def get_user_config(self, key: str, default: Any = None) -> Any:
        """获取用户配置"""
        return self.user_config.get(key, default)
    
    def set_user_config(self, key: str, value: Any) -> bool:
        """设置用户配置"""
        self.user_config[key] = value
        self._save_user_config()
        return True
    
    def set_deployment_stage(self, stage: DeploymentStage):
        """设置部署阶段"""
        self.current_deployment_stage = stage
        self.main_config.deployment_stage = stage
        self._save_main_config()
    
    def set_current_user(self, user_id: str):
        """设置当前用户"""
        self.current_user_id = user_id
    
    def get_enabled_features(self, user_id: Optional[str] = None) -> List[str]:
        """获取启用的功能列表"""
        enabled_features = []
        for feature_name in self.feature_configs:
            if self.is_feature_enabled(feature_name, user_id):
                enabled_features.append(feature_name)
        return enabled_features
    
    def get_feature_rollout_status(self) -> Dict[str, Dict[str, Any]]:
        """获取功能部署状态"""
        status = {}
        for feature_name, feature in self.feature_configs.items():
            status[feature_name] = {
                'enabled': feature.enabled,
                'flag': feature.flag.value,
                'rollout_percentage': feature.rollout_percentage,
                'deployment_stages': [stage.value for stage in feature.deployment_stages],
                'available_in_current_stage': feature.is_available_for_stage(self.current_deployment_stage),
                'enabled_for_current_user': self.is_feature_enabled(feature_name)
            }
        return status
    
    def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 验证主配置
        if self.main_config.state_cache_size <= 0:
            validation_result['errors'].append('状态缓存大小必须大于0')
        
        if self.main_config.memory_cache_size <= 0:
            validation_result['errors'].append('记忆缓存大小必须大于0')
        
        if self.main_config.vector_dimension <= 0:
            validation_result['errors'].append('向量维度必须大于0')
        
        # 验证功能配置
        for feature_name, feature in self.feature_configs.items():
            if not (0 <= feature.rollout_percentage <= 100):
                validation_result['errors'].append(f'功能 {feature_name} 的部署百分比必须在0-100之间')
            
            if not feature.deployment_stages:
                validation_result['warnings'].append(f'功能 {feature_name} 没有指定部署阶段')
        
        # 检查功能依赖
        for feature_name, feature in self.feature_configs.items():
            for dependency in feature.dependencies:
                if dependency not in self.feature_configs:
                    validation_result['errors'].append(f'功能 {feature_name} 依赖的功能 {dependency} 不存在')
                elif not self.is_feature_enabled(dependency):
                    validation_result['warnings'].append(f'功能 {feature_name} 依赖的功能 {dependency} 未启用')
        
        validation_result['valid'] = len(validation_result['errors']) == 0
        return validation_result
    
    def export_config(self, include_user_config: bool = False) -> Dict[str, Any]:
        """导出配置"""
        export_data = {
            'main_config': self.main_config.to_dict(),
            'feature_configs': {
                name: config.to_dict() 
                for name, config in self.feature_configs.items()
            },
            'export_timestamp': datetime.now().isoformat(),
            'deployment_stage': self.current_deployment_stage.value
        }
        
        if include_user_config:
            export_data['user_config'] = self.user_config.copy()
        
        return export_data
    
    def import_config(self, config_data: Dict[str, Any], merge: bool = True) -> bool:
        """导入配置"""
        try:
            # 导入主配置
            if 'main_config' in config_data:
                if merge:
                    # 合并配置
                    for key, value in config_data['main_config'].items():
                        if hasattr(self.main_config, key):
                            setattr(self.main_config, key, value)
                else:
                    # 替换配置
                    self.main_config = PATEOASConfig.from_dict(config_data['main_config'])
            
            # 导入功能配置
            if 'feature_configs' in config_data:
                for feature_name, feature_data in config_data['feature_configs'].items():
                    feature_config = FeatureConfig.from_dict(feature_data)
                    self.feature_configs[feature_name] = feature_config
            
            # 导入用户配置
            if 'user_config' in config_data:
                if merge:
                    self.user_config.update(config_data['user_config'])
                else:
                    self.user_config = config_data['user_config'].copy()
            
            # 保存所有配置
            self._save_all_configs()
            return True
            
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.main_config = PATEOASConfig()
        self.feature_configs.clear()
        self.user_config.clear()
        
        self._initialize_default_features()
        self._save_all_configs()
    
    def _load_all_configs(self):
        """加载所有配置"""
        self._load_main_config()
        self._load_features_config()
        self._load_user_config()
    
    def _save_all_configs(self):
        """保存所有配置"""
        self._save_main_config()
        self._save_features_config()
        self._save_user_config()
    
    def _load_main_config(self):
        """加载主配置"""
        if self.main_config_file.exists():
            try:
                with open(self.main_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.main_config = PATEOASConfig.from_dict(data)
            except Exception as e:
                print(f"加载主配置失败: {e}")
    
    def _save_main_config(self):
        """保存主配置"""
        try:
            with open(self.main_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.main_config.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存主配置失败: {e}")
    
    def _load_features_config(self):
        """加载功能配置"""
        if self.features_config_file.exists():
            try:
                with open(self.features_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for feature_name, feature_data in data.items():
                        self.feature_configs[feature_name] = FeatureConfig.from_dict(feature_data)
            except Exception as e:
                print(f"加载功能配置失败: {e}")
    
    def _save_features_config(self):
        """保存功能配置"""
        try:
            data = {
                name: config.to_dict() 
                for name, config in self.feature_configs.items()
            }
            with open(self.features_config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存功能配置失败: {e}")
    
    def _load_user_config(self):
        """加载用户配置"""
        if self.user_config_file.exists():
            try:
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    self.user_config = json.load(f)
            except Exception as e:
                print(f"加载用户配置失败: {e}")
    
    def _save_user_config(self):
        """保存用户配置"""
        try:
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户配置失败: {e}")


# 全局配置管理器实例
_config_manager: Optional[PATEOASConfigManager] = None


def get_pateoas_config_manager() -> PATEOASConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = PATEOASConfigManager()
    return _config_manager


def is_feature_enabled(feature_name: str, user_id: Optional[str] = None) -> bool:
    """检查功能是否启用的便捷函数"""
    return get_pateoas_config_manager().is_feature_enabled(feature_name, user_id)


def get_pateoas_config() -> PATEOASConfig:
    """获取PATEOAS主配置的便捷函数"""
    return get_pateoas_config_manager().get_main_config()