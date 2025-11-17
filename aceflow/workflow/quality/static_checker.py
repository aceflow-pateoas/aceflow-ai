"""
Static Code Checker for AceFlow v4.0

Provides lightweight static analysis for common issues:
- Syntax checking (basic patterns)
- Style checking (naming, formatting)
- Type checking (simple type errors)
- Auto-fix capabilities
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import re


class IssueSeverity(Enum):
    """Issue severity levels"""
    ERROR = "error"      # Must fix
    WARNING = "warning"  # Should fix
    INFO = "info"        # Nice to have


class IssueCategory(Enum):
    """Issue categories"""
    SYNTAX = "syntax"
    STYLE = "style"
    TYPE = "type"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class CodeIssue:
    """A code issue found by static checker"""
    category: IssueCategory
    severity: IssueSeverity
    line: int
    column: int = 0
    message: str = ""
    suggestion: str = ""
    auto_fixable: bool = False
    fix_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'category': self.category.value,
            'severity': self.severity.value,
            'line': self.line,
            'column': self.column,
            'message': self.message,
            'suggestion': self.suggestion,
            'auto_fixable': self.auto_fixable,
            'fix_code': self.fix_code,
            'metadata': self.metadata
        }


class StaticChecker:
    """
    Lightweight static code checker

    Provides basic static analysis without external tools.
    For production use, integrate with ESLint/Flake8/mypy.
    """

    def check_syntax(self, code: str, language: str) -> List[CodeIssue]:
        """
        Check for basic syntax issues

        Args:
            code: Source code
            language: Programming language

        Returns:
            List of syntax issues
        """
        issues = []
        language = language.lower()

        if language == "python":
            issues.extend(self._check_python_syntax(code))
        elif language in ["javascript", "typescript"]:
            issues.extend(self._check_js_syntax(code))

        return issues

    def check_style(self, code: str, language: str) -> List[CodeIssue]:
        """
        Check for code style issues

        Args:
            code: Source code
            language: Programming language

        Returns:
            List of style issues
        """
        issues = []
        language = language.lower()

        if language == "python":
            issues.extend(self._check_python_style(code))
        elif language in ["javascript", "typescript"]:
            issues.extend(self._check_js_style(code))

        return issues

    def check_types(self, code: str, language: str) -> List[CodeIssue]:
        """
        Check for basic type issues

        Args:
            code: Source code
            language: Programming language

        Returns:
            List of type issues
        """
        issues = []
        language = language.lower()

        if language == "python":
            issues.extend(self._check_python_types(code))
        elif language == "typescript":
            issues.extend(self._check_ts_types(code))

        return issues

    def auto_fix(self, code: str, issues: List[CodeIssue]) -> Tuple[str, List[CodeIssue]]:
        """
        Automatically fix auto-fixable issues

        Args:
            code: Source code
            issues: List of issues

        Returns:
            (fixed_code, remaining_issues)
        """
        fixed_code = code
        remaining_issues = []

        for issue in issues:
            if issue.auto_fixable and issue.fix_code is not None:
                # Apply fix
                lines = fixed_code.split('\n')
                if 0 <= issue.line - 1 < len(lines):
                    lines[issue.line - 1] = issue.fix_code
                    fixed_code = '\n'.join(lines)
            else:
                remaining_issues.append(issue)

        return fixed_code, remaining_issues

    # ====== Python-specific checkers ======

    def _check_python_syntax(self, code: str) -> List[CodeIssue]:
        """Check Python syntax issues"""
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, start=1):
            # Check for common syntax errors
            if re.search(r'^\s+\S', line) and not line.strip().startswith('#'):
                # Check indentation (should be multiple of 4)
                indent = len(line) - len(line.lstrip())
                if indent % 4 != 0:
                    issues.append(CodeIssue(
                        category=IssueCategory.SYNTAX,
                        severity=IssueSeverity.ERROR,
                        line=i,
                        message=f"Indentation should be multiple of 4 (found {indent} spaces)",
                        suggestion="Use 4 spaces for indentation",
                        auto_fixable=True,
                        fix_code=line.replace(' ' * indent, ' ' * ((indent // 4) * 4))
                    ))

            # Check for missing colons in def/class/if/for/while
            if re.search(r'^\s*(def|class|if|for|while|try|except|finally|with)\s+.*[^:]$', line):
                issues.append(CodeIssue(
                    category=IssueCategory.SYNTAX,
                    severity=IssueSeverity.ERROR,
                    line=i,
                    message="Missing colon at end of statement",
                    suggestion="Add ':' at the end",
                    auto_fixable=True,
                    fix_code=line.rstrip() + ':'
                ))

            # Check for print without parentheses (Python 3)
            if re.search(r'\bprint\s+[^(]', line) and not line.strip().startswith('#'):
                issues.append(CodeIssue(
                    category=IssueCategory.SYNTAX,
                    severity=IssueSeverity.ERROR,
                    line=i,
                    message="print is a function in Python 3, use print(...)",
                    suggestion="Use print() with parentheses",
                    auto_fixable=False
                ))

        return issues

    def _check_python_style(self, code: str) -> List[CodeIssue]:
        """Check Python style issues (PEP 8)"""
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, start=1):
            # Check line length
            if len(line) > 100:
                issues.append(CodeIssue(
                    category=IssueCategory.STYLE,
                    severity=IssueSeverity.WARNING,
                    line=i,
                    message=f"Line too long ({len(line)} > 100 characters)",
                    suggestion="Break line into multiple lines",
                    auto_fixable=False
                ))

            # Check for variable names (should be snake_case)
            # Match both camelCase (userName) and PascalCase (UserName)
            var_match = re.search(r'\b([a-z]+[A-Z]\w*|[A-Z][a-z]+[A-Z]\w*)\s*=', line)
            if var_match and not line.strip().startswith('#'):
                var_name = var_match.group(1)
                issues.append(CodeIssue(
                    category=IssueCategory.STYLE,
                    severity=IssueSeverity.WARNING,
                    line=i,
                    message=f"Variable '{var_name}' should use snake_case",
                    suggestion=f"Rename to '{self._to_snake_case(var_name)}'",
                    auto_fixable=False
                ))

            # Check for multiple statements on one line
            if ';' in line and not line.strip().startswith('#'):
                issues.append(CodeIssue(
                    category=IssueCategory.STYLE,
                    severity=IssueSeverity.WARNING,
                    line=i,
                    message="Multiple statements on one line",
                    suggestion="Use separate lines for each statement",
                    auto_fixable=False
                ))

        return issues

    def _check_python_types(self, code: str) -> List[CodeIssue]:
        """Check Python type issues"""
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, start=1):
            # Check for missing return type hints in function definitions
            if re.search(r'^\s*def\s+\w+\([^)]*\)\s*:', line) and '->' not in line:
                if not line.strip().startswith('#'):
                    issues.append(CodeIssue(
                        category=IssueCategory.TYPE,
                        severity=IssueSeverity.INFO,
                        line=i,
                        message="Function missing return type hint",
                        suggestion="Add -> ReturnType before :",
                        auto_fixable=False
                    ))

            # Check for common type errors
            if re.search(r'\blen\([^)]+\)\s*==\s*0', line):
                issues.append(CodeIssue(
                    category=IssueCategory.TYPE,
                    severity=IssueSeverity.INFO,
                    line=i,
                    message="Use 'not collection' instead of 'len(collection) == 0'",
                    suggestion="Pythonic way: if not collection:",
                    auto_fixable=False
                ))

        return issues

    # ====== JavaScript/TypeScript-specific checkers ======

    def _check_js_syntax(self, code: str) -> List[CodeIssue]:
        """Check JavaScript/TypeScript syntax issues"""
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, start=1):
            # Check for missing semicolons
            if re.search(r'(const|let|var|return)\s+[^;]+$', line.strip()):
                if not line.strip().startswith('//') and not line.strip().endswith('{'):
                    issues.append(CodeIssue(
                        category=IssueCategory.SYNTAX,
                        severity=IssueSeverity.WARNING,
                        line=i,
                        message="Missing semicolon",
                        suggestion="Add semicolon at the end",
                        auto_fixable=True,
                        fix_code=line.rstrip() + ';'
                    ))

            # Check for == instead of ===
            if '==' in line and '===' not in line and not line.strip().startswith('//'):
                issues.append(CodeIssue(
                    category=IssueCategory.SYNTAX,
                    severity=IssueSeverity.WARNING,
                    line=i,
                    message="Use === instead of ==",
                    suggestion="Use strict equality (===)",
                    auto_fixable=True,
                    fix_code=line.replace('==', '===')
                ))

        return issues

    def _check_js_style(self, code: str) -> List[CodeIssue]:
        """Check JavaScript/TypeScript style issues"""
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, start=1):
            # Check for var instead of const/let
            if re.search(r'\bvar\s+', line) and not line.strip().startswith('//'):
                issues.append(CodeIssue(
                    category=IssueCategory.STYLE,
                    severity=IssueSeverity.WARNING,
                    line=i,
                    message="Use 'const' or 'let' instead of 'var'",
                    suggestion="var is deprecated, use const/let",
                    auto_fixable=False
                ))

            # Check for console.log in production code
            if 'console.log' in line and not line.strip().startswith('//'):
                issues.append(CodeIssue(
                    category=IssueCategory.STYLE,
                    severity=IssueSeverity.INFO,
                    line=i,
                    message="Remove console.log before production",
                    suggestion="Use proper logging library",
                    auto_fixable=False
                ))

        return issues

    def _check_ts_types(self, code: str) -> List[CodeIssue]:
        """Check TypeScript type issues"""
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, start=1):
            # Check for missing type annotations
            # Match: const user = ... or let user = ...
            # Ensure type annotation (: Type) is not present before the = sign
            var_decl_match = re.search(r'(const|let)\s+(\w+)\s*=', line)
            if var_decl_match and not line.strip().startswith('//'):
                var_start = var_decl_match.start(2)  # Start of variable name
                equals_pos = var_decl_match.end()    # Position after =
                # Check if there's a type annotation between variable name and =
                between_text = line[var_start:equals_pos]
                if ':' not in between_text or ' =' in between_text:
                    issues.append(CodeIssue(
                        category=IssueCategory.TYPE,
                        severity=IssueSeverity.INFO,
                        line=i,
                        message="Variable missing type annotation",
                        suggestion="Add : Type after variable name",
                        auto_fixable=False
                    ))

            # Check for 'any' type usage
            if re.search(r':\s*any\b', line):
                issues.append(CodeIssue(
                    category=IssueCategory.TYPE,
                    severity=IssueSeverity.WARNING,
                    line=i,
                    message="Avoid using 'any' type",
                    suggestion="Use specific type instead",
                    auto_fixable=False
                ))

        return issues

    # ====== Helper methods ======

    def _to_snake_case(self, name: str) -> str:
        """Convert camelCase to snake_case"""
        # Insert underscore before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        # Insert underscore before uppercase letters followed by lowercase
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def get_summary(self, issues: List[CodeIssue]) -> Dict[str, Any]:
        """
        Get summary of issues

        Returns:
            {
                "total": int,
                "by_severity": {"error": int, "warning": int, "info": int},
                "by_category": {"syntax": int, "style": int, "type": int},
                "auto_fixable": int
            }
        """
        summary = {
            "total": len(issues),
            "by_severity": {"error": 0, "warning": 0, "info": 0},
            "by_category": {"syntax": 0, "style": 0, "type": 0, "security": 0, "performance": 0},
            "auto_fixable": 0
        }

        for issue in issues:
            summary["by_severity"][issue.severity.value] += 1
            summary["by_category"][issue.category.value] += 1
            if issue.auto_fixable:
                summary["auto_fixable"] += 1

        return summary
