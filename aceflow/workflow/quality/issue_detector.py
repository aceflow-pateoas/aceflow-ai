"""
Potential Issue Detector for AceFlow v4.0

Detects potential issues in code:
- Missing test scenarios
- Security risks
- Performance issues
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import re


class IssueRisk(Enum):
    """Risk levels for potential issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueType(Enum):
    """Types of potential issues"""
    MISSING_TEST = "missing_test"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BEST_PRACTICE = "best_practice"


@dataclass
class PotentialIssue:
    """A potential issue detected in code"""
    type: IssueType
    risk: IssueRisk
    description: str
    suggestion: str
    line: Optional[int] = None
    code_snippet: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'type': self.type.value,
            'risk': self.risk.value,
            'description': self.description,
            'suggestion': self.suggestion,
            'line': self.line,
            'code_snippet': self.code_snippet,
            'metadata': self.metadata
        }


class IssueDetector:
    """
    Detector for potential code issues

    Analyzes code and test files to identify:
    - Missing test scenarios (concurrency, errors, edge cases)
    - Security risks (SQL injection, XSS, hardcoded secrets)
    - Performance issues (N+1 queries, inefficient loops)
    """

    def detect_missing_tests(self, code: str, tests: str = "", language: str = "python") -> List[PotentialIssue]:
        """
        Detect missing test scenarios

        Args:
            code: Source code
            tests: Test code
            language: Programming language

        Returns:
            List of missing test scenarios
        """
        issues = []

        # Check for authentication/authorization code without concurrency tests
        if self._has_auth_code(code):
            if not self._has_concurrent_tests(tests):
                issues.append(PotentialIssue(
                    type=IssueType.MISSING_TEST,
                    risk=IssueRisk.HIGH,
                    description="Authentication code lacks concurrent access tests",
                    suggestion="Add tests for concurrent login attempts to detect race conditions",
                    metadata={'test_type': 'concurrent', 'feature': 'authentication'}
                ))

        # Check for database operations without error handling tests
        if self._has_database_code(code):
            if not self._has_error_handling_tests(tests):
                issues.append(PotentialIssue(
                    type=IssueType.MISSING_TEST,
                    risk=IssueRisk.MEDIUM,
                    description="Database operations lack error handling tests",
                    suggestion="Add tests for connection failures, timeouts, and transaction rollbacks",
                    metadata={'test_type': 'error_handling', 'feature': 'database'}
                ))

        # Check for API endpoints without edge case tests
        if self._has_api_endpoints(code):
            if not self._has_edge_case_tests(tests):
                issues.append(PotentialIssue(
                    type=IssueType.MISSING_TEST,
                    risk=IssueRisk.MEDIUM,
                    description="API endpoints lack edge case tests",
                    suggestion="Add tests for invalid input, empty data, and boundary conditions",
                    metadata={'test_type': 'edge_cases', 'feature': 'api'}
                ))

        # Check for file operations without permission tests
        if self._has_file_operations(code):
            if not self._has_permission_tests(tests):
                issues.append(PotentialIssue(
                    type=IssueType.MISSING_TEST,
                    risk=IssueRisk.MEDIUM,
                    description="File operations lack permission error tests",
                    suggestion="Add tests for read-only files, missing directories, and access denied scenarios",
                    metadata={'test_type': 'permissions', 'feature': 'file_io'}
                ))

        # Check for async code without timeout tests
        if self._has_async_code(code, language):
            if not self._has_timeout_tests(tests):
                issues.append(PotentialIssue(
                    type=IssueType.MISSING_TEST,
                    risk=IssueRisk.HIGH,
                    description="Async operations lack timeout tests",
                    suggestion="Add tests for operation timeouts and cancellation",
                    metadata={'test_type': 'timeout', 'feature': 'async'}
                ))

        return issues

    def detect_security_risks(self, code: str, language: str = "python") -> List[PotentialIssue]:
        """
        Detect security risks in code

        Args:
            code: Source code
            language: Programming language

        Returns:
            List of security risks
        """
        issues = []
        lines = code.split('\n')

        for i, line in enumerate(lines, start=1):
            # Check for SQL injection risks
            if self._has_sql_injection_risk(line, language):
                issues.append(PotentialIssue(
                    type=IssueType.SECURITY,
                    risk=IssueRisk.CRITICAL,
                    description="Potential SQL injection vulnerability",
                    suggestion="Use parameterized queries or ORM instead of string concatenation",
                    line=i,
                    code_snippet=line.strip(),
                    metadata={'vulnerability': 'sql_injection'}
                ))

            # Check for hardcoded secrets (may have multiple on one line)
            hardcoded_secrets = self._find_hardcoded_secrets(line)
            for secret_type in hardcoded_secrets:
                issues.append(PotentialIssue(
                    type=IssueType.SECURITY,
                    risk=IssueRisk.CRITICAL,
                    description=f"Hardcoded secret or API key detected ({secret_type})",
                    suggestion="Move secrets to environment variables or secret management service",
                    line=i,
                    code_snippet="<redacted>",
                    metadata={'vulnerability': 'hardcoded_secret', 'secret_type': secret_type}
                ))

            # Check for unsafe eval/exec usage
            if self._has_unsafe_eval(line, language):
                issues.append(PotentialIssue(
                    type=IssueType.SECURITY,
                    risk=IssueRisk.HIGH,
                    description="Unsafe use of eval/exec detected",
                    suggestion="Avoid dynamic code execution; use safer alternatives like ast.literal_eval",
                    line=i,
                    code_snippet=line.strip(),
                    metadata={'vulnerability': 'code_injection'}
                ))

            # Check for weak crypto
            if self._has_weak_crypto(line, language):
                issues.append(PotentialIssue(
                    type=IssueType.SECURITY,
                    risk=IssueRisk.HIGH,
                    description="Use of weak cryptographic algorithm",
                    suggestion="Use modern algorithms like bcrypt, scrypt, or Argon2 for passwords",
                    line=i,
                    code_snippet=line.strip(),
                    metadata={'vulnerability': 'weak_crypto'}
                ))

            # Check for XSS risks (for web frameworks)
            if self._has_xss_risk(line, language):
                issues.append(PotentialIssue(
                    type=IssueType.SECURITY,
                    risk=IssueRisk.HIGH,
                    description="Potential XSS vulnerability",
                    suggestion="Escape or sanitize user input before rendering in templates",
                    line=i,
                    code_snippet=line.strip(),
                    metadata={'vulnerability': 'xss'}
                ))

        return issues

    def detect_performance_issues(self, code: str, language: str = "python") -> List[PotentialIssue]:
        """
        Detect performance issues in code

        Args:
            code: Source code
            language: Programming language

        Returns:
            List of performance issues
        """
        issues = []
        lines = code.split('\n')

        # State tracking
        in_loop = False
        in_async_context = False
        indent_level = 0

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                continue

            # Calculate indentation
            current_indent = len(line) - len(line.lstrip())

            # Track loop context
            if language == "python":
                if re.search(r'^\s*for\s+\w+\s+in\s+', line):
                    in_loop = True
                    indent_level = current_indent
                elif in_loop and current_indent <= indent_level:
                    in_loop = False
            elif language in ["javascript", "typescript"]:
                if re.search(r'for\s*\(', line):
                    in_loop = True
                    indent_level = current_indent
                elif in_loop and current_indent <= indent_level and '}' in line:
                    in_loop = False

            # Track async context
            if 'async' in line:
                in_async_context = True
                indent_level = max(indent_level, current_indent)
            elif in_async_context and current_indent <= indent_level and not any(kw in line for kw in ['async', 'await']):
                in_async_context = False

            # Check for N+1 query pattern (queries inside loops)
            if in_loop and self._is_query_line(line, language):
                issues.append(PotentialIssue(
                    type=IssueType.PERFORMANCE,
                    risk=IssueRisk.HIGH,
                    description="Potential N+1 query problem",
                    suggestion="Use eager loading or join queries to fetch related data",
                    line=i,
                    code_snippet=line.strip(),
                    metadata={'issue': 'n_plus_one'}
                ))

            # Check for inefficient string concatenation in loops
            if in_loop and self._is_string_concat_line(line, language):
                issues.append(PotentialIssue(
                    type=IssueType.PERFORMANCE,
                    risk=IssueRisk.MEDIUM,
                    description="Inefficient string concatenation in loop",
                    suggestion="Use join() or list comprehension instead of repeated concatenation",
                    line=i,
                    code_snippet=line.strip(),
                    metadata={'issue': 'string_concat'}
                ))

            # Check for missing database indexes
            if self._needs_database_index(line, language):
                issues.append(PotentialIssue(
                    type=IssueType.PERFORMANCE,
                    risk=IssueRisk.MEDIUM,
                    description="Query may benefit from database index",
                    suggestion="Add index on frequently queried columns",
                    line=i,
                    code_snippet=line.strip(),
                    metadata={'issue': 'missing_index'}
                ))

            # Check for synchronous I/O in async context
            if in_async_context and self._is_blocking_io_line(line, language):
                issues.append(PotentialIssue(
                    type=IssueType.PERFORMANCE,
                    risk=IssueRisk.HIGH,
                    description="Blocking I/O operation in async context",
                    suggestion="Use async I/O operations to avoid blocking the event loop",
                    line=i,
                    code_snippet=line.strip(),
                    metadata={'issue': 'blocking_io'}
                ))

        return issues

    def detect_all_issues(
        self,
        code: str,
        tests: str = "",
        language: str = "python",
        scope: str = "all"
    ) -> Dict[str, List[PotentialIssue]]:
        """
        Detect all potential issues

        Args:
            code: Source code
            tests: Test code
            language: Programming language
            scope: Scope of detection (all/security/performance/testing)

        Returns:
            {
                "missing_tests": [...],
                "security": [...],
                "performance": [...]
            }
        """
        result = {
            "missing_tests": [],
            "security": [],
            "performance": []
        }

        if scope in ["all", "testing"]:
            result["missing_tests"] = self.detect_missing_tests(code, tests, language)

        if scope in ["all", "security"]:
            result["security"] = self.detect_security_risks(code, language)

        if scope in ["all", "performance"]:
            result["performance"] = self.detect_performance_issues(code, language)

        return result

    # ====== Helper methods for missing tests detection ======

    def _has_auth_code(self, code: str) -> bool:
        """Check if code has authentication/authorization logic"""
        auth_keywords = ['login', 'authenticate', 'token', 'password', 'session', 'auth']
        return any(keyword in code.lower() for keyword in auth_keywords)

    def _has_concurrent_tests(self, tests: str) -> bool:
        """Check if tests include concurrent/threading scenarios"""
        concurrent_keywords = ['thread', 'concurrent', 'parallel', 'async', 'await', 'lock']
        return any(keyword in tests.lower() for keyword in concurrent_keywords)

    def _has_database_code(self, code: str) -> bool:
        """Check if code has database operations"""
        db_keywords = ['query', 'select', 'insert', 'update', 'delete', 'execute', 'commit']
        return any(keyword in code.lower() for keyword in db_keywords)

    def _has_error_handling_tests(self, tests: str) -> bool:
        """Check if tests include error handling scenarios"""
        error_keywords = ['exception', 'error', 'fail', 'raises', 'throw', 'catch']
        return any(keyword in tests.lower() for keyword in error_keywords)

    def _has_api_endpoints(self, code: str) -> bool:
        """Check if code defines API endpoints"""
        api_patterns = [r'@app\.route', r'@router\.', r'app\.get', r'app\.post', r'express\(']
        return any(re.search(pattern, code) for pattern in api_patterns)

    def _has_edge_case_tests(self, tests: str) -> bool:
        """Check if tests include edge cases"""
        edge_keywords = ['edge', 'boundary', 'limit', 'empty', 'null', 'invalid', 'maximum', 'minimum']
        return any(keyword in tests.lower() for keyword in edge_keywords)

    def _has_file_operations(self, code: str) -> bool:
        """Check if code has file I/O operations"""
        file_keywords = ['open(', 'read(', 'write(', 'file', 'Path(']
        return any(keyword in code for keyword in file_keywords)

    def _has_permission_tests(self, tests: str) -> bool:
        """Check if tests include permission scenarios"""
        perm_keywords = ['permission', 'denied', 'forbidden', '403', 'unauthorized', '401']
        return any(keyword in tests.lower() for keyword in perm_keywords)

    def _has_async_code(self, code: str, language: str) -> bool:
        """Check if code has async operations"""
        if language == "python":
            return 'async def' in code or 'await' in code
        elif language in ["javascript", "typescript"]:
            return 'async ' in code or '.then(' in code or 'await' in code
        return False

    def _has_timeout_tests(self, tests: str) -> bool:
        """Check if tests include timeout scenarios"""
        timeout_keywords = ['timeout', 'cancel', 'abort', 'deadline']
        return any(keyword in tests.lower() for keyword in timeout_keywords)

    # ====== Helper methods for security detection ======

    def _has_sql_injection_risk(self, line: str, language: str) -> bool:
        """Check for SQL injection risk"""
        # Look for string concatenation in SQL queries
        if language == "python":
            if re.search(r'(execute|query|select|insert|update|delete).*["\'].*\+.*["\']', line.lower()):
                return True
            if re.search(r'(execute|query).*%.*%', line.lower()):
                return True
        elif language in ["javascript", "typescript"]:
            if re.search(r'(query|execute).*`.*\$\{', line.lower()):
                return True
        return False

    def _has_hardcoded_secret(self, line: str) -> bool:
        """Check for hardcoded secrets (deprecated, use _find_hardcoded_secrets)"""
        return len(self._find_hardcoded_secrets(line)) > 0

    def _find_hardcoded_secrets(self, line: str) -> List[str]:
        """Find all hardcoded secrets on a line and return their types"""
        secret_types = []

        # Pattern 1: api_key, password, secret, token with values
        pattern1 = r'(api[_-]?key|password|secret|token)\s*=\s*["\'][^"\']{6,}["\']'
        for match in re.finditer(pattern1, line, re.IGNORECASE):
            secret_types.append(match.group(1).lower())

        # Pattern 2: AWS/Azure/GCP keys
        pattern2 = r'(aws|azure|gcp)[_-]?(key|secret)\s*='
        for match in re.finditer(pattern2, line, re.IGNORECASE):
            secret_types.append(f"{match.group(1)}_{match.group(2)}".lower())

        # Pattern 3: Bearer tokens
        if re.search(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', line):
            secret_types.append("bearer_token")

        return secret_types

    def _has_unsafe_eval(self, line: str, language: str) -> bool:
        """Check for unsafe eval/exec usage"""
        if language == "python":
            return bool(re.search(r'\b(eval|exec)\s*\(', line))
        elif language in ["javascript", "typescript"]:
            return bool(re.search(r'\beval\s*\(', line))
        return False

    def _has_weak_crypto(self, line: str, language: str) -> bool:
        """Check for weak cryptographic algorithms"""
        weak_algos = ['md5', 'sha1', 'des', 'rc4']
        return any(algo in line.lower() for algo in weak_algos)

    def _has_xss_risk(self, line: str, language: str) -> bool:
        """Check for XSS vulnerability"""
        if language == "python":
            # Check for unsafe template rendering
            return bool(re.search(r'render.*\|safe', line))
        elif language in ["javascript", "typescript"]:
            # Check for innerHTML with user input
            return 'innerHTML' in line and ('input' in line.lower() or 'user' in line.lower())
        return False

    # ====== Helper methods for performance detection ======

    def _is_query_line(self, line: str, language: str) -> bool:
        """Check if line contains a database query"""
        query_keywords = ['query', 'select', 'execute', 'get', 'find', 'fetch']
        db_patterns = ['db.', 'database.', '.query(', '.execute(', '.get(', '.find(']
        line_lower = line.lower()
        return any(keyword in line_lower for keyword in query_keywords) or \
               any(pattern in line for pattern in db_patterns)

    def _is_string_concat_line(self, line: str, language: str) -> bool:
        """Check if line does string concatenation"""
        if language == "python":
            return bool(re.search(r'\w+\s*\+=\s*.*str\(', line)) or \
                   bool(re.search(r'\w+\s*\+=\s*["\']', line))
        elif language in ["javascript", "typescript"]:
            return bool(re.search(r'\w+\s*\+=', line))
        return False

    def _is_blocking_io_line(self, line: str, language: str) -> bool:
        """Check if line contains blocking I/O operations"""
        blocking_ops = ['open(', '.read(', '.write(', 'requests.get', 'requests.post',
                       'fs.readFileSync', 'fs.writeFileSync']
        return any(op in line for op in blocking_ops)

    def _has_n_plus_one_pattern(self, line: str, language: str) -> bool:
        """Check for N+1 query pattern (deprecated, kept for compatibility)"""
        # Simplified check: query inside a loop
        return bool(re.search(r'for\s+.*:\s*(query|select|get)', line.lower()))

    def _has_inefficient_string_concat(self, line: str, language: str) -> bool:
        """Check for inefficient string concatenation (deprecated, kept for compatibility)"""
        if language == "python":
            return bool(re.search(r'for\s+.*:\s*.*\+=\s*["\']', line))
        elif language in ["javascript", "typescript"]:
            return bool(re.search(r'for\s*\(.*\)\s*\{.*\+=', line))
        return False

    def _needs_database_index(self, line: str, language: str) -> bool:
        """Check if query might need an index"""
        # Look for WHERE clauses without apparent indexes
        return bool(re.search(r'where\s+\w+\s*=', line.lower())) and 'index' not in line.lower()

    def _has_blocking_io_in_async(self, line: str, language: str) -> bool:
        """Check for blocking I/O in async context (deprecated, kept for compatibility)"""
        if 'async' in line or 'await' in line:
            blocking_ops = ['open(', 'read(', 'write(', 'requests.get', 'requests.post']
            return any(op in line for op in blocking_ops)
        return False

    def get_summary(self, all_issues: Dict[str, List[PotentialIssue]]) -> Dict[str, Any]:
        """
        Get summary of all issues

        Returns:
            {
                "total": int,
                "by_type": {...},
                "by_risk": {...},
                "top_issues": [...]
            }
        """
        all_issues_list = []
        for issues in all_issues.values():
            all_issues_list.extend(issues)

        summary = {
            "total": len(all_issues_list),
            "by_type": {
                "missing_test": len(all_issues["missing_tests"]),
                "security": len(all_issues["security"]),
                "performance": len(all_issues["performance"])
            },
            "by_risk": {"critical": 0, "high": 0, "medium": 0, "low": 0}
        }

        for issue in all_issues_list:
            summary["by_risk"][issue.risk.value] += 1

        # Get top 3 critical issues
        critical_issues = [i for i in all_issues_list if i.risk == IssueRisk.CRITICAL]
        high_issues = [i for i in all_issues_list if i.risk == IssueRisk.HIGH]
        summary["top_issues"] = (critical_issues + high_issues)[:3]

        return summary
