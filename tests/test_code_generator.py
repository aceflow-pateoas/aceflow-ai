"""
Unit tests for Code Generation Strategy (Task 3.2)
"""

import pytest
from aceflow.workflow.quality import (
    CodeGenerationStrategy,
    CodeSkeleton,
    GenerationStep,
    GenerationPriority,
    CodeLanguage
)


class TestGenerationStep:
    """Test GenerationStep data model"""

    def test_generation_step_creation(self):
        """Test basic GenerationStep creation"""
        step = GenerationStep(
            order=1,
            title="生成代码骨架",
            description="创建基本的类和函数结构",
            priority=GenerationPriority.CRITICAL,
            estimated_lines=50
        )

        assert step.order == 1
        assert step.title == "生成代码骨架"
        assert step.priority == GenerationPriority.CRITICAL
        assert step.estimated_lines == 50
        assert step.dependencies == []

    def test_generation_step_with_dependencies(self):
        """Test GenerationStep with dependencies"""
        step = GenerationStep(
            order=2,
            title="实现核心逻辑",
            description="实现业务逻辑",
            priority=GenerationPriority.HIGH,
            dependencies=["生成代码骨架"]
        )

        assert len(step.dependencies) == 1
        assert step.dependencies[0] == "生成代码骨架"

    def test_generation_step_serialization(self):
        """Test GenerationStep to_dict method"""
        step = GenerationStep(
            order=1,
            title="测试步骤",
            description="测试描述",
            priority=GenerationPriority.MEDIUM,
            estimated_lines=100
        )

        data = step.to_dict()

        assert data['order'] == 1
        assert data['title'] == "测试步骤"
        assert data['priority'] == "medium"
        assert data['estimated_lines'] == 100


class TestCodeSkeleton:
    """Test CodeSkeleton data model"""

    def test_code_skeleton_creation(self):
        """Test basic CodeSkeleton creation"""
        skeleton = CodeSkeleton(
            language=CodeLanguage.PYTHON,
            content="class Example:\n    pass",
            structure={'classes': ['Example']},
            placeholders=["# TODO: Implement Example"]
        )

        assert skeleton.language == CodeLanguage.PYTHON
        assert "class Example" in skeleton.content
        assert skeleton.structure['classes'] == ['Example']
        assert len(skeleton.placeholders) == 1

    def test_code_skeleton_serialization(self):
        """Test CodeSkeleton to_dict method"""
        skeleton = CodeSkeleton(
            language=CodeLanguage.JAVASCRIPT,
            content="function test() {}",
            structure={'functions': ['test']},
            next_steps=["Implement test function"]
        )

        data = skeleton.to_dict()

        assert data['language'] == "javascript"
        assert data['content'] == "function test() {}"
        assert len(data['next_steps']) == 1


class TestCodeGenerationStrategy:
    """Test CodeGenerationStrategy class"""

    def setup_method(self):
        self.strategy = CodeGenerationStrategy()

    def test_suggest_generation_order_low_complexity(self):
        """Test generation order for low complexity task"""
        steps = self.strategy.suggest_generation_order(
            task_description="Simple CRUD API",
            language="python",
            complexity="low"
        )

        # Low complexity: skeleton + core + tests (no helpers)
        assert len(steps) >= 3
        assert steps[0].title == "展示代码结构"
        assert steps[0].order == 1
        assert steps[1].title == "生成核心逻辑"
        assert steps[-1].title == "生成测试代码"

    def test_suggest_generation_order_medium_complexity(self):
        """Test generation order for medium complexity task"""
        steps = self.strategy.suggest_generation_order(
            task_description="User authentication system",
            language="python",
            complexity="medium"
        )

        # Medium complexity: skeleton + core + helpers + tests
        assert len(steps) >= 4
        assert steps[0].title == "展示代码结构"
        assert steps[1].title == "生成核心逻辑"
        assert any(step.title == "生成辅助函数" for step in steps)
        assert steps[-1].title == "生成测试代码"

    def test_suggest_generation_order_high_complexity(self):
        """Test generation order for high complexity task"""
        steps = self.strategy.suggest_generation_order(
            task_description="Distributed transaction system",
            language="python",
            complexity="high"
        )

        # High complexity: skeleton + core + helpers + tests + docs
        assert len(steps) >= 5
        assert steps[0].title == "展示代码结构"
        assert any(step.title == "生成辅助函数" for step in steps)
        assert any(step.title == "生成文档" for step in steps)
        assert steps[-1].title == "生成文档"

    def test_generation_order_dependencies(self):
        """Test that generation steps have correct dependencies"""
        steps = self.strategy.suggest_generation_order(
            task_description="Complex feature",
            complexity="high"
        )

        # First step should have no dependencies
        assert len(steps[0].dependencies) == 0

        # Later steps should have dependencies
        for step in steps[1:]:
            if step.title != "生成文档":  # Documentation depends on core
                assert len(step.dependencies) > 0

    def test_generate_python_skeleton_simple_class(self):
        """Test Python skeleton generation for simple class"""
        design = {
            'feature_name': 'UserManager',
            'classes': [
                {
                    'name': 'UserManager',
                    'description': 'Manages user operations',
                    'methods': [
                        {
                            'name': '__init__',
                            'parameters': []
                        },
                        {
                            'name': 'create_user',
                            'parameters': ['username', 'email'],
                            'returns': 'User',
                            'description': 'Create a new user'
                        },
                        {
                            'name': 'get_user',
                            'parameters': ['user_id'],
                            'returns': 'Optional[User]',
                            'description': 'Get user by ID'
                        }
                    ]
                }
            ],
            'functions': []
        }

        skeleton = self.strategy.generate_code_skeleton(design, language="python")

        assert skeleton.language == CodeLanguage.PYTHON
        assert "class UserManager:" in skeleton.content
        assert "def __init__(self):" in skeleton.content
        assert "def create_user(self, username, email) -> User:" in skeleton.content
        assert "def get_user(self, user_id) -> Optional[User]:" in skeleton.content
        assert len(skeleton.placeholders) > 0
        assert len(skeleton.next_steps) > 0

    def test_generate_python_skeleton_with_functions(self):
        """Test Python skeleton generation with standalone functions"""
        design = {
            'feature_name': 'Utilities',
            'classes': [],
            'functions': [
                {
                    'name': 'validate_email',
                    'parameters': ['email'],
                    'returns': 'bool',
                    'description': 'Validate email format'
                },
                {
                    'name': 'hash_password',
                    'parameters': ['password'],
                    'returns': 'str',
                    'description': 'Hash password using bcrypt'
                }
            ]
        }

        skeleton = self.strategy.generate_code_skeleton(design, language="python")

        assert "def validate_email(email) -> bool:" in skeleton.content
        assert "def hash_password(password) -> str:" in skeleton.content
        assert "# TODO: Implement validate_email" in skeleton.placeholders
        assert "# TODO: Implement hash_password" in skeleton.placeholders

    def test_generate_python_skeleton_structure(self):
        """Test that Python skeleton contains correct structure metadata"""
        design = {
            'feature_name': 'AuthService',
            'classes': [
                {
                    'name': 'AuthService',
                    'methods': [
                        {'name': '__init__', 'parameters': []},
                        {'name': 'login', 'parameters': ['username', 'password'], 'returns': 'Token'}
                    ]
                }
            ],
            'functions': [
                {'name': 'verify_token', 'parameters': ['token'], 'returns': 'bool'}
            ]
        }

        skeleton = self.strategy.generate_code_skeleton(design, language="python")

        assert 'classes' in skeleton.structure
        assert 'functions' in skeleton.structure
        assert len(skeleton.structure['classes']) == 1
        assert skeleton.structure['classes'][0]['name'] == 'AuthService'
        assert len(skeleton.structure['functions']) == 1
        assert skeleton.structure['functions'][0]['name'] == 'verify_token'

    def test_generate_javascript_skeleton(self):
        """Test JavaScript skeleton generation"""
        design = {
            'feature_name': 'LoginController',
            'classes': [
                {
                    'name': 'LoginController',
                    'description': 'Handles login operations',
                    'methods': [
                        {
                            'name': 'constructor',
                            'parameters': []
                        },
                        {
                            'name': 'login',
                            'parameters': ['req', 'res'],
                            'async': True,
                            'description': 'Handle login request'
                        },
                        {
                            'name': 'validatePassword',
                            'parameters': ['password', 'hash'],
                            'async': True,
                            'returns': 'boolean'
                        }
                    ]
                }
            ],
            'functions': []
        }

        skeleton = self.strategy.generate_code_skeleton(design, language="javascript")

        assert skeleton.language == CodeLanguage.JAVASCRIPT
        assert "class LoginController {" in skeleton.content
        assert "constructor()" in skeleton.content
        assert "async login(req, res)" in skeleton.content
        assert "async validatePassword(password, hash)" in skeleton.content
        assert "// TODO: Implement" in skeleton.content

    def test_generate_typescript_skeleton(self):
        """Test TypeScript skeleton generation with type annotations"""
        design = {
            'feature_name': 'UserService',
            'classes': [
                {
                    'name': 'UserService',
                    'methods': [
                        {
                            'name': 'constructor'
                        },
                        {
                            'name': 'getUser',
                            'parameters': ['id: string'],
                            'returns': 'Promise<User>',
                            'async': True
                        }
                    ]
                }
            ],
            'functions': [
                {
                    'name': 'formatUser',
                    'parameters': ['user: User'],
                    'returns': 'string'
                }
            ]
        }

        skeleton = self.strategy.generate_code_skeleton(design, language="typescript")

        assert skeleton.language == CodeLanguage.TYPESCRIPT
        assert "class UserService {" in skeleton.content
        assert "async getUser(id: string): Promise<User>" in skeleton.content
        assert "function formatUser(user: User): string" in skeleton.content

    def test_generate_skeleton_with_multiple_classes(self):
        """Test skeleton generation with multiple classes"""
        design = {
            'feature_name': 'AuthModule',
            'classes': [
                {
                    'name': 'AuthController',
                    'methods': [
                        {'name': '__init__'},
                        {'name': 'login', 'parameters': ['credentials'], 'returns': 'Token'}
                    ]
                },
                {
                    'name': 'TokenManager',
                    'methods': [
                        {'name': '__init__'},
                        {'name': 'generate', 'parameters': ['user'], 'returns': 'str'},
                        {'name': 'verify', 'parameters': ['token'], 'returns': 'bool'}
                    ]
                }
            ],
            'functions': []
        }

        skeleton = self.strategy.generate_code_skeleton(design, language="python")

        assert "class AuthController:" in skeleton.content
        assert "class TokenManager:" in skeleton.content
        assert len(skeleton.structure['classes']) == 2
        assert skeleton.structure['classes'][0]['name'] == 'AuthController'
        assert skeleton.structure['classes'][1]['name'] == 'TokenManager'

    def test_unsupported_language_raises_error(self):
        """Test that unsupported language raises ValueError"""
        design = {'feature_name': 'Test', 'classes': [], 'functions': []}

        with pytest.raises(ValueError, match="Unsupported language"):
            self.strategy.generate_code_skeleton(design, language="ruby")

    def test_skeleton_contains_next_steps(self):
        """Test that skeleton includes clear next steps"""
        design = {
            'feature_name': 'Example',
            'classes': [
                {
                    'name': 'Example',
                    'methods': [
                        {'name': '__init__'},
                        {'name': 'process', 'parameters': ['data'], 'returns': 'Result'}
                    ]
                }
            ],
            'functions': []
        }

        skeleton = self.strategy.generate_code_skeleton(design, language="python")

        assert len(skeleton.next_steps) > 0
        assert any("Review" in step or "review" in step for step in skeleton.next_steps)
        assert any("Implement" in step or "implement" in step for step in skeleton.next_steps)
        assert any("test" in step.lower() for step in skeleton.next_steps)

    def test_skeleton_placeholders_match_structure(self):
        """Test that placeholders correspond to structure elements"""
        design = {
            'feature_name': 'Calculator',
            'classes': [
                {
                    'name': 'Calculator',
                    'methods': [
                        {'name': '__init__'},
                        {'name': 'add', 'parameters': ['a', 'b'], 'returns': 'float'},
                        {'name': 'subtract', 'parameters': ['a', 'b'], 'returns': 'float'}
                    ]
                }
            ],
            'functions': [
                {'name': 'format_result', 'parameters': ['value'], 'returns': 'str'}
            ]
        }

        skeleton = self.strategy.generate_code_skeleton(design, language="python")

        # Should have placeholders for __init__, add, subtract, and format_result
        assert len(skeleton.placeholders) >= 4
        assert any("Calculator.__init__" in p for p in skeleton.placeholders)
        assert any("Calculator.add" in p for p in skeleton.placeholders)
        assert any("Calculator.subtract" in p for p in skeleton.placeholders)
        assert any("format_result" in p for p in skeleton.placeholders)


class TestCodeGenerationComplexity:
    """Test complexity-based code generation"""

    def setup_method(self):
        self.strategy = CodeGenerationStrategy()

    def test_complexity_affects_step_count(self):
        """Test that complexity affects number of generation steps"""
        low_steps = self.strategy.suggest_generation_order(
            task_description="Simple task",
            complexity="low"
        )

        medium_steps = self.strategy.suggest_generation_order(
            task_description="Medium task",
            complexity="medium"
        )

        high_steps = self.strategy.suggest_generation_order(
            task_description="Complex task",
            complexity="high"
        )

        assert len(low_steps) < len(medium_steps)
        assert len(medium_steps) <= len(high_steps)

    def test_complexity_affects_line_estimates(self):
        """Test that complexity affects estimated lines of code"""
        low_steps = self.strategy.suggest_generation_order(
            task_description="Simple task",
            complexity="low"
        )

        high_steps = self.strategy.suggest_generation_order(
            task_description="Complex task",
            complexity="high"
        )

        # Core logic step should have different estimates
        low_core = next(s for s in low_steps if s.title == "生成核心逻辑")
        high_core = next(s for s in high_steps if s.title == "生成核心逻辑")

        assert low_core.estimated_lines < high_core.estimated_lines

    def test_all_steps_have_priority(self):
        """Test that all generation steps have priority assigned"""
        steps = self.strategy.suggest_generation_order(
            task_description="Test task",
            complexity="high"
        )

        for step in steps:
            assert step.priority in GenerationPriority
            assert isinstance(step.priority, GenerationPriority)

    def test_critical_steps_come_first(self):
        """Test that critical priority steps come before others"""
        steps = self.strategy.suggest_generation_order(
            task_description="Test task",
            complexity="high"
        )

        critical_steps = [s for s in steps if s.priority == GenerationPriority.CRITICAL]
        assert len(critical_steps) > 0

        # Critical steps should be early in the sequence
        for critical_step in critical_steps:
            assert critical_step.order <= len(steps) // 2
