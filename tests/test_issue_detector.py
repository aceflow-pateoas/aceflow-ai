"""
Unit tests for IssueDetector (Task 3.4)
"""

import pytest
from aceflow.workflow.quality.issue_detector import (
    IssueDetector,
    PotentialIssue,
    IssueRisk,
    IssueType
)


class TestIssueDetectorMissingTests:
    """Test missing test detection"""

    def setup_method(self):
        """Setup test environment"""
        self.detector = IssueDetector()

    def test_detect_missing_concurrent_tests_for_auth(self):
        """Test detection of missing concurrent tests for authentication code"""
        code = """
def login(username, password):
    session = create_session()
    return authenticate(username, password, session)
"""
        tests = """
def test_login_success():
    assert login("user", "pass") is not None
"""
        issues = self.detector.detect_missing_tests(code, tests, "python")

        concurrent_issues = [i for i in issues if "concurrent" in i.description.lower()]
        assert len(concurrent_issues) > 0
        assert concurrent_issues[0].risk == IssueRisk.HIGH
        assert concurrent_issues[0].type == IssueType.MISSING_TEST

    def test_detect_missing_error_handling_tests_for_database(self):
        """Test detection of missing error handling tests for database operations"""
        code = """
def query_users():
    conn = database.connect()
    return conn.execute("SELECT * FROM users")
"""
        tests = """
def test_query_users_success():
    users = query_users()
    assert len(users) > 0
"""
        issues = self.detector.detect_missing_tests(code, tests, "python")

        error_issues = [i for i in issues if "error handling" in i.description.lower()]
        assert len(error_issues) > 0
        assert error_issues[0].risk == IssueRisk.MEDIUM

    def test_detect_missing_edge_case_tests_for_api(self):
        """Test detection of missing edge case tests for API endpoints"""
        code = """
@app.route('/api/users/<user_id>')
def get_user(user_id):
    return User.get(user_id)
"""
        tests = """
def test_get_user():
    response = client.get('/api/users/1')
    assert response.status_code == 200
"""
        issues = self.detector.detect_missing_tests(code, tests, "python")

        edge_case_issues = [i for i in issues if "edge case" in i.description.lower()]
        assert len(edge_case_issues) > 0

    def test_detect_missing_permission_tests_for_file_ops(self):
        """Test detection of missing permission tests for file operations"""
        code = """
def save_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)
"""
        tests = """
def test_save_file():
    save_file("test.txt", "content")
    assert os.path.exists("test.txt")
"""
        issues = self.detector.detect_missing_tests(code, tests, "python")

        permission_issues = [i for i in issues if "permission" in i.description.lower()]
        assert len(permission_issues) > 0

    def test_detect_missing_timeout_tests_for_async(self):
        """Test detection of missing timeout tests for async operations"""
        code = """
async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
"""
        tests = """
async def test_fetch_data():
    data = await fetch_data("http://example.com")
    assert data is not None
"""
        issues = self.detector.detect_missing_tests(code, tests, "python")

        timeout_issues = [i for i in issues if "timeout" in i.description.lower()]
        assert len(timeout_issues) > 0
        assert timeout_issues[0].risk == IssueRisk.HIGH

    def test_no_missing_tests_when_comprehensive(self):
        """Test that comprehensive tests don't trigger warnings"""
        code = """
def login(username, password):
    return authenticate(username, password)
"""
        tests = """
def test_login_concurrent():
    # Concurrent test
    pass

def test_login_error():
    # Error handling
    pass

def test_login_edge_cases():
    # Edge cases
    pass
"""
        issues = self.detector.detect_missing_tests(code, tests, "python")

        # Should have no missing test issues
        assert len(issues) == 0


class TestIssueDetectorSecurityRisks:
    """Test security risk detection"""

    def setup_method(self):
        """Setup test environment"""
        self.detector = IssueDetector()

    def test_detect_sql_injection_string_concat(self):
        """Test detection of SQL injection via string concatenation"""
        code = """
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    return db.execute(query)
"""
        issues = self.detector.detect_security_risks(code, "python")

        sql_issues = [i for i in issues if i.type == IssueType.SECURITY and "SQL" in i.description]
        assert len(sql_issues) > 0
        assert sql_issues[0].risk == IssueRisk.CRITICAL
        assert sql_issues[0].line is not None

    def test_detect_sql_injection_percent_formatting(self):
        """Test detection of SQL injection via % formatting"""
        code = """
query = "SELECT * FROM users WHERE name = %s" % username
"""
        issues = self.detector.detect_security_risks(code, "python")

        sql_issues = [i for i in issues if "SQL" in i.description]
        assert len(sql_issues) > 0

    def test_detect_hardcoded_api_key(self):
        """Test detection of hardcoded API keys"""
        code = """
API_KEY = "sk_live_1234567890abcdef"
"""
        issues = self.detector.detect_security_risks(code, "python")

        secret_issues = [i for i in issues if "secret" in i.description.lower() or "key" in i.description.lower()]
        assert len(secret_issues) > 0
        assert secret_issues[0].risk == IssueRisk.CRITICAL

    def test_detect_hardcoded_password(self):
        """Test detection of hardcoded passwords"""
        code = """
PASSWORD = "super_secret_password_123"
"""
        issues = self.detector.detect_security_risks(code, "python")

        secret_issues = [i for i in issues if "secret" in i.description.lower()]
        assert len(secret_issues) > 0

    def test_detect_unsafe_eval(self):
        """Test detection of unsafe eval usage"""
        code = """
def process_input(user_input):
    result = eval(user_input)
    return result
"""
        issues = self.detector.detect_security_risks(code, "python")

        eval_issues = [i for i in issues if "eval" in i.description.lower()]
        assert len(eval_issues) > 0
        assert eval_issues[0].risk == IssueRisk.HIGH

    def test_detect_weak_crypto_md5(self):
        """Test detection of weak cryptographic algorithms"""
        code = """
import hashlib

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()
"""
        issues = self.detector.detect_security_risks(code, "python")

        crypto_issues = [i for i in issues if "crypto" in i.description.lower()]
        assert len(crypto_issues) > 0
        assert crypto_issues[0].risk == IssueRisk.HIGH

    def test_detect_xss_python(self):
        """Test detection of XSS vulnerabilities in Python"""
        code = """
def render_message(message):
    return render_template('message.html', content=message|safe)
"""
        issues = self.detector.detect_security_risks(code, "python")

        xss_issues = [i for i in issues if "XSS" in i.description]
        assert len(xss_issues) > 0

    def test_detect_xss_javascript(self):
        """Test detection of XSS vulnerabilities in JavaScript"""
        code = """
function displayUserInput(input) {
    document.getElementById('output').innerHTML = input;
}
"""
        issues = self.detector.detect_security_risks(code, "javascript")

        xss_issues = [i for i in issues if "XSS" in i.description]
        assert len(xss_issues) > 0

    def test_no_security_issues_safe_code(self):
        """Test that safe code has no security issues"""
        code = """
def get_user(user_id):
    # Using parameterized query
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,))
"""
        issues = self.detector.detect_security_risks(code, "python")

        # Should have no SQL injection issues
        sql_issues = [i for i in issues if "SQL" in i.description]
        assert len(sql_issues) == 0


class TestIssueDetectorPerformanceIssues:
    """Test performance issue detection"""

    def setup_method(self):
        """Setup test environment"""
        self.detector = IssueDetector()

    def test_detect_n_plus_one_query(self):
        """Test detection of N+1 query pattern"""
        code = """
for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user.id)
    process_orders(orders)
"""
        issues = self.detector.detect_performance_issues(code, "python")

        n_plus_one_issues = [i for i in issues if "N+1" in i.description]
        assert len(n_plus_one_issues) > 0
        assert n_plus_one_issues[0].risk == IssueRisk.HIGH

    def test_detect_inefficient_string_concat_python(self):
        """Test detection of inefficient string concatenation in Python"""
        code = """
result = ""
for item in items:
    result += str(item)
"""
        issues = self.detector.detect_performance_issues(code, "python")

        concat_issues = [i for i in issues if "string concatenation" in i.description.lower()]
        assert len(concat_issues) > 0
        assert concat_issues[0].risk == IssueRisk.MEDIUM

    def test_detect_inefficient_string_concat_javascript(self):
        """Test detection of inefficient string concatenation in JavaScript"""
        code = """
for (let i = 0; i < items.length; i++) {
    result += items[i];
}
"""
        issues = self.detector.detect_performance_issues(code, "javascript")

        concat_issues = [i for i in issues if "string concatenation" in i.description.lower()]
        assert len(concat_issues) > 0

    def test_detect_missing_database_index(self):
        """Test detection of queries that might need indexes"""
        code = """
query = "SELECT * FROM users WHERE email = 'test@example.com'"
"""
        issues = self.detector.detect_performance_issues(code, "python")

        index_issues = [i for i in issues if "index" in i.description.lower()]
        assert len(index_issues) > 0
        assert index_issues[0].risk == IssueRisk.MEDIUM

    def test_detect_blocking_io_in_async(self):
        """Test detection of blocking I/O in async context"""
        code = """
async def process_file():
    with open('data.txt', 'r') as f:
        data = f.read()
    return data
"""
        issues = self.detector.detect_performance_issues(code, "python")

        blocking_issues = [i for i in issues if "blocking" in i.description.lower()]
        assert len(blocking_issues) > 0
        assert blocking_issues[0].risk == IssueRisk.HIGH

    def test_no_performance_issues_optimized_code(self):
        """Test that optimized code has no performance issues"""
        code = """
# Optimized: using join instead of concatenation
result = "".join(str(item) for item in items)
"""
        issues = self.detector.detect_performance_issues(code, "python")

        # Should have no string concatenation issues
        concat_issues = [i for i in issues if "string concatenation" in i.description.lower()]
        assert len(concat_issues) == 0


class TestIssueDetectorDetectAll:
    """Test detect_all_issues method"""

    def setup_method(self):
        """Setup test environment"""
        self.detector = IssueDetector()

    def test_detect_all_with_multiple_issue_types(self):
        """Test detecting all issue types together"""
        code = """
def login(username, password):
    # SQL injection risk
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    user = db.execute(query)

    # Hardcoded secret
    API_KEY = "sk_live_1234567890"

    # N+1 query pattern
    for order in orders:
        items = db.query("SELECT * FROM items WHERE order_id = ?", order.id)
"""
        tests = ""  # No tests

        all_issues = self.detector.detect_all_issues(code, tests, "python", scope="all")

        assert "missing_tests" in all_issues
        assert "security" in all_issues
        assert "performance" in all_issues

        # Should have issues in all categories
        assert len(all_issues["security"]) > 0
        assert len(all_issues["performance"]) > 0

    def test_detect_all_scope_security_only(self):
        """Test detecting security issues only"""
        code = """
PASSWORD = "secret123"
query = "SELECT * FROM users WHERE id = " + user_id
"""
        all_issues = self.detector.detect_all_issues(code, "", "python", scope="security")

        assert len(all_issues["security"]) > 0
        assert len(all_issues["missing_tests"]) == 0
        assert len(all_issues["performance"]) == 0

    def test_detect_all_scope_performance_only(self):
        """Test detecting performance issues only"""
        code = """
for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user.id)
"""
        all_issues = self.detector.detect_all_issues(code, "", "python", scope="performance")

        assert len(all_issues["performance"]) > 0
        assert len(all_issues["security"]) == 0

    def test_detect_all_scope_testing_only(self):
        """Test detecting missing tests only"""
        code = """
def login(username, password):
    return authenticate(username, password)
"""
        tests = ""

        all_issues = self.detector.detect_all_issues(code, tests, "python", scope="testing")

        assert len(all_issues["missing_tests"]) > 0
        assert len(all_issues["security"]) == 0
        assert len(all_issues["performance"]) == 0


class TestIssueDetectorSummary:
    """Test summary generation"""

    def setup_method(self):
        """Setup test environment"""
        self.detector = IssueDetector()

    def test_summary_structure(self):
        """Test that summary has correct structure"""
        code = """
PASSWORD = "secret"  # CRITICAL security issue
query = "SELECT * FROM users WHERE id = " + user_id  # CRITICAL SQL injection
"""
        all_issues = self.detector.detect_all_issues(code, "", "python")
        summary = self.detector.get_summary(all_issues)

        assert "total" in summary
        assert "by_type" in summary
        assert "by_risk" in summary
        assert "top_issues" in summary

        assert summary["total"] > 0
        assert summary["by_risk"]["critical"] > 0

    def test_summary_top_issues_prioritizes_critical(self):
        """Test that top issues prioritizes critical and high risks"""
        code = """
PASSWORD = "secret"  # CRITICAL
API_KEY = "key123"  # CRITICAL
query = "SELECT * FROM users WHERE id = " + user_id  # CRITICAL
"""
        all_issues = self.detector.detect_all_issues(code, "", "python")
        summary = self.detector.get_summary(all_issues)

        # Top issues should contain critical issues first
        top_issues = summary["top_issues"]
        assert len(top_issues) > 0
        assert all(issue.risk in [IssueRisk.CRITICAL, IssueRisk.HIGH] for issue in top_issues)

    def test_summary_counts_by_type(self):
        """Test that summary correctly counts by type"""
        code = """
PASSWORD = "secret"  # Security
for user in users:
    orders = db.query("SELECT * FROM orders")  # Performance
"""
        tests = ""  # Missing tests

        all_issues = self.detector.detect_all_issues(code, tests, "python")
        summary = self.detector.get_summary(all_issues)

        assert summary["by_type"]["security"] > 0
        assert summary["by_type"]["performance"] > 0


class TestIssueDetectorMultiLanguage:
    """Test multi-language support"""

    def setup_method(self):
        """Setup test environment"""
        self.detector = IssueDetector()

    def test_javascript_security_detection(self):
        """Test security detection for JavaScript"""
        code = """
function queryUsers(userId) {
    const query = `SELECT * FROM users WHERE id = ${userId}`;
    return db.query(query);
}
"""
        issues = self.detector.detect_security_risks(code, "javascript")

        sql_issues = [i for i in issues if "SQL" in i.description]
        assert len(sql_issues) > 0

    def test_javascript_async_detection(self):
        """Test async detection for JavaScript"""
        code = """
async function fetchData() {
    const data = await fetch(url);
    return data;
}
"""
        tests = ""

        issues = self.detector.detect_missing_tests(code, tests, "javascript")

        timeout_issues = [i for i in issues if "timeout" in i.description.lower()]
        assert len(timeout_issues) > 0

    def test_typescript_async_detection(self):
        """Test async detection for TypeScript"""
        code = """
async function getData(): Promise<Data> {
    const response = await http.get(url);
    return response.data;
}
"""
        tests = ""

        issues = self.detector.detect_missing_tests(code, tests, "typescript")

        timeout_issues = [i for i in issues if "timeout" in i.description.lower()]
        assert len(timeout_issues) > 0


class TestIssueDetectorEdgeCases:
    """Test edge cases"""

    def setup_method(self):
        """Setup test environment"""
        self.detector = IssueDetector()

    def test_empty_code(self):
        """Test with empty code"""
        issues = self.detector.detect_all_issues("", "", "python")

        assert issues["missing_tests"] == []
        assert issues["security"] == []
        assert issues["performance"] == []

    def test_comments_only(self):
        """Test with comments only"""
        code = """
# This is a comment
# Another comment
"""
        issues = self.detector.detect_security_risks(code, "python")

        # Comments should not trigger issues
        assert len(issues) == 0

    def test_multiple_issues_same_line(self):
        """Test multiple issues on the same line"""
        code = """
PASSWORD = "secret"; API_KEY = "key123"
"""
        issues = self.detector.detect_security_risks(code, "python")

        # Should detect both hardcoded secrets
        assert len(issues) >= 2
