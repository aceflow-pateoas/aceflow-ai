# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AceFlow-AI is a dual-purpose AI-driven development framework consisting of:

1. **aceflow** - Core workflow engine with 4 modes (Minimal, Standard, Complete, Smart) for AI-driven development
2. **aceflow-mcp-server** - MCP (Model Context Protocol) server providing 25+ tools for AI collaboration (21 workflow + 4 contract-first tools)

**Current Version**: v3.0.0
**Python**: 3.8+
**Key Technology**: PATEOAS (Prompt as the Engine of AI State) architecture

## Repository Structure

```
aceflow-ai/
├── aceflow/                    # Core workflow engine package
│   ├── workflow/              # Main workflow system (v3.0)
│   │   ├── core/             # WorkflowEngine, StateManager
│   │   ├── modes/            # 4 workflow modes implementations
│   │   ├── memory/           # Memory system for decisions/issues/learnings
│   │   ├── templates/        # Jinja2 template system
│   │   ├── gates/            # Quality decision gates (DG1/DG2/DG3)
│   │   ├── exporter/         # Document export (MD/HTML/JSON/Archive)
│   │   └── mcp/              # MCP tools integration
│   ├── pateoas/              # Legacy PATEOAS system (being phased out)
│   ├── templates/            # Workflow templates (unified source)
│   └── config/               # Configuration management
│
├── aceflow-mcp-server/        # MCP server package (separate deployable)
│   ├── aceflow_mcp_server/
│   │   ├── core/             # Core MCP implementations
│   │   ├── workflow/         # Workflow-specific MCP tools
│   │   ├── contract/         # Contract-First development tools
│   │   ├── security/         # Security systems (4 modules)
│   │   ├── performance/      # Performance optimization (3 modules)
│   │   ├── recovery/         # Fault detection & auto-recovery (3 modules)
│   │   ├── error_handling/   # Unified error handling
│   │   └── cli/              # CLI commands
│   └── tests/                # MCP server tests (57 tests, 88.1% coverage)
│
├── tests/                     # Main package tests (132 tests, 99.2% pass rate)
├── docs/                      # Comprehensive documentation (~170K words)
└── demo/                      # Demo projects and examples
```

## Development Commands

### Testing

```bash
# Run all tests for main package
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=aceflow --cov-report=html --cov-report=term-missing

# Run specific test markers
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m workflow      # Workflow-related tests
pytest -m mcp           # MCP tool tests
pytest -m slow          # Slow tests (usually skipped)

# Run single test file
pytest tests/test_workflow.py -v

# Run specific test function
pytest tests/test_workflow.py::test_minimal_workflow -v

# MCP Server tests (in aceflow-mcp-server/)
cd aceflow-mcp-server
pytest tests/ -v
```

### Code Quality

```bash
# Format code (line length: 100 for aceflow, 88 for MCP server)
black aceflow/ --line-length 100
black aceflow-mcp-server/ --line-length 88

# Sort imports
isort aceflow/
isort aceflow-mcp-server/

# Linting
flake8 aceflow/
flake8 aceflow-mcp-server/

# Type checking
mypy aceflow/
mypy aceflow-mcp-server/
```

### Building and Installing

```bash
# Install in development mode (main package)
pip install -e .
pip install -e ".[dev]"      # With dev dependencies
pip install -e ".[all]"      # With all extras (dev, mcp, export)

# Install MCP server (separate package)
cd aceflow-mcp-server
pip install -e .
pip install -e ".[all]"      # With all extras

# Build packages
python -m build              # Main package
cd aceflow-mcp-server && python -m build  # MCP server

# Verify package
twine check dist/*
```

### Running MCP Server

```bash
# STDIO mode (for Claude Desktop, Cline, etc.)
aceflow-mcp-server

# HTTP mode (for web-based clients)
aceflow-mcp-http --port 8000

# Unified server (both STDIO and HTTP)
aceflow-mcp-unified

# CLI commands
aceflow init --mode standard
aceflow contract generate --feature user-management
```

## Architecture Deep Dive

### Workflow System Architecture (aceflow/workflow/)

The workflow system is built on a **state machine pattern** with PATEOAS principles:

1. **WorkflowEngine** (`workflow/core/engine.py`)
   - Entry point for workflow operations
   - Manages mode registration and iteration initialization
   - Constructor: `WorkflowEngine(project_id: str)`
   - Key method: `initialize(mode, metadata, iteration_id)`

2. **StateManager** (`workflow/core/state.py`)
   - Persistent state storage using JSON files in `.aceflow/state/`
   - Manages iteration lifecycle and stage transitions
   - Constructor: `StateManager(project_id: str, state_dir: Path = None)`
   - Critical: Thread-safe operations for state updates

3. **4 Workflow Modes** (`workflow/modes/`)
   - **Minimal**: User Stories → Implementation → Testing
   - **Standard**: 7 stages (user_stories → task_breakdown → test_design → implementation → unit_test → integration_test → code_review)
   - **Complete**: 10 stages (adds requirement_analysis, architecture_design, performance_test)
   - **Smart**: Adaptive mode that selects appropriate workflow based on task complexity

4. **Memory System** (`workflow/memory/`)
   - `MemoryManager`: Stores and retrieves project knowledge
   - 5 memory types: context, decision, pattern, issue, learning
   - Contextual search with relevance scoring
   - Storage: `.aceflow/memory/` as JSON

5. **Template System** (`workflow/templates/`)
   - Jinja2-based templates for each stage
   - Auto-discovery from `aceflow/templates/{mode}/`
   - Variable substitution for dynamic content
   - Templates are the **single source of truth** (unified under aceflow/templates/)

6. **Quality Gates** (`workflow/gates/`)
   - DG1: Security & Architecture Review
   - DG2: Code Quality & Test Coverage
   - DG3: Performance & Production Readiness
   - Only active in Complete mode

### MCP Server Architecture (aceflow-mcp-server/)

The MCP server provides **25 tools** organized into 5 systems:

1. **Core MCP Tools** (4 tools in `tools.py`)
   - `aceflow_init`, `aceflow_stage`, `aceflow_validate`, `aceflow_template`
   - Standard workflow management

2. **Contract-First Tools** (21 tools in `contract_tools.py`)
   - Project init, feature definition, API design
   - Contract generation, Git push/pull
   - Mock server management (Prism-based)
   - Contract validation and completion

3. **Enterprise Systems** (NEW - 85-90% complete)
   - **Performance** (`performance/`): CacheManager, PerformanceMonitor, LazyLoader
   - **Security** (`security/`): InputValidator, AccessController, DataProtector, AuditLogger
   - **Recovery** (`recovery/`): FaultDetector, AutoRecovery, HealthChecker
   - **Error Handling** (`error_handling/`): Unified error handling with 5 severity levels

4. **MCP Protocol Layers**
   - STDIO Server (`mcp_stdio_server.py`): For desktop clients
   - HTTP Server (`mcp_http_server.py`): FastAPI-based for web clients
   - Unified Server (`unified_server.py`): Both protocols simultaneously

### Critical Data Flow

```
User Request (AI Client)
    ↓
MCP Tool Call → WorkflowEngine.initialize(mode="standard")
    ↓
StateManager.initialize_iteration(iteration)
    ↓
Mode Implementation (e.g., StandardWorkflow.get_stages())
    ↓
TemplateManager.get_stage_template(stage_id)
    ↓
Return stage guidance to AI
    ↓
AI completes stage → StateManager.advance_stage()
    ↓
MemoryManager.record_output(stage_output)
    ↓
Quality Gates evaluation (if Complete mode)
    ↓
Next stage or iteration completion
```

## Critical Design Patterns

### 1. Template Directory Structure (IMPORTANT)

**aceflow/templates/** is the **ONLY** template source. Never create templates elsewhere.

```
aceflow/templates/
├── minimal/      # Minimal mode templates
├── standard/     # Standard mode templates (7 stages)
├── complete/     # Complete mode templates (10 stages)
└── document_templates/  # Shared document templates
```

**DO NOT** use `aceflow-mcp-server/aceflow_mcp_server/workflow/templates/` - this is deprecated.

### 2. State Persistence Pattern

All state is stored in `.aceflow/` directory:
- `.aceflow/state/{project_id}/` - Iteration states (JSON)
- `.aceflow/memory/{project_id}/` - Memory storage (JSON)
- `.aceflow/config.yaml` - Project configuration

**NEVER** modify state files directly - always use StateManager/MemoryManager APIs.

### 3. MCP Tool Response Format

All MCP tools MUST return this structure:

```python
{
    "success": bool,
    "data": dict,      # Tool-specific data
    "message": str,    # Human-readable message
    "error": str | None  # Only if success=False
}
```

### 4. Error Handling Pattern

Use the unified error handler from `aceflow_mcp_server.error_handling`:

```python
from aceflow_mcp_server.error_handling import ErrorHandler, ErrorCategory

@ErrorHandler.handle_errors(category=ErrorCategory.VALIDATION)
def my_function():
    # Your code
    pass
```

## Known Issues and Gotchas

### Git Status Warnings

The repository currently has **untracked files** in `aceflow-mcp-server/aceflow_mcp_server/`:
- `error_handling/` (NEW enterprise system)
- `performance/` (NEW enterprise system)
- `recovery/` (NEW enterprise system)
- `security/` (NEW enterprise system)
- Various `tools_*.py` backup files

These are completed but not yet committed on the `feature/refactoring` branch.

### Dual Package Structure

This is **intentionally** a monorepo with 2 separate Python packages:
- `aceflow-ai` (main package) - Published to PyPI
- `aceflow-mcp-server` (MCP server) - Published separately to PyPI

Each has its own `pyproject.toml` and can be installed independently.

### Legacy Code to Avoid

- `aceflow/pateoas/` - Legacy system, being phased out
- `aceflow-mcp-server/aceflow_mcp_server/workflow/templates/` - Use `aceflow/templates/` instead
- Any `tools_backup.py`, `tools_temp.py`, etc. - Temporary files during refactoring

### Test Execution Context

When running tests, ensure you're in the correct directory:
- Main tests: Run from repository root
- MCP server tests: Run from `aceflow-mcp-server/` directory

Tests expect specific directory structures in `.aceflow/` - they create temporary test directories.

## Version and Release Information

**Main Package** (aceflow-ai):
- Current: v3.0.0
- Released: 2025-01-09
- Changelog: CHANGELOG.md

**MCP Server** (aceflow-mcp-server):
- Current: v3.0.2
- Status: Ready for PyPI (95% deployment ready)
- Release guide: aceflow-mcp-server/PYPI_PUBLISH_GUIDE.md

## Documentation Structure

Key docs for reference:
- `docs/WORKFLOW_API_REFERENCE.md` - Complete API documentation (~7500 words)
- `docs/WORKFLOW_QUICK_START.md` - 10-minute tutorial
- `docs/MCP_TOOLS_COMPLETE_CATALOG.md` - All 25 MCP tools
- `aceflow-mcp-server/SYSTEM_COMPLETION_REPORT.md` - Enterprise systems status
- `aceflow-mcp-server/COMPLETION_REPORT.md` - MCP server completion report

## Working with This Codebase

### When Adding New Features

1. **Workflow changes**: Modify `aceflow/workflow/` modules
2. **New MCP tools**: Add to `aceflow-mcp-server/aceflow_mcp_server/tools.py` or `contract_tools.py`
3. **New templates**: Add to `aceflow/templates/{mode}/`
4. **Tests**: Add to appropriate `tests/` directory with pytest markers

### When Debugging

1. Check `.aceflow/state/` for current iteration state
2. Check `.aceflow/memory/` for stored memories
3. Enable debug logging in StateManager/WorkflowEngine
4. Use `pytest -v -s` to see print statements

### When Refactoring

1. This is a production system with users - maintain backward compatibility
2. Update CHANGELOG.md following Keep a Changelog format
3. Maintain 80%+ test coverage
4. Update API reference docs if public APIs change
5. Templates are user-facing - changes affect AI guidance quality
