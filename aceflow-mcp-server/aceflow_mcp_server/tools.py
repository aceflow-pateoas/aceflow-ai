"""AceFlow MCP Tools implementation."""

from typing import Dict, Any, Optional, List
import json
import os
import sys
from pathlib import Path
import shutil
import datetime

# Import core functionality
from .core import ProjectManager, WorkflowEngine, TemplateManager

# Import v4.0 workflow system from main aceflow package
try:
    from aceflow.workflow.core.engine import WorkflowEngine as AceFlowV4Engine
    from aceflow.workflow.core.state import StateManager as AceFlowV4StateManager
    from aceflow.workflow.models import WorkflowType, WorkItemStatus, TaskStatus, Task
    from aceflow.workflow.workflows import (
        FeatureWorkflow,
        BugfixWorkflow,
        RefactorWorkflow,
        ReviewWorkflow,
        DocumentationWorkflow,
        PerformanceWorkflow
    )
    from aceflow.workflow.task_manager import TaskManager, TaskSuggestion
    from aceflow.workflow.quality import CodeGenerationStrategy
    from aceflow.workflow.memory import (
        V4MemoryManager,
        MemoryExtractor,
        MemoryInjector,
        MemoryInjectionContext,
        DecisionScope,
        LessonCategory
    )
    V4_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] v4.0 workflow system not available: {e}", file=sys.stderr)
    V4_AVAILABLE = False
    AceFlowV4Engine = None
    WorkflowType = None
    TaskManager = None
    CodeGenerationStrategy = None

# Import existing AceFlow functionality
current_dir = Path(__file__).parent
aceflow_scripts_dir = current_dir.parent.parent / "aceflow" / "scripts"
sys.path.insert(0, str(aceflow_scripts_dir))

try:
    from utils.platform_compatibility import PlatformUtils, SafeFileOperations, EnhancedErrorHandler
except ImportError:
    # Fallback implementations if utils are not available
    class PlatformUtils:
        @staticmethod
        def get_os_type(): return "unknown"
    
    class SafeFileOperations:
        @staticmethod
        def write_text_file(path, content, encoding="utf-8"):
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
    
    class EnhancedErrorHandler:
        @staticmethod
        def handle_file_error(error, context=""): return str(error)


class AceFlowTools:
    """AceFlow MCP Tools collection."""
    
    def __init__(self, working_directory: Optional[str] = None, project_id: str = "default"):
        """Initialize tools with necessary dependencies."""
        self.platform_utils = PlatformUtils()
        self.file_ops = SafeFileOperations()
        self.error_handler = EnhancedErrorHandler()
        self.project_manager = ProjectManager()
        self.workflow_engine = WorkflowEngine()  # v3.0 engine
        self.template_manager = TemplateManager()

        # Initialize v4.0 workflow system
        if V4_AVAILABLE:
            self.v4_engine = AceFlowV4Engine(project_id=project_id)
            self._register_v4_workflows()
            self.task_manager = TaskManager(self.v4_engine.state_manager)
            self.code_generator = CodeGenerationStrategy()

            # Initialize memory system (v4.0)
            # Memory storage path: .aceflow/memory/{project_id}/memories.json
            memory_storage_path = Path(".aceflow/memory") / project_id / "memories.json"
            self.memory_manager = V4MemoryManager(storage_path=memory_storage_path)
            self.memory_extractor = MemoryExtractor(self.memory_manager)
            self.memory_injector = MemoryInjector(self.memory_manager)
        else:
            self.v4_engine = None
            self.task_manager = None
            self.code_generator = None
            self.memory_manager = None
            self.memory_extractor = None
            self.memory_injector = None

        # Store initial working directory for fallback, but don't use it as fixed
        self.fallback_working_directory = working_directory
        
        # Debug logging
        print(f"[DEBUG] AceFlowTools initialized with fallback_directory: {self.fallback_working_directory}", file=sys.stderr)
    
    def _get_dynamic_working_directory(self, provided_directory: Optional[str] = None) -> str:
        """Dynamically detect the current working directory for IDE integration.
        
        This method is called on each tool invocation to get the current working directory,
        supporting IDE environment variables and cross-platform compatibility.
        Windows IDEs often launch MCP servers from their installation directories,
        so we prioritize environment variables over os.getcwd().
        
        Args:
            provided_directory: Optional directory provided by user
            
        Returns:
            Current working directory path
            
        Raises:
            ValueError: If directory cannot be determined
        """
        if provided_directory:
            if provided_directory in [".", "./"]:
                # Handle relative current directory references
                # On Windows, this might still be IDE installation path
                current_cwd = os.getcwd()
                if not self._is_ide_installation_path(current_cwd):
                    print(f"[DEBUG] Resolved '.' to: {current_cwd}", file=sys.stderr)
                    return current_cwd
                else:
                    print(f"[DEBUG] '.' resolved to IDE path {current_cwd}, trying alternatives", file=sys.stderr)
                    # Fall through to environment variable detection
            else:
                return os.path.abspath(provided_directory)
        
        # Priority order for dynamic working directory detection
        candidates = []
        
        # 1. IDE-specific environment variables (HIGHEST priority for Windows)
        ide_env_vars = [
            # VS Code working directory variables
            'VSCODE_CWD',           # VS Code current working directory
            'VSCODE_FILE_CWD',      # VS Code file directory  
            'VSCODE_WORKSPACE',     # VS Code workspace
            
            # Cursor (VS Code fork)
            'CURSOR_CWD',           # Cursor current working directory
            'CURSOR_WORKSPACE',     # Cursor workspace
            
            # CodeBuddy IDE
            'CODEBUDDY_CWD',        # CodeBuddy current working directory
            'CODEBUDDY_WORKSPACE',  # CodeBuddy workspace
            
            # JetBrains IDEs
            'PROJECT_DIR',          # JetBrains project directory
            'IDEA_INITIAL_DIRECTORY', # IntelliJ IDEA
            'WORKSPACE_DIR',        # General workspace directory
            
            # Eclipse
            'PROJECT_LOC',          # Eclipse project location
            'WORKSPACE_LOC',        # Eclipse workspace location
            
            # Generic IDE variables
            'IDE_PROJECT_DIR',      # Generic IDE project directory
            'IDE_WORKSPACE',        # Generic IDE workspace
            'WORKSPACE_ROOT',       # Workspace root directory
            
            # MCP/Client specific
            'MCP_PROJECT_DIR',      # MCP-specific project directory
            'CLIENT_CWD',           # Client current working directory
            'MCP_CWD',              # MCP current working directory
            'MCP_WORKSPACE',        # MCP workspace directory
        ]
        
        for env_var in ide_env_vars:
            env_path = os.environ.get(env_var)
            if env_path and os.path.exists(env_path) and not self._is_ide_installation_path(env_path):
                candidates.append((env_var, env_path))
        
        # 2. Current working directory (lower priority on Windows)
        current_cwd = os.getcwd()
        if not self._is_ide_installation_path(current_cwd):
            candidates.append(("current_cwd", current_cwd))
        else:
            print(f"[DEBUG] Skipping IDE installation path: {current_cwd}", file=sys.stderr)
        
        # 3. System environment variables (Unix-like)
        system_vars = [
            'PWD',                  # Present working directory (Unix)
            'OLDPWD',               # Previous working directory (Unix)
        ]
        
        for env_var in system_vars:
            env_path = os.environ.get(env_var)
            if env_path and os.path.exists(env_path) and not self._is_ide_installation_path(env_path):
                candidates.append((env_var, env_path))
        
        # 4. Windows-specific environment variables
        if os.name == 'nt':
            windows_vars = [
                'CD',               # Current directory (Windows)
                'USERPROFILE',      # User profile directory (fallback)
            ]
            for env_var in windows_vars:
                env_path = os.environ.get(env_var)
                if env_path and os.path.exists(env_path) and not self._is_ide_installation_path(env_path):
                    candidates.append((env_var, env_path))
        
        # Debug logging
        print(f"[DEBUG] Working directory candidates: {candidates}", file=sys.stderr)
        print(f"[DEBUG] Current os.getcwd(): {current_cwd}", file=sys.stderr)
        print(f"[DEBUG] IDE installation path check: {self._is_ide_installation_path(current_cwd)}", file=sys.stderr)
        
        # Select the best candidate (prioritize IDE environment variables)
        for source, path in candidates:
            if self._is_valid_working_directory(path):
                print(f"[DEBUG] Selected working directory from {source}: {path}", file=sys.stderr)
                return path
        
        # Fallback to provided directory during initialization
        if self.fallback_working_directory:
            fallback_path = os.path.abspath(self.fallback_working_directory)
            if self._is_valid_working_directory(fallback_path) and not self._is_ide_installation_path(fallback_path):
                print(f"[DEBUG] Using fallback working directory: {fallback_path}", file=sys.stderr)
                return fallback_path
        
        # If all fails, require user input
        error_msg = (
            "⚠️  无法自动检测项目工作目录\n\n"
            "为确保AceFlow文件创建在正确位置，请在调用工具时明确指定 'directory' 参数：\n\n"
            "📁 示例用法：\n"
            "  • Windows: {\"directory\": \"C:\\\\Users\\\\YourName\\\\your-project\"}\n"
            "  • Linux/Mac: {\"directory\": \"/path/to/your/project\"}\n"
            "  • 当前目录: {\"directory\": \".\"} (仅在确认当前目录正确时使用)\n\n"
            "🤖 如果您使用Cline等AI助手：\n"
            "请要求AI助手提供当前打开项目的完整路径作为directory参数\n\n"
            f"🔍 调试信息：\n"
            f"  检测到的目录: {current_cwd}\n"
            f"  候选目录: {[path for _, path in candidates] if candidates else '无'}"
        )
        raise ValueError(error_msg)
    
    def _is_ide_installation_path(self, path: str) -> bool:
        """Check if path looks like an IDE installation directory."""
        path_lower = path.lower()
        
        # Common IDE installation path patterns (expanded for better detection)
        ide_patterns = [
            # VS Code patterns
            'microsoft vs code',
            'visual studio code',
            'code.exe',
            'vscode',
            '\\vscode\\',
            '/vscode/',
            
            # Cursor patterns  
            'cursor',
            '\\cursor\\',
            '/cursor/',
            
            # CodeBuddy patterns
            'codebuddy',
            '\\codebuddy\\',
            '/codebuddy/',
            
            # JetBrains patterns
            'jetbrains',
            'intellij',
            'pycharm',
            'webstorm',
            'phpstorm',
            
            # General IDE patterns
            'program files',
            'programme',
            'applications',
            'appdata\\local',
            'appdata\\roaming',
            
            # Other editors
            'notepad++',
            'sublime text',
            'atom',
            
            # Development tool patterns
            '.vscode-server',
            'code-server',
            
            # Common installation directories
            '/opt/',
            '/usr/share/',
            '/snap/',
            'c:\\program files',
            'c:\\program files (x86)',
        ]
        
        return any(pattern in path_lower for pattern in ide_patterns)
    
    def _is_valid_working_directory(self, path: str) -> bool:
        """Check if a path is a valid working directory.
        
        Args:
            path: Directory path to validate
            
        Returns:
            True if path is valid and accessible
        """
        try:
            return os.path.exists(path) and os.path.isdir(path) and os.access(path, os.R_OK | os.W_OK)
        except (OSError, PermissionError):
            return False
    
    def aceflow_init(
        self,
        mode: str,
        project_name: Optional[str] = None,
        directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initialize AceFlow project with specified mode.

        Args:
            mode: Workflow mode (standard, complete)
            project_name: Optional project name
            directory: 项目目录的完整路径。强烈建议明确指定以确保文件创建在正确位置。
                      示例: "C:\\Users\\YourName\\your-project" 或 "/path/to/your/project"
                      提示：如果使用Cline等AI助手，请确保提供当前打开项目的完整路径

        Returns:
            Dict with success status, message, and project info
        """
        try:
            # Validate mode
            valid_modes = ["standard", "complete"]
            if mode not in valid_modes:
                return {
                    "success": False,
                    "error": f"Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}",
                    "message": "Mode validation failed"
                }
            
            # Determine target directory using dynamic detection
            working_dir = self._get_dynamic_working_directory(directory)
            target_dir = Path(working_dir).resolve()
            
            # Debug logging for troubleshooting
            print(f"[DEBUG] Dynamic working directory detection:", file=sys.stderr)
            print(f"[DEBUG] Selected working_directory: {working_dir}", file=sys.stderr)
            print(f"[DEBUG] Final target_dir: {target_dir}", file=sys.stderr)
            
            # Create directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Set project name
            if not project_name:
                project_name = target_dir.name
            
            # Check if already initialized (unless forced)
            aceflow_dir = target_dir / ".aceflow"
            clinerules_file = target_dir / ".clinerules"
            
            if aceflow_dir.exists() or clinerules_file.exists():
                return {
                    "success": False,
                    "error": "Directory already contains AceFlow configuration",
                    "message": f"Directory '{target_dir}' is already initialized. Use force=true to overwrite."
                }
            
            # Initialize project structure
            result = self._initialize_project_structure(target_dir, project_name, mode)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Project '{project_name}' initialized successfully in {mode} mode",
                    "project_info": {
                        "name": project_name,
                        "mode": mode,
                        "directory": str(target_dir),
                        "created_files": result.get("created_files", []),
                        "debug_info": {
                            "detected_working_dir": str(target_dir),
                            "original_cwd": os.getcwd(),
                            "pwd_env": os.environ.get('PWD'),
                            "cwd_env": os.environ.get('CWD')
                        }
                    }
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize project",
                "debug_info": {
                    "exception_type": type(e).__name__,
                    "working_directory": os.getcwd(),
                    "target_directory": str(target_dir) if 'target_dir' in locals() else "unknown"
                }
            }
    
    def _initialize_project_structure(self, target_dir: Path, project_name: str, mode: str) -> Dict[str, Any]:
        """Initialize the complete project structure."""
        created_files = []
        
        try:
            # Create .aceflow directory
            aceflow_dir = target_dir / ".aceflow"
            aceflow_dir.mkdir(exist_ok=True)
            created_files.append(".aceflow/")
            
            # Create aceflow_result directory
            result_dir = target_dir / "aceflow_result"
            result_dir.mkdir(exist_ok=True)
            created_files.append("aceflow_result/")
            
            # Create project state file
            state_data = {
                "project": {
                    "name": project_name,
                    "mode": mode.upper(),
                    "created_at": datetime.datetime.now().isoformat(),
                    "version": "3.0"
                },
                "flow": {
                    "current_stage": "user_stories" if mode != "minimal" else "implementation",
                    "completed_stages": [],
                    "progress_percentage": 0
                },
                "metadata": {
                    "total_stages": self._get_stage_count(mode),
                    "last_updated": datetime.datetime.now().isoformat()
                }
            }
            
            state_file = aceflow_dir / "current_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            created_files.append(".aceflow/current_state.json")
            
            # Create .clinerules file
            clinerules_content = self._generate_clinerules(project_name, mode)
            clinerules_file = target_dir / ".clinerules"
            with open(clinerules_file, 'w', encoding='utf-8') as f:
                f.write(clinerules_content)
            created_files.append(".clinerules")
            
            # Create template.yaml
            template_content = self._generate_template_yaml(mode)
            template_file = aceflow_dir / "template.yaml"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            created_files.append(".aceflow/template.yaml")
            
            # Create spec document 
            spec_content = self._get_aceflow_spec_content()
            spec_file = aceflow_dir / "aceflow-spec_v3.0.md"
            with open(spec_file, 'w', encoding='utf-8') as f:
                f.write(spec_content)
            created_files.append(".aceflow/aceflow-spec_v3.0.md")
            
            # Note: In MCP environment, we don't copy Python scripts
            # All operations are handled through MCP tools
            
            # Create README
            readme_content = self._generate_readme(project_name, mode)
            readme_file = target_dir / "README_ACEFLOW.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            created_files.append("README_ACEFLOW.md")
            
            return {
                "success": True,
                "created_files": created_files
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create project structure"
            }
    
    def _get_stage_count(self, mode: str) -> int:
        """Get the number of stages for the given mode."""
        stage_counts = {
            "standard": 7,
            "complete": 10
        }
        return stage_counts.get(mode, 7)
    
    def _generate_clinerules(self, project_name: str, mode: str) -> str:
        """Generate .clinerules content."""
        return f"""# AceFlow v3.0 - AI Agent 集成配置
# 项目: {project_name}
# 模式: {mode}
# 初始化时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 工作模式配置
AceFlow模式: {mode}
输出目录: aceflow_result/
配置目录: .aceflow/
项目名称: {project_name}

## 核心工作原则  
1. 所有项目文档和代码必须输出到 aceflow_result/ 目录
2. 严格按照 .aceflow/template.yaml 中定义的流程执行
3. 每个阶段完成后更新项目状态文件
4. 保持跨对话的工作记忆和上下文连续性
5. 遵循AceFlow v3.0规范进行标准化输出

## 质量标准
- 代码质量: 遵循项目编码规范，注释完整
- 文档质量: 结构清晰，内容完整，格式统一
- 测试覆盖: 根据模式要求执行相应测试策略
- 交付标准: 符合 aceflow-spec_v3.0.md 规范

## 工具集成命令
- python aceflow-validate.py: 验证项目状态和合规性
- python aceflow-stage.py: 管理项目阶段和进度
- python aceflow-templates.py: 管理模板配置

记住: AceFlow是AI Agent的增强层，通过规范化输出和状态管理，实现跨对话的工作连续性。
"""
    
    def _generate_template_yaml(self, mode: str) -> str:
        """Generate template.yaml content based on mode."""
        templates = {
            "standard": """# AceFlow Standard模式配置
name: "Standard Workflow"
version: "3.0"
description: "标准软件开发工作流"

stages:
  - name: "user_stories"
    description: "用户故事分析"
    required: true
  - name: "task_breakdown"
    description: "任务分解"
    required: true
  - name: "test_design"
    description: "测试用例设计"
    required: true
  - name: "implementation"
    description: "功能实现"
    required: true
  - name: "unit_test"
    description: "单元测试"
    required: true
  - name: "integration_test"
    description: "集成测试"
    required: true
  - name: "code_review"
    description: "代码审查"
    required: true

quality_gates:
  - stage: "user_stories"
    criteria: ["用户故事完整", "验收标准明确"]
  - stage: "implementation"
    criteria: ["代码质量合格", "功能完整"]
  - stage: "unit_test"
    criteria: ["测试覆盖率 > 80%", "所有测试通过"]""",

            "complete": """# AceFlow Complete模式配置
name: "Complete Workflow"
version: "3.0"
description: "完整企业级开发工作流"

stages:
  - name: "requirement_analysis"
    description: "需求分析"
    required: true
  - name: "architecture_design"
    description: "架构设计"
    required: true
  - name: "user_stories"
    description: "用户故事分析"
    required: true
  - name: "task_breakdown"
    description: "任务分解"
    required: true
  - name: "test_design"
    description: "测试用例设计"
    required: true
  - name: "implementation"
    description: "功能实现"
    required: true
  - name: "unit_test"
    description: "单元测试"
    required: true
  - name: "integration_test"
    description: "集成测试"
    required: true
  - name: "performance_test"
    description: "性能测试"
    required: false
  - name: "code_review"
    description: "代码审查"
    required: true

quality_gates:
  - stage: "architecture_design"
    criteria: ["架构设计完整", "技术选型合理"]
  - stage: "implementation"
    criteria: ["代码质量优秀", "性能满足要求"]
  - stage: "code_review"
    criteria: ["代码评审通过", "无重大问题"]"""
        }

        return templates.get(mode, templates["standard"])
    
    def _generate_readme(self, project_name: str, mode: str) -> str:
        """Generate README content."""
        return f"""# {project_name}

## 🤖 AI助手角色定义

**你是AceFlow项目的专属AI助手，具备以下核心职责：**

### 🎯 核心身份
- **工作流专家**: 深度理解AceFlow v3.0规范和流程
- **MCP工具操作员**: 熟练使用所有aceflow_*系列工具  
- **项目状态管理员**: 主动跟踪和更新项目进度
- **质量守护者**: 确保所有输出符合AceFlow标准

### 🌐 环境上下文
- **项目名称**: {project_name}
- **工作流模式**: {mode.upper()}
- **初始化时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **AceFlow版本**: 3.0
- **当前状态获取**: 读取`.aceflow/current_state.json`
- **规范依据**: 参考`.aceflow/aceflow-spec_v3.0.md`

---

## 📐 工作原则与约束

### ✅ 必须遵循 (MUST)
1. **路径约束**: 所有项目输出必须放在`aceflow_result/`目录
2. **工具优先**: 优先使用MCP工具而非直接文件操作
3. **状态同步**: 每次重要操作后使用`aceflow_stage`更新项目状态
4. **规范合规**: 所有输出必须符合AceFlow v3.0规范要求
5. **质量门控**: 阶段转换前必须通过`aceflow_validate`验证

### 🔄 推荐行为 (SHOULD)  
1. **主动检查**: 定期使用`aceflow_validate`检查项目健康度
2. **前置验证**: 阶段转换前确认所有前置条件已满足
3. **清晰反馈**: 提供具体的进度反馈和下一步建议
4. **错误恢复**: 遇到问题时主动诊断并提供解决方案

### ⚠️ 严格禁止 (MUST NOT)
1. **跳过验证**: 不得绕过质量检查直接推进阶段
2. **文件越界**: 不得在aceflow_result/之外创建项目文件
3. **状态不同步**: 不得进行重要操作后不更新项目状态
4. **规范偏离**: 不得创建不符合AceFlow规范的输出

---

## 🧠 思考链模板

对于复杂任务，请严格按以下步骤思考和执行：

### 1️⃣ 需求理解
```
- 用户具体要求是什么？
- 期望的最终结果是什么？
- 有哪些隐含的需求？
```

### 2️⃣ 状态评估  
```
- 当前项目处于哪个阶段？（检查current_state.json）
- 该阶段的完成度如何？
- 是否存在阻塞问题？
```

### 3️⃣ 路径规划
```
- 实现目标需要经过哪些步骤？
- 是否需要推进到新阶段？
- 哪些依赖需要先满足？
```

### 4️⃣ 工具选择
```
- 需要使用哪些MCP工具？
- 工具调用的正确顺序是什么？
- 如何处理潜在的工具错误？
```

### 5️⃣ 执行计划
```
- 制定具体的操作步骤
- 确定每步的输出要求
- 设置质量检查点
```

### 6️⃣ 质量检查
```
- 结果是否符合AceFlow规范？
- 是否通过了所有验证？
- 用户需求是否完全满足？
```

### 7️⃣ 状态更新
```
- 更新项目状态
- 记录完成的工作
- 确定下一步行动计划
```

---

## 💡 标准操作示例

### 示例1: 开始新功能开发
**用户输入**: "我要添加用户登录功能"

**AI标准响应流程**:
```
1. 使用 aceflow_stage(action="status") 查看当前状态
2. 分析任务与当前阶段的匹配度
3. 如需要，使用 aceflow_stage(action="next") 推进到相应阶段
4. 按当前阶段规范开始执行任务
5. 将输出保存到 aceflow_result/ 目录
6. 使用 aceflow_validate 检查质量
7. 更新项目状态
```

### 示例2: 阶段完成确认
**AI标准流程**:
```
1. 检查当前阶段所有交付物完整性
2. 使用 aceflow_validate(mode="basic", report=true) 生成质量报告
3. 确认所有质量门控通过
4. 使用 aceflow_stage(action="next") 推进到下一阶段
5. 提供阶段总结和下一步计划
```

### 示例3: 错误处理
**遇到问题时的响应**:
```
1. 立即使用 aceflow_validate 诊断问题
2. 查看 .aceflow/current_state.json 确认状态
3. 提供具体的错误分析和解决建议
4. 如有必要，使用 aceflow_stage(action="reset") 重置状态
5. 指导用户正确的操作流程
```

---

## 🔄 动态信息引用

**在每次交互开始时，请主动执行以下检查：**

### 📊 项目状态检查
- 读取`.aceflow/current_state.json`获取最新状态
- 确认当前阶段和完成度
- 识别任何阻塞或异常情况

### 🎯 阶段目标确认  
- 明确当前阶段的具体目标
- 检查已完成的交付物
- 确定剩余任务和优先级

### 🔍 质量状态评估
- 检查是否有未解决的验证问题
- 确认所有输出都在正确位置
- 验证符合规范要求

### 🛠️ 环境状态验证
- 确认MCP工具可用性
- 检查必要目录结构存在
- 验证配置文件完整性

---

## 📋 当前项目信息

### 目录结构
```
{project_name}/
├── .aceflow/                    # AceFlow配置目录
│   ├── current_state.json       # 项目状态文件
│   ├── template.yaml            # 工作流模板
│   └── aceflow-spec_v3.0.md    # 完整规范文档
├── aceflow_result/              # 项目输出目录
├── .clinerules                  # AI Agent工作配置
└── README_ACEFLOW.md            # 本文件（AI助手指南）
```

### 工作流阶段

根据 **{mode.upper()}** 模式，项目将按以下阶段进行：

{self._get_stage_description(mode)}

---

## 🛠️ MCP工具使用指南

### 核心工具集
你可以使用以下MCP工具进行项目管理：

#### 🔍 aceflow_stage - 阶段管理
```json
{{
  "tool": "aceflow_stage",
  "actions": {{
    "status": "查看当前阶段状态",
    "next": "推进到下一阶段", 
    "list": "查看所有阶段列表",
    "reset": "重置项目状态"
  }}
}}
```

#### ✅ aceflow_validate - 质量验证
```json
{{
  "tool": "aceflow_validate", 
  "parameters": {{
    "mode": "basic|complete",
    "fix": "true|false",
    "report": "true|false"
  }}
}}
```

#### 📋 aceflow_template - 模板管理
```json
{{
  "tool": "aceflow_template",
  "actions": {{
    "list": "查看可用模板",
    "apply": "应用指定模板",
    "validate": "验证当前模板"
  }}
}}
```

### 工具使用最佳实践

1. **状态优先**: 每次操作前先检查项目状态
2. **验证频繁**: 重要操作后立即验证结果
3. **错误处理**: 工具报错时仔细分析并提供解决方案
4. **进度跟踪**: 定期更新项目状态和进度信息

---

## 🚀 MCP客户端集成说明

### 在Cline中使用
1. 确保AceFlow MCP服务器已启动
2. 在Cline设置中配置MCP服务器连接  
3. 直接使用上述MCP工具命令进行项目管理

### 在Claude Desktop中使用
1. 在MCP服务器配置中添加aceflow-mcp-server
2. 重启Claude Desktop
3. 在对话中直接调用MCP工具

### 通过HTTP API使用
如果使用HTTP模式的MCP服务器：
```bash
curl -X POST http://localhost:8000/mcp \\
  -H "Content-Type: application/json" \\
  -d '{{
    "jsonrpc": "2.0",
    "id": "1", 
    "method": "tools/call",
    "params": {{
      "name": "aceflow_stage",
      "arguments": {{"action": "status"}}
    }}
  }}'
```

---

## 📚 帮助和支持

### 🔗 关键资源
- **📖 完整规范**: [.aceflow/aceflow-spec_v3.0.md](.aceflow/aceflow-spec_v3.0.md)
- **📊 项目状态**: `.aceflow/current_state.json`  
- **⚙️ 工作流配置**: `.aceflow/template.yaml`
- **🛠️ MCP工具**: 在MCP客户端中查看完整工具列表

### 📋 规范文档
本项目严格遵循AceFlow v3.0规范：
- **规范位置**: `.aceflow/aceflow-spec_v3.0.md`
- **规范版本**: v3.0.0
- **更新时间**: 项目初始化时自动生成
- **核心内容**: 工作流规范、质量标准、文件系统规范、最佳实践

**AI助手和开发者必须**在项目开发过程中参考本地规范文档，确保项目完全符合AceFlow标准。

---

## 🔧 故障排除

### 1. MCP工具无法使用
```
诊断步骤：
✓ 确认MCP服务器正在运行
✓ 检查客户端MCP配置是否正确
✓ 验证工具权限和网络连接
✓ 查看MCP服务器日志
```

### 2. 工作目录不正确  
```
解决方案：
✓ 确保在正确的项目根目录中操作
✓ 检查.aceflow目录是否存在
✓ 验证current_state.json文件完整性
✓ 使用aceflow_validate检查项目结构
```

### 3. 阶段推进失败
```
故障处理：
✓ 使用aceflow_validate检查当前状态
✓ 确认前置条件已满足
✓ 查看.aceflow/current_state.json详细信息
✓ 必要时使用aceflow_stage(action="reset")重置
```

### 4. 质量验证不通过
```
改进流程：
✓ 仔细阅读验证报告中的具体问题
✓ 按照AceFlow规范要求修正问题
✓ 重新验证直到通过所有检查
✓ 记录问题和解决方案供后续参考
```

---

**🎯 记住：你的目标是成为最高效、最可靠的AceFlow AI助手，帮助用户在严格遵循规范的前提下，高质量地完成项目开发任务。**

---
*Generated by AceFlow v3.0 MCP Server - Optimized for AI Assistant*"""
    
    def _get_stage_description(self, mode: str) -> str:
        """Get stage descriptions for the mode."""
        descriptions = {
            "standard": """1. **User Stories** - 用户故事分析
2. **Task Breakdown** - 任务分解
3. **Test Design** - 测试用例设计
4. **Implementation** - 功能实现
5. **Unit Test** - 单元测试
6. **Integration Test** - 集成测试
7. **Code Review** - 代码审查""",

            "complete": """1. **Requirement Analysis** - 需求分析
2. **Architecture Design** - 架构设计
3. **User Stories** - 用户故事分析
4. **Task Breakdown** - 任务分解
5. **Test Design** - 测试用例设计
6. **Implementation** - 功能实现
7. **Unit Test** - 单元测试
8. **Integration Test** - 集成测试
9. **Performance Test** - 性能测试 (可选)
10. **Code Review** - 代码审查"""
        }

        return descriptions.get(mode, descriptions["standard"])
    
    def aceflow_stage(
        self,
        action: str,
        stage: Optional[str] = None,
        progress: Optional[float] = None
    ) -> Dict[str, Any]:
        """Manage project stages and workflow.

        Args:
            action: Stage management action (status, next, list, reset, update_progress)
            stage: Optional target stage name
            progress: Optional progress value (0-100) for update_progress action

        Returns:
            Dict with success status and stage information
        """
        try:
            if action == "status":
                result = self.workflow_engine.get_current_status()
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
            elif action == "next":
                result = self.workflow_engine.advance_to_next_stage()
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
            elif action == "list":
                stages = self.workflow_engine.list_all_stages()
                return {
                    "success": True,
                    "action": action,
                    "result": {
                        "stages": stages
                    }
                }
            elif action == "reset":
                result = self.workflow_engine.reset_project()
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
            elif action == "update_progress":
                if progress is None:
                    return {
                        "success": False,
                        "error": "progress parameter required for update_progress action",
                        "message": "Missing progress value"
                    }
                result = self.workflow_engine.update_stage_progress(progress)
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "error": f"Invalid action '{action}'. Valid actions: status, next, list, reset, update_progress",
                    "message": "Action not supported"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute stage action: {action}"
            }
    
    def aceflow_validate(
        self,
        mode: str = "basic",
        fix: bool = False,
        report: bool = False
    ) -> Dict[str, Any]:
        """Validate project compliance and quality.
        
        Args:
            mode: Validation mode (basic, complete)
            fix: Auto-fix issues if possible
            report: Generate detailed report
            
        Returns:
            Dict with validation results
        """
        try:
            validator = self.project_manager.get_validator()
            validation_result = validator.validate(mode=mode, auto_fix=fix, generate_report=report)
            
            return {
                "success": True,
                "validation_result": {
                    "status": validation_result["status"],
                    "checks_total": validation_result["checks"]["total"],
                    "checks_passed": validation_result["checks"]["passed"],
                    "checks_failed": validation_result["checks"]["failed"],
                    "mode": mode,
                    "auto_fix_enabled": fix,
                    "report_generated": report
                },
                "message": f"Validation completed in {mode} mode"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Validation failed"
            }
    
    def aceflow_template(
        self,
        action: str,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Manage workflow templates.
        
        Args:
            action: Template action (list, apply, validate)
            template: Optional template name
            
        Returns:
            Dict with template operation results
        """
        try:
            if action == "list":
                result = self.template_manager.list_templates()
                return {
                    "success": True,
                    "action": action,
                    "result": {
                        "available_templates": result["available"],
                        "current_template": result["current"]
                    }
                }
            elif action == "apply":
                if not template:
                    return {
                        "success": False,
                        "error": "Template name is required for apply action",
                        "message": "Please specify a template name"
                    }
                result = self.template_manager.apply_template(template)
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
            elif action == "validate":
                result = self.template_manager.validate_current_template()
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "error": f"Invalid action '{action}'. Valid actions: list, apply, validate",
                    "message": "Action not supported"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Template action failed: {action}"
            }
    
    def _get_aceflow_spec_content(self) -> str:
        """Get the AceFlow v3.0 specification content."""
        try:
            # Try to read from the main aceflow directory
            spec_path = Path(__file__).parent.parent.parent.parent / "aceflow" / "aceflow-spec_v3.0.md"
            if spec_path.exists():
                with open(spec_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # Fallback: return embedded spec content
                return self._get_embedded_spec_content()
        except Exception:
            # Last resort: return embedded spec content
            return self._get_embedded_spec_content()
    
    def _get_embedded_spec_content(self) -> str:
        """Return embedded AceFlow v3.0 specification content."""
        return """# AceFlow v3.0 完整规范文档

> **版本**: v3.0.0  
> **更新时间**: 2025-07-11  
> **类型**: 统一技术规范  
> **适用范围**: AI驱动的软件开发工作流管理系统

## 🎯 系统概述

AceFlow v3.0是一个AI驱动的软件开发工作流管理系统，结合PATEOAS（Prompt as the Engine of AI State）理念和传统软件工程最佳实践，提供智能化、标准化、可扩展的开发流程管理。

### 核心理念
- **智能自适应**: AI根据任务特征自动选择最优执行路径
- **状态驱动**: 基于项目状态和上下文进行工作流管理
- **分层架构**: 系统规范、AI执行、实战模板三层分离
- **标准化**: 统一的文件格式、路径规范和输出标准

## 📋 v3.0 新特性

### 🆕 主要改进
1. **智能模式选择**: AI自动分析任务复杂度，推荐最佳流程模式
2. **统一CLI工具**: 完整的命令行界面，支持所有操作
3. **Web可视化**: 实时状态展示和进度监控
4. **IDE深度集成**: VSCode、Cursor等主流IDE原生支持
5. **记忆池系统**: 跨项目知识积累和学习能力

### 🔄 架构升级
- **模块化设计**: 核心引擎、扩展插件、用户界面分离
- **标准化接口**: RESTful API和WebSocket实时通信
- **容器化部署**: Docker支持，一键部署
- **多语言支持**: Python、Node.js、Java、Go等主流技术栈

## 🔧 流程模式规范

### 1. 智能模式 (Smart Mode)
**代码标识**: `smart`  
**特点**: AI自动选择最优流程，动态调整执行路径

### 2. 轻量级模式 (Minimal Mode)
**代码标识**: `minimal`  
**适用场景**: 1-5人团队，快速迭代，Bug修复  
**典型周期**: 0.5-2天

工作流: P → D → R
- P (Planning/规划): 快速分析、简单设计
- D (Development/开发): 快速编码、即时测试
- R (Review/评审): 基本验证、简单文档

### 3. 标准模式 (Standard Mode)
**代码标识**: `standard`  
**适用场景**: 3-10人团队，企业应用，新功能开发  
**典型周期**: 3-7天

工作流: P1 → P2 → D1 → D2 → R1
- P1 (需求分析): 详细需求分析、用户故事
- P2 (技术设计): 架构设计、接口定义
- D1 (功能开发): 核心功能实现
- D2 (测试验证): 全面测试、性能优化
- R1 (发布准备): 代码审查、文档整理

### 4. 完整模式 (Complete Mode)
**代码标识**: `complete`  
**适用场景**: 10+人团队，关键系统，复杂项目  
**典型周期**: 1-4周

工作流: S1 → S2 → S3 → S4 → S5 → S6 → S7 → S8
- S1 (用户故事): 完整用户故事分析
- S2 (任务拆分): 详细任务分解和规划
- S3 (测试设计): 完整测试策略和用例设计
- S4-S5 (开发测试循环): 迭代式开发和测试
- S6 (代码评审): 全面代码质量检查
- S7 (演示反馈): 用户演示和反馈收集
- S8 (总结归档): 项目总结和知识沉淀

## 📁 文件系统规范

### 目录结构
```
project_root/
├── .aceflow/                           # AceFlow核心目录
│   ├── current_state.json              # 项目状态文件
│   ├── template.yaml                   # 工作流模板
│   └── aceflow-spec_v3.0.md           # 本规范文档
├── aceflow_result/                     # 项目输出目录
├── .clinerules                         # AI Agent工作配置
└── README_ACEFLOW.md                   # 项目文档
```

## 🔧 质量标准

### 交付标准
- 符合 aceflow-spec_v3.0.md 规范
- 所有阶段产出物完整
- 质量门控检查通过
- 用户验收测试通过

## 📞 支持和反馈

### 技术支持
- 📚 文档: 查看本地规范文档
- 🔧 MCP工具: 使用aceflow_*系列工具
- 📊 状态跟踪: .aceflow/current_state.json

---

*AceFlow v3.0 - 让AI驱动软件开发工作流，提升团队效率和代码质量。*

**© 2025 AceFlow Team. All rights reserved.**
"""

    # ==================== v4.0 MCP Tools ====================

    def _register_v4_workflows(self):
        """Register all 6 v4.0 workflow implementations."""
        if not V4_AVAILABLE:
            return

        try:
            self.v4_engine.register_workflow_implementation(WorkflowType.FEATURE, FeatureWorkflow())
            self.v4_engine.register_workflow_implementation(WorkflowType.BUGFIX, BugfixWorkflow())
            self.v4_engine.register_workflow_implementation(WorkflowType.REFACTOR, RefactorWorkflow())
            self.v4_engine.register_workflow_implementation(WorkflowType.REVIEW, ReviewWorkflow())
            self.v4_engine.register_workflow_implementation(WorkflowType.DOCUMENTATION, DocumentationWorkflow())
            self.v4_engine.register_workflow_implementation(WorkflowType.PERFORMANCE, PerformanceWorkflow())

            print("[INFO] v4.0 workflows registered: feature, bugfix, refactor, review, documentation, performance", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] Failed to register v4.0 workflows: {e}", file=sys.stderr)

    def aceflow_v4_start_work_item(
        self,
        type: str,
        title: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start a new v4.0 work item with specified workflow type.

        ⚠️ IMPORTANT: After starting a work item, you will be in the first stage.
        Complete all checklist items for that stage, then call aceflow_v4_complete_stage()
        to advance to the next stage.

        Args:
            type: Workflow type (feature, bugfix, refactor, review, documentation, performance)
            title: Work item title
            description: Detailed description
            metadata: Optional metadata

        Returns:
            Dict with work item details, current stage guidance, and reminder

        Example:
            >>> aceflow_v4_start_work_item(type="feature", title="User Login API")
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            # Convert string to WorkflowType enum
            workflow_type = WorkflowType(type.lower())

            # Start work item
            result = self.v4_engine.start_work_item(
                type=workflow_type,
                title=title,
                description=description,
                metadata=metadata
            )

            # Add reminder for next action
            if result.get('success') and result.get('current_stage'):
                current_stage = result['current_stage']
                tasks_count = len(current_stage.get('tasks', []))
                tasks_indicator = f"{tasks_count} tasks" if tasks_count > 0 else "the checklist items"

                result['reminder'] = (
                    f"⚠️ NEXT STEP: You are now in the '{current_stage.get('name')}' stage. "
                    f"Please complete {tasks_indicator}, then "
                    f"call aceflow_v4_complete_stage(work_item_id='{result['work_item_id']}', "
                    f"stage_id='{current_stage.get('stage_id')}') to advance."
                )

            return result

        except ValueError:
            return {
                "success": False,
                "error": f"Invalid workflow type '{type}'. Valid types: feature, bugfix, refactor, review, documentation, performance",
                "message": "Invalid workflow type"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to start work item"
            }

    def aceflow_v4_get_current_work_item(self) -> Dict[str, Any]:
        """Get the currently active v4.0 work item.

        Returns:
            Dict with current work item details or None if no active work item
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            result = self.v4_engine.get_current_work_item()

            if result is None:
                return {
                    "success": True,
                    "active": False,
                    "message": "No active work item found"
                }

            return {
                "success": True,
                "active": True,
                "work_item": result
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get current work item"
            }

    def aceflow_v4_list_work_items(
        self,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all v4.0 work items with optional status filter.

        Args:
            status: Optional status filter (pending/in_progress/completed/cancelled/blocked)

        Returns:
            Dict with list of work items
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            work_items = self.v4_engine.list_all_work_items(status)

            return {
                "success": True,
                "count": len(work_items),
                "work_items": work_items,
                "filter": status or "all"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list work items"
            }

    def aceflow_v4_complete_stage(
        self,
        work_item_id: str,
        stage_id: str,
        checklist_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Complete a stage and advance to the next one (v4.0).

        ⚠️ IMPORTANT: After completing all checklist items in a stage, you MUST call this tool
        to mark the stage as completed and advance to the next stage. Forgetting to call this
        will leave the workflow stuck in the current stage.

        Args:
            work_item_id: Work item ID
            stage_id: Current stage ID to complete
            checklist_results: Optional checklist completion results (for record keeping)

        Returns:
            Dict with completion status, next stage info, and reminder to complete next stage

        Example:
            After finishing all tasks in "requirement" stage:
            >>> aceflow_v4_complete_stage(work_item_id="work_abc123", stage_id="requirement")
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            # Complete the stage using StateManager
            success = self.v4_engine.state_manager.complete_stage(
                work_item_id=work_item_id,
                stage_id=stage_id,
                checklist_results=checklist_results
            )

            if success:
                # Get updated work item
                work_item = self.v4_engine.state_manager.get_work_item(work_item_id)

                if not work_item:
                    return {
                        "success": False,
                        "error": "Work item not found after completion",
                        "message": "Failed to retrieve updated work item"
                    }

                current_stage = work_item.current_stage

                # Build enhanced response with next stage reminder
                response = {
                    "success": True,
                    "message": f"✅ Stage '{stage_id}' completed successfully",
                    "overall_progress": work_item.overall_progress
                }

                # Add current/next stage information and reminder
                if current_stage and current_stage.status.value == 'in_progress':
                    # There is a next stage
                    response["current_stage"] = current_stage.to_dict()
                    response["next_stage_name"] = current_stage.name

                    # Use tasks list length or description as indicator
                    tasks_count = len(current_stage.tasks) if current_stage.tasks else 0
                    tasks_indicator = f"{tasks_count} tasks" if tasks_count > 0 else "the checklist items"

                    response["reminder"] = (
                        f"⚠️ NEXT STEP: You are now in the '{current_stage.name}' stage. "
                        f"Please complete {tasks_indicator}, then "
                        f"call aceflow_v4_complete_stage(work_item_id='{work_item_id}', "
                        f"stage_id='{current_stage.stage_id}') to advance."
                    )
                else:
                    # All stages completed
                    response["current_stage"] = current_stage.to_dict() if current_stage else None
                    response["next_stage_name"] = None
                    response["reminder"] = (
                        "🎉 All stages completed! You can now mark the work item as completed "
                        "or perform final delivery steps."
                    )

                return response
            else:
                return {
                    "success": False,
                    "error": "Failed to complete stage",
                    "message": "Stage completion failed (stage or work item not found)"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to complete stage"
            }

    def aceflow_v4_add_task(
        self,
        work_item_id: str,
        task_id: str,
        title: str,
        description: str = "",
        dependencies: Optional[List[str]] = None,
        position: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a task to a work item (v4.0 - FEATURE type only).

        Args:
            work_item_id: Work item ID
            task_id: Unique task ID
            title: Task title
            description: Task description
            dependencies: List of task IDs this task depends on
            position: Optional position (e.g., "after:task_2")

        Returns:
            Dict with success status
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            # Create task object
            task = Task(
                task_id=task_id,
                title=title,
                description=description,
                dependencies=dependencies or []
            )

            # Add task using StateManager
            success = self.v4_engine.state_manager.add_task(
                work_item_id=work_item_id,
                task=task,
                position=position
            )

            if success:
                return {
                    "success": True,
                    "message": f"Task '{task_id}' added to work item '{work_item_id}'",
                    "task": {
                        "task_id": task_id,
                        "title": title,
                        "status": "pending"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to add task",
                    "message": "Task addition failed (work item may not support tasks or not found)"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to add task"
            }

    def aceflow_v4_update_task_status(
        self,
        work_item_id: str,
        task_id: str,
        status: str
    ) -> Dict[str, Any]:
        """Update task status (v4.0).

        ⚠️ IMPORTANT: After completing all tasks in the current stage, remember to call
        aceflow_v4_complete_stage() to mark the stage as completed and advance to the next stage.

        Args:
            work_item_id: Work item ID
            task_id: Task ID to update
            status: New status (pending/in_progress/completed/skipped)

        Returns:
            Dict with success status, task progress, and reminder if all tasks completed
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            # Update task status using StateManager
            success = self.v4_engine.state_manager.update_task_status(
                work_item_id=work_item_id,
                task_id=task_id,
                status=status
            )

            if success:
                # Get updated task progress
                work_item = self.v4_engine.state_manager.get_work_item(work_item_id)

                if not work_item:
                    return {
                        "success": True,
                        "message": f"Task '{task_id}' status updated to '{status}'",
                        "task_progress": 0
                    }

                response = {
                    "success": True,
                    "message": f"Task '{task_id}' status updated to '{status}'",
                    "task_progress": work_item.task_progress,
                    "total_tasks": len(work_item.tasks),
                    "completed_tasks": len([t for t in work_item.tasks if t.status.value == 'completed'])
                }

                # Add reminder if all tasks are completed
                if work_item.task_progress >= 1.0 and work_item.current_stage:
                    response["reminder"] = (
                        f"🎉 All tasks completed! You can now complete the '{work_item.current_stage.name}' stage. "
                        f"Call aceflow_v4_complete_stage(work_item_id='{work_item_id}', "
                        f"stage_id='{work_item.current_stage.stage_id}') to advance."
                    )

                return response
            else:
                return {
                    "success": False,
                    "error": "Failed to update task status",
                    "message": "Task update failed (task or work item not found)"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update task status"
            }

    # ====== NEW TASK MANAGEMENT TOOLS (Task 2.2) ======

    def aceflow_v4_suggest_tasks(
        self,
        work_item_id: str,
        requirement: str,
        max_tasks: int = 10
    ) -> Dict[str, Any]:
        """Suggest tasks for a work item (v4.0 - AI-driven task breakdown).

        Args:
            work_item_id: Work item ID (must be FEATURE type)
            requirement: Requirement description for task suggestion
            max_tasks: Maximum number of tasks to suggest

        Returns:
            Dict with suggested tasks
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            work_item = self.v4_engine.state_manager.get_work_item(work_item_id)
            if not work_item:
                return {
                    "success": False,
                    "error": "Work item not found",
                    "message": f"Work item '{work_item_id}' not found"
                }

            suggestions = self.task_manager.suggest_tasks(
                work_item=work_item,
                requirement=requirement,
                max_tasks=max_tasks
            )

            return {
                "success": True,
                "work_item_id": work_item_id,
                "count": len(suggestions),
                "suggestions": [s.to_dict() for s in suggestions],
                "message": f"Generated {len(suggestions)} task suggestions for '{work_item.title}'"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to suggest tasks"
            }

    def aceflow_v4_create_tasks(
        self,
        work_item_id: str,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Batch create tasks for a work item (v4.0 - after user confirmation).

        Args:
            work_item_id: Work item ID (must be FEATURE type)
            tasks: List of task dictionaries with task_id, title, description, dependencies

        Returns:
            Dict with creation status
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            success = self.task_manager.create_tasks(work_item_id, tasks)

            if success:
                work_item = self.v4_engine.state_manager.get_work_item(work_item_id)
                return {
                    "success": True,
                    "work_item_id": work_item_id,
                    "tasks_created": len(tasks),
                    "total_tasks": len(work_item.tasks) if work_item else 0,
                    "message": f"Created {len(tasks)} tasks successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create tasks",
                    "message": "Task creation failed (work item may not support tasks or not found)"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create tasks"
            }

    def aceflow_v4_get_task_context(
        self,
        work_item_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        """Get task context for AI assistance (v4.0).

        Args:
            work_item_id: Work item ID
            task_id: Task ID to get context for

        Returns:
            Dict with task context including related tasks, work item info, and progress
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            context = self.task_manager.get_task_context(work_item_id, task_id)

            if 'error' in context:
                return {
                    "success": False,
                    "error": context['error'],
                    "message": f"Failed to get context: {context['error']}"
                }

            return {
                "success": True,
                "context": context,
                "message": f"Retrieved context for task '{task_id}'"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get task context"
            }

    def aceflow_v4_get_pending_tasks(
        self,
        work_item_id: str
    ) -> Dict[str, Any]:
        """Get all pending tasks that are ready to start (v4.0).

        Returns tasks whose dependencies are all completed.

        Args:
            work_item_id: Work item ID

        Returns:
            Dict with list of pending tasks
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            pending_tasks = self.task_manager.get_pending_tasks(work_item_id)

            return {
                "success": True,
                "work_item_id": work_item_id,
                "count": len(pending_tasks),
                "pending_tasks": [task.to_dict() for task in pending_tasks],
                "message": f"Found {len(pending_tasks)} tasks ready to start"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get pending tasks"
            }

    def aceflow_v4_get_next_task(
        self,
        work_item_id: str
    ) -> Dict[str, Any]:
        """Get the next task to work on based on dependencies and priority (v4.0).

        Args:
            work_item_id: Work item ID

        Returns:
            Dict with next task information
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            next_task = self.task_manager.get_next_task(work_item_id)

            if next_task:
                return {
                    "success": True,
                    "has_next_task": True,
                    "next_task": next_task.to_dict(),
                    "message": f"Next task: {next_task.title}"
                }
            else:
                return {
                    "success": True,
                    "has_next_task": False,
                    "next_task": None,
                    "message": "No pending tasks available (all completed or dependencies not met)"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get next task"
            }

    # ====== CODE GENERATION TOOLS (Task 3.2) ======

    def aceflow_v4_request_code_generation(
        self,
        work_item_id: str,
        task_id: str,
        design_doc: Dict[str, Any],
        language: str = "python",
        complexity: str = "medium"
    ) -> Dict[str, Any]:
        """Request code generation strategy and skeleton (v4.0).

        Returns generation order, code skeleton, and implementation guidance.

        Args:
            work_item_id: Work item ID
            task_id: Task ID requesting code generation
            design_doc: Design document containing:
                - feature_name: Name of the feature
                - classes: List of class definitions
                - functions: List of function definitions
                - interfaces: List of interface definitions (optional)
            language: Programming language (python/javascript/typescript/java/go)
            complexity: Task complexity (low/medium/high)

        Returns:
            Dict with generation strategy, code skeleton, and reminders

        Example:
            >>> aceflow_v4_request_code_generation(
                work_item_id="work_abc123",
                task_id="task_1",
                design_doc={
                    "feature_name": "UserManager",
                    "classes": [{
                        "name": "UserManager",
                        "methods": [
                            {"name": "__init__"},
                            {"name": "create_user", "parameters": ["username", "email"], "returns": "User"}
                        ]
                    }],
                    "functions": []
                },
                language="python",
                complexity="medium"
            )
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            # Verify work item and task exist
            work_item = self.v4_engine.state_manager.get_work_item(work_item_id)
            if not work_item:
                return {
                    "success": False,
                    "error": f"Work item '{work_item_id}' not found",
                    "message": "Invalid work item ID"
                }

            task = work_item.get_task_by_id(task_id)
            if not task:
                return {
                    "success": False,
                    "error": f"Task '{task_id}' not found in work item '{work_item_id}'",
                    "message": "Invalid task ID"
                }

            # Get generation order suggestion
            task_description = design_doc.get('feature_name', task.title)
            generation_steps = self.code_generator.suggest_generation_order(
                task_description=task_description,
                language=language,
                complexity=complexity
            )

            # Generate code skeleton
            skeleton = self.code_generator.generate_code_skeleton(
                design=design_doc,
                language=language
            )

            # Build response
            return {
                "success": True,
                "work_item_id": work_item_id,
                "task_id": task_id,
                "strategy": {
                    "order": [step.title for step in generation_steps],
                    "steps": [step.to_dict() for step in generation_steps],
                    "total_estimated_lines": sum(
                        step.estimated_lines for step in generation_steps
                        if step.estimated_lines
                    )
                },
                "skeleton": {
                    "language": skeleton.language.value,
                    "content": skeleton.content,
                    "structure": skeleton.structure,
                    "placeholders": skeleton.placeholders,
                    "next_steps": skeleton.next_steps
                },
                "reminder": (
                    f"📝 代码结构已生成（{skeleton.language.value}）。\n"
                    f"建议按以下顺序实现：{' → '.join([step.title for step in generation_steps])}\n"
                    f"请先确认代码结构符合需求，然后按TODO标记逐步实现功能。"
                ),
                "message": f"Code generation strategy created for task '{task.title}'"
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Invalid language or design document"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate code strategy"
            }

    # ====== MEMORY SYSTEM TOOLS (Task 4.7) ======

    def aceflow_v4_extract_memories(
        self,
        work_item_id: str,
        stage_id: str,
        stage_output: str
    ) -> Dict[str, Any]:
        """Extract technical decisions and lessons from stage output (v4.0).

        Automatically detects and extracts structured memories from unstructured text.
        Returns suggestions that need user confirmation before storage.

        Args:
            work_item_id: Work item ID
            stage_id: Stage ID where output was generated
            stage_output: The text output from completing the stage

        Returns:
            Dict with detected decisions and lessons (unconfirmed)

        Example:
            >>> aceflow_v4_extract_memories(
                work_item_id="work_abc123",
                stage_id="design",
                stage_output="We decided to use PostgreSQL for its JSONB support..."
            )
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            # Extract memories
            result = self.memory_extractor.extract_from_stage_output(
                stage_output=stage_output,
                work_item_id=work_item_id,
                stage_id=stage_id
            )

            # result is a dict with 'decisions', 'lessons', and 'summary'
            decisions_count = len(result['decisions'])
            lessons_count = len(result['lessons'])

            return {
                "success": True,
                "extraction_result": result,
                "decisions_detected": decisions_count,
                "lessons_detected": lessons_count,
                "reminder": (
                    f"📝 检测到 {decisions_count} 个技术决策和 {lessons_count} 个经验教训。\n"
                    f"请使用 aceflow_v4_confirm_decision 和 aceflow_v4_confirm_lesson 确认并存储这些记忆。"
                ),
                "message": f"Extracted {decisions_count} decisions and {lessons_count} lessons"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to extract memories"
            }

    def aceflow_v4_confirm_decision(
        self,
        decision: Dict[str, Any],
        work_item_id: str,
        stage_id: str
    ) -> Dict[str, Any]:
        """Confirm and store a detected technical decision (v4.0).

        ⚠️ IMPORTANT: This stores the decision permanently. Only call after user confirms
        the auto-detected decision is accurate and complete.

        Args:
            decision: Decision dict with: title, decision, reason, scope, alternatives, tech_stack, impact
            work_item_id: Work item ID
            stage_id: Stage ID where decision was made

        Returns:
            Dict with stored decision details

        Example:
            >>> aceflow_v4_confirm_decision(
                decision={
                    "title": "Use PostgreSQL",
                    "decision": "Choose PostgreSQL as primary database",
                    "reason": "JSONB support, ACID compliance, proven reliability",
                    "scope": "architecture",
                    "alternatives": ["MySQL", "MongoDB"],
                    "tech_stack": ["PostgreSQL", "pg_vector"],
                    "impact": "All data access patterns must support relational model"
                },
                work_item_id="work_abc123",
                stage_id="design"
            )
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            # Convert scope string to enum
            scope_str = decision.get('scope', 'module')
            scope = DecisionScope(scope_str.lower())

            # Store decision
            decision_obj = self.memory_manager.record_tech_decision(
                title=decision['title'],
                decision=decision['decision'],
                reason=decision['reason'],
                scope=scope,
                alternatives=decision.get('alternatives', []),
                tech_stack=decision.get('tech_stack', []),
                impact=decision.get('impact', ''),
                work_item_id=work_item_id,
                stage_id=stage_id,
                tags=decision.get('tags', [])
            )

            return {
                "success": True,
                "decision_id": decision_obj.decision_id,
                "message": f"✅ Technical decision '{decision['title']}' stored successfully",
                "reminder": "💡 此决策已永久存储，将在未来相关阶段自动注入。"
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Invalid decision scope or data"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store decision"
            }

    def aceflow_v4_confirm_lesson(
        self,
        lesson: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Confirm and store a detected lesson learned (v4.0).

        ⚠️ IMPORTANT: This stores the lesson permanently. Only call after user confirms
        the auto-detected lesson is valuable and actionable.

        Args:
            lesson: Lesson dict with: title, content, category, what_happened, what_learned,
                   how_to_apply, applicability, applicable_scenarios

        Returns:
            Dict with stored lesson details

        Example:
            >>> aceflow_v4_confirm_lesson(
                lesson={
                    "title": "JWT Key Management",
                    "content": "Never hardcode JWT secrets",
                    "category": "best_practice",
                    "what_happened": "Hardcoded JWT secret in code led to security audit finding",
                    "what_learned": "JWT secrets must be stored in environment variables or key management services",
                    "how_to_apply": "Use environment variables for JWT_SECRET in all environments",
                    "applicability": "general",
                    "applicable_scenarios": ["authentication", "security", "api_design"]
                }
            )
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            # Convert category string to enum
            category_str = lesson.get('category', 'technical')
            # LessonCategory enum values are lowercase (e.g., "best_practice")
            category = LessonCategory(category_str)

            # Store lesson
            lesson_obj = self.memory_manager.record_lesson(
                title=lesson['title'],
                content=lesson['content'],
                category=category,
                what_happened=lesson['what_happened'],
                what_learned=lesson['what_learned'],
                how_to_apply=lesson['how_to_apply'],
                applicability=lesson.get('applicability', 'general'),
                applicable_scenarios=lesson.get('applicable_scenarios', []),
                tags=lesson.get('tags', [])
            )

            return {
                "success": True,
                "lesson_id": lesson_obj.lesson_id,
                "message": f"✅ Lesson '{lesson['title']}' stored successfully",
                "reminder": "📚 ��经验教训已永久存储，将在未来类似场景中提醒使用。"
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Invalid lesson category or data"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store lesson"
            }

    def aceflow_v4_inject_memories(
        self,
        template_content: str,
        context: Dict[str, Any],
        include_v3_memories: bool = True,
        include_decisions: bool = True,
        include_lessons: bool = True,
        include_documents: bool = True
    ) -> Dict[str, Any]:
        """Inject relevant memories into a stage template (v4.0).

        Replaces {{project_memory}} placeholder with formatted, relevant memories.

        Args:
            template_content: Template content with {{project_memory}} placeholder
            context: MemoryInjectionContext dict with:
                - work_item_id: Work item ID
                - work_item_type: Workflow type (feature/bugfix/refactor/etc)
                - work_item_title: Work item title
                - work_item_description: Work item description
                - stage_id: Current stage ID
                - stage_name: Current stage name
                - stage_type: Stage type (design/implementation/review/etc)
                - max_memories: Max memories per type (default 5)
                - min_relevance: Minimum relevance score (default 0.3)
                - search_keywords: List of keywords for search
                - search_tags: List of tags for filtering
            include_v3_memories: Include v3.0 generic memories
            include_decisions: Include technical decisions
            include_lessons: Include lessons learned
            include_documents: Include document references

        Returns:
            Dict with injected template and injection statistics

        Example:
            >>> aceflow_v4_inject_memories(
                template_content="# Design\\n\\n{{project_memory}}\\n\\n## Tasks\\n...",
                context={
                    "work_item_id": "work_abc123",
                    "work_item_type": "feature",
                    "work_item_title": "User Authentication",
                    "stage_id": "design",
                    "stage_name": "Design Phase",
                    "max_memories": 5,
                    "search_keywords": ["authentication", "jwt"],
                    "search_tags": ["security"]
                }
            )
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            # Create MemoryInjectionContext object
            injection_context = MemoryInjectionContext(
                work_item_id=context['work_item_id'],
                work_item_type=context['work_item_type'],
                work_item_title=context['work_item_title'],
                work_item_description=context.get('work_item_description', ''),
                stage_id=context['stage_id'],
                stage_name=context['stage_name'],
                stage_type=context.get('stage_type', context['stage_id']),
                max_memories=context.get('max_memories', 5),
                min_relevance=context.get('min_relevance', 0.3),
                search_keywords=context.get('search_keywords', []),
                search_tags=context.get('search_tags', [])
            )

            # Inject memories
            injected_template, result = self.memory_injector.inject_memories_into_template(
                template_content=template_content,
                context=injection_context,
                include_v3_memories=include_v3_memories,
                include_decisions=include_decisions,
                include_lessons=include_lessons,
                include_documents=include_documents
            )

            return {
                "success": True,
                "injected_template": injected_template,
                "injection_result": result.to_dict(),
                "total_memories": result.total_count,
                "reminder": (
                    f"📝 已注入 {result.total_count} 条项目记忆（"
                    f"决策: {result.decisions_count}, "
                    f"教训: {result.lessons_count}, "
                    f"背景: {result.v3_memories_count}"
                    f"）到模板中。"
                ),
                "message": f"Injected {result.total_count} memories into template"
            }

        except KeyError as e:
            return {
                "success": False,
                "error": f"Missing required context field: {e}",
                "message": "Invalid injection context"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to inject memories"
            }

    def aceflow_v4_preview_injection(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Preview memory injection without actually injecting (v4.0).

        Shows what memories would be injected for the given context.

        Args:
            context: MemoryInjectionContext dict (same as aceflow_v4_inject_memories)

        Returns:
            Dict with injection summary and preview

        Example:
            >>> aceflow_v4_preview_injection(
                context={
                    "work_item_id": "work_abc123",
                    "work_item_type": "feature",
                    "stage_id": "design",
                    "stage_name": "Design Phase",
                    "search_keywords": ["authentication"]
                }
            )
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            # Create MemoryInjectionContext object
            injection_context = MemoryInjectionContext(
                work_item_id=context['work_item_id'],
                work_item_type=context['work_item_type'],
                work_item_title=context.get('work_item_title', ''),
                work_item_description=context.get('work_item_description', ''),
                stage_id=context['stage_id'],
                stage_name=context['stage_name'],
                stage_type=context.get('stage_type', context['stage_id']),
                max_memories=context.get('max_memories', 5),
                min_relevance=context.get('min_relevance', 0.3),
                search_keywords=context.get('search_keywords', []),
                search_tags=context.get('search_tags', [])
            )

            # Get injection summary
            summary = self.memory_injector.get_injection_summary(injection_context)

            return {
                "success": True,
                "summary": summary,
                "total_memories": summary['counts']['total'],
                "message": f"Found {summary['counts']['total']} relevant memories for injection"
            }

        except KeyError as e:
            return {
                "success": False,
                "error": f"Missing required context field: {e}",
                "message": "Invalid injection context"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to preview injection"
            }

    def aceflow_v4_list_decisions(
        self,
        scope: Optional[str] = None,
        tags: Optional[List[str]] = None,
        work_item_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all technical decisions with optional filtering (v4.0).

        Args:
            scope: Filter by decision scope (local/module/architecture/project)
            tags: Filter by tags
            work_item_id: Filter by work item ID

        Returns:
            Dict with list of decisions

        Example:
            >>> aceflow_v4_list_decisions(scope="architecture", tags=["database"])
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            # Get all decisions
            all_decisions = self.memory_manager.list_decisions()

            # Apply filters
            filtered_decisions = all_decisions

            if scope:
                scope_enum = DecisionScope(scope.lower())
                filtered_decisions = [d for d in filtered_decisions if d.scope == scope_enum]

            if tags:
                filtered_decisions = [
                    d for d in filtered_decisions
                    if any(tag in d.tags for tag in tags)
                ]

            if work_item_id:
                filtered_decisions = [
                    d for d in filtered_decisions
                    if d.work_item_id == work_item_id
                ]

            return {
                "success": True,
                "count": len(filtered_decisions),
                "decisions": [d.to_dict() for d in filtered_decisions],
                "message": f"Found {len(filtered_decisions)} technical decisions"
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Invalid scope value"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list decisions"
            }

    def aceflow_v4_list_lessons(
        self,
        category: Optional[str] = None,
        applicability: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List all lessons learned with optional filtering (v4.0).

        Args:
            category: Filter by category (technical/process/team/tooling/best_practice)
            applicability: Filter by applicability (specific/general/universal)
            tags: Filter by tags

        Returns:
            Dict with list of lessons

        Example:
            >>> aceflow_v4_list_lessons(category="best_practice", applicability="general")
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            # Get all lessons
            all_lessons = self.memory_manager.list_lessons()

            # Apply filters
            filtered_lessons = all_lessons

            if category:
                # LessonCategory enum values are lowercase (e.g., "best_practice")
                category_enum = LessonCategory(category)
                filtered_lessons = [l for l in filtered_lessons if l.category == category_enum]

            if applicability:
                filtered_lessons = [
                    l for l in filtered_lessons
                    if l.applicability == applicability
                ]

            if tags:
                filtered_lessons = [
                    l for l in filtered_lessons
                    if any(tag in l.tags for tag in tags)
                ]

            return {
                "success": True,
                "count": len(filtered_lessons),
                "lessons": [l.to_dict() for l in filtered_lessons],
                "message": f"Found {len(filtered_lessons)} lessons learned"
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Invalid category value"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list lessons"
            }

    def aceflow_v4_get_decision(
        self,
        decision_id: str
    ) -> Dict[str, Any]:
        """Get a specific technical decision by ID (v4.0).

        Args:
            decision_id: Decision ID

        Returns:
            Dict with decision details

        Example:
            >>> aceflow_v4_get_decision(decision_id="dec_abc123")
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            decision = self.memory_manager.get_decision(decision_id)

            if not decision:
                return {
                    "success": False,
                    "error": f"Decision '{decision_id}' not found",
                    "message": "Decision not found"
                }

            return {
                "success": True,
                "decision": decision.to_dict(),
                "message": f"Retrieved decision '{decision.title}'"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get decision"
            }

    def aceflow_v4_get_lesson(
        self,
        lesson_id: str
    ) -> Dict[str, Any]:
        """Get a specific lesson learned by ID (v4.0).

        Args:
            lesson_id: Lesson ID

        Returns:
            Dict with lesson details

        Example:
            >>> aceflow_v4_get_lesson(lesson_id="lesson_abc123")
        """
        if not V4_AVAILABLE:
            return {
                "success": False,
                "error": "v4.0 workflow system not available",
                "message": "Please ensure aceflow package is properly installed"
            }

        try:
            lesson = self.memory_manager.get_lesson(lesson_id)

            if not lesson:
                return {
                    "success": False,
                    "error": f"Lesson '{lesson_id}' not found",
                    "message": "Lesson not found"
                }

            return {
                "success": True,
                "lesson": lesson.to_dict(),
                "message": f"Retrieved lesson '{lesson.title}'"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get lesson"
            }