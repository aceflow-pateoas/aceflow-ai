"""
Unit tests for StaticChecker (Task 3.3)
"""

import pytest
from aceflow.workflow.quality import (
    StaticChecker,
    CodeIssue,
    IssueSeverity,
    IssueCategory
)


class TestStaticCheckerPythonSyntax:
    """Test Python syntax checking"""

    def setup_method(self):
        """Setup test environment"""
        self.checker = StaticChecker()

    def test_indentation_error(self):
        """Test detection of incorrect indentation"""
        code = """
def example():
  return True
"""
        issues = self.checker.check_syntax(code, "python")

        # Should detect indentation error (2 spaces instead of 4)
        indentation_issues = [i for i in issues if "Indentation" in i.message]
        assert len(indentation_issues) > 0
        assert indentation_issues[0].severity == IssueSeverity.ERROR
        assert indentation_issues[0].auto_fixable

    def test_missing_colon(self):
        """Test detection of missing colons"""
        code = """
def example()
    return True
"""
        issues = self.checker.check_syntax(code, "python")

        colon_issues = [i for i in issues if "colon" in i.message.lower()]
        assert len(colon_issues) > 0
        assert colon_issues[0].severity == IssueSeverity.ERROR

    def test_print_without_parentheses(self):
        """Test detection of Python 2 style print"""
        code = """
print "Hello World"
"""
        issues = self.checker.check_syntax(code, "python")

        print_issues = [i for i in issues if "print" in i.message.lower()]
        assert len(print_issues) > 0
        assert print_issues[0].severity == IssueSeverity.ERROR

    def test_valid_python_code(self):
        """Test that valid Python code has no syntax issues"""
        code = """
def example():
    return True
"""
        issues = self.checker.check_syntax(code, "python")
        assert len(issues) == 0


class TestStaticCheckerPythonStyle:
    """Test Python style checking"""

    def setup_method(self):
        """Setup test environment"""
        self.checker = StaticChecker()

    def test_line_too_long(self):
        """Test detection of lines exceeding 100 characters"""
        code = "x = " + "1" * 120  # Line with 120+ characters
        issues = self.checker.check_style(code, "python")

        length_issues = [i for i in issues if "too long" in i.message.lower()]
        assert len(length_issues) > 0
        assert length_issues[0].severity == IssueSeverity.WARNING

    def test_camel_case_variable(self):
        """Test detection of camelCase variables (should be snake_case)"""
        code = """
userName = "Alice"
"""
        issues = self.checker.check_style(code, "python")

        naming_issues = [i for i in issues if "snake_case" in i.message.lower()]
        assert len(naming_issues) > 0
        assert naming_issues[0].severity == IssueSeverity.WARNING

    def test_multiple_statements_on_one_line(self):
        """Test detection of multiple statements on one line"""
        code = """
x = 1; y = 2; z = 3
"""
        issues = self.checker.check_style(code, "python")

        multi_stmt_issues = [i for i in issues if "Multiple statements" in i.message]
        assert len(multi_stmt_issues) > 0
        assert multi_stmt_issues[0].severity == IssueSeverity.WARNING


class TestStaticCheckerPythonTypes:
    """Test Python type checking"""

    def setup_method(self):
        """Setup test environment"""
        self.checker = StaticChecker()

    def test_missing_return_type_hint(self):
        """Test detection of missing return type hints"""
        code = """
def get_user(user_id):
    return {"id": user_id}
"""
        issues = self.checker.check_types(code, "python")

        type_issues = [i for i in issues if "type hint" in i.message.lower()]
        assert len(type_issues) > 0
        assert type_issues[0].severity == IssueSeverity.INFO

    def test_len_equals_zero_pattern(self):
        """Test detection of len(x) == 0 pattern"""
        code = """
if len(items) == 0:
    print("Empty")
"""
        issues = self.checker.check_types(code, "python")

        len_issues = [i for i in issues if "len(" in i.message.lower()]
        assert len(len_issues) > 0
        assert len_issues[0].severity == IssueSeverity.INFO


class TestStaticCheckerJavaScriptSyntax:
    """Test JavaScript syntax checking"""

    def setup_method(self):
        """Setup test environment"""
        self.checker = StaticChecker()

    def test_missing_semicolon(self):
        """Test detection of missing semicolons"""
        code = """
const x = 10
let y = 20
"""
        issues = self.checker.check_syntax(code, "javascript")

        semicolon_issues = [i for i in issues if "semicolon" in i.message.lower()]
        assert len(semicolon_issues) > 0
        assert semicolon_issues[0].auto_fixable

    def test_double_equals(self):
        """Test detection of == instead of ==="""
        code = """
if (x == y) {
    return true;
}
"""
        issues = self.checker.check_syntax(code, "javascript")

        equality_issues = [i for i in issues if "===" in i.message]
        assert len(equality_issues) > 0
        assert equality_issues[0].auto_fixable


class TestStaticCheckerJavaScriptStyle:
    """Test JavaScript style checking"""

    def setup_method(self):
        """Setup test environment"""
        self.checker = StaticChecker()

    def test_var_usage(self):
        """Test detection of var instead of const/let"""
        code = """
var x = 10;
"""
        issues = self.checker.check_style(code, "javascript")

        var_issues = [i for i in issues if "var" in i.message.lower()]
        assert len(var_issues) > 0
        assert var_issues[0].severity == IssueSeverity.WARNING

    def test_console_log(self):
        """Test detection of console.log"""
        code = """
console.log("Debug message");
"""
        issues = self.checker.check_style(code, "javascript")

        console_issues = [i for i in issues if "console.log" in i.message]
        assert len(console_issues) > 0
        assert console_issues[0].severity == IssueSeverity.INFO


class TestStaticCheckerTypeScriptTypes:
    """Test TypeScript type checking"""

    def setup_method(self):
        """Setup test environment"""
        self.checker = StaticChecker()

    def test_missing_type_annotation(self):
        """Test detection of missing type annotations"""
        code = """
const user = { name: "Alice" };
"""
        issues = self.checker.check_types(code, "typescript")

        type_issues = [i for i in issues if "type annotation" in i.message.lower()]
        assert len(type_issues) > 0
        assert type_issues[0].severity == IssueSeverity.INFO

    def test_any_type_usage(self):
        """Test detection of 'any' type usage"""
        code = """
function process(data: any): void {
    console.log(data);
}
"""
        issues = self.checker.check_types(code, "typescript")

        any_issues = [i for i in issues if "any" in i.message.lower()]
        assert len(any_issues) > 0
        assert any_issues[0].severity == IssueSeverity.WARNING


class TestStaticCheckerAutoFix:
    """Test auto-fix functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.checker = StaticChecker()

    def test_auto_fix_indentation(self):
        """Test auto-fixing indentation"""
        code = """
def example():
  return True
"""
        issues = self.checker.check_syntax(code, "python")
        fixed_code, remaining_issues = self.checker.auto_fix(code, issues)

        # Should have fewer issues after auto-fix
        assert len(remaining_issues) < len(issues)

    def test_auto_fix_semicolons(self):
        """Test auto-fixing missing semicolons"""
        code = "const x = 10"
        issues = self.checker.check_syntax(code, "javascript")
        fixed_code, remaining_issues = self.checker.auto_fix(code, issues)

        # Fixed code should have semicolon
        assert fixed_code.strip().endswith(';')

    def test_auto_fix_equality_operators(self):
        """Test auto-fixing == to ==="""
        code = "if (x == y) { return true; }"
        issues = self.checker.check_syntax(code, "javascript")
        fixed_code, remaining_issues = self.checker.auto_fix(code, issues)

        # Fixed code should use ===
        assert '===' in fixed_code
        assert '==' not in fixed_code or '===' in fixed_code


class TestStaticCheckerSummary:
    """Test summary generation"""

    def setup_method(self):
        """Setup test environment"""
        self.checker = StaticChecker()

    def test_summary_structure(self):
        """Test that summary has correct structure"""
        code = """
def example():
  userName = "Alice"  # Indentation + naming issues
  print "Hello"  # Print without parentheses
"""
        issues = self.checker.check_syntax(code, "python")
        issues.extend(self.checker.check_style(code, "python"))

        summary = self.checker.get_summary(issues)

        assert "total" in summary
        assert "by_severity" in summary
        assert "by_category" in summary
        assert "auto_fixable" in summary

        assert summary["total"] > 0
        assert summary["by_severity"]["error"] > 0

    def test_summary_counts_auto_fixable(self):
        """Test that summary correctly counts auto-fixable issues"""
        code = "const x = 10"  # Missing semicolon (auto-fixable)
        issues = self.checker.check_syntax(code, "javascript")

        summary = self.checker.get_summary(issues)

        assert summary["auto_fixable"] > 0


class TestStaticCheckerIntegration:
    """Integration tests for StaticChecker"""

    def setup_method(self):
        """Setup test environment"""
        self.checker = StaticChecker()

    def test_complete_python_check(self):
        """Test complete check for Python code"""
        code = """
def getUserData(userId):  # camelCase + missing type hints
  userName = "Alice"  # camelCase variable (style issue)
  if len(users) == 0:  # Indentation + len pattern
      print "No users"  # Print without parens
  return {"id": userId}
"""
        syntax_issues = self.checker.check_syntax(code, "python")
        style_issues = self.checker.check_style(code, "python")
        type_issues = self.checker.check_types(code, "python")

        all_issues = syntax_issues + style_issues + type_issues
        assert len(all_issues) > 0

        # Should have issues from all categories
        categories = {issue.category for issue in all_issues}
        assert IssueCategory.SYNTAX in categories
        assert IssueCategory.STYLE in categories

    def test_complete_javascript_check(self):
        """Test complete check for JavaScript code"""
        code = """
var userName = "Alice"
if (x == 10) {
    console.log("Debug")
}
"""
        syntax_issues = self.checker.check_syntax(code, "javascript")
        style_issues = self.checker.check_style(code, "javascript")

        all_issues = syntax_issues + style_issues
        assert len(all_issues) > 0

    def test_empty_code(self):
        """Test checking empty code"""
        code = ""
        issues = self.checker.check_syntax(code, "python")

        assert len(issues) == 0
