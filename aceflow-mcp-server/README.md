# AceFlow MCP Server v1.1.0

🚀 **Enhanced AI-driven workflow management through Model Context Protocol**

## ✨ What's New in v1.1.0

### 🎯 **Enhanced .clinerules System**
- **5 Comprehensive Prompt Files**: Complete AI Agent guidance system
- **SPEC Integration**: Full integration with AceFlow v3.0 specification
- **Project-Specific Configuration**: Tailored prompts for each project
- **Quality Standards**: Comprehensive quality gate system (DG1-DG5)

### 📋 **New .clinerules Files**
1. **`system_prompt.md`** - Enhanced AI Agent identity and behavior rules
2. **`aceflow_integration.md`** - Complete AceFlow integration guidelines  
3. **`spec_summary.md`** - Quick reference to AceFlow v3.0 specification
4. **`spec_query_helper.md`** - SPEC document query assistance
5. **`quality_standards.md`** - Comprehensive quality standards

## 🚀 Quick Start

### Installation
```bash
pip install aceflow-mcp-server
```

### Basic Usage
```python
# Initialize a new AceFlow project
aceflow_init(mode="standard", project_name="my-project")

# Check project status
aceflow_stage(action="status")

# Validate project quality
aceflow_validate(mode="detailed", report=True)
```

## 📁 Project Structure

```
aceflow-mcp-server/
├── aceflow_mcp_server/          # Core package directory
│   ├── core/                    # Core functionality modules
│   ├── main.py                  # Main entry point
│   ├── tools.py                 # Tool implementations
│   └── ...
├── tests/                       # Formal test suite
├── examples/                    # Examples and demo code
├── scripts/                     # Build and deployment scripts
│   ├── build/                   # Build-related scripts
│   ├── deploy/                  # Deployment scripts
│   └── dev/                     # Development tools
├── docs/                        # Documentation
│   ├── user-guide/              # User guides
│   ├── developer-guide/         # Developer guides
│   └── project/                 # Project documentation
├── dev-tests/                   # Development tests and experiments
└── pyproject.toml               # Project configuration
```

## Overview

AceFlow MCP Server provides structured software development workflows through the Model Context Protocol (MCP), enabling AI clients like Kiro, Cursor, and Claude to manage projects with standardized processes.

## Features

### 🛠️ MCP Tools
- **aceflow_init**: Initialize projects with different workflow modes
- **aceflow_stage**: Manage project stages and workflow progression  
- **aceflow_validate**: Validate project compliance and quality
- **aceflow_template**: Manage workflow templates

### 📊 MCP Resources
- **aceflow://project/state**: Current project state and progress
- **aceflow://workflow/config**: Workflow configuration and settings
- **aceflow://stage/guide/{stage}**: Stage-specific guidance and instructions

### 🤖 MCP Prompts
- **workflow_assistant**: Context-aware workflow guidance
- **stage_guide**: Stage-specific assistance and best practices

## Quick Start

### Installation

```bash
# Install via uvx (recommended)
uvx aceflow-mcp-server

# Or install traditionally
pip install aceflow-mcp-server
```

### MCP Client Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "aceflow": {
      "command": "uvx",
      "args": ["aceflow-mcp-server@latest"],
      "env": {
        "ACEFLOW_LOG_LEVEL": "INFO"
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

### Usage Example

```
User: "I want to start a new AI project with standard workflow"

AI: I'll help you initialize a new project using AceFlow.

[Uses aceflow_init tool]
✅ Project initialized successfully in standard mode!

Current status:
- Project: ai-project
- Mode: STANDARD
- Stage: user_stories (0% complete)

Ready to begin with user story analysis. Would you like guidance for this stage?
```

## Workflow Modes

### Minimal Mode
Fast prototyping and concept validation
- 3 stages: Implementation → Test → Demo
- Ideal for MVPs and quick experiments

### Standard Mode  
Traditional software development workflow
- 8 stages: User Stories → Task Breakdown → Test Design → Implementation → Unit Test → Integration Test → Code Review → Demo
- Balanced approach for most projects

### Complete Mode
Enterprise-grade development process
- 12 stages: Full requirements analysis through security review
- Comprehensive quality gates and documentation

### Smart Mode
AI-enhanced adaptive workflow
- 10 stages with intelligent adaptation
- Dynamic complexity assessment and optimization

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Client     │    │  MCP Server     │    │  AceFlow Core   │
│  (Kiro/Cursor)  │◄──►│   (FastMCP)     │◄──►│    Engine       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  File System    │
                       │ (.aceflow/...)  │
                       └─────────────────┘
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/aceflow/aceflow-mcp-server
cd aceflow-mcp-server

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=aceflow_mcp_server
```

### Project Structure

```
aceflow-mcp-server/
├── aceflow_mcp_server/
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   ├── tools.py           # MCP tools implementation
│   ├── resources.py       # MCP resources
│   ├── prompts.py         # MCP prompts
│   └── core/              # Core functionality
├── tests/                 # Test suite
├── docs/                  # Documentation
└── pyproject.toml         # Project configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation**: https://docs.aceflow.dev/mcp
- **Issues**: https://github.com/aceflow/aceflow-mcp-server/issues
- **Discussions**: https://github.com/aceflow/aceflow-mcp-server/discussions

---

*Generated by AceFlow v3.0 MCP Server*