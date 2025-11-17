"""
Unit tests for Test Reporter (Task 3.1)
"""

import pytest
from datetime import datetime
from aceflow.workflow.quality import (
    TestReporter,
    TestResults,
    TestCase,
    TestFailure,
    TestStatus,
    FailureCategory,
    FixSuggestion
)


class TestTestCaseModel:
    """Test TestCase data model"""

    def test_test_case_creation(self):
        """Test basic TestCase creation"""
        test_case = TestCase(
            name="test_login_success",
            status=TestStatus.PASSED,
            description="Test successful login",
            duration=0.5
        )

        assert test_case.name == "test_login_success"
        assert test_case.status == TestStatus.PASSED
        assert test_case.description == "Test successful login"
        assert test_case.duration == 0.5

    def test_test_case_serialization(self):
        """Test TestCase to_dict method"""
        test_case = TestCase(
            name="test_example",
            status=TestStatus.FAILED,
            error_message="AssertionError: Expected True"
        )

        data = test_case.to_dict()

        assert data['name'] == "test_example"
        assert data['status'] == "failed"
        assert data['error_message'] == "AssertionError: Expected True"


class TestTestResultsModel:
    """Test TestResults data model"""

    def test_test_results_creation(self):
        """Test TestResults creation"""
        results = TestResults(
            total=10,
            passed=8,
            failed=2,
            duration=5.0
        )

        assert results.total == 10
        assert results.passed == 8
        assert results.failed == 2
        assert results.pass_rate == 80.0

    def test_pass_rate_calculation(self):
        """Test pass rate calculation"""
        results = TestResults(total=5, passed=3, failed=2)
        assert results.pass_rate == 60.0

        # Edge case: no tests
        results_empty = TestResults(total=0, passed=0, failed=0)
        assert results_empty.pass_rate == 0.0

    def test_test_results_with_test_cases(self):
        """Test TestResults with test cases"""
        test_cases = [
            TestCase(name="test_1", status=TestStatus.PASSED),
            TestCase(name="test_2", status=TestStatus.FAILED),
        ]

        results = TestResults(
            total=2,
            passed=1,
            failed=1,
            test_cases=test_cases
        )

        assert len(results.test_cases) == 2
        assert results.test_cases[0].name == "test_1"


class TestTestReporter:
    """Test TestReporter class"""

    def setup_method(self):
        self.reporter = TestReporter()

    def test_format_all_tests_passed(self):
        """Test formatting when all tests pass"""
        test_cases = [
            TestCase(name="test_login", status=TestStatus.PASSED, description="认证成功场景"),
            TestCase(name="test_logout", status=TestStatus.PASSED, description="登出场景"),
            TestCase(name="test_token", status=TestStatus.PASSED, description="Token验证"),
        ]

        results = TestResults(
            total=3,
            passed=3,
            failed=0,
            duration=1.2,
            test_cases=test_cases
        )

        output = self.reporter.format_test_results(results)

        # Should show success header
        assert "✅ 所有测试通过 (3/3)" in output
        # Should list all tests
        assert "test_login" in output
        assert "认证成功场景" in output
        # Should show execution time
        assert "1.20s" in output

    def test_format_partial_failures(self):
        """Test formatting when some tests fail"""
        test_cases = [
            TestCase(name="test_success", status=TestStatus.PASSED),
            TestCase(
                name="test_fail",
                status=TestStatus.FAILED,
                error_message="AssertionError: Expected True but got False"
            ),
        ]

        results = TestResults(
            total=2,
            passed=1,
            failed=1,
            test_cases=test_cases
        )

        output = self.reporter.format_test_results(results)

        # Should show summary
        assert "1通过 / 1失败" in output
        # Should show passed section
        assert "✅ 通过：1个测试" in output
        # Should show failed section
        assert "❌ 失败：1个测试" in output
        assert "test_fail" in output
        assert "AssertionError" in output
        # Should show classification
        assert "问题分类" in output

    def test_classify_single_failure_auto_fixable(self):
        """Test classification of auto-fixable failures"""
        test_case = TestCase(
            name="test_import",
            status=TestStatus.FAILED,
            error_message="ModuleNotFoundError: No module named 'requests'"
        )

        category = self.reporter._classify_single_failure(test_case)

        assert category == FailureCategory.AUTO_FIXABLE

    def test_classify_single_failure_needs_decision(self):
        """Test classification of failures needing decision"""
        test_case = TestCase(
            name="test_logic",
            status=TestStatus.FAILED,
            error_message="AssertionError: Password validation failed"
        )

        category = self.reporter._classify_single_failure(test_case)

        assert category == FailureCategory.NEEDS_DECISION

    def test_classify_single_failure_blocked(self):
        """Test classification of blocked failures"""
        test_case = TestCase(
            name="test_database",
            status=TestStatus.FAILED,
            error_message="ConnectionError: Connection refused to database"
        )

        category = self.reporter._classify_single_failure(test_case)

        assert category == FailureCategory.BLOCKED

    def test_classify_failures_batch(self):
        """Test batch classification of failures"""
        failures = [
            TestFailure(
                test_case=TestCase(name="test_1", status=TestStatus.FAILED),
                category=FailureCategory.AUTO_FIXABLE,
                root_cause="Import error",
                impact="low"
            ),
            TestFailure(
                test_case=TestCase(name="test_2", status=TestStatus.FAILED),
                category=FailureCategory.NEEDS_DECISION,
                root_cause="Logic error",
                impact="high"
            ),
            TestFailure(
                test_case=TestCase(name="test_3", status=TestStatus.FAILED),
                category=FailureCategory.BLOCKED,
                root_cause="Database unavailable",
                impact="medium"
            ),
        ]

        classified = self.reporter.classify_failures(failures)

        assert len(classified['auto_fixable']) == 1
        assert len(classified['needs_decision']) == 1
        assert len(classified['blocked']) == 1

    def test_suggest_fixes_for_import_error(self):
        """Test fix suggestions for import errors"""
        failure = TestFailure(
            test_case=TestCase(
                name="test_api",
                status=TestStatus.FAILED,
                error_message="ModuleNotFoundError: No module named 'requests'"
            ),
            category=FailureCategory.AUTO_FIXABLE,
            root_cause="Missing module",
            impact="low"
        )

        suggestions = self.reporter.suggest_fixes(failure)

        assert len(suggestions) > 0
        # Should suggest installing dependency
        assert any('安装' in s.title for s in suggestions)
        # Should suggest checking import path
        assert any('导入路径' in s.title for s in suggestions)

    def test_suggest_fixes_for_assertion_error(self):
        """Test fix suggestions for assertion errors"""
        failure = TestFailure(
            test_case=TestCase(
                name="test_logic",
                status=TestStatus.FAILED,
                error_message="AssertionError: Expected 200 but got 400"
            ),
            category=FailureCategory.NEEDS_DECISION,
            root_cause="Logic error",
            impact="high"
        )

        suggestions = self.reporter.suggest_fixes(failure)

        assert len(suggestions) > 0
        # Should suggest fixing business logic
        assert any('业务逻辑' in s.title for s in suggestions)
        # Should suggest adjusting test expectations
        assert any('测试预期' in s.title for s in suggestions)

    def test_detect_potential_issues_few_tests(self):
        """Test detection of potential issues - few tests"""
        test_cases = [
            TestCase(name="test_basic", status=TestStatus.PASSED),
            TestCase(name="test_login", status=TestStatus.PASSED),
        ]

        results = TestResults(
            total=2,
            passed=2,
            failed=0,
            test_cases=test_cases
        )

        issues = self.reporter._detect_potential_issues(results)

        # Should detect low test count
        assert any('测试用例数量较少' in issue for issue in issues)

    def test_detect_potential_issues_missing_concurrent_tests(self):
        """Test detection of missing concurrent tests for auth scenarios"""
        test_cases = [
            TestCase(name="test_login_success", status=TestStatus.PASSED),
            TestCase(name="test_login_failure", status=TestStatus.PASSED),
            TestCase(name="test_auth_token", status=TestStatus.PASSED),
            TestCase(name="test_logout", status=TestStatus.PASSED),
            TestCase(name="test_refresh_token", status=TestStatus.PASSED),
        ]

        results = TestResults(
            total=5,
            passed=5,
            failed=0,
            test_cases=test_cases
        )

        issues = self.reporter._detect_potential_issues(results)

        # Should detect missing concurrent login tests
        assert any('并发登录' in issue for issue in issues)

    def test_detect_potential_issues_missing_error_handling(self):
        """Test detection of missing error handling tests"""
        test_cases = [
            TestCase(name="test_create_user", status=TestStatus.PASSED),
            TestCase(name="test_get_user", status=TestStatus.PASSED),
            TestCase(name="test_update_user", status=TestStatus.PASSED),
            TestCase(name="test_delete_user", status=TestStatus.PASSED),
            TestCase(name="test_list_users", status=TestStatus.PASSED),
        ]

        results = TestResults(
            total=5,
            passed=5,
            failed=0,
            test_cases=test_cases
        )

        issues = self.reporter._detect_potential_issues(results)

        # Should detect missing error handling tests
        assert any('异常处理' in issue for issue in issues)

    def test_format_fix_suggestions(self):
        """Test formatting of fix suggestions"""
        failure = TestFailure(
            test_case=TestCase(
                name="test_example",
                status=TestStatus.FAILED,
                error_message="ImportError: Cannot import module"
            ),
            category=FailureCategory.AUTO_FIXABLE,
            root_cause="Import error",
            impact="low"
        )

        output = self.reporter.format_fix_suggestions(failure)

        # Should include header
        assert "修复方案建议" in output
        # Should include fix titles
        assert "方案1" in output
        # Should include details
        assert "优点" in output
        assert "缺点" in output
        assert "影响" in output

    def test_truncate_long_error_messages(self):
        """Test that long error messages are truncated"""
        long_error = "A" * 300  # 300 character error

        test_case = TestCase(
            name="test_long_error",
            status=TestStatus.FAILED,
            error_message=long_error
        )

        results = TestResults(
            total=1,
            passed=0,
            failed=1,
            test_cases=[test_case]
        )

        output = self.reporter.format_test_results(results)

        # Error should be truncated with ellipsis
        assert "..." in output
        # Should not contain the full 300 character error
        assert long_error not in output


class TestFixSuggestion:
    """Test FixSuggestion model"""

    def test_fix_suggestion_creation(self):
        """Test creating a fix suggestion"""
        suggestion = FixSuggestion(
            title="使用bcrypt",
            description="使用bcrypt进行密码加密",
            pros=["安全", "标准"],
            cons=["需要引入库"],
            impact="需要修改密码存储逻辑",
            estimated_effort="30分钟",
            priority=1
        )

        assert suggestion.title == "使用bcrypt"
        assert len(suggestion.pros) == 2
        assert len(suggestion.cons) == 1
        assert suggestion.priority == 1

    def test_fix_suggestion_serialization(self):
        """Test fix suggestion to_dict"""
        suggestion = FixSuggestion(
            title="Test Fix",
            description="Test description",
            pros=["pro1"],
            cons=["con1"],
            impact="low",
            estimated_effort="5 min"
        )

        data = suggestion.to_dict()

        assert data['title'] == "Test Fix"
        assert data['pros'] == ["pro1"]
        assert data['cons'] == ["con1"]
