"""
Test Result Reporter for AceFlow v4.0

Provides comprehensive test result formatting and analysis including:
- Multi-scenario test result formatting (all pass, partial fail, potential issues)
- Intelligent failure classification
- Fix suggestion generation
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TestStatus(Enum):
    """Test case status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class FailureCategory(Enum):
    """Test failure categories for AI decision making"""
    AUTO_FIXABLE = "auto_fixable"      # AI can fix automatically
    NEEDS_DECISION = "needs_decision"  # Requires human decision
    BLOCKED = "blocked"                # Blocked by external factors


@dataclass
class TestCase:
    """Individual test case"""
    name: str
    status: TestStatus
    description: str = ""
    duration: float = 0.0  # seconds
    error_message: Optional[str] = None
    error_trace: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'status': self.status.value,
            'description': self.description,
            'duration': self.duration,
            'error_message': self.error_message,
            'error_trace': self.error_trace,
            'metadata': self.metadata
        }


@dataclass
class TestFailure:
    """Test failure details"""
    test_case: TestCase
    category: FailureCategory
    root_cause: str
    impact: str  # low/medium/high
    related_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'test_case': self.test_case.to_dict(),
            'category': self.category.value,
            'root_cause': self.root_cause,
            'impact': self.impact,
            'related_code': self.related_code,
            'metadata': self.metadata
        }


@dataclass
class FixSuggestion:
    """Fix suggestion with pros/cons analysis"""
    title: str
    description: str
    pros: List[str]
    cons: List[str]
    impact: str
    estimated_effort: str  # e.g., "10 minutes", "1 hour"
    priority: int = 1  # 1=highest priority
    code_example: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'description': self.description,
            'pros': self.pros,
            'cons': self.cons,
            'impact': self.impact,
            'estimated_effort': self.estimated_effort,
            'priority': self.priority,
            'code_example': self.code_example
        }


@dataclass
class TestResults:
    """Complete test execution results"""
    total: int
    passed: int
    failed: int
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0  # total execution time in seconds
    test_cases: List[TestCase] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate"""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total': self.total,
            'passed': self.passed,
            'failed': self.failed,
            'skipped': self.skipped,
            'errors': self.errors,
            'duration': self.duration,
            'pass_rate': self.pass_rate,
            'test_cases': [tc.to_dict() for tc in self.test_cases],
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class TestReporter:
    """
    Test result reporter - Formats test results for AI consumption

    Provides intelligent formatting for different scenarios:
    - All tests passing
    - Partial failures with classification
    - Potential issues detection
    """

    def format_test_results(self, results: TestResults) -> str:
        """
        Format test results based on scenario

        Scenarios:
        A. All tests passed - Success message with details
        B. Partial failures - Failure analysis with suggestions
        C. All passed but potential issues - Warning with recommendations

        Args:
            results: TestResults object

        Returns:
            Formatted markdown string
        """
        # Scenario A: All tests passed
        if results.failed == 0 and results.errors == 0:
            return self._format_success_scenario(results)

        # Scenario B: Some tests failed
        return self._format_failure_scenario(results)

    def _format_success_scenario(self, results: TestResults) -> str:
        """Format scenario A: All tests passed"""
        output = []

        # Header
        output.append(f"✅ 所有测试通过 ({results.passed}/{results.total})")
        output.append("")

        # Detailed results
        output.append("详细结果：")
        for i, test_case in enumerate(results.test_cases, 1):
            if test_case.status == TestStatus.PASSED:
                desc = f" - {test_case.description}" if test_case.description else ""
                output.append(f"{i}. ✅ {test_case.name}{desc}")

        # Execution time
        output.append("")
        output.append(f"执行时间：{results.duration:.2f}s")

        # Check for potential issues (if any)
        potential_issues = self._detect_potential_issues(results)
        if potential_issues:
            output.append("")
            output.append("⚠️ 潜在问题发现：")
            for issue in potential_issues:
                output.append(f"- {issue}")

        return "\n".join(output)

    def _format_failure_scenario(self, results: TestResults) -> str:
        """Format scenario B: Some tests failed"""
        output = []

        # Header with summary
        output.append(f"测试结果：{results.passed}通过 / {results.failed}失败")
        if results.errors > 0:
            output.append(f"  (错误：{results.errors})")
        output.append("")

        # Passed tests (summary only)
        if results.passed > 0:
            output.append(f"✅ 通过：{results.passed}个测试")
            passed_tests = [tc for tc in results.test_cases if tc.status == TestStatus.PASSED]
            for test_case in passed_tests[:3]:  # Show first 3
                output.append(f"  - {test_case.name}")
            if len(passed_tests) > 3:
                output.append(f"  ... 以及其他{len(passed_tests) - 3}个")
            output.append("")

        # Failed tests (detailed)
        failed_tests = [tc for tc in results.test_cases
                       if tc.status in (TestStatus.FAILED, TestStatus.ERROR)]
        if failed_tests:
            output.append(f"❌ 失败：{len(failed_tests)}个测试")
            for test_case in failed_tests:
                output.append(f"  - {test_case.name}")
                if test_case.error_message:
                    # Truncate long error messages
                    error_msg = test_case.error_message
                    if len(error_msg) > 200:
                        error_msg = error_msg[:200] + "..."
                    output.append(f"    错误：{error_msg}")
            output.append("")

        # Classification
        failures = [TestFailure(
            test_case=tc,
            category=self._classify_single_failure(tc),
            root_cause=self._truncate_error(tc.error_message) if tc.error_message else "Unknown error",
            impact="medium"
        ) for tc in failed_tests]

        classified = self.classify_failures(failures)

        output.append("问题分类：")
        if classified['auto_fixable']:
            output.append(f"🔧 可自动修复：{len(classified['auto_fixable'])}个")
            for failure in classified['auto_fixable'][:2]:
                output.append(f"  - {failure.test_case.name}")
        else:
            output.append("🔧 可自动修复：无")

        if classified['needs_decision']:
            output.append(f"⚠️ 需要决策：{len(classified['needs_decision'])}个")
            for failure in classified['needs_decision']:
                output.append(f"  - {failure.test_case.name}: {failure.root_cause}")

        if classified['blocked']:
            output.append(f"🚫 被阻塞：{len(classified['blocked'])}个")
            for failure in classified['blocked']:
                output.append(f"  - {failure.test_case.name}")

        return "\n".join(output)

    def classify_failures(self, failures: List[TestFailure]) -> Dict[str, List[TestFailure]]:
        """
        Classify test failures into categories

        Args:
            failures: List of TestFailure objects

        Returns:
            Dictionary with categorized failures:
            {
                "auto_fixable": [...],      # AI can fix automatically
                "needs_decision": [...],    # Requires human decision
                "blocked": [...]            # Blocked by external factors
            }
        """
        result = {
            'auto_fixable': [],
            'needs_decision': [],
            'blocked': []
        }

        for failure in failures:
            category = failure.category.value
            if category in result:
                result[category].append(failure)

        return result

    def _classify_single_failure(self, test_case: TestCase) -> FailureCategory:
        """
        Classify a single test failure

        Classification rules:
        - AUTO_FIXABLE: Syntax errors, simple type errors, missing imports
        - NEEDS_DECISION: Logic errors, algorithm choices, security issues
        - BLOCKED: External dependencies, environment issues

        Args:
            test_case: TestCase object

        Returns:
            FailureCategory enum
        """
        if not test_case.error_message:
            return FailureCategory.NEEDS_DECISION

        error_msg = test_case.error_message.lower()

        # Auto-fixable patterns
        auto_fixable_patterns = [
            'syntaxerror',
            'indentationerror',
            'namenotdefined',
            'modulenotfounderror',
            'importerror',
            'missing 1 required',
            'unexpected indent'
        ]

        for pattern in auto_fixable_patterns:
            if pattern in error_msg.replace(' ', ''):
                return FailureCategory.AUTO_FIXABLE

        # Blocked patterns
        blocked_patterns = [
            'connection refused',
            'timeout',
            'no such file or directory',
            'permission denied',
            'network',
            'database',
            'redis'
        ]

        for pattern in blocked_patterns:
            if pattern in error_msg:
                return FailureCategory.BLOCKED

        # Default to needs decision
        return FailureCategory.NEEDS_DECISION

    def suggest_fixes(self, failure: TestFailure) -> List[FixSuggestion]:
        """
        Generate fix suggestions for a test failure

        Args:
            failure: TestFailure object

        Returns:
            List of 2-3 fix suggestions with pros/cons
        """
        suggestions = []

        # Analyze error message to generate specific suggestions
        error_msg = failure.test_case.error_message or ""

        # Example: Import error
        if 'import' in error_msg.lower() or 'module' in error_msg.lower():
            suggestions.append(FixSuggestion(
                title="方案1：安装缺失的依赖",
                description="使用 pip install 安装所需的库",
                pros=["快速解决", "标准方案"],
                cons=["需要修改 requirements.txt"],
                impact="需要添加依赖到项目配置",
                estimated_effort="2 分钟",
                priority=1
            ))

            suggestions.append(FixSuggestion(
                title="方案2：修改导入路径",
                description="调整 import 语句使用正确的模块路径",
                pros=["无需添加依赖", "可能是路径错误"],
                cons=["需要确认正确路径"],
                impact="仅修改导入语句",
                estimated_effort="5 分钟",
                priority=2
            ))

        # Example: Assertion error (logic issue)
        elif 'assert' in error_msg.lower():
            suggestions.append(FixSuggestion(
                title="方案1：修正业务逻辑",
                description="检查并修正核心业务逻辑实现",
                pros=["彻底解决问题", "符合需求"],
                cons=["需要理解业务逻辑"],
                impact="可能影响相关功能",
                estimated_effort="15-30 分钟",
                priority=1
            ))

            suggestions.append(FixSuggestion(
                title="方案2：调整测试预期",
                description="如果业务逻辑正确，调整测试用例的预期结果",
                pros=["快速解决", "可能是测试错误"],
                cons=["需要确认业务逻辑正确"],
                impact="仅修改测试用例",
                estimated_effort="5 分钟",
                priority=2
            ))

        # Default suggestions if no specific pattern matched
        if not suggestions:
            suggestions.append(FixSuggestion(
                title="方案1：详细分析错误",
                description="查看完整错误堆栈，定位具体问题代码",
                pros=["准确定位问题"],
                cons=["需要时间分析"],
                impact="根据具体问题而定",
                estimated_effort="10-20 分钟",
                priority=1
            ))

        return suggestions[:3]  # Return max 3 suggestions

    def _detect_potential_issues(self, results: TestResults) -> List[str]:
        """
        Detect potential issues even when all tests pass

        Returns:
            List of potential issues
        """
        issues = []

        # Check test coverage (example heuristic)
        if results.total < 5:
            issues.append("测试用例数量较少，建议补充更多测试场景")

        # Check for missing edge cases (heuristic based on test names)
        test_names = [tc.name.lower() for tc in results.test_cases]

        # Check for concurrent testing
        if not any('concurrent' in name or '并发' in name for name in test_names):
            if any('login' in name or 'auth' in name for name in test_names):
                issues.append("并发登录场景未测试")

        # Check for error handling
        if not any('error' in name or '错误' in name or 'exception' in name for name in test_names):
            issues.append("异常处理场景覆盖不足，建议补充错误处理测试")

        # Check for boundary conditions
        if not any('boundary' in name or '边界' in name or 'edge' in name for name in test_names):
            issues.append("边界条件测试缺失，建议补充边界值测试")

        return issues

    def _truncate_error(self, error_msg: str, max_length: int = 200) -> str:
        """
        Truncate long error messages for better readability

        Args:
            error_msg: Error message to truncate
            max_length: Maximum length before truncation (default: 200)

        Returns:
            Truncated error message with ellipsis if needed
        """
        if len(error_msg) > max_length:
            return error_msg[:max_length] + "..."
        return error_msg

    def format_fix_suggestions(self, failure: TestFailure) -> str:
        """
        Format fix suggestions as markdown

        Args:
            failure: TestFailure object

        Returns:
            Formatted markdown string
        """
        output = []

        output.append("修复方案建议：")
        output.append("")

        suggestions = self.suggest_fixes(failure)

        for suggestion in suggestions:
            output.append(f"**{suggestion.title}**")
            output.append(f"  描述：{suggestion.description}")
            output.append(f"  优点：{', '.join(suggestion.pros)}")
            output.append(f"  缺点：{', '.join(suggestion.cons)}")
            output.append(f"  影响：{suggestion.impact}")
            output.append(f"  预计耗时：{suggestion.estimated_effort}")
            if suggestion.code_example:
                output.append(f"  代码示例：")
                output.append(f"  ```")
                output.append(f"  {suggestion.code_example}")
                output.append(f"  ```")
            output.append("")

        return "\n".join(output)
