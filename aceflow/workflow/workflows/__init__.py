"""
Workflow Implementations - 工作流实现

提供6种场景化工作流实现。
"""

from .base import BaseWorkflow, StageDefinition, ValidationResult
from .feature import FeatureWorkflow
from .bugfix import BugfixWorkflow
from .refactor import RefactorWorkflow
from .review import ReviewWorkflow
from .documentation import DocumentationWorkflow
from .performance import PerformanceWorkflow

__all__ = [
    'BaseWorkflow',
    'StageDefinition',
    'ValidationResult',
    'FeatureWorkflow',
    'BugfixWorkflow',
    'RefactorWorkflow',
    'ReviewWorkflow',
    'DocumentationWorkflow',
    'PerformanceWorkflow',
]
