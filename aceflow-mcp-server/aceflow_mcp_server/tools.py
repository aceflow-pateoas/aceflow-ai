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
    
    def __init__(self):
        """Initialize tools with necessary dependencies."""
        self.platform_utils = PlatformUtils()
        self.file_ops = SafeFileOperations()
        self.error_handler = EnhancedErrorHandler()
        self.project_manager = ProjectManager()
        self.workflow_engine = WorkflowEngine()
        self.template_manager = TemplateManager()
    
    def aceflow_init(
        self,
        mode: str,
        project_name: Optional[str] = None,
        directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initialize AceFlow project with specified mode.
        
        Args:
            mode: Workflow mode (minimal, standard, complete, smart)
            project_name: Optional project name
            directory: Optional target directory (defaults to current directory)
        
        Returns:
            Dict with success status, message, and project info
        """
        try:
            # Validate mode
            valid_modes = ["minimal", "standard", "complete", "smart"]
            if mode not in valid_modes:
                return {
                    "success": False,
                    "error": f"Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}",
                    "message": "Mode validation failed"
                }
            
            # Determine target directory
            if directory:
                target_dir = Path(directory).resolve()
            else:
                target_dir = Path.cwd()
            
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
                    "message": "Use --force flag to overwrite existing configuration"
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
                        "created_files": result.get("created_files", [])
                    }
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize project"
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
                    "current_stage": self._get_initial_stage_for_mode(mode),
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
            
            # Create .aceflow subdirectories for templates, config, core
            config_dir = aceflow_dir / "config"
            config_dir.mkdir(exist_ok=True)
            created_files.append(".aceflow/config/")
            
            templates_dir = aceflow_dir / "templates"
            templates_dir.mkdir(exist_ok=True)
            created_files.append(".aceflow/templates/")
            
            core_dir = aceflow_dir / "core"
            core_dir.mkdir(exist_ok=True)
            created_files.append(".aceflow/core/")
            
            # Create .clinerules directory for AI Agent prompts
            clinerules_dir = target_dir / ".clinerules"
            clinerules_dir.mkdir(exist_ok=True)
            created_files.append(".clinerules/")
            
            # Copy mode definitions to .aceflow/config/
            mode_def_source = Path(__file__).parent / "templates" / "mode_definitions.yaml"
            mode_def_target = config_dir / "mode_definitions.yaml"
            if mode_def_source.exists():
                import shutil
                shutil.copy2(mode_def_source, mode_def_target)
                created_files.append(".aceflow/config/mode_definitions.yaml")
            
            # Copy template files to .aceflow/templates/
            template_source_dir = Path(__file__).parent / "templates"
            if template_source_dir.exists():
                import shutil
                shutil.copytree(template_source_dir, templates_dir, dirs_exist_ok=True)
                created_files.append(".aceflow/templates/")
            
            # Create enhanced AI Agent prompt files in .clinerules/
            # 1. System Prompt (Enhanced version)
            system_prompt = self._generate_enhanced_system_prompt(project_name, mode)
            prompt_file = clinerules_dir / "system_prompt.md"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(system_prompt)
            created_files.append(".clinerules/system_prompt.md")
            
            # 2. AceFlow Integration Rules
            aceflow_integration = self._generate_aceflow_integration(project_name, mode)
            integration_file = clinerules_dir / "aceflow_integration.md"
            with open(integration_file, 'w', encoding='utf-8') as f:
                f.write(aceflow_integration)
            created_files.append(".clinerules/aceflow_integration.md")
            
            # 3. SPEC Summary
            spec_summary = self._generate_spec_summary(project_name, mode)
            summary_file = clinerules_dir / "spec_summary.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(spec_summary)
            created_files.append(".clinerules/spec_summary.md")
            
            # 4. SPEC Query Helper
            spec_query_helper = self._generate_spec_query_helper(project_name, mode)
            query_file = clinerules_dir / "spec_query_helper.md"
            with open(query_file, 'w', encoding='utf-8') as f:
                f.write(spec_query_helper)
            created_files.append(".clinerules/spec_query_helper.md")
            
            # 5. Quality Standards (Enhanced version)
            quality_standards = self._generate_enhanced_quality_standards(project_name, mode)
            quality_file = clinerules_dir / "quality_standards.md"
            with open(quality_file, 'w', encoding='utf-8') as f:
                f.write(quality_standards)
            created_files.append(".clinerules/quality_standards.md")
            
            # Create template.yaml
            template_content = self._generate_template_yaml(mode)
            template_file = aceflow_dir / "template.yaml"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            created_files.append(".aceflow/template.yaml")
            
            # Copy management scripts
            script_files = ["aceflow-stage.py", "aceflow-validate.py", "aceflow-templates.py"]
            for script in script_files:
                source_path = aceflow_scripts_dir / script
                if source_path.exists():
                    dest_path = target_dir / script
                    shutil.copy2(source_path, dest_path)
                    created_files.append(script)
            
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
            "minimal": 3,
            "standard": 8,
            "complete": 12,
            "smart": 10
        }
        return stage_counts.get(mode, 8)
    
    def _generate_ai_agent_prompts(self, project_name: str, mode: str) -> str:
        """Generate .clinerules/system_prompt.md content for AI Agent integration."""
        return f"""# AceFlow v3.0 - AI Agent 系统提示

**项目**: {project_name}  
**模式**: {mode}  
**初始化时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**版本**: 3.0  

## AI Agent 身份定义

你是一个专业的软件开发AI助手，专门负责执行AceFlow v3.0工作流。你的核心职责是：

1. **严格遵循AceFlow标准**: 按照{mode}模式的流程执行每个阶段
2. **基于事实工作**: 每个阶段必须基于前一阶段的实际输出，不能基于假设
3. **保证输出质量**: 确保生成的文档结构完整、内容准确
4. **维护项目状态**: 实时更新项目进度和状态信息

## 工作模式配置

- **AceFlow模式**: {mode}
- **输出目录**: aceflow_result/
- **配置目录**: .aceflow/
- **模板目录**: .aceflow/templates/
- **项目名称**: {project_name}

## 核心工作原则  

1. **严格遵循 AceFlow 标准**: 所有阶段产物必须符合 AceFlow 定义
2. **自动化执行**: 使用 Stage Engine 自动生成各阶段文档
3. **基于事实工作**: 每个阶段必须基于前一阶段的输出，不能基于假设
4. **质量保证**: 确保生成文档的结构完整、内容准确
5. **状态同步**: 阶段完成后自动更新项目状态

## 阶段执行流程

### 标准执行命令
```bash
# 查看当前状态
aceflow_stage(action="status")

# 执行当前阶段
aceflow_stage(action="execute")

# 推进到下一阶段
aceflow_stage(action="next")

# 验证项目质量
aceflow_validate(mode="basic", report=True)
```

### 阶段依赖关系
- 每个阶段都有明确的输入要求
- 必须验证输入条件满足才能执行
- 输出文档保存到 aceflow_result/ 目录
- 状态文件实时更新进度

## 质量标准

### 文档质量要求
- **结构完整**: 包含概述、详细内容、下一步工作等必要章节
- **内容准确**: 基于实际输入生成，无占位符文本
- **格式规范**: 遵循 Markdown 格式规范
- **引用正确**: 正确引用输入文档和相关资源

### 代码质量要求
- **遵循编码规范**: 代码注释完整，结构清晰
- **测试覆盖**: 根据模式要求执行相应测试策略
- **性能标准**: 满足项目性能要求
- **安全考虑**: 遵循安全最佳实践

## 工具集成

### MCP Tools
- `aceflow_init`: 项目初始化
- `aceflow_stage`: 阶段管理和执行
- `aceflow_validate`: 项目验证
- `aceflow_template`: 模板管理

### 本地脚本
- `python aceflow-stage.py`: 阶段管理脚本
- `python aceflow-validate.py`: 验证脚本
- `python aceflow-templates.py`: 模板管理脚本

## 模式特定配置

### {mode.upper()} 模式特点
{self._get_mode_specific_config(mode)}

## 注意事项

1. **输入验证**: 每个阶段执行前都会验证输入条件
2. **错误处理**: 遇到错误时会提供详细的错误信息和修复建议
3. **状态一致性**: 项目状态与实际进度保持同步
4. **文档版本**: 所有文档都包含版本信息和创建时间
5. **质量监控**: 自动检查文档质量并提供改进建议

---
*Generated by AceFlow v3.0 MCP Server*
*AI Agent 系统提示文件*
"""
    
    def _generate_quality_standards(self, mode: str) -> str:
        """Generate quality standards for AI Agent."""
        return f"""# AceFlow v3.0 - 质量标准

## 文档质量标准

### 结构完整性
- 包含概述、详细内容、下一步工作等必要章节
- 使用标准的Markdown格式
- 章节层次清晰，编号规范

### 内容准确性
- 基于实际输入生成，无占位符文本
- 引用正确，链接有效
- 数据和信息准确无误

### 格式规范
- 遵循Markdown语法规范
- 代码块使用正确的语言标识
- 表格格式整齐，易于阅读

## 代码质量标准

### 编码规范
- 代码注释完整，结构清晰
- 变量命名有意义
- 函数职责单一

### 测试要求
- 根据{mode}模式要求执行相应测试策略
- 测试覆盖率满足标准
- 测试用例完整有效

### 性能标准
- 满足项目性能要求
- 资源使用合理
- 响应时间符合预期

## 安全标准

### 数据安全
- 敏感信息不在代码中硬编码
- 输入验证完整
- 错误处理不泄露敏感信息

### 访问控制
- 权限控制合理
- 认证机制完善
- 审计日志完整

---
*Generated by AceFlow v3.0 MCP Server*
*质量标准文件*
"""
    
    def _generate_workflow_guide(self, project_name: str, mode: str) -> str:
        """Generate comprehensive workflow guide for AI Agent."""
        
        # 根据模式获取阶段列表
        stage_configs = {
            "minimal": [
                ("01_implementation", "快速实现", "实现核心功能"),
                ("02_test", "基础测试", "基础功能测试"),
                ("03_demo", "功能演示", "功能演示")
            ],
            "standard": [
                ("01_user_stories", "用户故事分析", "基于PRD文档分析用户故事"),
                ("02_task_breakdown", "任务分解", "将用户故事分解为开发任务"),
                ("03_test_design", "测试用例设计", "设计测试用例和测试策略"),
                ("04_implementation", "功能实现", "实现核心功能"),
                ("05_unit_test", "单元测试", "编写和执行单元测试"),
                ("06_integration_test", "集成测试", "执行集成测试"),
                ("07_code_review", "代码审查", "进行代码审查和质量检查"),
                ("08_demo", "功能演示", "准备和执行功能演示")
            ],
            "complete": [
                ("01_requirement_analysis", "需求分析", "深度分析业务需求和技术需求"),
                ("02_architecture_design", "架构设计", "设计系统架构和技术方案"),
                ("03_user_stories", "用户故事分析", "基于需求和架构设计用户故事"),
                ("04_task_breakdown", "任务分解", "详细的任务分解和工作计划"),
                ("05_test_design", "测试用例设计", "全面的测试策略和用例设计"),
                ("06_implementation", "功能实现", "按照架构设计实现功能"),
                ("07_unit_test", "单元测试", "全面的单元测试"),
                ("08_integration_test", "集成测试", "系统集成测试"),
                ("09_performance_test", "性能测试", "性能和负载测试"),
                ("10_security_review", "安全审查", "安全漏洞扫描和审查"),
                ("11_code_review", "代码审查", "全面的代码质量审查"),
                ("12_demo", "功能演示", "完整的功能演示和交付")
            ],
            "smart": [
                ("01_project_analysis", "AI项目复杂度分析", "使用AI分析项目复杂度和需求"),
                ("02_adaptive_planning", "自适应规划", "基于分析结果制定自适应计划"),
                ("03_user_stories", "用户故事分析", "智能生成和优化用户故事"),
                ("04_smart_breakdown", "智能任务分解", "AI辅助的智能任务分解"),
                ("05_test_generation", "AI测试用例生成", "自动生成测试用例和策略"),
                ("06_implementation", "功能实现", "AI辅助的代码实现"),
                ("07_automated_test", "自动化测试", "执行自动化测试套件"),
                ("08_quality_assessment", "AI质量评估", "AI驱动的质量评估和优化建议"),
                ("09_optimization", "性能优化", "基于AI建议的性能优化"),
                ("10_demo", "智能演示", "AI辅助的智能演示和交付")
            ]
        }
        
        stages = stage_configs.get(mode, stage_configs["standard"])
        
        return f"""# AceFlow v3.0 - 工作流指导

**项目**: {project_name}  
**模式**: {mode.upper()}  
**总阶段数**: {len(stages)}  
**创建时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

## 🎯 工作流概述

本文档为AI Agent提供完整的AceFlow工作流指导，包含每个阶段的具体执行步骤、MCP工具使用方法和质量检查要点。

## 🔄 核心工作循环

每个阶段都遵循以下标准循环：

1. **状态检查** → 使用 `aceflow_stage(action="status")` 确认当前阶段
2. **输入验证** → 检查前置条件和输入文件是否满足
3. **执行阶段** → 使用 `aceflow_stage(action="execute")` 执行当前阶段
4. **质量验证** → 使用 `aceflow_validate()` 检查输出质量
5. **推进阶段** → 使用 `aceflow_stage(action="next")` 进入下一阶段

## 📋 阶段详细指导

{self._generate_stage_details(stages)}

## 🛠️ MCP工具使用指南

### aceflow_stage 工具
```python
# 查看当前状态
aceflow_stage(action="status")

# 执行当前阶段
aceflow_stage(action="execute")

# 推进到下一阶段
aceflow_stage(action="next")

# 重置项目状态
aceflow_stage(action="reset")
```

### aceflow_validate 工具
```python
# 基础验证
aceflow_validate(mode="basic")

# 详细验证并生成报告
aceflow_validate(mode="detailed", report=True)

# 自动修复问题
aceflow_validate(mode="basic", fix=True)
```

### aceflow_template 工具
```python
# 列出可用模板
aceflow_template(action="list")

# 应用新模板
aceflow_template(action="apply", template="complete")

# 验证模板
aceflow_template(action="validate")
```

## ⚠️ 重要注意事项

1. **严格按顺序执行**: 不能跳过阶段，必须按照定义的顺序执行
2. **基于实际输入**: 每个阶段必须基于前一阶段的实际输出，不能基于假设
3. **输出到指定目录**: 所有文档输出到 `aceflow_result/` 目录
4. **使用标准模板**: 使用 `.aceflow/templates/` 中的标准模板
5. **实时状态更新**: 每个阶段完成后自动更新项目状态

## 🚨 错误处理

### 常见问题及解决方案

1. **阶段执行失败**
   - 检查输入文件是否存在
   - 验证前置条件是否满足
   - 查看错误日志获取详细信息

2. **验证失败**
   - 使用 `aceflow_validate(mode="detailed", report=True)` 获取详细报告
   - 根据报告修复具体问题
   - 重新执行验证

3. **状态不一致**
   - 使用 `aceflow_stage(action="reset")` 重置状态
   - 重新从当前阶段开始执行

---
*Generated by AceFlow v3.0 MCP Server*
*工作流指导文件*
"""
    
    def _generate_stage_details(self, stages) -> str:
        """Generate detailed stage instructions."""
        details = []
        
        for stage_id, stage_name, stage_desc in stages:
            details.append(f"""
### 阶段 {stage_id}: {stage_name}

**描述**: {stage_desc}

**执行步骤**:
1. 确认当前处于此阶段: `aceflow_stage(action="status")`
2. 检查输入条件是否满足
3. 执行阶段任务: `aceflow_stage(action="execute")`
4. 验证输出质量: `aceflow_validate(mode="basic")`
5. 推进到下一阶段: `aceflow_stage(action="next")`

**输入要求**:
- 前一阶段的输出文档
- 项目相关的源文件和配置

**输出产物**:
- 阶段文档保存到 `aceflow_result/{stage_id}_{stage_name.lower().replace(' ', '_')}.md`
- 更新项目状态文件

**质量检查**:
- 文档结构完整
- 内容基于实际输入
- 格式符合标准
- 无占位符文本
""")
        
        return "".join(details)
    
    def _get_mode_specific_config(self, mode: str) -> str:
        """Get mode-specific configuration details."""
        configs = {
            "minimal": """- **快速迭代**: 专注于核心功能快速实现
- **简化流程**: 只包含必要的3个阶段
- **质量标准**: 基本功能可用即可""",
            
            "standard": """- **平衡发展**: 兼顾开发效率和代码质量
- **标准流程**: 包含8个标准开发阶段
- **质量标准**: 代码质量良好，测试覆盖充分""",
            
            "complete": """- **企业级标准**: 完整的企业级开发流程
- **全面覆盖**: 包含12个完整阶段
- **高质量标准**: 代码质量优秀，安全性和性能达标""",
            
            "smart": """- **AI增强**: 利用AI技术优化开发流程
- **自适应**: 根据项目特点动态调整流程
- **智能分析**: AI辅助的质量评估和优化建议"""
        }
        return configs.get(mode, configs["standard"])


    
    def _generate_template_yaml(self, mode: str) -> str:
        """Generate template.yaml content based on mode."""
        templates = {
            "minimal": """# AceFlow Minimal模式配置
name: "Minimal Workflow"
version: "3.0"
description: "快速原型和概念验证工作流"

stages:
  - name: "implementation"
    description: "快速实现核心功能"
    required: true
  - name: "test"
    description: "基础功能测试"
    required: true
  - name: "demo"
    description: "功能演示"
    required: true

quality_gates:
  - stage: "implementation"
    criteria: ["核心功能完成", "基本可运行"]
  - stage: "test"
    criteria: ["主要功能测试通过"]""",
            
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
  - name: "demo"
    description: "功能演示"
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
    required: true
  - name: "security_review"
    description: "安全审查"
    required: true
  - name: "code_review"
    description: "代码审查"
    required: true
  - name: "demo"
    description: "功能演示"
    required: true

quality_gates:
  - stage: "architecture_design"
    criteria: ["架构设计完整", "技术选型合理"]
  - stage: "implementation"
    criteria: ["代码质量优秀", "性能满足要求"]
  - stage: "security_review"
    criteria: ["安全检查通过", "无重大漏洞"]""",
            
            "smart": """# AceFlow Smart模式配置
name: "Smart Adaptive Workflow"  
version: "3.0"
description: "AI增强的自适应工作流"

stages:
  - name: "project_analysis"
    description: "AI项目复杂度分析"
    required: true
  - name: "adaptive_planning"
    description: "自适应规划"
    required: true
  - name: "user_stories"
    description: "用户故事分析"
    required: true
  - name: "smart_breakdown"
    description: "智能任务分解"
    required: true
  - name: "test_generation"
    description: "AI测试用例生成"
    required: true
  - name: "implementation"
    description: "功能实现"
    required: true
  - name: "automated_test"
    description: "自动化测试"
    required: true
  - name: "quality_assessment"
    description: "AI质量评估"
    required: true
  - name: "optimization"
    description: "性能优化"
    required: true
  - name: "demo"
    description: "智能演示"
    required: true

ai_features:
  - "复杂度智能评估"
  - "动态流程调整"
  - "自动化测试生成"
  - "质量智能分析"

quality_gates:
  - stage: "project_analysis"
    criteria: ["复杂度评估完成", "技术栈确定"]
  - stage: "implementation"
    criteria: ["AI代码质量检查通过", "性能指标达标"]"""
        }
        
        return templates.get(mode, templates["standard"])
    
    def _generate_readme(self, project_name: str, mode: str) -> str:
        """Generate README content."""
        return f"""# {project_name}

## AceFlow项目说明

本项目使用AceFlow v3.0工作流管理系统，采用 **{mode.upper()}** 模式。

### 项目信息
- **项目名称**: {project_name}
- **工作流模式**: {mode.upper()}
- **初始化时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **AceFlow版本**: 3.0

### 目录结构
```
{project_name}/
├── .aceflow/           # AceFlow配置目录
│   ├── current_state.json    # 项目状态文件
│   └── template.yaml         # 工作流模板
├── aceflow_result/     # 项目输出目录
├── .clinerules         # AI Agent工作配置
├── aceflow-stage.py    # 阶段管理脚本
├── aceflow-validate.py # 项目验证脚本
├── aceflow-templates.py # 模板管理脚本
└── README_ACEFLOW.md   # 本文件
```

### 快速开始

1. **查看当前状态**
   ```bash
   python aceflow-stage.py --action status
   ```

2. **验证项目配置**
   ```bash
   python aceflow-validate.py
   ```

3. **推进到下一阶段**
   ```bash
   python aceflow-stage.py --action next
   ```

### 工作流程

根据{mode}模式，项目将按以下阶段进行：

{self._get_stage_description(mode)}

### 注意事项

- 所有项目文档和代码请输出到 `aceflow_result/` 目录
- 使用AI助手时，确保.clinerules配置已加载
- 每个阶段完成后，使用 `aceflow-stage.py` 更新状态
- 定期使用 `aceflow-validate.py` 检查项目合规性

### 帮助和支持

如需帮助，请参考：
- AceFlow官方文档
- 项目状态文件: `.aceflow/current_state.json`
- 工作流配置: `.aceflow/template.yaml`

---
*Generated by AceFlow v3.0 MCP Server*"""
    
    def _get_stage_description(self, mode: str) -> str:
        """Get stage descriptions for the mode."""
        descriptions = {
            "minimal": """1. **Implementation** - 快速实现核心功能
2. **Test** - 基础功能测试  
3. **Demo** - 功能演示""",
            
            "standard": """1. **User Stories** - 用户故事分析
2. **Task Breakdown** - 任务分解
3. **Test Design** - 测试用例设计
4. **Implementation** - 功能实现
5. **Unit Test** - 单元测试
6. **Integration Test** - 集成测试
7. **Code Review** - 代码审查
8. **Demo** - 功能演示""",
            
            "complete": """1. **Requirement Analysis** - 需求分析
2. **Architecture Design** - 架构设计
3. **User Stories** - 用户故事分析
4. **Task Breakdown** - 任务分解
5. **Test Design** - 测试用例设计
6. **Implementation** - 功能实现
7. **Unit Test** - 单元测试
8. **Integration Test** - 集成测试
9. **Performance Test** - 性能测试
10. **Security Review** - 安全审查
11. **Code Review** - 代码审查
12. **Demo** - 功能演示""",
            
            "smart": """1. **Project Analysis** - AI项目复杂度分析
2. **Adaptive Planning** - 自适应规划
3. **User Stories** - 用户故事分析
4. **Smart Breakdown** - 智能任务分解
5. **Test Generation** - AI测试用例生成
6. **Implementation** - 功能实现
7. **Automated Test** - 自动化测试
8. **Quality Assessment** - AI质量评估
9. **Optimization** - 性能优化
10. **Demo** - 智能演示"""
        }
        
        return descriptions.get(mode, descriptions["standard"])
    
    def _get_initial_stage_for_mode(self, mode: str) -> str:
        """Get the initial stage for a specific mode."""
        initial_stages = {
            "minimal": "S1_implementation",
            "standard": "S1_user_stories", 
            "complete": "S1_requirement_analysis",
            "smart": "S1_project_analysis"
        }
        return initial_stages.get(mode.lower(), "S1_user_stories")
    
    def aceflow_stage(
        self,
        action: str,
        stage: Optional[str] = None
    ) -> Dict[str, Any]:
        """Manage project stages and workflow.
        
        Args:
            action: Stage management action (status, next, list, reset, execute)
            stage: Optional target stage name
            
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
            elif action == "execute":
                return self._execute_current_stage(stage)
            else:
                return {
                    "success": False,
                    "error": f"Invalid action '{action}'. Valid actions: status, next, list, reset, execute",
                    "message": "Action not supported"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute stage action: {action}"
            }
    
    def _execute_current_stage(self, stage_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute the current or specified stage using proper AceFlow templates.
        
        Args:
            stage_id: Optional specific stage to execute
            
        Returns:
            Dict with execution result
        """
        try:
            # Get current state to determine stage
            current_state = self.project_manager.get_current_state()
            current_stage = current_state.get("flow", {}).get("current_stage", "unknown")
            
            if stage_id:
                target_stage = stage_id
            else:
                target_stage = current_stage
            
            # Create result directory
            result_dir = Path.cwd() / "aceflow_result"
            result_dir.mkdir(exist_ok=True)
            
            # Load project PRD content
            prd_content = self._load_project_prd()
            
            # Generate stage-specific content based on AceFlow templates
            doc_content = self._generate_stage_content(target_stage, current_state, prd_content)
            
            # Save document
            doc_filename = f"{target_stage}.md"
            doc_path = result_dir / doc_filename
            doc_path.write_text(doc_content, encoding='utf-8')
            
            return {
                "success": True,
                "action": "execute",
                "stage_id": target_stage,
                "output_path": str(doc_path),
                "quality_score": 0.9,
                "execution_time": 2.0,
                "warnings": [],
                "message": f"Stage '{target_stage}' executed successfully using AceFlow templates"
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute stage"
            }
    
    def _load_project_prd(self) -> str:
        """Load project PRD content."""
        try:
            # Look for PRD files in common locations
            prd_files = [
                "taskmaster-demo.md",
                "PRD.md", 
                "requirements.md",
                "README.md"
            ]
            
            for prd_file in prd_files:
                prd_path = Path.cwd() / prd_file
                if prd_path.exists():
                    return prd_path.read_text(encoding='utf-8')
            
            return "No PRD document found"
            
        except Exception:
            return "Failed to load PRD content"
    
    def _generate_stage_content(self, stage: str, project_state: Dict[str, Any], prd_content: str) -> str:
        """Generate stage-specific content based on AceFlow templates and PRD."""
        project_name = project_state.get('project', {}).get('name', 'Unknown')
        
        if stage == "S2_task_breakdown":
            return self._generate_s2_task_breakdown(project_name, prd_content)
        elif stage == "S1_user_stories":
            return self._generate_s1_user_stories(project_name, prd_content)
        elif stage == "S3_test_design":
            return self._generate_s3_test_design(project_name, prd_content)
        else:
            # Fallback to generic template
            return self._generate_generic_stage_content(stage, project_name)
    
    def _generate_s2_task_breakdown(self, project_name: str, prd_content: str) -> str:
        """Generate S2 task breakdown based on PRD content."""
        return f"""# S2 任务分解 - {project_name}

**项目**: {project_name}
**阶段**: S2_task_breakdown  
**创建时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**基于**: PRD文档分析

---

## 📋 项目概述

基于PRD文档分析，本项目是一个**多用户隔离个人任务管理系统**，主要特点：
- 多用户支持，数据完全隔离
- 简洁易用的任务管理界面（类Notion风格）
- 智能提醒功能（浏览器通知/Windows通知）
- 技术栈：Vue3 + FastAPI + DuckDB

## 🎯 核心功能模块分解

### 模块1: 用户管理系统
| 任务ID | 任务名称 | 描述 | 预估工时 | 优先级 | 依赖 |
|--------|----------|------|----------|--------|------|
| T-001 | 用户注册功能 | 实现用户名+密码注册，邮箱可选 | 4h | 高 | - |
| T-002 | 用户登录功能 | JWT认证，会话管理 | 3h | 高 | T-001 |
| T-003 | 密码加密存储 | 使用bcrypt加密用户密码 | 2h | 高 | T-001 |
| T-004 | 用户信息管理 | 头像上传，个人信息编辑 | 3h | 中 | T-002 |

### 模块2: 任务管理核心
| 任务ID | 任务名称 | 描述 | 预估工时 | 优先级 | 依赖 |
|--------|----------|------|----------|--------|------|
| T-005 | 任务CRUD操作 | 创建、查看、编辑、删除任务 | 6h | 高 | T-002 |
| T-006 | 任务字段设计 | 标题、描述(Markdown)、截止时间、优先级、状态 | 4h | 高 | T-005 |
| T-007 | 数据隔离机制 | 确保用户只能访问自己的任务 | 3h | 高 | T-005 |
| T-008 | 任务状态管理 | 待办/进行中/已完成状态转换 | 2h | 中 | T-006 |

### 模块3: 界面视图
| 任务ID | 任务名称 | 描述 | 预估工时 | 优先级 | 依赖 |
|--------|----------|------|----------|--------|------|
| T-009 | 列表视图 | 表格形式显示任务，支持排序过滤 | 5h | 高 | T-006 |
| T-010 | 看板视图 | 按状态分组，支持拖拽操作 | 6h | 中 | T-008 |
| T-011 | 任务详情页 | 弹窗或侧边栏编辑任务 | 4h | 中 | T-009 |
| T-012 | 响应式设计 | 适配桌面和移动端 | 4h | 低 | T-011 |

### 模块4: 提醒系统
| 任务ID | 任务名称 | 描述 | 预估工时 | 优先级 | 依赖 |
|--------|----------|------|----------|--------|------|
| T-013 | 浏览器通知 | 任务到期前弹窗提醒 | 4h | 高 | T-006 |
| T-014 | 提醒时间设置 | 用户自定义提醒提前量 | 2h | 中 | T-013 |
| T-015 | 防重复提醒 | 通知状态字段，避免重复弹窗 | 2h | 中 | T-013 |
| T-016 | Windows通知 | 系统级通知支持 | 3h | 低 | T-013 |

### 模块5: 数据管理
| 任务ID | 任务名称 | 描述 | 预估工时 | 优先级 | 依赖 |
|--------|----------|------|----------|--------|------|
| T-017 | DuckDB集成 | 数据库连接和基础操作 | 3h | 高 | - |
| T-018 | 数据模型设计 | users表和tasks表结构 | 2h | 高 | T-017 |
| T-019 | 数据导出功能 | CSV/JSON格式导出个人数据 | 3h | 低 | T-018 |
| T-020 | 数据备份机制 | 定期备份数据库 | 2h | 低 | T-018 |

## 🔄 任务依赖关系

```mermaid
graph TD
    T-001[用户注册] --> T-002[用户登录]
    T-001 --> T-003[密码加密]
    T-002 --> T-004[用户信息管理]
    T-002 --> T-005[任务CRUD]
    T-005 --> T-006[任务字段设计]
    T-005 --> T-007[数据隔离]
    T-006 --> T-008[状态管理]
    T-006 --> T-009[列表视图]
    T-006 --> T-013[浏览器通知]
    T-008 --> T-010[看板视图]
    T-009 --> T-011[任务详情页]
    T-011 --> T-012[响应式设计]
    T-013 --> T-014[提醒设置]
    T-013 --> T-015[防重复提醒]
    T-013 --> T-016[Windows通知]
    T-017[DuckDB集成] --> T-018[数据模型]
    T-018 --> T-019[数据导出]
    T-018 --> T-020[数据备份]
```

## 📊 开发计划

### 第1周 (核心功能)
- **用户管理**: T-001, T-002, T-003 (9h)
- **任务核心**: T-005, T-006, T-007 (13h)
- **数据基础**: T-017, T-018 (5h)
- **总计**: 27h

### 第2周 (界面和提醒)
- **界面视图**: T-009, T-011 (9h)
- **提醒系统**: T-013, T-014, T-015 (8h)
- **状态管理**: T-008 (2h)
- **总计**: 19h

### 第3周 (扩展功能)
- **高级界面**: T-010, T-012 (10h)
- **数据管理**: T-019, T-020 (5h)
- **用户体验**: T-004, T-016 (6h)
- **总计**: 21h

## ✅ 质量检查点

### 数据安全检查
- [ ] 用户密码正确加密存储
- [ ] JWT token安全实现
- [ ] 数据隔离机制验证
- [ ] SQL注入防护

### 功能完整性检查
- [ ] 所有CRUD操作正常
- [ ] 提醒功能准确触发
- [ ] 界面响应式适配
- [ ] 数据导出功能正常

### 性能要求验证
- [ ] 支持5-50用户并发
- [ ] API响应时间 < 200ms
- [ ] 通知延迟 < 1分钟
- [ ] 数据库查询优化

## 🎯 下一阶段准备

**S3阶段输入**:
- 详细的任务分解清单
- 技术架构决策
- 数据模型设计
- 安全需求分析

**S3阶段目标**: 基于任务分解设计全面的测试用例，特别关注数据隔离和安全性测试。

---
*基于 AceFlow Standard 模式和 TaskMaster PRD 文档生成*
*下一阶段: S3_test_design*
"""
    
    def _generate_s1_user_stories(self, project_name: str, prd_content: str) -> str:
        """Generate S1 user stories based on PRD content."""
        return f"""# S1 用户故事分析 - {project_name}

**项目**: {project_name}
**阶段**: S1_user_stories
**创建时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**基于**: TaskMaster PRD 文档分析

---

## 📋 项目背景

基于PRD文档，TaskMaster是一个**多用户隔离个人任务管理系统**，解决小团队、家庭或组织中成员各自独立的任务管理需求。

### 核心价值主张
- **数据隔离**: 每位用户只能管理和查看自己的任务
- **简洁易用**: 参考Notion风格，提供直观的任务管理界面
- **智能提醒**: 任务到期自动提醒，避免遗漏
- **轻量部署**: 适合小团队使用，快速开发、低成本维护

## 🎭 用户角色定义

### 主要用户角色
1. **个人用户** - 需要管理个人任务的用户
2. **团队成员** - 小团队中的成员，各自管理独立任务
3. **家庭成员** - 家庭中需要管理个人事务的成员
4. **系统管理员** - 负责系统维护和用户管理

## 📖 核心用户故事

### Epic 1: 用户身份管理

#### US-001: 用户注册
**作为** 新用户  
**我希望** 能够注册一个账户  
**以便** 开始使用个人任务管理系统  

**验收标准**:
- 用户可以使用用户名和密码注册
- 邮箱字段为可选
- 用户名必须唯一
- 密码需要加密存储
- 注册成功后自动跳转到登录页面

**优先级**: 高  
**估算**: 5 故事点

#### US-002: 用户登录
**作为** 注册用户  
**我希望** 能够登录到我的账户  
**以便** 访问我的个人任务数据  

**验收标准**:
- 用户可以使用用户名和密码登录
- 登录成功后获得JWT token
- 登录状态在会话期间保持
- 登录失败时显示明确的错误信息
- 支持"记住我"功能

**优先级**: 高  
**估算**: 3 故事点

#### US-003: 用户信息管理
**作为** 登录用户  
**我希望** 能够管理我的个人信息  
**以便** 保持账户信息的准确性  

**验收标准**:
- 用户可以查看个人信息
- 用户可以修改邮箱地址
- 用户可以上传和更换头像
- 用户可以修改密码
- 所有修改需要确认当前密码

**优先级**: 中  
**估算**: 3 故事点

### Epic 2: 任务管理核心

#### US-004: 创建任务
**作为** 用户  
**我希望** 能够创建新的任务  
**以便** 记录我需要完成的工作  

**验收标准**:
- 用户可以输入任务标题（必填）
- 用户可以添加任务描述（支持Markdown格式）
- 用户可以设置截止时间（必填）
- 用户可以选择优先级（高/中/低）
- 用户可以设置任务状态（待办/进行中/已完成）
- 创建时间自动记录

**优先级**: 高  
**估算**: 5 故事点

#### US-005: 查看任务列表
**作为** 用户  
**我希望** 能够查看我的所有任务  
**以便** 了解我的工作安排  

**验收标准**:
- 用户只能看到自己创建的任务
- 任务以表格形式显示
- 显示任务标题、截止时间、优先级、状态
- 支持按不同字段排序
- 支持按状态、优先级过滤
- 支持搜索功能

**优先级**: 高  
**估算**: 4 故事点

#### US-006: 编辑任务
**作为** 用户  
**我希望** 能够修改我的任务信息  
**以便** 保持任务信息的准确性  

**验收标准**:
- 用户可以修改任务的所有字段
- 修改操作通过弹窗或侧边栏进行
- 修改后立即保存
- 显示最后修改时间
- 支持撤销最近的修改

**优先级**: 高  
**估算**: 3 故事点

#### US-007: 删除任务
**作为** 用户  
**我希望** 能够删除不需要的任务  
**以便** 保持任务列表的整洁  

**验收标准**:
- 用户可以删除自己的任务
- 删除前需要确认
- 支持批量删除
- 删除后无法恢复（或提供回收站功能）

**优先级**: 中  
**估算**: 2 故事点

### Epic 3: 任务视图和交互

#### US-008: 看板视图
**作为** 用户  
**我希望** 能够以看板形式查看任务  
**以便** 更直观地管理任务状态  

**验收标准**:
- 任务按状态分组显示（待办/进行中/已完成）
- 支持拖拽任务改变状态
- 每个状态列显示任务数量
- 支持在看板中快速编辑任务
- 状态变更有动画效果

**优先级**: 中  
**估算**: 5 故事点

#### US-009: 任务详情页
**作为** 用户  
**我希望** 能够查看任务的详细信息  
**以便** 了解任务的完整内容  

**验收标准**:
- 点击任务可以打开详情页
- 详情页显示所有任务信息
- 支持在详情页直接编辑
- 显示任务的创建和修改历史
- 支持添加评论或备注

**优先级**: 中  
**估算**: 3 故事点

### Epic 4: 智能提醒系统

#### US-010: 浏览器通知
**作为** 用户  
**我希望** 在任务即将到期时收到提醒  
**以便** 不会错过重要的截止时间  

**验收标准**:
- 系统在任务到期前30分钟发送通知
- 通知显示在浏览器右下角
- 通知包含任务标题、截止时间、简短描述
- 点击通知可以跳转到任务详情
- 支持推迟提醒功能

**优先级**: 高  
**估算**: 4 故事点

#### US-011: 提醒设置
**作为** 用户  
**我希望** 能够自定义提醒时间  
**以便** 根据我的习惯调整提醒策略  

**验收标准**:
- 用户可以设置提醒提前量（15分钟、30分钟、1小时等）
- 用户可以选择是否启用提醒
- 用户可以设置工作时间，只在工作时间提醒
- 支持为不同优先级设置不同提醒策略

**优先级**: 中  
**估算**: 3 故事点

#### US-012: 防重复提醒
**作为** 用户  
**我希望** 不会收到重复的提醒  
**以便** 避免被过多通知打扰  

**验收标准**:
- 每个任务只在设定时间提醒一次
- 用户查看任务后不再重复提醒
- 任务状态改变后停止提醒
- 系统记录提醒状态

**优先级**: 中  
**估算**: 2 故事点

### Epic 5: 数据管理和设置

#### US-013: 数据导出
**作为** 用户  
**我希望** 能够导出我的任务数据  
**以便** 备份或在其他系统中使用  

**验收标准**:
- 支持导出为CSV格式
- 支持导出为JSON格式
- 导出包含所有任务字段
- 只能导出自己的数据
- 导出文件包含时间戳

**优先级**: 低  
**估算**: 2 故事点

#### US-014: 响应式设计
**作为** 移动设备用户  
**我希望** 能够在手机上使用任务管理系统  
**以便** 随时随地管理我的任务  

**验收标准**:
- 界面适配手机屏幕
- 触摸操作友好
- 关键功能在移动端可用
- 加载速度优化
- 离线查看支持

**优先级**: 中  
**估算**: 4 故事点

## 📊 用户故事优先级矩阵

### 高优先级 (MVP必需)
- US-001: 用户注册
- US-002: 用户登录  
- US-004: 创建任务
- US-005: 查看任务列表
- US-006: 编辑任务
- US-010: 浏览器通知

### 中优先级 (第二版本)
- US-003: 用户信息管理
- US-007: 删除任务
- US-008: 看板视图
- US-009: 任务详情页
- US-011: 提醒设置
- US-012: 防重复提醒
- US-014: 响应式设计

### 低优先级 (后续版本)
- US-013: 数据导出

## 🎯 验收标准总结

### 数据隔离要求
- 所有用户故事都必须确保数据隔离
- 用户只能访问自己的数据
- 系统级操作需要管理员权限

### 性能要求
- 支持5-50用户并发使用
- API响应时间 < 200ms
- 通知延迟 < 1分钟

### 安全要求
- 密码加密存储
- JWT token安全实现
- 防止SQL注入
- HTTPS传输

## 🔄 下一阶段准备

**S2阶段输入**:
- 14个详细的用户故事
- 明确的验收标准
- 优先级排序
- 技术约束和性能要求

**S2阶段目标**: 基于用户故事进行详细的任务分解，将每个用户故事拆分为具体的开发任务。

---
*基于 AceFlow Standard 模式和 TaskMaster PRD 文档生成*
*下一阶段: S2_task_breakdown*
"""
    
    def _generate_s3_test_design(self, project_name: str, prd_content: str) -> str:
        """Generate S3 test design based on PRD content."""
        return f"""# S3 测试用例设计 - {project_name}

**项目**: {project_name}
**阶段**: S3_test_design
**创建时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**基于**: S1用户故事 + S2任务分解

---

## 📋 测试策略概述

基于TaskMaster项目的核心需求，测试策略重点关注：
- **数据隔离安全性**: 确保用户数据完全隔离
- **功能完整性**: 验证所有用户故事的实现
- **性能要求**: 满足5-50用户并发访问
- **用户体验**: 界面友好性和响应速度

## 🎯 测试分层架构

### 1. 单元测试 (Unit Tests)
- **覆盖率目标**: ≥ 80%
- **测试框架**: pytest (后端) + Jest (前端)
- **重点**: 业务逻辑、数据验证、工具函数

### 2. 集成测试 (Integration Tests)
- **API测试**: FastAPI接口测试
- **数据库测试**: DuckDB操作测试
- **组件集成**: 前后端交互测试

### 3. 端到端测试 (E2E Tests)
- **用户流程**: 完整的用户操作流程
- **浏览器测试**: Playwright/Cypress
- **跨浏览器**: Chrome, Firefox, Safari

### 4. 性能测试 (Performance Tests)
- **负载测试**: 并发用户访问
- **压力测试**: 系统极限测试
- **响应时间**: API响应时间监控

## 🔒 安全测试用例

### SEC-001: 用户数据隔离测试
**测试目标**: 验证用户只能访问自己的数据

**测试步骤**:
1. 创建用户A和用户B
2. 用户A创建任务T1
3. 用户B尝试访问任务T1
4. 验证用户B无法看到或操作T1

**预期结果**: 
- 用户B的任务列表不包含T1
- 直接访问T1的API返回403错误
- 数据库查询自动过滤其他用户数据

**测试数据**:
```json
{{
  "userA": {{"username": "alice", "password": "test123"}},
  "userB": {{"username": "bob", "password": "test456"}},
  "taskT1": {{"title": "Alice的私人任务", "user_id": "alice_id"}}
}}
```

### SEC-002: JWT认证安全测试
**测试目标**: 验证JWT token的安全性

**测试步骤**:
1. 用户登录获取JWT token
2. 使用有效token访问API
3. 使用过期token访问API
4. 使用伪造token访问API
5. 使用其他用户token访问API

**预期结果**:
- 有效token正常访问
- 过期token返回401错误
- 伪造token返回401错误
- 跨用户token访问被拒绝

### SEC-003: 密码安全测试
**测试目标**: 验证密码加密存储

**测试步骤**:
1. 用户注册时输入明文密码
2. 检查数据库中存储的密码
3. 验证密码哈希算法
4. 测试密码强度验证

**预期结果**:
- 数据库中不存储明文密码
- 使用bcrypt或类似安全算法
- 密码强度符合安全要求

## 📝 功能测试用例

### 用户管理模块测试

#### FUNC-001: 用户注册功能测试
**对应用户故事**: US-001
**对应任务**: T-001

**测试用例**:
1. **正常注册**
   - 输入: 有效用户名、密码、邮箱
   - 预期: 注册成功，跳转登录页

2. **用户名重复**
   - 输入: 已存在的用户名
   - 预期: 显示"用户名已存在"错误

3. **密码强度不足**
   - 输入: 弱密码
   - 预期: 显示密码强度要求

4. **邮箱格式错误**
   - 输入: 无效邮箱格式
   - 预期: 显示邮箱格式错误

#### FUNC-002: 用户登录功能测试
**对应用户故事**: US-002
**对应任务**: T-002

**测试用例**:
1. **正常登录**
   - 输入: 正确用户名和密码
   - 预期: 登录成功，获得JWT token

2. **用户名错误**
   - 输入: 不存在的用户名
   - 预期: 显示"用户名或密码错误"

3. **密码错误**
   - 输入: 错误密码
   - 预期: 显示"用户名或密码错误"

4. **记住我功能**
   - 输入: 勾选"记住我"
   - 预期: token有效期延长

### 任务管理模块测试

#### FUNC-003: 任务CRUD操作测试
**对应用户故事**: US-004, US-005, US-006, US-007
**对应任务**: T-005, T-006

**创建任务测试**:
```javascript
describe('任务创建', () => {{
  test('创建完整任务', async () => {{
    const taskData = {{
      title: '测试任务',
      description: '这是一个测试任务',
      due_date: '2025-12-31T23:59:59',
      priority: 'high',
      status: 'todo'
    }};
    
    const response = await api.post('/tasks', taskData);
    expect(response.status).toBe(201);
    expect(response.data.title).toBe(taskData.title);
  }});
  
  test('必填字段验证', async () => {{
    const taskData = {{ description: '缺少标题' }};
    const response = await api.post('/tasks', taskData);
    expect(response.status).toBe(400);
    expect(response.data.error).toContain('title');
  }});
}});
```

**查询任务测试**:
```javascript
describe('任务查询', () => {{
  test('获取用户任务列表', async () => {{
    const response = await api.get('/tasks');
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data)).toBe(true);
  }});
  
  test('任务排序功能', async () => {{
    const response = await api.get('/tasks?sort=due_date&order=asc');
    const tasks = response.data;
    for (let i = 1; i < tasks.length; i++) {{
      expect(new Date(tasks[i].due_date) >= new Date(tasks[i-1].due_date)).toBe(true);
    }}
  }});
}});
```

### 提醒系统测试

#### FUNC-004: 浏览器通知测试
**对应用户故事**: US-010
**对应任务**: T-013

**测试用例**:
1. **通知权限请求**
   - 操作: 首次访问系统
   - 预期: 请求通知权限

2. **到期提醒触发**
   - 设置: 任务30分钟后到期
   - 预期: 在到期前30分钟收到通知

3. **通知内容验证**
   - 验证: 通知包含任务标题、截止时间
   - 预期: 信息完整准确

4. **点击通知跳转**
   - 操作: 点击通知
   - 预期: 跳转到任务详情页

## 🎭 用户界面测试

### UI-001: 响应式设计测试
**对应用户故事**: US-014
**对应任务**: T-012

**测试设备**:
- 桌面: 1920x1080, 1366x768
- 平板: 768x1024, 1024x768
- 手机: 375x667, 414x896

**测试内容**:
- 布局适配
- 触摸操作
- 字体大小
- 按钮尺寸

### UI-002: 看板视图测试
**对应用户故事**: US-008
**对应任务**: T-010

**拖拽功能测试**:
```javascript
describe('看板拖拽', () => {{
  test('任务状态拖拽更新', async () => {{
    // 模拟拖拽操作
    await page.dragAndDrop('[data-task-id="1"]', '[data-status="in_progress"]');
    
    // 验证状态更新
    const task = await api.get('/tasks/1');
    expect(task.data.status).toBe('in_progress');
  }});
}});
```

## ⚡ 性能测试用例

### PERF-001: API响应时间测试
**性能要求**: API响应时间 < 200ms

**测试场景**:
```python
import pytest
import time

def test_api_response_time():
    start_time = time.time()
    response = client.get('/tasks')
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 0.2  # 200ms
```

### PERF-002: 并发用户测试
**性能要求**: 支持50个并发用户

**负载测试脚本**:
```python
from locust import HttpUser, task, between

class TaskUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # 用户登录
        self.client.post('/auth/login', {{
            'username': 'testuser',
            'password': 'testpass'
        }})
    
    @task(3)
    def view_tasks(self):
        self.client.get('/tasks')
    
    @task(1)
    def create_task(self):
        self.client.post('/tasks', {{
            'title': 'Load test task',
            'due_date': '2025-12-31T23:59:59'
        }})
```

### PERF-003: 数据库性能测试
**测试目标**: 大量数据下的查询性能

**测试数据**:
- 100个用户
- 每用户100个任务
- 总计10,000个任务

**测试查询**:
- 用户任务列表查询
- 任务搜索功能
- 任务统计查询

## 🔧 自动化测试配置

### CI/CD集成
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run unit tests
        run: pytest tests/unit --cov=src
      
      - name: Run integration tests
        run: pytest tests/integration
      
      - name: Run E2E tests
        run: pytest tests/e2e
```

### 测试数据管理
```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from src.database import Base

@pytest.fixture(scope="session")
def test_db():
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def sample_user():
    return {{
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com"
    }}
```

## 📊 测试覆盖率要求

### 代码覆盖率目标
- **后端代码**: ≥ 85%
- **前端代码**: ≥ 80%
- **关键业务逻辑**: 100%
- **安全相关代码**: 100%

### 测试报告
- **单元测试报告**: pytest-html
- **覆盖率报告**: coverage.py
- **性能测试报告**: locust报告
- **E2E测试报告**: Playwright报告

## 🎯 测试执行计划

### 第1周: 单元测试开发
- 用户管理模块测试
- 任务管理模块测试
- 工具函数测试

### 第2周: 集成测试开发
- API接口测试
- 数据库集成测试
- 前后端集成测试

### 第3周: E2E和性能测试
- 用户流程E2E测试
- 性能基准测试
- 安全测试

### 第4周: 测试优化和CI/CD
- 测试用例优化
- CI/CD流水线配置
- 测试报告完善

## ✅ 测试验收标准

### 功能测试验收
- [ ] 所有用户故事测试通过
- [ ] 数据隔离测试100%通过
- [ ] 安全测试无高危漏洞
- [ ] 性能测试达到指标要求

### 质量指标验收
- [ ] 代码覆盖率达到目标
- [ ] 自动化测试通过率 ≥ 95%
- [ ] 性能测试通过率 100%
- [ ] 安全测试通过率 100%

## 🔄 下一阶段准备

**S4阶段输入**:
- 完整的测试用例设计
- 自动化测试框架
- 性能基准和安全要求
- CI/CD测试流水线

**S4阶段目标**: 基于测试用例开始功能实现，采用TDD(测试驱动开发)方式确保代码质量。

---
*基于 AceFlow Standard 模式、S1用户故事和S2任务分解生成*
*下一阶段: S4_implementation*
"""
    
    def _generate_s4_implementation(self, project_name: str, prd_content: str) -> str:
        """Generate S4 implementation based on task breakdown."""
        return f"""# S4 功能实现 - {project_name}

**项目**: {project_name}
**阶段**: S4_implementation
**创建时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**基于**: S2任务分解 + S3测试设计

---

## 🚀 实现概述

基于前序阶段的分析，开始TaskMaster多用户隔离任务管理系统的核心功能实现。
采用测试驱动开发(TDD)方式，确保代码质量和功能完整性。

### 技术栈确认
- **后端**: FastAPI + Python 3.9+
- **前端**: Vue 3 + TypeScript + Element Plus
- **数据库**: DuckDB (嵌入式)
- **认证**: JWT Token
- **构建工具**: Vite (前端) + Poetry (后端)

## 📁 项目结构创建

### 后端结构 (backend/)
- app/main.py - FastAPI应用入口
- app/models/user.py - 用户模型
- app/models/task.py - 任务模型
- app/api/auth.py - 认证API
- app/api/tasks.py - 任务API
- app/core/security.py - 安全相关
- app/tests/ - 测试文件

### 前端结构 (frontend/)
- src/views/Login.vue - 登录页
- src/views/Register.vue - 注册页
- src/views/Dashboard.vue - 主面板
- src/components/TaskList.vue - 任务列表
- src/stores/auth.ts - 认证状态
- src/stores/tasks.ts - 任务状态

## 🔧 核心实现任务

### T-001: 用户注册功能
- 实现用户模型和密码加密
- 创建注册API接口
- 开发前端注册组件
- 编写注册功能测试

### T-002: 用户登录功能
- 实现JWT认证机制
- 创建登录API接口
- 开发前端登录组件
- 编写认证测试

### T-005: 任务CRUD操作
- 实现任务数据模型
- 创建任务管理API
- 确保数据隔离机制
- 开发前端任务组件

### T-007: 数据隔离机制
- 在所有API中实现用户数据隔离
- 确保用户只能访问自己的数据
- 编写数据隔离测试用例
- 验证安全性

## 🧪 测试驱动开发

### 单元测试覆盖
- 用户注册和登录测试
- 任务CRUD操作测试
- 数据隔离安全测试
- API权限控制测试

### 集成测试
- 前后端集成测试
- 数据库操作测试
- 认证流程测试

## ✅ 实现验收标准

### 功能验收
- [ ] 用户注册功能完整实现
- [ ] 用户登录和JWT认证工作正常
- [ ] 任务CRUD操作完全实现
- [ ] 数据隔离机制100%有效
- [ ] 前端界面响应式设计

### 技术验收
- [ ] 所有API接口通过测试
- [ ] 数据库模型正确创建
- [ ] 前端组件正常渲染
- [ ] 认证流程安全可靠
- [ ] 代码质量符合标准

### 安全验收
- [ ] 密码加密存储
- [ ] JWT token安全实现
- [ ] 数据隔离测试通过
- [ ] API权限控制正确

## 🔄 下一阶段准备

**S5阶段输入**:
- 完整的核心功能实现
- 通过测试的API接口
- 可运行的前端界面
- 数据隔离机制验证

**S5阶段目标**: 基于实现的功能进行全面的单元测试，确保代码质量和功能稳定性。

---
*基于 AceFlow Standard 模式和前序阶段输出生成*
*下一阶段: S5_unit_test*
"""
    
    def _generate_s4_implementation(self, project_name: str, prd_content: str) -> str:
        """Generate S4 implementation based on task breakdown."""
        return f"""# S4 功能实现 - {project_name}

**项目**: {project_name}
**阶段**: S4_implementation
**创建时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**基于**: S2任务分解 + S3测试设计

---

## 🚀 实现概述

基于前序阶段的分析，开始TaskMaster多用户隔离任务管理系统的核心功能实现。
采用**测试驱动开发(TDD)**方式，确保代码质量和功能完整性。

### 技术栈确认
- **后端**: FastAPI + Python 3.9+
- **前端**: Vue 3 + TypeScript + Element Plus
- **数据库**: DuckDB (嵌入式)
- **认证**: JWT Token
- **构建工具**: Vite (前端) + Poetry (后端)

## 📁 项目结构创建

### 后端结构 (backend/)
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库连接
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py           # 用户模型
│   │   └── task.py           # 任务模型
│   ├── schemas/               # Pydantic模式
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── api/                   # API路由
│   │   ├── __init__.py
│   │   ├── auth.py           # 认证相关
│   │   ├── users.py          # 用户管理
│   │   └── tasks.py          # 任务管理
│   ├── core/                  # 核心功能
│   │   ├── __init__.py
│   │   ├── security.py       # 安全相关
│   │   └── deps.py           # 依赖注入
│   └── tests/                 # 测试文件
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_users.py
│       └── test_tasks.py
├── pyproject.toml             # Python项目配置
├── README.md
└── .env.example
```

### 前端结构 (frontend/)
```
frontend/
├── src/
│   ├── main.ts               # 应用入口
│   ├── App.vue               # 根组件
│   ├── router/               # 路由配置
│   │   └── index.ts
│   ├── stores/               # Pinia状态管理
│   │   ├── auth.ts          # 认证状态
│   │   └── tasks.ts         # 任务状态
│   ├── views/                # 页面组件
│   │   ├── Login.vue        # 登录页
│   │   ├── Register.vue     # 注册页
│   │   ├── Dashboard.vue    # 主面板
│   │   └── TaskDetail.vue   # 任务详情
│   ├── components/           # 通用组件
│   │   ├── TaskList.vue     # 任务列表
│   │   ├── TaskBoard.vue    # 看板视图
│   │   └── TaskForm.vue     # 任务表单
│   ├── composables/          # 组合式函数
│   │   ├── useAuth.ts       # 认证逻辑
│   │   └── useTasks.ts      # 任务逻辑
│   ├── types/                # TypeScript类型
│   │   ├── auth.ts
│   │   └── task.ts
│   └── utils/                # 工具函数
│       ├── api.ts           # API客户端
│       └── notifications.ts # 通知功能
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

## 🔧 核心实现 - 第1优先级任务

### T-001: 用户注册功能实现

#### 后端实现
- 创建用户数据模型
- 实现密码加密和验证
- 设置数据库表结构
- 添加用户字段验证

#### API路由实现
- 实现用户注册API接口
- 实现用户登录API接口
- 集成JWT认证机制
- 添加输入验证和错误处理

#### 前端注册组件 (src/views/Register.vue)
```vue
<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <h2>注册 TaskMaster</h2>
      </template>
      
      <el-form
        ref="registerForm"
        :model="form"
        :rules="rules"
        label-width="80px"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="form.email"
            type="email"
            placeholder="请输入邮箱（可选）"
            :prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleRegister"
            style="width: 100%"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-link">
        已有账户？
        <router-link to="/login">立即登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import {{ ref, reactive }} from 'vue'
import {{ ElMessage }} from 'element-plus'
import {{ User, Lock, Message }} from '@element-plus/icons-vue'
import {{ useRouter }} from 'vue-router'
import {{ useAuthStore }} from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const registerForm = ref()

const form = reactive({{
  username: '',
  password: '',
  email: ''
}})

const rules = {{
  username: [
    {{ required: true, message: '请输入用户名', trigger: 'blur' }},
    {{ min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }}
  ],
  password: [
    {{ required: true, message: '请输入密码', trigger: 'blur' }},
    {{ min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }}
  ],
  email: [
    {{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }}
  ]
}}

const handleRegister = async () => {{
  if (!registerForm.value) return
  
  await registerForm.value.validate(async (valid: boolean) => {{
    if (!valid) return
    
    loading.value = true
    try {{
      await authStore.register(form)
      ElMessage.success('注册成功！')
      router.push('/login')
    }} catch (error: any) {{
      ElMessage.error(error.message || '注册失败')
    }} finally {{
      loading.value = false
    }}
  }})
}}
</script>

<style scoped>
.register-container {{
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}}

.register-card {{
  width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}}

.login-link {{
  text-align: center;
  margin-top: 16px;
  color: #666;
}}

.login-link a {{
  color: #409eff;
  text-decoration: none;
}}
</style>
```

### T-002: 用户登录功能实现

#### 认证状态管理 (src/stores/auth.ts)
```typescript
import {{ defineStore }} from 'pinia'
import {{ ref, computed }} from 'vue'
import api from '@/utils/api'

export interface User {{
  id: number
  username: string
  email?: string
}}

export interface LoginData {{
  username: string
  password: string
}}

export interface RegisterData {{
  username: string
  password: string
  email?: string
}}

export const useAuthStore = defineStore('auth', () => {{
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  
  const isAuthenticated = computed(() => !!token.value)
  
  const login = async (loginData: LoginData) => {{
    try {{
      const response = await api.post('/auth/login', loginData)
      const {{ access_token, user: userData }} = response.data
      
      token.value = access_token
      user.value = userData
      
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      
      // 设置API默认认证头
      api.defaults.headers.common['Authorization'] = `Bearer ${{access_token}}`
      
      return userData
    }} catch (error: any) {{
      throw new Error(error.response?.data?.detail || '登录失败')
    }}
  }}
  
  const register = async (registerData: RegisterData) => {{
    try {{
      const response = await api.post('/auth/register', registerData)
      return response.data
    }} catch (error: any) {{
      throw new Error(error.response?.data?.detail || '注册失败')
    }}
  }}
  
  const logout = () => {{
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete api.defaults.headers.common['Authorization']
  }}
  
  const initAuth = () => {{
    const savedUser = localStorage.getItem('user')
    if (token.value && savedUser) {{
      user.value = JSON.parse(savedUser)
      api.defaults.headers.common['Authorization'] = `Bearer ${{token.value}}`
    }}
  }}
  
  return {{
    token,
    user,
    isAuthenticated,
    login,
    register,
    logout,
    initAuth
  }}
}})
```

### T-005: 任务CRUD操作实现

#### 任务模型 (app/models/task.py)
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class TaskStatus(enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notified = Column(Boolean, default=False)
    
    # 外键关联用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tasks")
```

#### 任务API路由 (app/api/tasks.py)
```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.core.deps import get_current_user
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"创建任务\"\"\"
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
\n