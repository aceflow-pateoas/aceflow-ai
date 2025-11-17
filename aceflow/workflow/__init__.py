"""
AceFlow Workflow Module

Unified workflow engine for AI-driven development process management.

This module provides:
- v4.0 workflow system with 6 workflow types
- State management with persistent storage
- Memory system for cross-stage knowledge
- Task tracking and dependency management
- Quality checking and code generation

v4.0 Features:
- FeatureWorkflow: Full-featured development workflow
- BugfixWorkflow: Rapid bug fixing workflow
- RefactorWorkflow: Code refactoring workflow
- ReviewWorkflow: Code review workflow
- DocumentationWorkflow: Documentation writing workflow
- PerformanceWorkflow: Performance optimization workflow
"""

# Core v4.0 components
from .core.engine import WorkflowEngine
from .core.state import StateManager

# v4.0 Models
from .models import (
    WorkflowType,
    WorkItem,
    WorkItemStatus,
    Stage,
    StageStatus,
    Task,
    TaskStatus
)

# v4.0 Workflows
from .workflows import (
    FeatureWorkflow,
    BugfixWorkflow,
    RefactorWorkflow,
    ReviewWorkflow,
    DocumentationWorkflow,
    PerformanceWorkflow
)

# v4.0 Memory System
from .memory import (
    V4MemoryManager,
    MemoryExtractor,
    MemoryInjector
)

__all__ = [
    # Core
    'WorkflowEngine',
    'StateManager',

    # Models
    'WorkflowType',
    'WorkItem',
    'WorkItemStatus',
    'Stage',
    'StageStatus',
    'Task',
    'TaskStatus',

    # Workflows
    'FeatureWorkflow',
    'BugfixWorkflow',
    'RefactorWorkflow',
    'ReviewWorkflow',
    'DocumentationWorkflow',
    'PerformanceWorkflow',

    # Memory
    'V4MemoryManager',
    'MemoryExtractor',
    'MemoryInjector'
]

__version__ = '4.0.0'
