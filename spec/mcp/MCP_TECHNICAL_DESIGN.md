# AceFlow MCP Server - 技术设计文档

## 🏗️ 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Client Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    Kiro     │  │   Cursor    │  │   Claude    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP Protocol
┌─────────────────────▼───────────────────────────────────────┐
│                MCP Server Layer                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              FastMCP Framework                          ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    ││
│  │  │    Tools    │  │  Resources  │  │   Prompts   │    ││
│  │  └─────────────┘  └─────────────┘  └─────────────┘    ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │ Python API
┌─────────────────────▼───────────────────────────────────────┐
│                AceFlow Core Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Project   │  │  Workflow   │  │  Template   │        │
│  │   Manager   │  │   Engine    │  │   System    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────┬───────────────────────────────────────┘
                      │ File I/O
┌─────────────────────▼───────────────────────────────────────┐
│                 File System Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ .aceflow/   │  │aceflow_result/│ │.clinerules/ │        │
│  │   config    │  │   outputs   │  │   prompts   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件设计

#### 1. MCP Server 主程序

```python
# aceflow_mcp_server/server.py
from fastmcp import FastMCP
from .tools import AceFlowTools
from .resources import AceFlowResources
from .prompts import AceFlowPrompts

class AceFlowMCPServer:
    def __init__(self):
        self.mcp = FastMCP("AceFlow")
        self.tools = AceFlowTools()
        self.resources = AceFlowResources()
        self.prompts = AceFlowPrompts()
        
        self._register_tools()
        self._register_resources()
        self._register_prompts()
    
    def _register_tools(self):
        """注册所有工具"""
        self.mcp.add_tool(self.tools.aceflow_init)
        self.mcp.add_tool(self.tools.aceflow_stage)
        self.mcp.add_tool(self.tools.aceflow_validate)
        self.mcp.add_tool(self.tools.aceflow_template)
    
    def _register_resources(self):
        """注册所有资源"""
        self.mcp.add_resource(self.resources.project_state)
        self.mcp.add_resource(self.resources.workflow_config)
        self.mcp.add_resource(self.resources.stage_guide)
    
    def _register_prompts(self):
        """注册所有提示词"""
        self.mcp.add_prompt(self.prompts.workflow_assistant)
        self.mcp.add_prompt(self.prompts.stage_guide)
    
    def run(self):
        """启动MCP服务器"""
        self.mcp.run()
```

#### 2. 工具实现

```python
# aceflow_mcp_server/tools.py
from fastmcp.tools import tool
from aceflow.core import ProjectManager, WorkflowEngine
from typing import Dict, Any, Optional

class AceFlowTools:
    def __init__(self):
        self.project_manager = ProjectManager()
        self.workflow_engine = WorkflowEngine()
    
    @tool
    def aceflow_init(
        self,
        mode: str,
        project_name: Optional[str] = None,
        directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initialize AceFlow project with specified mode"""
        try:
            result = self.project_manager.initialize_project(
                mode=mode,
                name=project_name,
                directory=directory
            )
            return {
                "success": True,
                "message": f"Project initialized successfully in {mode} mode",
                "project_info": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize project"
            }
    
    @tool
    def aceflow_stage(
        self,
        action: str,
        stage: Optional[str] = None
    ) -> Dict[str, Any]:
        """Manage project stages and workflow"""
        try:
            if action == "status":
                result = self.workflow_engine.get_current_status()
            elif action == "next":
                result = self.workflow_engine.advance_to_next_stage()
            elif action == "list":
                result = self.workflow_engine.list_all_stages()
            elif action == "reset":
                result = self.workflow_engine.reset_project()
            else:
                raise ValueError(f"Unknown action: {action}")
            
            return {
                "success": True,
                "action": action,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute stage action: {action}"
            }
    
    @tool
    def aceflow_validate(
        self,
        mode: str = "basic",
        fix: bool = False,
        report: bool = False
    ) -> Dict[str, Any]:
        """Validate project compliance and quality"""
        try:
            validator = self.project_manager.get_validator()
            result = validator.validate(
                mode=mode,
                auto_fix=fix,
                generate_report=report
            )
            return {
                "success": True,
                "validation_result": result,
                "message": "Validation completed successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Validation failed"
            }
    
    @tool
    def aceflow_template(
        self,
        action: str,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Manage workflow templates"""
        try:
            template_manager = self.project_manager.get_template_manager()
            
            if action == "list":
                result = template_manager.list_templates()
            elif action == "apply":
                if not template:
                    raise ValueError("Template name required for apply action")
                result = template_manager.apply_template(template)
            elif action == "validate":
                result = template_manager.validate_current_template()
            else:
                raise ValueError(f"Unknown action: {action}")
            
            return {
                "success": True,
                "action": action,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Template action failed: {action}"
            }
```

#### 3. 资源提供

```python
# aceflow_mcp_server/resources.py
from fastmcp.resources import resource
from aceflow.core import ProjectManager
from typing import Dict, Any
import json

class AceFlowResources:
    def __init__(self):
        self.project_manager = ProjectManager()
    
    @resource("aceflow://project/state")
    def project_state(self) -> str:
        """Get current project state"""
        try:
            state = self.project_manager.get_current_state()
            return json.dumps(state, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "message": "Failed to get project state"
            })
    
    @resource("aceflow://workflow/config")
    def workflow_config(self) -> str:
        """Get workflow configuration"""
        try:
            config = self.project_manager.get_workflow_config()
            return json.dumps(config, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "message": "Failed to get workflow config"
            })
    
    @resource("aceflow://stage/guide/{stage}")
    def stage_guide(self, stage: str) -> str:
        """Get stage-specific guidance"""
        try:
            guide = self.project_manager.get_stage_guide(stage)
            return guide
        except Exception as e:
            return f"# Error\n\nFailed to get guide for stage '{stage}': {str(e)}"
```

#### 4. 提示词管理

```python
# aceflow_mcp_server/prompts.py
from fastmcp.prompts import prompt
from aceflow.core import ProjectManager
from typing import Dict, Any, Optional

class AceFlowPrompts:
    def __init__(self):
        self.project_manager = ProjectManager()
    
    @prompt
    def workflow_assistant(
        self,
        task: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """Generate workflow assistance prompt"""
        try:
            current_state = self.project_manager.get_current_state()
            current_stage = current_state.get("flow", {}).get("current_stage", "unknown")
            
            base_prompt = f"""
You are an AceFlow workflow assistant. You help users manage their software development projects using structured workflows.

Current Project Status:
- Project: {current_state.get("project", {}).get("name", "Unknown")}
- Mode: {current_state.get("project", {}).get("mode", "Unknown")}
- Current Stage: {current_stage}
- Progress: {current_state.get("flow", {}).get("progress_percentage", 0)}%

Available Tools:
- aceflow_init: Initialize new projects
- aceflow_stage: Manage project stages
- aceflow_validate: Validate project compliance
- aceflow_template: Manage templates

Guidelines:
1. Always check current project status before making changes
2. Follow the defined workflow stages in order
3. Validate project compliance regularly
4. Provide clear, actionable guidance
5. Use appropriate templates for consistency
"""
            
            if task:
                base_prompt += f"\n\nCurrent Task: {task}"
            
            if context:
                base_prompt += f"\n\nAdditional Context: {context}"
            
            return base_prompt
            
        except Exception as e:
            return f"Error generating workflow assistant prompt: {str(e)}"
    
    @prompt
    def stage_guide(self, stage: str) -> str:
        """Generate stage-specific guidance prompt"""
        try:
            guide = self.project_manager.get_stage_guide(stage)
            
            prompt = f"""
You are providing guidance for the '{stage}' stage of an AceFlow project.

Stage Guide:
{guide}

Instructions:
1. Help the user understand what needs to be done in this stage
2. Provide specific, actionable steps
3. Suggest best practices and quality standards
4. Identify potential risks and mitigation strategies
5. Prepare for the next stage transition

Remember to:
- Be specific and practical
- Focus on deliverables and outcomes
- Maintain quality standards
- Consider the overall project context
"""
            return prompt
            
        except Exception as e:
            return f"Error generating stage guide prompt for '{stage}': {str(e)}"
```

### 打包和分发

#### 1. PyPI 包结构

```
aceflow-mcp-server/
├── aceflow_mcp_server/
│   ├── __init__.py
│   ├── server.py
│   ├── tools.py
│   ├── resources.py
│   ├── prompts.py
│   └── core/
│       ├── __init__.py
│       ├── project_manager.py
│       ├── workflow_engine.py
│       └── template_manager.py
├── tests/
│   ├── __init__.py
│   ├── test_tools.py
│   ├── test_resources.py
│   └── test_integration.py
├── docs/
│   ├── README.md
│   ├── INSTALLATION.md
│   └── API.md
├── pyproject.toml
├── README.md
└── LICENSE
```

#### 2. pyproject.toml 配置

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "aceflow-mcp-server"
version = "1.0.0"
description = "AceFlow MCP Server for AI-driven workflow management"
readme = "README.md"
license = {file = "LICENSE"}
authors = [
    {name = "AceFlow Team", email = "team@aceflow.dev"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
requires-python = ">=3.8"
dependencies = [
    "fastmcp>=0.1.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "click>=8.0.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/aceflow/aceflow-mcp-server"
Documentation = "https://docs.aceflow.dev/mcp"
Repository = "https://github.com/aceflow/aceflow-mcp-server.git"
Issues = "https://github.com/aceflow/aceflow-mcp-server/issues"

[project.scripts]
aceflow-mcp-server = "aceflow_mcp_server.server:main"

[tool.hatch.build.targets.wheel]
packages = ["aceflow_mcp_server"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=aceflow_mcp_server --cov-report=html --cov-report=term-missing"
```

#### 3. 入口点实现

```python
# aceflow_mcp_server/__main__.py
import sys
from .server import main

if __name__ == "__main__":
    sys.exit(main())
```

```python
# aceflow_mcp_server/server.py (main函数)
import click
from .server import AceFlowMCPServer

@click.command()
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--port', default=8000, type=int, help='Port to bind to')
@click.option('--log-level', default='INFO', help='Log level')
@click.version_option()
def main(host: str, port: int, log_level: str):
    """Start AceFlow MCP Server"""
    server = AceFlowMCPServer()
    server.run(host=host, port=port, log_level=log_level)

if __name__ == "__main__":
    main()
```

### 部署和使用

#### 1. 发布到 PyPI

```bash
# 构建包
python -m build

# 上传到 PyPI
python -m twine upload dist/*
```

#### 2. 用户安装和使用

```bash
# 安装 (通过 uvx)
uvx aceflow-mcp-server

# 或者传统安装
pip install aceflow-mcp-server
```

#### 3. MCP 客户端配置

```json
{
  "mcpServers": {
    "aceflow": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@latest"],
      "env": {
        "ACEFLOW_LOG_LEVEL": "INFO",
        "ACEFLOW_CONFIG_DIR": "~/.aceflow"
      },
      "disabled": false,
      "autoApprove": [
        "aceflow_init",
        "aceflow_stage",
        "aceflow_validate",
        "aceflow_template"
      ]
    }
  }
}
```

### 测试策略

#### 1. 单元测试

```python
# tests/test_tools.py
import pytest
from aceflow_mcp_server.tools import AceFlowTools

class TestAceFlowTools:
    def setup_method(self):
        self.tools = AceFlowTools()
    
    def test_aceflow_init_success(self):
        result = self.tools.aceflow_init(
            mode="minimal",
            project_name="test-project"
        )
        assert result["success"] is True
        assert "test-project" in result["message"]
    
    def test_aceflow_init_invalid_mode(self):
        result = self.tools.aceflow_init(mode="invalid")
        assert result["success"] is False
        assert "error" in result
    
    def test_aceflow_stage_status(self):
        # 先初始化项目
        self.tools.aceflow_init(mode="standard", project_name="test")
        
        result = self.tools.aceflow_stage(action="status")
        assert result["success"] is True
        assert "result" in result
```

#### 2. 集成测试

```python
# tests/test_integration.py
import pytest
import tempfile
import os
from aceflow_mcp_server.server import AceFlowMCPServer

class TestIntegration:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        self.server = AceFlowMCPServer()
    
    def test_full_workflow(self):
        # 测试完整的工作流程
        # 1. 初始化项目
        init_result = self.server.tools.aceflow_init(
            mode="minimal",
            project_name="integration-test"
        )
        assert init_result["success"] is True
        
        # 2. 检查状态
        status_result = self.server.tools.aceflow_stage(action="status")
        assert status_result["success"] is True
        
        # 3. 验证项目
        validate_result = self.server.tools.aceflow_validate()
        assert validate_result["success"] is True
    
    def teardown_method(self):
        os.chdir("/")
        # 清理临时目录
```

这个技术设计文档提供了AceFlow MCP Server的详细实现方案，包括架构设计、核心组件实现、打包分发和测试策略。通过这个设计，用户可以通过简单的`uvx aceflow-mcp-server`命令就能使用AceFlow的所有功能，大大简化了安装和使用流程。