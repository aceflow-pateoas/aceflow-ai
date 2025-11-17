"""
Unit tests for MCP Code Generation Tool (Task 3.2)
"""

import pytest
import shutil
import uuid
from pathlib import Path

# Import necessary modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "aceflow-mcp-server"))

from aceflow_mcp_server.tools import AceFlowTools
from aceflow.workflow.models import WorkflowType


def get_unique_project_id():
    """Generate unique project ID for test isolation"""
    return f"test_{uuid.uuid4().hex[:8]}"


class TestMCPCodeGenerationTool:
    """Test aceflow_v4_request_code_generation MCP tool"""

    def setup_method(self):
        """Setup test environment"""
        self.project_id = get_unique_project_id()
        self.tools = AceFlowTools(project_id=self.project_id)

    def teardown_method(self):
        """Cleanup test files"""
        aceflow_dir = Path.cwd() / ".aceflow" / "state" / self.project_id
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_request_code_generation_for_python(self):
        """Test code generation request for Python"""
        # Create a feature work item with a task
        result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="User Management System",
            description="Build user management API"
        )
        assert result['success']
        work_item_id = result['work_item_id']

        # Add a task
        task_result = self.tools.aceflow_v4_add_task(
            work_item_id=work_item_id,
            task_id="task_1",
            title="Implement UserManager class",
            description="Create user manager with CRUD operations"
        )
        assert task_result['success']

        # Request code generation
        design_doc = {
            "feature_name": "UserManager",
            "classes": [
                {
                    "name": "UserManager",
                    "description": "Manages user operations",
                    "methods": [
                        {
                            "name": "__init__",
                            "parameters": []
                        },
                        {
                            "name": "create_user",
                            "parameters": ["username", "email"],
                            "returns": "User",
                            "description": "Create a new user"
                        },
                        {
                            "name": "get_user",
                            "parameters": ["user_id"],
                            "returns": "Optional[User]",
                            "description": "Get user by ID"
                        }
                    ]
                }
            ],
            "functions": []
        }

        gen_result = self.tools.aceflow_v4_request_code_generation(
            work_item_id=work_item_id,
            task_id="task_1",
            design_doc=design_doc,
            language="python",
            complexity="medium"
        )

        assert gen_result['success']
        assert gen_result['work_item_id'] == work_item_id
        assert gen_result['task_id'] == "task_1"

        # Check strategy
        assert 'strategy' in gen_result
        assert 'order' in gen_result['strategy']
        assert '展示代码结构' in gen_result['strategy']['order']
        assert '生成核心逻辑' in gen_result['strategy']['order']
        assert '生成测试代码' in gen_result['strategy']['order']

        # Check skeleton
        assert 'skeleton' in gen_result
        assert gen_result['skeleton']['language'] == 'python'
        assert 'class UserManager:' in gen_result['skeleton']['content']
        assert 'def create_user(' in gen_result['skeleton']['content']
        assert 'def get_user(' in gen_result['skeleton']['content']

        # Check placeholders
        assert len(gen_result['skeleton']['placeholders']) > 0
        assert any('create_user' in p for p in gen_result['skeleton']['placeholders'])

        # Check next steps
        assert len(gen_result['skeleton']['next_steps']) > 0

        # Check reminder
        assert 'reminder' in gen_result
        assert 'python' in gen_result['reminder']

    def test_request_code_generation_for_javascript(self):
        """Test code generation request for JavaScript"""
        # Create work item and task
        result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Login API"
        )
        work_item_id = result['work_item_id']

        self.tools.aceflow_v4_add_task(
            work_item_id=work_item_id,
            task_id="task_js",
            title="Implement LoginController"
        )

        # Request JavaScript code generation
        design_doc = {
            "feature_name": "LoginController",
            "classes": [
                {
                    "name": "LoginController",
                    "methods": [
                        {"name": "constructor"},
                        {"name": "login", "parameters": ["req", "res"], "async": True}
                    ]
                }
            ],
            "functions": []
        }

        gen_result = self.tools.aceflow_v4_request_code_generation(
            work_item_id=work_item_id,
            task_id="task_js",
            design_doc=design_doc,
            language="javascript",
            complexity="low"
        )

        assert gen_result['success']
        assert gen_result['skeleton']['language'] == 'javascript'
        assert 'class LoginController {' in gen_result['skeleton']['content']
        assert 'async login(req, res)' in gen_result['skeleton']['content']

    def test_request_code_generation_for_typescript(self):
        """Test code generation request for TypeScript"""
        # Create work item and task
        result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="User Service"
        )
        work_item_id = result['work_item_id']

        self.tools.aceflow_v4_add_task(
            work_item_id=work_item_id,
            task_id="task_ts",
            title="Implement UserService"
        )

        # Request TypeScript code generation
        design_doc = {
            "feature_name": "UserService",
            "classes": [
                {
                    "name": "UserService",
                    "methods": [
                        {"name": "constructor"},
                        {
                            "name": "getUser",
                            "parameters": ["id: string"],
                            "returns": "Promise<User>",
                            "async": True
                        }
                    ]
                }
            ],
            "functions": []
        }

        gen_result = self.tools.aceflow_v4_request_code_generation(
            work_item_id=work_item_id,
            task_id="task_ts",
            design_doc=design_doc,
            language="typescript",
            complexity="medium"
        )

        assert gen_result['success']
        assert gen_result['skeleton']['language'] == 'typescript'
        assert 'class UserService {' in gen_result['skeleton']['content']
        assert 'Promise<User>' in gen_result['skeleton']['content']

    def test_request_code_generation_invalid_work_item(self):
        """Test code generation with invalid work item ID"""
        design_doc = {"feature_name": "Test", "classes": [], "functions": []}

        gen_result = self.tools.aceflow_v4_request_code_generation(
            work_item_id="invalid_id",
            task_id="task_1",
            design_doc=design_doc
        )

        assert not gen_result['success']
        assert 'not found' in gen_result['error']

    def test_request_code_generation_invalid_task(self):
        """Test code generation with invalid task ID"""
        # Create work item only
        result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test Feature"
        )
        work_item_id = result['work_item_id']

        design_doc = {"feature_name": "Test", "classes": [], "functions": []}

        gen_result = self.tools.aceflow_v4_request_code_generation(
            work_item_id=work_item_id,
            task_id="invalid_task",
            design_doc=design_doc
        )

        assert not gen_result['success']
        assert 'not found' in gen_result['error']

    def test_request_code_generation_unsupported_language(self):
        """Test code generation with unsupported language"""
        # Create work item and task
        result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Test Feature"
        )
        work_item_id = result['work_item_id']

        self.tools.aceflow_v4_add_task(
            work_item_id=work_item_id,
            task_id="task_1",
            title="Test Task"
        )

        design_doc = {"feature_name": "Test", "classes": [], "functions": []}

        gen_result = self.tools.aceflow_v4_request_code_generation(
            work_item_id=work_item_id,
            task_id="task_1",
            design_doc=design_doc,
            language="ruby"  # Unsupported
        )

        assert not gen_result['success']
        assert 'language' in gen_result['message'].lower()

    def test_request_code_generation_complexity_affects_steps(self):
        """Test that complexity affects generation steps"""
        # Create work item and task
        result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Complex Feature"
        )
        work_item_id = result['work_item_id']

        self.tools.aceflow_v4_add_task(
            work_item_id=work_item_id,
            task_id="task_complex",
            title="Complex Task"
        )

        design_doc = {
            "feature_name": "ComplexService",
            "classes": [{"name": "ComplexService", "methods": [{"name": "__init__"}]}],
            "functions": []
        }

        # Test low complexity
        gen_low = self.tools.aceflow_v4_request_code_generation(
            work_item_id=work_item_id,
            task_id="task_complex",
            design_doc=design_doc,
            complexity="low"
        )

        # Test high complexity
        gen_high = self.tools.aceflow_v4_request_code_generation(
            work_item_id=work_item_id,
            task_id="task_complex",
            design_doc=design_doc,
            complexity="high"
        )

        assert gen_low['success']
        assert gen_high['success']

        # High complexity should have more steps
        assert len(gen_high['strategy']['steps']) > len(gen_low['strategy']['steps'])

        # High complexity should have documentation step
        assert '生成文档' in gen_high['strategy']['order']
        assert '生成文档' not in gen_low['strategy']['order']

    def test_request_code_generation_with_functions(self):
        """Test code generation with standalone functions"""
        # Create work item and task
        result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Utility Functions"
        )
        work_item_id = result['work_item_id']

        self.tools.aceflow_v4_add_task(
            work_item_id=work_item_id,
            task_id="task_util",
            title="Utility Functions"
        )

        # Design with functions only
        design_doc = {
            "feature_name": "Utilities",
            "classes": [],
            "functions": [
                {
                    "name": "validate_email",
                    "parameters": ["email"],
                    "returns": "bool",
                    "description": "Validate email format"
                },
                {
                    "name": "hash_password",
                    "parameters": ["password"],
                    "returns": "str",
                    "description": "Hash password"
                }
            ]
        }

        gen_result = self.tools.aceflow_v4_request_code_generation(
            work_item_id=work_item_id,
            task_id="task_util",
            design_doc=design_doc,
            language="python"
        )

        assert gen_result['success']
        assert 'def validate_email(email) -> bool:' in gen_result['skeleton']['content']
        assert 'def hash_password(password) -> str:' in gen_result['skeleton']['content']


class TestMCPCodeGenerationIntegration:
    """Integration tests for code generation workflow"""

    def setup_method(self):
        """Setup test environment"""
        self.project_id = get_unique_project_id()
        self.tools = AceFlowTools(project_id=self.project_id)

    def teardown_method(self):
        """Cleanup test files"""
        aceflow_dir = Path.cwd() / ".aceflow" / "state" / self.project_id
        if aceflow_dir.exists():
            shutil.rmtree(aceflow_dir)

    def test_complete_code_generation_workflow(self):
        """Test complete workflow: create work item → add task → request code generation"""
        # 1. Start feature work item
        work_item_result = self.tools.aceflow_v4_start_work_item(
            type="feature",
            title="Authentication System",
            description="Build authentication with JWT"
        )
        assert work_item_result['success']
        work_item_id = work_item_result['work_item_id']

        # 2. Add task
        task_result = self.tools.aceflow_v4_add_task(
            work_item_id=work_item_id,
            task_id="auth_task",
            title="Implement AuthService",
            description="JWT-based authentication service"
        )
        assert task_result['success']

        # 3. Request code generation
        design_doc = {
            "feature_name": "AuthService",
            "classes": [
                {
                    "name": "AuthService",
                    "description": "JWT authentication service",
                    "methods": [
                        {"name": "__init__", "parameters": []},
                        {
                            "name": "login",
                            "parameters": ["username", "password"],
                            "returns": "Token",
                            "description": "Authenticate user and return JWT"
                        },
                        {
                            "name": "verify_token",
                            "parameters": ["token"],
                            "returns": "bool",
                            "description": "Verify JWT token"
                        }
                    ]
                }
            ],
            "functions": [
                {
                    "name": "hash_password",
                    "parameters": ["password"],
                    "returns": "str",
                    "description": "Hash password using bcrypt"
                }
            ]
        }

        gen_result = self.tools.aceflow_v4_request_code_generation(
            work_item_id=work_item_id,
            task_id="auth_task",
            design_doc=design_doc,
            language="python",
            complexity="medium"
        )

        # Verify complete generation result
        assert gen_result['success']

        # Verify strategy
        strategy = gen_result['strategy']
        assert len(strategy['order']) >= 4  # skeleton, core, helpers, tests
        assert strategy['total_estimated_lines'] > 0

        # Verify skeleton
        skeleton = gen_result['skeleton']
        assert 'class AuthService:' in skeleton['content']
        assert 'def login(' in skeleton['content']
        assert 'def verify_token(' in skeleton['content']
        assert 'def hash_password(' in skeleton['content']

        # Verify structure metadata
        assert len(skeleton['structure']['classes']) == 1
        assert skeleton['structure']['classes'][0]['name'] == 'AuthService'
        assert len(skeleton['structure']['functions']) == 1
        assert skeleton['structure']['functions'][0]['name'] == 'hash_password'

        # Verify placeholders
        assert any('AuthService.__init__' in p for p in skeleton['placeholders'])
        assert any('login' in p for p in skeleton['placeholders'])
        assert any('hash_password' in p for p in skeleton['placeholders'])

        # Verify next steps
        assert len(skeleton['next_steps']) > 0
        assert any('Review' in step or 'review' in step for step in skeleton['next_steps'])

        # Verify reminder
        assert 'python' in gen_result['reminder']
        assert '展示代码结构' in gen_result['reminder']
