# AceFlow 项目重构方案 v1.0

**创建时间**: 2025-11-08
**状态**: 草案
**目标**: 解决当前项目结构混乱、架构不受控的问题

---

## 📋 目录

1. [当前问题分析](#当前问题分析)
2. [重构目标](#重构目标)
3. [新架构设计](#新架构设计)
4. [重构计划](#重构计划)
5. [风险评估](#风险评估)

---

## 🔍 当前问题分析

### 1. 目录结构混乱

**问题表现**:
```
aceflow-ai/
├── aceflow/                    # 核心流程定义(22个Python文件)
│   ├── pateoas/                # PATEOAS实现(22个文件)
│   ├── ai/                     # AI决策引擎
│   ├── scripts/                # 各种脚本
│   ├── templates/              # 模板文件(刚整理完)
│   └── venv/                   # ❌ 虚拟环境不应在此
│
├── aceflow-mcp-server/         # MCP Server实现
│   ├── aceflow_mcp_server/     # 主包(44个Python文件)
│   ├── final_test_env/         # ❌ 测试环境
│   ├── verification_env/       # ❌ 测试环境
│   ├── test_v2_env/            # ❌ 测试环境
│   ├── pypi_test_env/          # ❌ 测试环境
│   ├── mcp_test_env/           # ❌ 测试环境
│   ├── build_env/              # ❌ 构建环境
│   ├── claude_code_test_env/   # ❌ 测试环境
│   ├── release_env/            # ❌ 发布环境
│   └── test_v204_env/          # ❌ 测试环境
│
├── test_install_env/           # ❌ 根目录测试环境
├── real_project_test/          # ❌ 测试目录
├── test_fixed_env/             # ❌ 测试环境
├── fresh_project_test/         # ❌ 测试目录
├── test/                       # ❌ 测试目录
└── .venv/                      # ❌ 根目录虚拟环境
```

**严重性**: 🔴 高
- 至少12个临时测试环境散落各处
- 功能模块职责不清晰
- 代码重复(aceflow和aceflow-mcp-server都有workflow相关代码)

### 2. 架构不受控

**问题表现**:
- `aceflow/pateoas/` 22个文件,部分功能重复
- `aceflow-mcp-server/` 44个文件,包含workflow engine和template manager
- aceflow和mcp-server之间边界模糊
- 4个核心功能分散在不同位置:
  - ❌ 流程定义在aceflow和mcp-server都有
  - ❌ 模板管理在aceflow和mcp-server都有
  - ❌ 记忆管理只在aceflow/pateoas
  - ❌ MCP工具在aceflow-mcp-server

**严重性**: 🔴 高

### 3. 代码重复

**发现的重复**:
- `aceflow/pateoas/state_manager.py` vs `aceflow/pateoas/optimized_state_manager.py`
- `aceflow/pateoas/decision_gates.py` vs `aceflow/pateoas/decision_gates_clean.py`
- `aceflow/scripts/cli/` 多个CLI实现
- Workflow engine在两个地方

**严重性**: 🟡 中

---

## 🎯 重构目标

### 核心目标

根据用户需求,聚焦4个核心功能:

1. **AceFlow 工作流流程定义** (Workflow Process Definition)
2. **工作流模板管理** (Template Management)
3. **工作流记忆管理** (Memory Management)
4. **MCP Tools 管理** (stdio + http 协议支持)

### 架构原则

1. **单一职责**: 每个模块只负责一个核心功能
2. **清晰边界**: 核心功能之间接口明确
3. **可测试性**: 代码可单元测试,测试环境隔离
4. **可维护性**: 代码组织清晰,易于理解和扩展
5. **零散文件清理**: 删除所有临时测试环境

---

## 🏗️ 新架构设计

### 顶层目录结构

```
aceflow-ai/
│
├── aceflow/                    # 核心库 (Core Library)
│   ├── __init__.py
│   ├── workflow/               # 核心功能1: 工作流流程定义
│   ├── templates/              # 核心功能2: 模板管理
│   ├── memory/                 # 核心功能3: 记忆管理
│   └── utils/                  # 工具函数
│
├── aceflow-mcp-server/         # MCP Server (核心功能4)
│   ├── __init__.py
│   ├── server/                 # MCP Server实现(stdio + http)
│   ├── tools/                  # MCP Tools定义
│   ├── adapters/               # 与aceflow核心的适配器
│   └── cli/                    # CLI工具
│
├── tests/                      # 所有测试 (统一管理)
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   └── e2e/                    # 端到端测试
│
├── docs/                       # 文档
│   ├── api/                    # API文档
│   ├── guides/                 # 使用指南
│   └── specs/                  # 规范文档
│
├── examples/                   # 示例项目
│
├── scripts/                    # 开发脚本
│   ├── setup.sh                # 环境设置
│   ├── clean.sh                # 清理临时文件
│   └── test.sh                 # 测试脚本
│
├── .aceflow/                   # AceFlow配置(供示例使用)
│   ├── config.yaml
│   └── templates/
│
├── .github/                    # GitHub配置
├── .gitignore                  # Git忽略配置
├── pyproject.toml              # 项目配置
├── README.md                   # 项目说明
└── CHANGELOG.md                # 变更日志
```

### 核心功能1: 工作流流程定义

**位置**: `aceflow/workflow/`

```
aceflow/workflow/
├── __init__.py
├── core/                       # 核心引擎
│   ├── __init__.py
│   ├── engine.py               # 统一的Workflow Engine
│   ├── state.py                # 状态管理(合并optimized_state_manager)
│   ├── transitions.py          # 状态转换逻辑
│   └── validators.py           # 验证器
│
├── modes/                      # 4种模式定义
│   ├── __init__.py
│   ├── minimal.py              # Minimal模式(P→D→R)
│   ├── standard.py             # Standard模式(P1→P2→D1→D2→R1)
│   ├── complete.py             # Complete模式(S1-S8)
│   └── smart.py                # Smart模式(AI驱动)
│
├── stages/                     # 阶段定义
│   ├── __init__.py
│   ├── base.py                 # 基础Stage类
│   ├── planning.py             # 规划阶段
│   ├── development.py          # 开发阶段
│   └── review.py               # 评审阶段
│
├── gates/                      # Decision Gates (质量门)
│   ├── __init__.py
│   ├── dg1.py                  # DG1: Development Readiness
│   ├── dg2.py                  # DG2: Implementation Quality
│   ├── dg3.py                  # DG3: Release Readiness
│   └── evaluator.py            # Gate评估器
│
└── models/                     # 数据模型
    ├── __init__.py
    ├── iteration.py            # Iteration模型
    ├── stage.py                # Stage模型
    └── task.py                 # Task模型
```

**职责**:
- ✅ 定义4种工作流模式(Minimal, Standard, Complete, Smart)
- ✅ 管理工作流状态转换
- ✅ 实现Decision Gates质量控制
- ✅ 提供工作流引擎核心API

**移除重复**:
- 合并 `pateoas/state_manager.py` 和 `pateoas/optimized_state_manager.py`
- 合并 `pateoas/decision_gates.py` 和 `pateoas/decision_gates_clean.py`
- 整合 `pateoas/flow_controller.py`

### 核心功能2: 模板管理

**位置**: `aceflow/templates/`

```
aceflow/templates/
├── __init__.py
├── manager.py                  # 模板管理器(统一)
├── renderer.py                 # 模板渲染引擎(Jinja2)
├── loader.py                   # 模板加载器
├── validator.py                # 模板验证器
│
├── library/                    # 模板库(已整理好的)
│   ├── README.md
│   ├── minimal/                # Minimal模式模板
│   ├── standard/               # Standard模式模板
│   ├── complete/               # Complete模式模板
│   ├── smart/                  # Smart模式模板
│   └── document_templates/     # 通用文档模板
│
└── custom/                     # 用户自定义模板
    └── README.md
```

**职责**:
- ✅ 管理所有模板文件(Minimal/Standard/Complete/Smart)
- ✅ 提供模板渲染功能(变量替换)
- ✅ 支持自定义模板
- ✅ 模板验证和加载

**移除重复**:
- 统一 `aceflow/templates/` 和 `aceflow-mcp-server/core/template_manager.py`

### 核心功能3: 记忆管理

**位置**: `aceflow/memory/`

```
aceflow/memory/
├── __init__.py
├── manager.py                  # 记忆管理器
├── storage.py                  # 存储引擎
├── retrieval.py                # 检索引擎(Smart Recall)
├── indexer.py                  # 索引器
│
├── categories/                 # 5种记忆类型
│   ├── __init__.py
│   ├── requirement.py          # REQ: 需求记忆
│   ├── decision.py             # DEC: 决策记忆
│   ├── pattern.py              # PATTERN: 模式记忆
│   ├── issue.py                # ISSUE: 问题记忆
│   └── learning.py             # LEARN: 学习记忆
│
└── models/                     # 记忆数据模型
    ├── __init__.py
    ├── base.py                 # 基础Memory类
    └── schemas.py              # 记忆Schema定义
```

**职责**:
- ✅ 管理5种记忆类型(REQ, DEC, PATTERN, ISSUE, LEARN)
- ✅ 实现智能检索(Smart Recall)
- ✅ 跨迭代记忆持久化
- ✅ 记忆索引和查询

**移除重复**:
- 整合 `pateoas/memory_system.py`
- 整合 `pateoas/optimized_memory_retrieval.py`
- 整合 `pateoas/smart_recall.py`
- 整合 `pateoas/memory_categories.py`

### 核心功能4: MCP Tools管理

**位置**: `aceflow-mcp-server/`

```
aceflow-mcp-server/
├── __init__.py
├── server/                     # MCP Server实现
│   ├── __init__.py
│   ├── stdio.py                # stdio协议支持
│   ├── http.py                 # http协议支持
│   └── unified.py              # 统一服务器(合并两种协议)
│
├── tools/                      # MCP Tools定义
│   ├── __init__.py
│   ├── workflow_tools.py       # 工作流相关工具
│   ├── template_tools.py       # 模板相关工具
│   ├── memory_tools.py         # 记忆相关工具
│   ├── contract_tools.py       # 契约管理工具
│   └── analysis_tools.py       # 分析工具
│
├── adapters/                   # 适配器层
│   ├── __init__.py
│   ├── workflow_adapter.py     # 连接aceflow.workflow
│   ├── template_adapter.py     # 连接aceflow.templates
│   └── memory_adapter.py       # 连接aceflow.memory
│
├── resources/                  # MCP Resources
│   ├── __init__.py
│   └── resources.py            # Resource定义
│
├── prompts/                    # MCP Prompts
│   ├── __init__.py
│   ├── generator.py            # Prompt生成器
│   └── intelligent.py          # 智能Prompt生成
│
├── cli/                        # CLI工具
│   ├── __init__.py
│   ├── main.py                 # 主CLI入口
│   ├── init.py                 # aceflow init
│   ├── contract.py             # 契约管理
│   └── mock.py                 # Mock Server
│
└── config/                     # 配置管理
    ├── __init__.py
    └── settings.py             # 配置类
```

**职责**:
- ✅ 提供MCP Server(stdio + http 双协议)
- ✅ 定义所有MCP Tools
- ✅ 通过适配器调用aceflow核心功能
- ✅ 提供CLI工具
- ✅ 契约管理(Contract-First开发)

**移除重复**:
- 统一 `mcp_stdio_server.py`, `mcp_http_server.py`, `unified_server.py`
- 整合所有tool定义到tools/
- 移除workflow_engine.py和template_manager.py(使用adapter调用aceflow核心)

---

## 📅 重构计划

### Phase 1: 清理和准备 (1-2天)

#### 任务清单

1. **清理临时文件** (0.5天)
   - [ ] 删除所有test_*_env目录 (12个)
   - [ ] 删除real_project_test/, fresh_project_test/, test/
   - [ ] 更新.gitignore,防止再次提交临时文件
   - [ ] 提交: "chore: clean up temporary test environments"

2. **备份当前代码** (0.5天)
   - [ ] 创建feature/refactoring分支
   - [ ] 标记当前状态为backup tag
   - [ ] 文档化当前功能清单

3. **依赖分析** (0.5天)
   - [ ] 列出aceflow和aceflow-mcp-server的所有依赖关系
   - [ ] 识别可复用的代码
   - [ ] 标记待删除的重复代码

### Phase 2: 核心功能重构 (5-7天)

#### 2.1 工作流流程定义 (2天)

- [ ] 创建 `aceflow/workflow/` 目录结构
- [ ] 实现 `workflow/core/engine.py` (统一引擎)
- [ ] 合并state_manager → `workflow/core/state.py`
- [ ] 合并decision_gates → `workflow/gates/`
- [ ] 实现4种模式: `workflow/modes/`
- [ ] 编写单元测试
- [ ] 提交: "refactor: implement unified workflow engine"

#### 2.2 模板管理 (1.5天)

- [ ] 保留已整理的 `aceflow/templates/library/`
- [ ] 实现 `templates/manager.py`
- [ ] 实现 `templates/renderer.py` (Jinja2)
- [ ] 从mcp-server移除template_manager,使用adapter
- [ ] 编写单元测试
- [ ] 提交: "refactor: unified template management system"

#### 2.3 记忆管理 (1.5天)

- [ ] 创建 `aceflow/memory/` 目录结构
- [ ] 整合memory_system → `memory/manager.py`
- [ ] 整合smart_recall → `memory/retrieval.py`
- [ ] 实现5种记忆类型: `memory/categories/`
- [ ] 编写单元测试
- [ ] 提交: "refactor: unified memory management system"

#### 2.4 MCP Tools管理 (2天)

- [ ] 创建 `aceflow-mcp-server/server/` (统一stdio+http)
- [ ] 创建 `aceflow-mcp-server/adapters/` (连接aceflow核心)
- [ ] 整合所有工具到 `tools/`
- [ ] 重构CLI: `cli/main.py`
- [ ] 编写集成测试
- [ ] 提交: "refactor: unified MCP server with dual protocols"

### Phase 3: 测试和文档 (2-3天)

#### 3.1 测试 (1.5天)

- [ ] 创建统一测试目录 `tests/`
- [ ] 单元测试覆盖率 >80%
- [ ] 集成测试(所有核心功能)
- [ ] E2E测试(完整工作流)
- [ ] 性能测试
- [ ] 提交: "test: comprehensive test suite for refactored codebase"

#### 3.2 文档 (1天)

- [ ] 更新README.md (新架构说明)
- [ ] 编写API文档 `docs/api/`
- [ ] 更新使用指南 `docs/guides/`
- [ ] 更新.clinerules/aceflow_integration.md
- [ ] 编写迁移指南 (从旧版本迁移)
- [ ] 提交: "docs: comprehensive documentation for v3.0 refactoring"

#### 3.3 发布准备 (0.5天)

- [ ] 更新CHANGELOG.md
- [ ] 更新版本号 → v3.0.0
- [ ] 创建发布说明
- [ ] 合并到main分支
- [ ] 标记v3.0.0 tag

---

## ⚠️ 风险评估

### 高风险

| 风险 | 可能性 | 影响度 | 应对措施 |
|------|--------|--------|----------|
| 重构破坏现有功能 | 中 | 高 | 1. 充分的单元测试<br/>2. 保留旧代码备份<br/>3. 逐步迁移 |
| 依赖关系复杂导致重构困难 | 中 | 高 | 1. 详细的依赖分析<br/>2. 先重构独立模块<br/>3. 使用适配器模式 |

### 中风险

| 风险 | 可能性 | 影响度 | 应对措施 |
|------|--------|--------|----------|
| 重构时间超出预期 | 高 | 中 | 1. 分阶段执行<br/>2. 每个Phase可独立交付<br/>3. 优先核心功能 |
| 测试覆盖不足 | 中 | 中 | 1. TDD开发模式<br/>2. 代码审查<br/>3. 集成CI/CD |

### 低风险

| 风险 | 可能性 | 影响度 | 应对措施 |
|------|--------|--------|----------|
| 文档不及时更新 | 低 | 低 | 1. 代码和文档同步更新<br/>2. 文档审查 |

---

## 📊 成功指标

### 代码质量

- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试通过率 100%
- [ ] 代码重复率 < 5%
- [ ] 代码复杂度降低 30%

### 架构清晰度

- [ ] 4个核心功能边界清晰
- [ ] 目录层级 ≤ 4层
- [ ] 每个模块职责单一
- [ ] 依赖关系单向

### 可维护性

- [ ] 新功能开发时间减少 20%
- [ ] Bug修复时间减少 30%
- [ ] 代码审查时间减少 25%

---

## 🚀 下一步行动

**立即执行** (需要用户确认):

1. ✅ 用户review本重构方案
2. ❓ 用户确认是否同意此方案
3. ❓ 是否立即开始Phase 1清理工作?

**建议**:
- 先执行Phase 1清理(低风险,快速见效)
- 然后逐步执行Phase 2重构(分模块,可回滚)
- 最后补充测试和文档(确保质量)

---

**文档版本**: v1.0
**作者**: Claude Code
**最后更新**: 2025-11-08
