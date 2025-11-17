"""
Code Generation Strategy for AceFlow v4.0

Provides intelligent code generation strategy and skeletal code generation:
- Generation order suggestion (skeleton → core → helpers → tests)
- Code skeleton generation with clear structure
- Language-specific patterns and best practices
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class GenerationPriority(Enum):
    """Code generation priority levels"""
    CRITICAL = "critical"  # Core business logic
    HIGH = "high"         # Important features
    MEDIUM = "medium"     # Helper functions
    LOW = "low"          # Optional features


class CodeLanguage(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"


@dataclass
class GenerationStep:
    """A single step in code generation process"""
    order: int
    title: str
    description: str
    priority: GenerationPriority
    estimated_lines: Optional[int] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'order': self.order,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value,
            'estimated_lines': self.estimated_lines,
            'dependencies': self.dependencies,
            'metadata': self.metadata
        }


@dataclass
class CodeSkeleton:
    """Generated code skeleton"""
    language: CodeLanguage
    content: str
    structure: Dict[str, Any]
    placeholders: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'language': self.language.value,
            'content': self.content,
            'structure': self.structure,
            'placeholders': self.placeholders,
            'next_steps': self.next_steps,
            'metadata': self.metadata
        }


class CodeGenerationStrategy:
    """
    Code generation strategy provider

    Core philosophy:
    - Show structure first, implement later
    - Prioritize core logic over helpers
    - Generate file by file
    - Always include test structure
    """

    def suggest_generation_order(
        self,
        task_description: str,
        language: str = "python",
        complexity: str = "medium"
    ) -> List[GenerationStep]:
        """
        Suggest code generation order based on task and complexity

        Priority: D > C > B
        - D: Skeleton first, then implementation
        - C: Core logic prioritized
        - B: File by file generation

        Args:
            task_description: Description of the coding task
            language: Programming language
            complexity: Task complexity (low/medium/high)

        Returns:
            List of generation steps in recommended order
        """
        steps = []

        # Step 1: Code structure/skeleton (ALWAYS FIRST)
        steps.append(GenerationStep(
            order=1,
            title="展示代码结构",
            description="生成函数签名、类定义、接口定义，不包含具体实现",
            priority=GenerationPriority.CRITICAL,
            estimated_lines=50,
            metadata={
                'focus': 'structure',
                'include': ['function_signatures', 'class_definitions', 'interfaces'],
                'exclude': ['implementation_details']
            }
        ))

        # Step 2: Core logic implementation
        steps.append(GenerationStep(
            order=2,
            title="生成核心逻辑",
            description="实现最核心的业务逻辑，保持简单清晰",
            priority=GenerationPriority.CRITICAL,
            estimated_lines=self._estimate_core_lines(complexity),
            dependencies=["展示代码结构"],
            metadata={
                'focus': 'core_logic',
                'principles': ['simple', 'clear', 'testable']
            }
        ))

        # Step 3: Helper functions (if complexity > low)
        if complexity in ['medium', 'high']:
            steps.append(GenerationStep(
                order=3,
                title="生成辅助函数",
                description="实现辅助函数、工具方法、验证逻辑",
                priority=GenerationPriority.HIGH,
                estimated_lines=self._estimate_helper_lines(complexity),
                dependencies=["生成核心逻辑"],
                metadata={
                    'focus': 'helpers',
                    'types': ['validators', 'utilities', 'formatters']
                }
            ))

        # Step 4: Test code (ALWAYS LAST)
        steps.append(GenerationStep(
            order=len(steps) + 1,
            title="生成测试代码",
            description="生成单元测试、集成测试框架",
            priority=GenerationPriority.HIGH,
            estimated_lines=self._estimate_test_lines(complexity),
            dependencies=["生成核心逻辑"],
            metadata={
                'focus': 'testing',
                'test_types': ['unit', 'integration'],
                'coverage_target': '80%'
            }
        ))

        # Step 5: Documentation (if high complexity)
        if complexity == 'high':
            steps.append(GenerationStep(
                order=len(steps) + 1,
                title="生成文档",
                description="生成API文档、使用示例、注释",
                priority=GenerationPriority.MEDIUM,
                dependencies=["生成核心逻辑"],
                metadata={
                    'focus': 'documentation',
                    'include': ['docstrings', 'examples', 'api_docs']
                }
            ))

        return steps

    def generate_code_skeleton(
        self,
        design: Dict[str, Any],
        language: str = "python"
    ) -> CodeSkeleton:
        """
        Generate code skeleton based on design document

        Args:
            design: Design document containing:
                - feature_name: Name of the feature
                - classes: List of class definitions
                - functions: List of function definitions
                - interfaces: List of interface definitions (optional)
            language: Programming language

        Returns:
            CodeSkeleton with structure and placeholders

        Raises:
            ValueError: If language is not supported
        """
        try:
            lang = CodeLanguage(language.lower())
        except ValueError:
            raise ValueError(f"Unsupported language: {language}")

        if lang == CodeLanguage.PYTHON:
            return self._generate_python_skeleton(design)
        elif lang in [CodeLanguage.JAVASCRIPT, CodeLanguage.TYPESCRIPT]:
            return self._generate_js_skeleton(design, lang)
        elif lang == CodeLanguage.JAVA:
            return self._generate_java_skeleton(design)
        elif lang == CodeLanguage.GO:
            return self._generate_go_skeleton(design)
        else:
            raise ValueError(f"Unsupported language: {language}")

    def _generate_python_skeleton(self, design: Dict[str, Any]) -> CodeSkeleton:
        """Generate Python code skeleton"""
        feature_name = design.get('feature_name', 'Feature')
        classes = design.get('classes', [])
        functions = design.get('functions', [])

        lines = []
        placeholders = []
        structure = {
            'classes': [],
            'functions': [],
            'imports': []
        }

        # Header comment
        lines.append(f'"""')
        lines.append(f'{feature_name}')
        lines.append('')
        lines.append('TODO: Add module description')
        lines.append('"""')
        lines.append('')

        # Imports placeholder
        lines.append('# TODO: Add necessary imports')
        lines.append('from typing import Dict, List, Any, Optional')
        lines.append('')
        placeholders.append('# TODO: Add necessary imports')
        structure['imports'].append('typing')

        # Generate class skeletons
        for cls_def in classes:
            class_name = cls_def.get('name', 'UnnamedClass')
            methods = cls_def.get('methods', [])
            description = cls_def.get('description', '')

            lines.append(f'class {class_name}:')
            if description:
                lines.append(f'    """{description}"""')
            lines.append('')

            structure['classes'].append({
                'name': class_name,
                'methods': [m.get('name') for m in methods]
            })

            # Constructor
            if any(m.get('name') == '__init__' for m in methods):
                init_method = next(m for m in methods if m.get('name') == '__init__')
                params = init_method.get('parameters', [])
                param_str = ', '.join(params) if params else ''
                lines.append(f'    def __init__(self{", " + param_str if param_str else ""}):')
                lines.append(f'        """Initialize {class_name}"""')
                lines.append('        # TODO: Implement initialization')
                lines.append('        pass')
                lines.append('')
                placeholders.append(f'# TODO: Implement {class_name}.__init__')

            # Other methods
            for method in methods:
                if method.get('name') == '__init__':
                    continue

                method_name = method.get('name', 'unnamed_method')
                params = method.get('parameters', [])
                returns = method.get('returns', 'None')
                method_desc = method.get('description', '')

                param_str = ', '.join(params) if params else ''
                lines.append(f'    def {method_name}(self{", " + param_str if param_str else ""}) -> {returns}:')
                if method_desc:
                    lines.append(f'        """{method_desc}"""')
                else:
                    lines.append(f'        """TODO: Add method description"""')
                lines.append('        # TODO: Implement logic')
                lines.append('        pass')
                lines.append('')
                placeholders.append(f'# TODO: Implement {class_name}.{method_name}')

        # Generate function skeletons
        for func_def in functions:
            func_name = func_def.get('name', 'unnamed_function')
            params = func_def.get('parameters', [])
            returns = func_def.get('returns', 'None')
            description = func_def.get('description', '')

            param_str = ', '.join(params) if params else ''
            lines.append(f'def {func_name}({param_str}) -> {returns}:')
            if description:
                lines.append(f'    """{description}"""')
            else:
                lines.append(f'    """TODO: Add function description"""')
            lines.append('    # TODO: Implement logic')
            lines.append('    pass')
            lines.append('')
            placeholders.append(f'# TODO: Implement {func_name}')

            structure['functions'].append({
                'name': func_name,
                'parameters': params,
                'returns': returns
            })

        content = '\n'.join(lines)

        return CodeSkeleton(
            language=CodeLanguage.PYTHON,
            content=content,
            structure=structure,
            placeholders=placeholders,
            next_steps=[
                "1. Review the code structure and verify it matches requirements",
                "2. Implement TODO items one by one, starting with core logic",
                "3. Add error handling and validation",
                "4. Write unit tests for each method",
                "5. Add docstrings and type hints"
            ],
            metadata={
                'feature_name': feature_name,
                'total_classes': len(classes),
                'total_functions': len(functions)
            }
        )

    def _generate_js_skeleton(
        self,
        design: Dict[str, Any],
        language: CodeLanguage
    ) -> CodeSkeleton:
        """Generate JavaScript/TypeScript code skeleton"""
        feature_name = design.get('feature_name', 'Feature')
        classes = design.get('classes', [])
        functions = design.get('functions', [])
        is_typescript = language == CodeLanguage.TYPESCRIPT

        lines = []
        placeholders = []
        structure = {
            'classes': [],
            'functions': [],
            'imports': []
        }

        # Header comment
        lines.append('/**')
        lines.append(f' * {feature_name}')
        lines.append(' *')
        lines.append(' * TODO: Add module description')
        lines.append(' */')
        lines.append('')

        # Generate class skeletons
        for cls_def in classes:
            class_name = cls_def.get('name', 'UnnamedClass')
            methods = cls_def.get('methods', [])
            description = cls_def.get('description', '')

            if description:
                lines.append('/**')
                lines.append(f' * {description}')
                lines.append(' */')

            lines.append(f'class {class_name} {{')

            structure['classes'].append({
                'name': class_name,
                'methods': [m.get('name') for m in methods]
            })

            # Constructor
            if any(m.get('name') in ['constructor', '__init__'] for m in methods):
                lines.append('  constructor() {')
                lines.append('    // TODO: Initialize properties')
                lines.append('  }')
                lines.append('')
                placeholders.append(f'// TODO: Implement {class_name} constructor')

            # Methods
            for method in methods:
                if method.get('name') in ['constructor', '__init__']:
                    continue

                method_name = method.get('name', 'unnamedMethod')
                params = method.get('parameters', [])
                is_async = method.get('async', False)
                method_desc = method.get('description', '')

                if method_desc:
                    lines.append('  /**')
                    lines.append(f'   * {method_desc}')
                    lines.append('   */')

                async_keyword = 'async ' if is_async else ''
                param_str = ', '.join(params) if params else ''

                if is_typescript:
                    returns = method.get('returns', 'void')
                    lines.append(f'  {async_keyword}{method_name}({param_str}): {returns} {{')
                else:
                    lines.append(f'  {async_keyword}{method_name}({param_str}) {{')

                lines.append('    // TODO: Implement logic')
                lines.append('  }')
                lines.append('')
                placeholders.append(f'// TODO: Implement {class_name}.{method_name}')

            lines.append('}')
            lines.append('')

        # Generate function skeletons
        for func_def in functions:
            func_name = func_def.get('name', 'unnamedFunction')
            params = func_def.get('parameters', [])
            is_async = func_def.get('async', False)
            description = func_def.get('description', '')

            if description:
                lines.append('/**')
                lines.append(f' * {description}')
                lines.append(' */')

            async_keyword = 'async ' if is_async else ''
            param_str = ', '.join(params) if params else ''

            if is_typescript:
                returns = func_def.get('returns', 'void')
                lines.append(f'{async_keyword}function {func_name}({param_str}): {returns} {{')
            else:
                lines.append(f'{async_keyword}function {func_name}({param_str}) {{')

            lines.append('  // TODO: Implement logic')
            lines.append('}')
            lines.append('')
            placeholders.append(f'// TODO: Implement {func_name}')

            structure['functions'].append({
                'name': func_name,
                'parameters': params
            })

        # Export statements
        if classes or functions:
            lines.append('// Exports')
            if classes:
                class_names = ', '.join([c.get('name', '') for c in classes])
                lines.append(f'module.exports = {{ {class_names} }};')
            lines.append('')

        content = '\n'.join(lines)

        return CodeSkeleton(
            language=language,
            content=content,
            structure=structure,
            placeholders=placeholders,
            next_steps=[
                "1. Review the code structure and class design",
                "2. Implement TODO items starting with core methods",
                "3. Add error handling with try-catch blocks",
                "4. Write unit tests using Jest/Mocha",
                "5. Add JSDoc comments for all public methods"
            ],
            metadata={
                'feature_name': feature_name,
                'total_classes': len(classes),
                'total_functions': len(functions),
                'is_typescript': is_typescript
            }
        )

    def _generate_java_skeleton(self, design: Dict[str, Any]) -> CodeSkeleton:
        """Generate Java code skeleton"""
        # Simplified Java skeleton generation
        return CodeSkeleton(
            language=CodeLanguage.JAVA,
            content="// Java skeleton generation - coming soon",
            structure={},
            placeholders=[],
            next_steps=["Implement Java skeleton generator"]
        )

    def _generate_go_skeleton(self, design: Dict[str, Any]) -> CodeSkeleton:
        """Generate Go code skeleton"""
        # Simplified Go skeleton generation
        return CodeSkeleton(
            language=CodeLanguage.GO,
            content="// Go skeleton generation - coming soon",
            structure={},
            placeholders=[],
            next_steps=["Implement Go skeleton generator"]
        )

    def _estimate_core_lines(self, complexity: str) -> int:
        """Estimate lines of code for core logic"""
        estimates = {
            'low': 50,
            'medium': 100,
            'high': 200
        }
        return estimates.get(complexity, 100)

    def _estimate_helper_lines(self, complexity: str) -> int:
        """Estimate lines of code for helper functions"""
        estimates = {
            'low': 20,
            'medium': 50,
            'high': 100
        }
        return estimates.get(complexity, 50)

    def _estimate_test_lines(self, complexity: str) -> int:
        """Estimate lines of code for tests"""
        estimates = {
            'low': 50,
            'medium': 100,
            'high': 200
        }
        return estimates.get(complexity, 100)
