"""
AceFlow MCP Unified Server
统一MCP服务器

A unified, modular MCP server that integrates aceflow-server and aceflow-enhanced-server
into a single, configurable, and extensible architecture.

统一的、模块化的MCP服务器，将aceflow-server和aceflow-enhanced-server
整合为单一的、可配置的、可扩展的架构。
"""

__version__ = "2.0.0"
__author__ = "AceFlow Team"
__email__ = "team@aceflow.dev"
__license__ = "MIT"
__description__ = "AceFlow MCP Unified Server - A unified, modular MCP server for workflow management"

# 导出主要组件
from .unified_server import UnifiedAceFlowServer, create_unified_server
from .unified_config import UnifiedConfig, ConfigManager, get_config_manager

# 导出模块基类
from .modules.base_module import BaseModule, ModuleMetadata
from .modules.module_manager import ModuleManager

# 导出核心模块
from .modules.core_module import CoreModule
from .modules.collaboration_module import CollaborationModule
from .modules.intelligence_module import IntelligenceModule

# 版本信息
VERSION_INFO = {
    "version": __version__,
    "author": __author__,
    "email": __email__,
    "license": __license__,
    "description": __description__,
    "python_requires": ">=3.8",
    "homepage": "https://github.com/aceflow/mcp-server",
    "documentation": "https://docs.aceflow.dev",
    "repository": "https://github.com/aceflow/mcp-server.git",
    "bug_tracker": "https://github.com/aceflow/mcp-server/issues",
}

# 兼容性别名 - 为了向后兼容
AceFlowServer = UnifiedAceFlowServer  # 兼容旧的类名
create_server = create_unified_server  # 兼容旧的函数名

def get_version():
    """获取版本信息"""
    return __version__

def get_version_info():
    """获取详细版本信息"""
    return VERSION_INFO.copy()

# 模块级别的配置
__all__ = [
    # 版本信息
    "__version__",
    "__author__", 
    "__email__",
    "__license__",
    "__description__",
    "VERSION_INFO",
    "get_version",
    "get_version_info",
    
    # 核心组件
    "UnifiedAceFlowServer",
    "create_unified_server",
    "UnifiedConfig",
    "ConfigManager", 
    "get_config_manager",
    
    # 模块系统
    "BaseModule",
    "ModuleMetadata",
    "ModuleManager",
    
    # 功能模块
    "CoreModule",
    "CollaborationModule", 
    "IntelligenceModule",
    
    # 兼容性别名
    "AceFlowServer",
    "create_server",
]

# 启动时的初始化检查
def _check_dependencies():
    """检查关键依赖是否可用"""
    try:
        import fastmcp
    except ImportError:
        import warnings
        warnings.warn(
            "FastMCP is not installed. Some features may not work properly. "
            "Install with: pip install fastmcp",
            ImportWarning
        )

# 执行依赖检查
_check_dependencies()

# 设置日志
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())