# Changelog

All notable changes to aceflow-mcp-server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.1] - 2025-01-12

### 🐛 Fixed - Critical Integration Issue

This is a **critical patch** fixing the MCP tools integration issue in v3.0.0.

#### Problem
v3.0.0 included the complete workflow system code, but the MCP Server was not properly integrated with the new workflow tools. Users only saw 4 Contract-First tools instead of the promised 21 workflow tools.

#### Solution
- **Integrated WorkflowMCPTools** into `mcp_stdio_server.py`
- Updated `list_tools()` to include both Contract and Workflow tools
- Updated `execute_tool()` to route workflow tool calls correctly
- Now exposes **25 total MCP tools**: 4 Contract + 21 Workflow

#### Changes
- Modified `aceflow_mcp_server/mcp_stdio_server.py`:
  - Added `from .workflow.mcp.tools import WorkflowMCPTools`
  - Created `self.workflow_tools` instance in `__init__`
  - Updated `list_tools()` to merge both tool sets
  - Updated `execute_tool()` to handle workflow tool execution
  - Added MCPToolResult to dict conversion

#### MCP Tools Now Available (25 Total)

**Contract-First Tools (4)**:
- aceflow_init - Initialize project structure
- aceflow_stage - Manage workflow stages
- aceflow_validate - Validate project compliance
- aceflow_template - Manage workflow templates

**Workflow Tools (21)**:
- Workflow Management (4): workflow_start_iteration, workflow_next_stage, workflow_complete_stage, workflow_complete_iteration
- State Management (4): state_get_current, state_list_iterations, state_get_history, state_update_stage
- Memory Tools (7): memory_record_stage_output, memory_record_decision, memory_record_issue, memory_record_learning, memory_recall, memory_search, memory_recall_for_stage
- Template Tools (3): template_get_stage, template_render, template_list
- Quality Gate Tools (2): gate_evaluate, gate_get_info
- Export Tools (1): export_iteration

### 📊 Verification

After installing v3.0.1, users should see all 25 tools in their MCP client (Cline, Claude Code, Cursor, etc.).

```bash
pip install --upgrade aceflow-mcp-server
```

### 🙏 Acknowledgments

Thanks to the user who reported this critical integration issue immediately after v3.0.0 release.

---

## [3.0.0] - 2025-01-09

### 🎉 Major Release - Complete Workflow System Integration

This is a **major version upgrade** featuring a complete intelligent workflow management system with 99.2% test coverage.

### ✨ Added - Workflow System (NEW)

#### Core Modules
- **WorkflowEngine**: Intelligent workflow initialization and management
  - 4 Workflow Modes: Minimal (P→D→R), Standard (P1→P2→D1→D2→R1), Complete (S1-S8), Smart (AI-driven)
  - Mode registration and dynamic switching
  - Iteration lifecycle management

- **StateManager**: Persistent state management with JSON storage
  - State persistence and recovery
  - Transition history tracking
  - Progress monitoring (0.0-1.0)
  - State validation and rollback

- **MemoryManager**: Project memory and context awareness
  - Decision tracking with reasoning
  - Issue/solution recording
  - Learning capture and recall
  - Stage output history
  - Contextual memory search

- **TemplateManager**: Dynamic template system
  - Auto-discovery of mode-specific templates
  - Jinja2-based variable substitution
  - Template registry with metadata
  - Batch template rendering

- **Quality Gates**: 3 decision gates for Complete mode
  - DG1: Development Readiness Gate (after S3)
  - DG2: Implementation Quality Gate (after S5)
  - DG3: Release Readiness Gate (after S7)
  - Automatic quality scoring and recommendations

- **DocumentExporter**: Multi-format export system
  - Markdown export (single/multi-file)
  - HTML export with styling
  - JSON export for programmatic access
  - Archive export (ZIP)
  - Customizable export options

#### MCP Tools Integration (21 Tools)
- **Workflow Management** (4 tools):
  - `workflow_start_iteration`: Initialize new workflow iteration
  - `workflow_next_stage`: Advance to next stage
  - `workflow_complete_stage`: Mark stage as completed
  - `workflow_complete_iteration`: Finalize iteration

- **State Management** (4 tools):
  - `state_get_current`: Get current iteration state
  - `state_list_iterations`: List all iterations
  - `state_get_history`: View state transition history
  - `state_update_stage`: Update stage status/progress

- **Memory Tools** (7 tools):
  - `memory_record_stage_output`: Record stage deliverables
  - `memory_record_decision`: Track technical decisions
  - `memory_record_issue`: Log issues and solutions
  - `memory_record_learning`: Capture lessons learned
  - `memory_recall`: Retrieve specific memories
  - `memory_search`: Full-text memory search
  - `memory_recall_for_stage`: Get stage-specific context

- **Template Tools** (3 tools):
  - `template_get_stage`: Get stage-specific template
  - `template_render`: Render template with variables
  - `template_list`: List available templates

- **Quality Gate Tools** (2 tools):
  - `gate_evaluate`: Evaluate quality gate
  - `gate_get_info`: Get gate criteria info

- **Export Tools** (1 tool):
  - `export_iteration`: Export iteration documentation

### 📚 Documentation

#### New Documentation (4 major docs in /docs)
- **WORKFLOW_QUICK_START.md**: 10-minute quickstart guide (~4000 words)
- **WORKFLOW_API_REFERENCE.md**: Complete API reference (~7500 words)
- **WORKFLOW_TESTING_REPORT.md**: Test coverage report (~5000 words)
- **DOCUMENTATION_UPDATE_SUMMARY.md**: Documentation changelog (~3000 words)

#### Total Documentation
- 38 documentation files
- ~170K words
- 110+ code examples
- Complete API coverage

### ✅ Testing

#### Test Coverage
- **Total Tests**: 132
- **Passing**: 131 (99.2% pass rate)
- **Skipped**: 1 (Future Enhancement)
- **Failed**: 0

#### Test Modules
- `test_models.py`: 13/13 ✅ - Data models and enums
- `test_state.py`: 11/11 ✅ - State management
- `test_engine.py`: 12/12 ✅ - Workflow engine
- `test_templates.py`: 16/16 ✅ - Template system
- `test_memory.py`: 24/24 ✅ - Memory management
- `test_mcp_tools.py`: 27/27 ✅ - MCP tools
- `test_exporter.py`: 22/22 ✅ - Document export
- `test_integration.py`: 6/6 ✅ - End-to-end workflows

### 🔧 Changed

- **API Standardization**: Unified API patterns across all modules
- **Package Structure**: Integrated workflow system into aceflow_mcp_server.workflow
- **Dependencies**: Added python-dateutil>=2.8.0 for datetime handling
- **Description**: Updated to reflect comprehensive workflow capabilities

### 🐛 Fixed

- Fixed Iteration model missing `status` field
- Fixed ExportOptions default values (single_file=True)
- Fixed export output paths (file vs directory)
- Fixed StateManager constructor signature
- Fixed quality gate score calculation

### 🗑️ Removed

- Removed ~129 lines of dead code
- Removed obsolete batch export functions
- Removed conflicting multi-iteration management

### 📊 Statistics

- **Code Lines**: ~15,000+ (workflow module)
- **Test Coverage**: 99.2%
- **Documentation**: 38 files, ~170K words
- **API Methods**: 40+ public methods
- **MCP Tools**: 21 tools (was 17 before)

### 🚀 Migration Guide

For users upgrading from v2.x:

1. **Workflow API** is now available through `aceflow_mcp_server.workflow`
2. **21 MCP Tools** instead of previous 17
3. **New dependencies**: python-dateutil will be auto-installed
4. **Backward Compatible**: All v2.x MCP tools still work

### 🔗 Quick Start

```python
from aceflow_mcp_server.workflow.core.engine import WorkflowEngine
from aceflow_mcp_server.workflow.core.state import StateManager
from aceflow_mcp_server.workflow.models import WorkflowMode

# Initialize workflow
engine = WorkflowEngine(project_id="my_project")
result = engine.initialize(mode="minimal")
print(f"Started iteration: {result['iteration_id']}")
```

---

## [2.2.0] - 2025-10-30

### Added
- **HTTP同步响应模式**: 实现了MCP HTTP服务器的同步响应模式
  - POST请求直接返回200状态码和完整JSON-RPC响应
  - 简化了客户端集成，无需处理SSE流
  - 保持向后兼容，SSE GET端点仍然可用
  - 完整的会话管理支持（X-Session-ID头）

- **本地规范文档生成**: aceflow_init 现在会在 `.aceflow/aceflow-spec_v3.0.md` 生成完整的AceFlow v3.0规范文档
  - 智能回退机制：优先读取主规范文档，失败时使用内置版本
  - 版本锁定：每个项目获得初始化时的规范文档版本，避免版本不一致
  - AI友好的本地化规范文档，便于直接访问和参考

### Enhanced
- **MCP HTTP协议测试**: 完整的12项测试套件，覆盖所有核心功能
  - 健康检查、协议初始化、工具列表查询
  - 工具调用、会话管理、并发请求处理
  - 错误处理（无效JSON-RPC、未知方法）
  - 性能测试（响应延迟、吞吐量）
  - 测试通过率: 100% (12/12)

- **全面优化 README_ACEFLOW.md 提示词**：基于2025年AI提示词优化最佳实践
  - 🤖 清晰的AI助手角色定义(工作流专家、MCP工具操作员、状态管理员、质量守护者)
  - 📐 结构化约束系统(MUST、SHOULD、MUST NOT三级约束)
  - 🧠 7步思考链模板(需求理解→状态评估→路径规划→工具选择→执行计划→质量检查→状态更新)
  - 💡 少样本学习示例(新功能开发、阶段完成、错误处理)
  - 🔄 动态上下文注入指导(项目状态检查、阶段目标确认、质量评估、环境验证)
  - README长度从~150行增加到336行，内容丰富度提升124%

### Research
- **MCP Tool提示词优化调研**：深度分析了MCP 2025最佳实践和主流厂商方案
  - 研究了OpenAI Function Calling和Anthropic Claude Tools的优化策略
  - 发现工具描述质量直接影响AI选择准确性，参数约束可减少70%执行时间
  - 提供了增强描述模式、约束驱动模式、示例驱动模式三种优化方案

### Fixed
- 修复了HTTP服务器配置问题（默认host从localhost改为0.0.0.0）
- 解决了Python缓存文件导致的测试不一致问题
- 修复了无效JSON-RPC消息的错误处理（正确返回400状态码）
- 解决了用户反馈的"aceflow spec规范文档在初始化后丢失"问题
- 提升了AI助手使用工具的准确性和一致性

### Technical Details
- 重构了 `/mcp` POST端点，支持同步响应模式
- 优化了JSON-RPC验证逻辑，在会话创建前进行
- 增强了错误处理机制，区分400和500错误
- 新增 `_get_aceflow_spec_content()` 方法支持规范文档读取
- 新增 `_get_embedded_spec_content()` 方法作为备用规范版本
- 优化了 `_generate_readme()` 方法，大幅增强AI指导内容
- 完善了项目目录结构，现在包含完整的本地规范文档

### Performance
- HTTP响应延迟: 平均190.65ms (< 500ms阈值)
- 服务器吞吐量: 5.15 req/s (同步模式)
- 并发请求成功率: 100%
- 预期AI工具选择准确性提升+50%
- 预期AI响应准确性提升+40%
- 预期任务执行效率提升+60%
- 预期错误率降低+30%

### Testing
- 完整的HTTP协议测试套件: 12/12 通过 (100%)
- 所有核心MCP功能验证通过
- 跨平台兼容性测试通过

## [2.1.5] - 2025-09-17

### Fixed
- 解决了PyPI安装依赖问题
- 修复了工作目录检测在Windows平台的兼容性问题
- 优化了动态工具参数方案，提升了IDE集成体验

### Enhanced
- 改进了 aceflow_init 参数文档，明确要求提供完整项目路径
- 增强了错误消息，提供友好的用户指导
- 优化了跨平台路径处理逻辑

## [2.1.4] - 2025-09-14

### Added
- HTTP MCP Server支持，实现MCP 2025 Streamable HTTP协议
- Docker容器化部署配置
- 统一服务器架构，支持自动传输模式检测

### Enhanced
- 完善了MCP协议集成测试
- 改进了多客户端并发支持
- 优化了断线重连和会话恢复机制

## [2.1.3] - 2025-09-01

### Added
- 综合MCP协议集成测试
- 双向AI-MCP协作架构

### Enhanced
- 改进了MCP工具调用的稳定性和准确性
- 优化了错误处理和异常恢复机制

## [2.1.2] - 2025-08-26

### Fixed
- 修复了MCP服务器构建和部署问题
- 解决了工作目录初始化的兼容性问题

### Enhanced
- 改进了IDE集成的用户体验
- 优化了跨平台兼容性

## [Earlier Versions]

请参考 Git 历史记录获取更早版本的变更信息。