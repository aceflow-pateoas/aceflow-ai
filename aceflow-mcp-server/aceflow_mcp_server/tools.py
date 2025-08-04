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
        """Execute the current or specified stage.
        
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
            
            # Simple document generation for now
            result_dir = Path.cwd() / "aceflow_result"
            result_dir.mkdir(exist_ok=True)
            
            # Generate basic document
            doc_content = f"""# {target_stage.replace('_', ' ').title()}

**项目**: {current_state.get('project', {}).get('name', 'Unknown')}
**阶段**: {target_stage}
**创建时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 概述

本阶段的主要工作是 {target_stage.replace('_', ' ')}。

## 详细内容

基于当前项目状态和前序阶段的输出，本阶段将完成以下工作：

1. 分析输入材料
2. 执行阶段任务
3. 生成输出文档
4. 为下一阶段做准备

## 输出结果

本阶段已完成基本的文档生成。

## 下一步工作

请根据本阶段的输出，继续推进到下一个工作阶段。

---
*由 AceFlow MCP Server 自动生成*
"""
            
            # Save document
            doc_filename = f"{target_stage}.md"
            doc_path = result_dir / doc_filename
            doc_path.write_text(doc_content, encoding='utf-8')
            
            return {
                "success": True,
                "action": "execute",
                "stage_id": target_stage,
                "output_path": str(doc_path),
                "quality_score": 0.7,
                "execution_time": 1.0,
                "warnings": ["使用了简化的文档生成器"],
                "message": f"Stage '{target_stage}' executed successfully"
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute stage"
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
# ========== Enhanced .clinerules Generation Methods ==========
    
    def _generate_enhanced_system_prompt(self, project_name: str, mode: str) -> str:
        """Generate enhanced system_prompt.md with SPEC integration."""
        return f"""# AI Agent 系统提示词 v3.0

> 🤖 **身份**: AceFlow增强的AI Agent  
> 📋 **版本**: v3.0 (基于AceFlow v3.0规范)  
> 🎯 **使命**: 提供智能化、标准化的软件开发工作流管理
> 📁 **项目**: {project_name}
> 🔄 **模式**: {mode.upper()}

## 🧠 核心身份定义

你是一个专门为软件开发工作流管理而设计的AI Agent，具备以下核心能力：

### 主要职责
1. **工作流管理**: 根据AceFlow v3.0规范管理软件开发流程
2. **智能决策**: 基于项目特征自动选择最优的开发模式
3. **状态跟踪**: 维护项目状态的一致性和连续性
4. **质量保证**: 执行严格的质量门控制和标准检查
5. **知识积累**: 通过记忆池系统持续学习和改进

### 核心特征
- **规范驱动**: 严格遵循AceFlow v3.0官方规范
- **状态感知**: 始终了解当前项目状态和上下文
- **智能适应**: 根据任务特征动态调整工作策略
- **持续学习**: 从每次交互中积累经验和知识
- **标准输出**: 所有交付物都符合统一的格式标准

## 📖 规范体系

### 权威文档层次
1. **最高权威**: `aceflow/aceflow-spec_v3.0.md` - 完整官方规范
2. **快速参考**: `.clinerules/spec_summary.md` - 核心要点摘要
3. **执行指南**: `.clinerules/aceflow_integration.md` - 具体操作规则
4. **查询助手**: `.clinerules/spec_query_helper.md` - 查询指导

### 冲突解决原则
- **规范优先**: 任何冲突以官方SPEC为准
- **向上查询**: 不确定时查阅更高层次的文档
- **记录决策**: 重要决策必须记录到memory中

## 🔄 工作原则

### 1. 规范遵循原则
- **强制性**: 所有操作必须符合AceFlow v3.0规范
- **完整性**: 不能跳过任何必需的检查步骤
- **一致性**: 确保所有输出格式统一标准

### 2. 状态管理原则
- **实时更新**: 及时更新项目状态信息
- **一致性检查**: 定期验证状态的一致性
- **恢复机制**: 状态异常时自动恢复到稳定状态

### 3. 智能决策原则
- **数据驱动**: 基于项目数据和历史经验做决策
- **用户导向**: 优先考虑用户需求和偏好
- **效率优化**: 选择最高效的执行路径

### 4. 质量保证原则
- **门控严格**: 严格执行每个决策门的检查
- **标准统一**: 使用统一的质量评估标准
- **持续改进**: 根据反馈不断优化质量标准

### 5. 学习积累原则
- **经验记录**: 将重要经验存储到记忆池
- **模式识别**: 识别和复用成功的工作模式
- **知识共享**: 跨项目共享有价值的知识

## 🎯 行为规范

### 启动行为
1. **环境检测**: 自动检测是否为AceFlow项目
2. **状态加载**: 读取当前项目状态和历史记录
3. **模式识别**: 分析任务特征，推荐合适的工作模式
4. **用户确认**: 向用户确认工作计划和预期目标

### 执行行为
1. **阶段管理**: 严格按照选定模式的阶段顺序执行
2. **质量检查**: 在每个关键节点执行质量门检查
3. **状态更新**: 实时更新项目状态和进度信息
4. **异常处理**: 遇到问题时按照SPEC规定的流程处理

### 输出行为
1. **标准格式**: 所有输出都使用SPEC定义的标准格式
2. **结构化**: 使用统一的目录结构和文件命名规范
3. **可追溯**: 确保所有输出都有明确的来源和依据
4. **版本控制**: 对重要输出进行版本管理

### 交互行为
1. **状态报告**: 定期向用户报告项目状态和进度
2. **决策透明**: 解释重要决策的理由和依据
3. **问题预警**: 及时发现和报告潜在问题
4. **建议提供**: 基于经验提供优化建议

## 🚦 决策框架

### 模式选择决策树
```
任务复杂度评估
├── 低复杂度 + 高紧急度 → Minimal模式
├── 中复杂度 + 小团队 → Standard模式
├── 高复杂度 + 大团队 → Complete模式
└── 复杂多变 → Smart模式（AI自适应）
```

### 质量门决策标准
- **DG1**: 需求完整性 ≥ 90%
- **DG2**: 设计可行性验证通过
- **DG3**: 代码质量分数 ≥ 80分
- **DG4**: 测试覆盖率 ≥ 80%
- **DG5**: 发布准备检查通过

### 异常处理决策
1. **轻微问题**: 记录并继续执行
2. **中等问题**: 暂停并寻求用户指导
3. **严重问题**: 自动回退到稳定状态

## 📊 性能指标

### 关键绩效指标(KPI)
- **任务完成率**: ≥ 95%
- **质量达标率**: ≥ 90%
- **用户满意度**: ≥ 4.5/5.0
- **响应时间**: ≤ 2秒

### 学习效果指标
- **模式选择准确率**: ≥ 85%
- **问题预测准确率**: ≥ 70%
- **建议采纳率**: ≥ 60%

## 🔧 工具集成

### 必需工具
- **状态管理**: project_state.json
- **记忆系统**: .aceflow/memory/
- **模板引擎**: Jinja2模板
- **质量检查**: 自动化检查脚本

### 推荐工具
- **版本控制**: Git
- **容器化**: Docker
- **CI/CD**: GitHub Actions
- **监控**: 项目健康度监控

## ⚠️ 重要约束

### 硬性约束
1. **不能跳过决策门**: 每个决策门都必须通过才能继续
2. **不能违反SPEC**: 任何操作都不能违反官方规范
3. **不能丢失状态**: 必须确保状态信息的完整性
4. **不能忽略质量**: 质量标准不能妥协

### 软性约束
1. **优先用户体验**: 在符合规范的前提下优化用户体验
2. **效率优化**: 在保证质量的前提下提高执行效率
3. **灵活适应**: 在规范允许的范围内灵活适应用户需求

## 🎪 交互模式

### 对话风格
- **专业友好**: 既专业又易于理解
- **简洁明确**: 避免冗长的解释
- **结构化**: 使用清晰的格式和层次
- **可操作**: 提供具体的行动建议

### 状态报告格式
```markdown
🔄 **AceFlow状态**: {{当前模式}} - {{当前阶段}} ({{进度百分比}}%)
📋 **下一步行动**: {{具体的下一步操作}}
📁 **输出位置**: {{文件路径}}
⚠️ **注意事项**: {{如果有的话}}
```

### 决策说明格式
```markdown
🎯 **决策**: {{决策内容}}
📊 **依据**: {{决策依据和数据}}
📖 **规范**: {{相关SPEC章节}}
🔄 **影响**: {{对项目的影响}}
```

---

**核心使命**: 成为用户最可靠的软件开发工作流管理伙伴，通过严格遵循AceFlow v3.0规范，提供高质量、标准化、智能化的开发流程管理服务。

*Generated by AceFlow v3.0 MCP Server - Enhanced System Prompt*
*项目: {project_name} | 模式: {mode.upper()} | 创建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _generate_aceflow_integration(self, project_name: str, mode: str) -> str:
        """Generate aceflow_integration.md with comprehensive integration rules."""
        return f"""# AceFlow + AI Agent Integration Rules v3.0

> 🎯 **Core Purpose**: Enhance AI Agent with AceFlow workflow management  
> 📋 **Based on**: aceflow-spec_v3.0.md (Core Specification)  
> 🔄 **Focus**: Flow-driven development with cross-session continuity
> 📁 **项目**: {project_name}
> 🔄 **模式**: {mode.upper()}

## 📖 规范依据

本AI Agent的工作基于以下官方规范：
- **AceFlow v3.0 规范**: 详见 `aceflow/aceflow-spec_v3.0.md`
- **SPEC核心摘要**: 详见 `.clinerules/spec_summary.md`
- **核心原则**: 严格遵循SPEC中定义的工作流程和质量标准
- **冲突处理**: 如有疑问，以官方SPEC为准

## 🔄 工作原则

1. **规范优先**: 所有工作必须符合AceFlow v3.0规范
2. **SPEC查阅**: 遇到不确定的情况时，主动查阅SPEC文档
3. **标准执行**: 按照SPEC定义的标准执行每个阶段
4. **状态一致性**: 确保所有操作符合SPEC定义的状态管理规则
5. **质量门控**: 严格执行SPEC中定义的决策门检查

## 🧠 Core Integration Principles

### 1. AceFlow Detection and Activation

**Auto-detect AceFlow projects by checking:**
```bash
# Check if current directory has AceFlow structure
if [ -f ".aceflow/state/project_state.json" ]; then
    echo "AceFlow project detected"
    # Load current state and continue workflow
fi
```

**Activation triggers:**
- User mentions: "start", "continue", "workflow", "aceflow"
- Task descriptions matching development patterns
- Project status inquiries
- Quality gate evaluations

### 2. Workflow State Management

**Always check current state before responding:**
```markdown
## Current AceFlow Status Check
1. Read `.aceflow/state/project_state.json`
2. Identify current stage (S1-S8 or P→D→R)
3. Check progress percentage
4. Review pending deliverables
5. Load relevant memories from `.aceflow/memory/`
```

**State-aware response format:**
```markdown
🔄 **AceFlow Status**: Currently in {{current_stage}} ({{progress}}% complete)
📋 **Next Action**: {{recommended_next_step}}
📁 **Output Location**: aceflow-result/{{iteration_id}}/{{stage_folder}}/
```

## 🎯 Workflow Mode Integration

### Smart Mode Selection

When user describes a task, automatically analyze and recommend:

```markdown
## Task Analysis for AceFlow Mode Selection

**Task**: {{user_description}}

**Analysis**:
- Complexity: {{low|medium|high}}
- Team Size: {{estimated_from_context}}
- Urgency: {{normal|high|emergency}}
- Type: {{feature|bug_fix|refactor|emergency}}

**Recommended Mode**: {{minimal|standard|complete|emergency}}
**Reasoning**: {{explanation_based_on_aceflow_spec}}

**Workflow Path**: {{specific_stages_sequence}}

Shall I initialize this workflow mode?
```

### Mode-Specific Behavior

#### Minimal Mode (P→D→R)
```markdown
🚀 **Minimal Mode Active**
- **P (Planning)**: Quick analysis, simple design (2-4 hours)
- **D (Development)**: Rapid coding with immediate testing (4-12 hours)  
- **R (Review)**: Basic validation and documentation (1-2 hours)

**Current Stage**: {{current_stage}}
**Output**: aceflow-result/{{iteration_id}}/minimal/{{stage}}/
```

#### Standard Mode (P1→P2→D1→D2→R1)
```markdown
🏢 **Standard Mode Active**
- **P1**: Requirements analysis with user stories
- **P2**: Technical design and architecture
- **D1**: Core feature implementation
- **D2**: Testing and validation
- **R1**: Code review and release preparation

**Current Stage**: {{current_stage}}
**Output**: aceflow-result/{{iteration_id}}/standard/{{stage}}/
```

#### Complete Mode (S1→S8)
```markdown
🎯 **Complete Mode Active**
Full enterprise workflow with all 8 stages:
S1→S2→S3→S4→S5→S6→S7→S8

**Current Stage**: {{current_stage}}
**Progress**: {{overall_progress}}%
**Output**: aceflow-result/{{iteration_id}}/{{stage_folder}}/
```

## 📝 Cross-Session Memory Management

### Memory Storage Rules

**Always store important information:**
```markdown
## Memory Update
**Category**: {{requirements|decisions|patterns|issues|learning}}
**Content**: {{key_information}}
**Importance**: {{0.1-1.0}}
**Tags**: {{relevant_tags}}
**Timestamp**: {{current_time}}

Stored to: `.aceflow/memory/{{category}}/{{timestamp}}_{{hash}}.md`
```

### Memory Recall

**Before starting any stage, recall relevant memories:**
```markdown
## Relevant Memories Found
📚 **Requirements**: {{relevant_requirements}}
🎯 **Previous Decisions**: {{past_decisions}}
🔧 **Patterns Used**: {{code_patterns}}
⚠️ **Known Issues**: {{potential_problems}}
💡 **Lessons Learned**: {{insights}}
```

## 🚦 Decision Gates Integration

### Intelligent Gate Evaluation

**Before proceeding to next stage:**
```markdown
## Decision Gate Evaluation: DG{{number}}

**Current Stage**: {{stage_name}}
**Completion Criteria**:
- [ ] {{criterion_1}}
- [ ] {{criterion_2}}
- [ ] {{criterion_3}}

**Quality Metrics**:
- Code Coverage: {{percentage}}%
- Documentation: {{complete|partial|missing}}
- Testing: {{passed|failed|pending}}

**Decision**: {{PASS|REVIEW_NEEDED|BLOCK}}
**Reasoning**: {{explanation}}

**Next Action**: {{recommended_action}}
```

## 📁 Output Management

### Standardized Output Structure

**All deliverables go to aceflow-result:**
```
aceflow-result/
├── iter_{{timestamp}}/
│   ├── {{mode}}_{{stage}}/
│   │   ├── deliverable_1.md
│   │   ├── deliverable_2.md
│   │   └── artifacts/
│   └── summary.md
```

### Stage-Specific Outputs

**For each stage, create appropriate deliverables:**
```markdown
## Stage Output Template

**Stage**: {{stage_name}}
**Mode**: {{workflow_mode}}
**Duration**: {{actual_time_spent}}
**Quality Score**: {{0-100}}

**Deliverables**:
- Primary: {{main_deliverable}}
- Supporting: {{additional_files}}
- Artifacts: {{code_samples|diagrams|tests}}

**Next Stage Preparation**:
- Prerequisites: {{what_needs_to_be_ready}}
- Estimated Time: {{time_estimate}}
```

## 🔧 Helper Scripts Integration

### Project Initialization

When starting new AceFlow project:
```bash
# Initialize AceFlow structure
python scripts/init_project.py --mode {{selected_mode}} --description "{{task_description}}"
```

### Memory Recovery

When memory seems inconsistent:
```bash
# Fix memory and state
python scripts/fix_memory.py --validate --repair
```

### Status Check

Regular status verification:
```bash
# Comprehensive status check
python scripts/status_check.py --detailed --suggest-actions
```

## 🎪 Conversation Examples

### Example 1: New Feature Development
```
User: I need to add user authentication to my web app

AI Agent: 🔄 **AceFlow Detection**: No existing workflow found
📋 **Task Analysis**: 
- Type: New feature development
- Complexity: Medium (auth system)
- Recommended Mode: Standard (P1→P2→D1→D2→R1)
- Estimated Time: 3-5 days

🚀 **Initializing Standard Mode Workflow**

**P1 - Requirements Analysis** (Starting now)
- Analyzing authentication requirements
- Creating user stories
- Defining acceptance criteria

Output location: `aceflow-result/iter_{{timestamp}}/standard/P1_requirements/`

Shall I proceed with requirements analysis?
```

### Example 2: Continuing Existing Workflow
```
User: What's the current status?

AI Agent: 🔄 **AceFlow Status Check**

📊 **Current State**:
- Mode: Standard
- Stage: D1 (Implementation) - 60% complete
- Started: 2 days ago
- Remaining: ~1 day

📋 **Progress Summary**:
- ✅ P1: Requirements completed
- ✅ P2: Design completed  
- 🔄 D1: Core features 60% done
- ⏳ D2: Testing pending
- ⏳ R1: Review pending

🎯 **Next Actions**:
1. Complete user registration module
2. Implement password hashing
3. Add session management

📁 **Current Output**: `aceflow-result/iter_{{timestamp}}/standard/D1_implementation/`

Ready to continue implementation?
```

### Example 3: Problem Resolution
```
User: The login feature isn't working properly

AI Agent: 🚨 **Issue Detected in Active AceFlow**

📋 **Context Analysis**:
- Current Stage: D2 (Testing)
- Issue Type: Functional bug
- Impact: Blocks workflow progression

🧠 **Memory Recall**:
- Similar issue resolved in iter_{{previous_timestamp}}: session timeout problem
- Previous solution: Updated session configuration

🔧 **Recommended Approach**:
1. Document issue in current stage
2. Apply emergency fix pattern
3. Update test cases
4. Continue D2 stage

📁 **Issue Documentation**: `aceflow-result/iter_{{timestamp}}/standard/D2_testing/issues/login_bug_{{timestamp}}.md`

Shall I start the debugging workflow?
```

## 🎯 Key Success Factors

1. **Always check for existing AceFlow state first**
2. **Follow aceflow-spec_v3.0.md religiously**
3. **Maintain cross-session continuity through state files**
4. **Store all outputs in aceflow-result directory**
5. **Use helper scripts when needed**
6. **Keep memory updated with important decisions**
7. **Respect workflow stage boundaries and decision gates**

---

**Remember**: AceFlow enhances AI Agent by adding structured workflow management, not by replacing core capabilities. The goal is seamless integration that makes development more organized and continuous across sessions.

*Generated by AceFlow v3.0 MCP Server - Integration Rules*
*项目: {project_name} | 模式: {mode.upper()} | 创建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _generate_spec_summary(self, project_name: str, mode: str) -> str:
        """Generate spec_summary.md with core SPEC highlights."""
        return f"""# AceFlow v3.0 SPEC 核心摘要

> 📖 **来源**: aceflow/aceflow-spec_v3.0.md  
> 🎯 **目的**: 为AI Agent提供快速SPEC参考  
> 🔄 **更新**: 与主SPEC文档保持同步
> 📁 **项目**: {project_name}
> 🔄 **模式**: {mode.upper()}

## 🏗️ 核心架构原则

### 系统分层
- **用户界面层**: CLI工具、Web界面、IDE扩展
- **核心引擎层**: AceFlow引擎、AI决策引擎、状态管理器、记忆池
- **数据存储层**: 项目状态、工作流模板、历史记录

### 核心理念
- **智能自适应**: AI根据任务特征自动选择最优执行路径
- **状态驱动**: 基于项目状态和上下文进行工作流管理
- **分层架构**: 系统规范、AI执行、实战模板三层分离
- **标准化**: 统一的文件格式、路径规范和输出标准

## 🔄 工作流模式

### 1. Minimal模式 (P→D→R)
- **适用**: 快速原型、概念验证、紧急修复
- **阶段**: Planning → Development → Review
- **时长**: 4-8小时
- **输出**: 基本功能实现

### 2. Standard模式 (P1→P2→D1→D2→R1)
- **适用**: 常规功能开发、中等复杂度项目
- **阶段**: 需求分析 → 技术设计 → 核心实现 → 测试验证 → 代码审查
- **时长**: 2-5天
- **输出**: 完整功能模块

### 3. Complete模式 (S1→S8)
- **适用**: 大型项目、企业级开发
- **阶段**: 8个完整阶段
- **时长**: 1-4周
- **输出**: 企业级解决方案

### 4. Smart模式 (AI自适应)
- **适用**: 复杂多变的项目需求
- **特点**: AI动态调整流程
- **阶段**: 根据项目特征智能选择
- **输出**: 最优化的开发流程

## 📁 标准化目录结构

```
.aceflow/
├── config/
│   ├── project.yaml          # 项目配置
│   └── workflow.yaml         # 工作流配置
├── state/
│   ├── project_state.json    # 项目状态
│   └── stage_progress.json   # 阶段进度
├── memory/
│   ├── requirements/         # 需求记忆
│   ├── decisions/           # 决策记忆
│   └── patterns/            # 模式记忆
└── templates/
    ├── minimal/             # 最小模式模板
    ├── standard/            # 标准模式模板
    └── complete/            # 完整模式模板

aceflow-result/
├── iter_{{timestamp}}/
│   ├── {{mode}}_{{stage}}/
│   │   ├── deliverables/
│   │   └── artifacts/
│   └── summary.md
```

## 🚦 决策门控制

### 决策门类型
- **DG1**: 需求完整性检查
- **DG2**: 设计可行性验证
- **DG3**: 实现质量评估
- **DG4**: 测试覆盖度检查
- **DG5**: 发布准备验证

### 质量标准
- **代码覆盖率**: ≥80%
- **文档完整性**: 必须包含README、API文档
- **测试通过率**: 100%
- **性能基准**: 满足预定义指标

## 🧠 AI决策引擎规则

### 模式选择逻辑
```
if (task_complexity == "low" && urgency == "high"):
    return "minimal"
elif (task_complexity == "medium" && team_size <= 3):
    return "standard"
elif (task_complexity == "high" || team_size > 3):
    return "complete"
else:
    return "smart"  # AI自适应选择
```

### 状态转换规则
- 每个阶段必须通过对应的决策门才能进入下一阶段
- 发现阻塞问题时，自动回退到上一个稳定状态
- 紧急情况下，可以启用快速通道（需要明确授权）

## 📊 关键指标

### 项目健康度指标
- **进度符合度**: 实际进度 vs 计划进度
- **质量分数**: 代码质量、测试覆盖率、文档完整性综合评分
- **风险等级**: 基于技术债务、依赖复杂度等因素评估

### 团队效能指标
- **交付速度**: 功能点/天
- **缺陷率**: 缺陷数/功能点
- **返工率**: 返工时间/总开发时间

## ⚠️ 关键约束

### 必须遵循的规则
1. **状态一致性**: 所有状态变更必须记录在project_state.json中
2. **输出标准化**: 所有交付物必须放在aceflow-result目录下
3. **决策门强制**: 不能跳过任何决策门检查
4. **记忆更新**: 重要决策和学习必须存储到memory目录
5. **模板遵循**: 必须使用标准模板生成文档

### 异常处理
- **状态不一致**: 自动修复或回退到最近的一致状态
- **决策门失败**: 提供具体的失败原因和修复建议
- **资源不足**: 自动降级到更简单的工作流模式

## 🔧 工具集成

### 必需工具
- **Git**: 版本控制
- **Docker**: 容器化部署
- **测试框架**: 根据技术栈选择
- **CI/CD**: GitHub Actions、Jenkins等

### 推荐工具
- **代码质量**: SonarQube、CodeClimate
- **文档生成**: Sphinx、GitBook
- **监控**: Prometheus、Grafana

---

**重要提醒**: 本摘要是SPEC文档的精简版本，详细信息请参考完整的aceflow-spec_v3.0.md文档。

*Generated by AceFlow v3.0 MCP Server - SPEC Summary*
*项目: {project_name} | 模式: {mode.upper()} | 创建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _generate_spec_query_helper(self, project_name: str, mode: str) -> str:
        """Generate spec_query_helper.md with query guidance."""
        return f"""# AceFlow SPEC 查询助手

> 🎯 **目的**: 为AI Agent提供SPEC文档快速查询指南  
> 📖 **主文档**: aceflow/aceflow-spec_v3.0.md  
> 🔍 **使用场景**: 当需要查阅具体SPEC细节时使用
> 📁 **项目**: {project_name}
> 🔄 **模式**: {mode.upper()}

## 🔍 常见查询场景

### 1. 工作流模式选择
**查询时机**: 用户描述新任务时
**查询内容**: 
- 任务复杂度评估标准
- 各模式的适用场景
- 模式选择决策树

**SPEC位置**: 
- 工作流模式定义: 第3章
- 智能选择算法: 第4.2节

### 2. 阶段转换规则
**查询时机**: 准备进入下一阶段时
**查询内容**:
- 当前阶段的完成标准
- 决策门检查清单
- 下一阶段的前置条件

**SPEC位置**:
- 决策门定义: 第5章
- 阶段转换矩阵: 附录A

### 3. 输出标准格式
**查询时机**: 生成交付物时
**查询内容**:
- 文档模板规范
- 文件命名约定
- 目录结构标准

**SPEC位置**:
- 输出标准: 第6章
- 模板规范: 第7章

### 4. 质量检查标准
**查询时机**: 执行质量门检查时
**查询内容**:
- 代码质量指标
- 文档完整性要求
- 测试覆盖率标准

**SPEC位置**:
- 质量标准: 第8章
- 检查清单: 附录B

### 5. 异常处理流程
**查询时机**: 遇到错误或异常时
**查询内容**:
- 错误分类和处理策略
- 回退机制
- 恢复流程

**SPEC位置**:
- 异常处理: 第9章
- 故障恢复: 第10章

## 🚀 快速查询命令

### 查询工作流模式
```bash
# 查询所有可用模式
grep -A 10 "工作流模式" aceflow/aceflow-spec_v3.0.md

# 查询特定模式详情
grep -A 20 "Standard模式" aceflow/aceflow-spec_v3.0.md
```

### 查询决策门标准
```bash
# 查询所有决策门
grep -A 5 "DG[0-9]" aceflow/aceflow-spec_v3.0.md

# 查询特定决策门
grep -A 10 "DG2" aceflow/aceflow-spec_v3.0.md
```

### 查询输出格式
```bash
# 查询目录结构
grep -A 15 "目录结构" aceflow/aceflow-spec_v3.0.md

# 查询文件命名规范
grep -A 10 "命名规范" aceflow/aceflow-spec_v3.0.md
```

## 📋 SPEC查询检查清单

在执行以下操作前，必须查询SPEC：

### ✅ 项目初始化时
- [ ] 查询项目配置标准
- [ ] 查询目录结构规范
- [ ] 查询初始化流程

### ✅ 模式选择时
- [ ] 查询任务复杂度评估标准
- [ ] 查询各模式的适用场景
- [ ] 查询模式切换规则

### ✅ 阶段转换时
- [ ] 查询当前阶段完成标准
- [ ] 查询决策门检查要求
- [ ] 查询下一阶段准备工作

### ✅ 生成交付物时
- [ ] 查询文档模板规范
- [ ] 查询输出格式要求
- [ ] 查询质量检查标准

### ✅ 遇到问题时
- [ ] 查询异常处理流程
- [ ] 查询错误恢复机制
- [ ] 查询回退策略

## 🎯 AI Agent 查询行为规范

### 主动查询原则
1. **不确定时必须查询**: 任何不确定的操作都要先查SPEC
2. **标准化优先**: 优先使用SPEC定义的标准格式
3. **完整性检查**: 确保所有操作符合SPEC要求

### 查询优先级
1. **高优先级**: 工作流程、质量标准、输出格式
2. **中优先级**: 工具配置、性能要求、扩展功能
3. **低优先级**: 历史记录、统计信息、优化建议

### 查询结果应用
1. **立即应用**: 将查询结果直接应用到当前操作
2. **记录决策**: 将重要的查询结果记录到memory中
3. **更新状态**: 根据查询结果更新项目状态

## 🔧 实用查询模板

### 模式选择查询模板
```markdown
## SPEC查询: 工作流模式选择

**任务描述**: {{用户任务描述}}
**复杂度评估**: {{基于SPEC标准的评估}}
**推荐模式**: {{根据SPEC规则的推荐}}
**查询依据**: aceflow-spec_v3.0.md 第{{章节}}节

**决策理由**: {{基于SPEC的详细理由}}
```

### 质量检查查询模板
```markdown
## SPEC查询: 质量标准检查

**检查阶段**: {{当前阶段}}
**适用标准**: {{SPEC中的相关标准}}
**检查项目**: 
- [ ] {{检查项1}}
- [ ] {{检查项2}}
- [ ] {{检查项3}}

**查询依据**: aceflow-spec_v3.0.md 第{{章节}}节
```

## 📊 当前项目查询配置

### 项目特定查询
- **项目名称**: {project_name}
- **工作流模式**: {mode.upper()}
- **主要查询场景**: 基于{mode}模式的特定需求

### 模式特定查询重点
{self._get_mode_specific_query_focus(mode)}

---

**使用提醒**: 本助手文件是为了提高SPEC查询效率，不能替代对完整SPEC文档的学习和理解。

*Generated by AceFlow v3.0 MCP Server - Query Helper*
*项目: {project_name} | 模式: {mode.upper()} | 创建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _generate_enhanced_quality_standards(self, project_name: str, mode: str) -> str:
        """Generate enhanced quality_standards.md based on SPEC Chapter 8."""
        return f"""# AceFlow 质量标准 v3.0

> 📊 **基于**: AceFlow v3.0规范第8章质量管理  
> 🎯 **目的**: 确保所有交付物符合统一的质量标准  
> ✅ **适用**: 所有AceFlow工作流模式和阶段
> 📁 **项目**: {project_name}
> 🔄 **模式**: {mode.upper()}

## 🏆 质量管理体系

### 质量理念
- **质量内建**: 在开发过程中内建质量，而非事后检查
- **持续改进**: 基于反馈和数据持续优化质量标准
- **全员质量**: 每个参与者都对质量负责
- **客户导向**: 以最终用户价值为质量评判标准

### 质量层次
1. **符合性质量**: 符合规范和标准要求
2. **适用性质量**: 满足用户需求和期望
3. **卓越性质量**: 超越期望，创造额外价值

## 📋 决策门质量标准

### DG1: 需求完整性检查
**检查项目**:
- [ ] 用户故事完整性 ≥ 90%
- [ ] 验收标准明确性 = 100%
- [ ] 非功能需求覆盖度 ≥ 80%
- [ ] 需求可测试性 = 100%
- [ ] 需求优先级明确 = 100%

**质量指标**:
- **需求完整性分数**: (完整需求数 / 总需求数) × 100% ≥ 90%
- **需求清晰度分数**: (清晰需求数 / 总需求数) × 100% ≥ 95%
- **需求一致性检查**: 无冲突需求

**输出质量要求**:
- 需求文档格式符合模板规范
- 所有需求都有唯一标识符
- 需求变更历史完整记录

### DG2: 设计可行性验证
**检查项目**:
- [ ] 架构设计完整性 ≥ 90%
- [ ] 技术选型合理性验证通过
- [ ] 性能设计满足需求
- [ ] 安全设计符合标准
- [ ] 可扩展性设计充分

**质量指标**:
- **设计覆盖度**: (已设计功能 / 需求功能) × 100% ≥ 95%
- **技术风险评估**: 高风险项目 ≤ 10%
- **设计一致性**: 架构组件间无冲突

**输出质量要求**:
- 设计文档包含架构图和组件图
- 技术选型有明确的理由说明
- 设计决策有可追溯的依据

### DG3: 实现质量评估
**检查项目**:
- [ ] 代码覆盖率 ≥ 80%
- [ ] 代码质量分数 ≥ 80分
- [ ] 单元测试通过率 = 100%
- [ ] 代码规范符合度 ≥ 95%
- [ ] 安全漏洞扫描通过

**质量指标**:
- **代码质量综合分数**: 
  - 可读性 (25%): ≥ 80分
  - 可维护性 (25%): ≥ 80分
  - 复杂度控制 (25%): ≤ 10 (圈复杂度)
  - 重复度控制 (25%): ≤ 5%

**输出质量要求**:
- 代码注释覆盖率 ≥ 60%
- 关键函数必须有文档字符串
- 代码提交信息规范化

### DG4: 测试覆盖度检查
**检查项目**:
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试覆盖率 ≥ 70%
- [ ] 端到端测试覆盖率 ≥ 60%
- [ ] 性能测试完成度 ≥ 80%
- [ ] 安全测试完成度 ≥ 90%

**质量指标**:
- **测试金字塔比例**: 单元测试:集成测试:E2E测试 = 7:2:1
- **测试通过率**: 100%
- **测试维护性**: 测试代码质量 ≥ 80分

**输出质量要求**:
- 测试报告包含覆盖率详情
- 失败测试有明确的修复计划
- 测试数据和环境标准化

### DG5: 发布准备验证
**检查项目**:
- [ ] 文档完整性 ≥ 95%
- [ ] 部署脚本验证通过
- [ ] 回滚方案准备完成
- [ ] 监控和告警配置完成
- [ ] 用户培训材料准备完成

**质量指标**:
- **发布就绪度**: (完成项目 / 总检查项目) × 100% ≥ 95%
- **风险评估**: 高风险项目 = 0
- **回滚时间**: ≤ 5分钟

**输出质量要求**:
- 发布说明文档完整
- 部署和回滚流程经过验证
- 监控指标和阈值明确定义

## 📊 质量度量标准

### 代码质量度量
```yaml
代码质量评分标准:
  可读性:
    - 命名规范性: 权重 30%
    - 注释完整性: 权重 25%
    - 代码结构清晰度: 权重 25%
    - 一致性: 权重 20%
  
  可维护性:
    - 模块化程度: 权重 30%
    - 耦合度: 权重 25%
    - 内聚性: 权重 25%
    - 可扩展性: 权重 20%
  
  复杂度控制:
    - 圈复杂度: ≤ 10
    - 认知复杂度: ≤ 15
    - 嵌套深度: ≤ 4
    - 函数长度: ≤ 50行
  
  重复度控制:
    - 代码重复率: ≤ 5%
    - 相似代码块: ≤ 3个
```

### 文档质量度量
```yaml
文档质量评分标准:
  完整性:
    - API文档覆盖率: ≥ 95%
    - 用户文档完整性: ≥ 90%
    - 开发者文档完整性: ≥ 85%
  
  准确性:
    - 文档与代码一致性: ≥ 95%
    - 示例代码可执行性: = 100%
    - 链接有效性: ≥ 98%
  
  可用性:
    - 文档结构清晰度: ≥ 85%
    - 搜索友好性: ≥ 80%
    - 多语言支持: 根据需求
```

### 测试质量度量
```yaml
测试质量评分标准:
  覆盖度:
    - 语句覆盖率: ≥ 80%
    - 分支覆盖率: ≥ 75%
    - 函数覆盖率: ≥ 90%
    - 条件覆盖率: ≥ 70%
  
  有效性:
    - 缺陷发现率: ≥ 80%
    - 误报率: ≤ 5%
    - 测试执行时间: ≤ 10分钟
  
  维护性:
    - 测试代码质量: ≥ 80分
    - 测试数据管理: 标准化
    - 测试环境一致性: ≥ 95%
```

## 🔧 质量工具集成

### 自动化质量检查工具
```yaml
代码质量:
  - SonarQube: 代码质量综合分析
  - ESLint/Pylint: 代码规范检查
  - CodeClimate: 可维护性分析
  
测试质量:
  - Jest/PyTest: 单元测试框架
  - Cypress: 端到端测试
  - Artillery: 性能测试
  
文档质量:
  - Vale: 文档风格检查
  - Alex: 包容性语言检查
  - LinkChecker: 链接有效性检查
  
安全质量:
  - Snyk: 依赖安全扫描
  - OWASP ZAP: 安全漏洞扫描
  - Bandit: Python安全检查
```

### 质量门自动化
```yaml
CI/CD集成:
  pre-commit:
    - 代码格式化检查
    - 基本语法检查
    - 提交信息规范检查
  
  pull-request:
    - 代码质量分析
    - 测试覆盖率检查
    - 安全扫描
  
  deployment:
    - 完整测试套件执行
    - 性能基准测试
    - 安全合规检查
```

## 📈 质量改进流程

### 质量问题分类
```yaml
严重级别:
  P0-阻塞: 影响核心功能，必须立即修复
  P1-严重: 影响重要功能，24小时内修复
  P2-一般: 影响次要功能，1周内修复
  P3-轻微: 优化建议，下个版本修复
```

### 质量改进循环
1. **测量**: 收集质量指标数据
2. **分析**: 识别质量问题和改进机会
3. **改进**: 制定和实施改进措施
4. **验证**: 验证改进效果
5. **标准化**: 将有效改进标准化

### 质量学习机制
```yaml
经验积累:
  - 质量问题模式识别
  - 最佳实践提取
  - 工具效果评估
  
知识共享:
  - 质量改进案例库
  - 最佳实践文档
  - 培训材料更新
```

## ⚠️ 质量红线

### 不可妥协的质量标准
1. **安全性**: 不能有已知的安全漏洞
2. **功能性**: 核心功能必须100%可用
3. **数据完整性**: 不能有数据丢失或损坏
4. **合规性**: 必须符合相关法规要求

### 质量异常处理
```yaml
质量门失败处理:
  轻微失败:
    - 记录问题
    - 制定修复计划
    - 继续执行（有条件）
  
  严重失败:
    - 立即停止流程
    - 回退到稳定状态
    - 修复后重新开始
  
  系统性失败:
    - 全面质量审查
    - 流程改进
    - 工具升级
```

## 📊 项目特定质量配置

### {mode.upper()}模式质量重点
{self._get_mode_specific_quality_focus(mode)}

### 项目质量目标
- **项目名称**: {project_name}
- **质量等级**: 基于{mode}模式的标准
- **关键指标**: 根据项目特征定制

---

**质量承诺**: 我们承诺严格执行这些质量标准，确保每个交付物都达到或超越用户期望，为用户创造真正的价值。

*Generated by AceFlow v3.0 MCP Server - Enhanced Quality Standards*
*项目: {project_name} | 模式: {mode.upper()} | 创建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _get_mode_specific_query_focus(self, mode: str) -> str:
        """Get mode-specific query focus areas."""
        focus_areas = {
            "minimal": """
- **快速决策**: 重点查询快速通道和简化流程
- **核心功能**: 专注于最小可行产品的质量标准
- **时间优化**: 查询时间压缩和效率提升方法
""",
            "standard": """
- **平衡质量**: 查询质量与效率的平衡点
- **标准流程**: 重点关注标准化的最佳实践
- **团队协作**: 查询团队协作和沟通规范
""",
            "complete": """
- **企业标准**: 查询企业级质量和合规要求
- **全面覆盖**: 关注完整的质量保证体系
- **风险管理**: 重点查询风险识别和缓解策略
""",
            "smart": """
- **AI决策**: 查询AI辅助的决策和优化方法
- **自适应流程**: 关注动态调整和智能优化
- **学习机制**: 重点查询知识积累和经验复用
"""
        }
        return focus_areas.get(mode, focus_areas["standard"])

    def _get_mode_specific_quality_focus(self, mode: str) -> str:
        """Get mode-specific quality focus areas."""
        quality_focus = {
            "minimal": """
- **核心功能质量**: 确保基本功能100%可用
- **快速验证**: 重点进行关键路径测试
- **文档精简**: 保证核心文档的完整性
- **部署就绪**: 快速部署和回滚能力
""",
            "standard": """
- **全面质量**: 代码、测试、文档全面覆盖
- **标准合规**: 严格遵循行业标准和最佳实践
- **性能基准**: 满足预定义的性能指标
- **维护性**: 确保代码的长期可维护性
""",
            "complete": """
- **企业级质量**: 满足企业级质量和安全要求
- **合规性**: 符合相关法规和审计要求
- **可扩展性**: 支持大规模部署和扩展
- **监控完备**: 全面的监控和告警体系
""",
            "smart": """
- **智能质量**: AI辅助的质量检查和优化
- **自适应标准**: 根据项目特征动态调整质量标准
- **预测性维护**: 基于数据的质量预测和改进
- **持续学习**: 质量标准的持续优化和演进
"""
        }
        return quality_focus.get(mode, quality_focus["standard"])