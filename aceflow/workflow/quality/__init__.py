"""
Quality checking module for AceFlow v4.0

Provides quality assurance tools including:
- Test result reporting and formatting
- Test failure classification
- Fix suggestion generation
- Code generation strategy
"""

from .test_reporter import (
    TestReporter,
    TestResults,
    TestCase,
    TestFailure,
    TestStatus,
    FailureCategory,
    FixSuggestion
)

from .code_generator import (
    CodeGenerationStrategy,
    CodeSkeleton,
    GenerationStep,
    GenerationPriority,
    CodeLanguage
)

from .static_checker import (
    StaticChecker,
    CodeIssue,
    IssueSeverity,
    IssueCategory
)

__all__ = [
    'TestReporter',
    'TestResults',
    'TestCase',
    'TestFailure',
    'TestStatus',
    'FailureCategory',
    'FixSuggestion',
    'CodeGenerationStrategy',
    'CodeSkeleton',
    'GenerationStep',
    'GenerationPriority',
    'CodeLanguage',
    'StaticChecker',
    'CodeIssue',
    'IssueSeverity',
    'IssueCategory'
]
