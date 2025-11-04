# AceFlow 产物文档结构设计讨论

> 讨论和定义 AceFlow 不同工作流模式下的统一目录结构

**日期**: 2025-01-04
**状态**: 草案 - 待讨论确定

---

## 🤔 现状问题

当前 AceFlow 存在**两套目录结构**，造成混淆：

### 1. 通用工作流模式 (tools.py)
```
project/
├── .aceflow/
│   ├── current_state.json       # 项目状态
│   ├── template.yaml            # 工作流模板
│   └── aceflow-spec_v3.0.md    # 规范文档
├── aceflow_result/              # ⭐ 所有产物输出到这里
│   ├── user_stories.md
│   ├── technical_approach.md
│   ├── test_plan.md
│   ├── src/
│   └── ...
└── README_ACEFLOW.md
```

### 2. Contract-First 模式 (contract_tools.py)
```
project/
├── .aceflow/                    # ⭐ 所有产物输出到这里
│   ├── config.yaml
│   ├── workflow.json
│   ├── contracts/               # OpenAPI 契约
│   ├── requirements/            # 功能需求
│   └── mock/                    # Mock Server PID
└── ...
```

---

## 🎯 统一设计目标

1. **单一产物目录**：所有 AceFlow 产物集中在一个目录
2. **模式区分清晰**：不同模式有不同的子目录结构
3. **易于理解**：开发者一眼就能明白目录用途
4. **工具友好**：方便 .gitignore、部署脚本、CI/CD 集成
5. **向后兼容**：尽量不破坏现有项目

---

## 💡 设计方案讨论

### 方案 A: 统一使用 `aceflow_result/` 作为主输出目录

```
project/
├── .aceflow/                        # ⭐ 配置和状态（不应该被 git 忽略）
│   ├── config.yaml                  # 项目配置
│   ├── workflow.json                # 工作流状态
│   └── current_state.json           # 通用工作流状态
│
├── aceflow_result/                  # ⭐ 所有产物输出（可被 git 忽略）
│   │
│   ├── contracts/                   # Contract-First 模式产物
│   │   ├── datasource-management.json
│   │   ├── data-access.json
│   │   └── ...
│   │
│   ├── requirements/                # 功能需求文档
│   │   ├── datasource-management.md
│   │   ├── data-access.md
│   │   └── ...
│   │
│   ├── docs/                        # 通用工作流模式产物
│   │   ├── user_stories.md
│   │   ├── technical_approach.md
│   │   ├── test_plan.md
│   │   └── ...
│   │
│   ├── src/                         # 源代码（如果 AI 生成）
│   │   ├── backend/
│   │   ├── frontend/
│   │   └── ...
│   │
│   ├── tests/                       # 测试代码
│   │
│   └── mock/                        # Mock Server 相关
│       ├── pids/                    # PID 文件
│       └── data/                    # Mock 数据
│
└── README_ACEFLOW.md                # AceFlow 使用说明
```

**优点**:
- ✅ 所有产物集中在一个目录，易于管理
- ✅ 可以整个目录加入 .gitignore（产物不需要版本控制）
- ✅ 符合现有 tools.py 的设计
- ✅ 清晰的子目录划分

**缺点**:
- ⚠️ 需要修改 contract_tools.py 中的所有路径
- ⚠️ 现有 Contract-First 项目需要迁移

---

### 方案 B: 根据工作流模式使用不同的主目录

```
# Contract-First 模式
project/
├── .aceflow/
│   ├── config.yaml
│   ├── workflow.json
│   ├── contracts/          # ⭐ Contract 产物在配置目录内
│   ├── requirements/
│   └── mock/
└── ...

# 通用工作流模式
project/
├── .aceflow/
│   ├── current_state.json
│   └── template.yaml
├── aceflow_result/         # ⭐ 通用产物在结果目录
│   ├── docs/
│   ├── src/
│   └── tests/
└── ...
```

**优点**:
- ✅ 保持现有两套系统不变
- ✅ 每个模式独立，互不干扰
- ✅ 无需大规模代码修改

**缺点**:
- ❌ 两套标准，用户困惑
- ❌ 难以记忆和理解
- ❌ 不利于模式切换

---

### 方案 C: 统一使用 `.aceflow/` + 明确产物分类

```
project/
├── .aceflow/
│   │
│   ├── config/                      # ⭐ 配置文件（需要版本控制）
│   │   ├── config.yaml
│   │   └── workflow.json
│   │
│   ├── state/                       # ⭐ 运行时状态（不需要版本控制）
│   │   ├── current_state.json
│   │   └── mock_pids/
│   │
│   ├── artifacts/                   # ⭐ 工作产物（根据需要版本控制）
│   │   ├── contracts/               # Contract-First 契约
│   │   ├── requirements/            # 需求文档
│   │   ├── docs/                    # 通用文档
│   │   ├── src/                     # 生成的代码
│   │   └── tests/                   # 测试代码
│   │
│   └── templates/                   # ⭐ 模板文件（需要版本控制）
│       └── template.yaml
│
├── .gitignore                       # 配置忽略规则
│   # .aceflow/state/               # 运行时状态不提交
│   # .aceflow/artifacts/src/       # 生成的代码不提交（可选）
│
└── README_ACEFLOW.md
```

**优点**:
- ✅ 所有 AceFlow 相关文件集中在 `.aceflow/`
- ✅ 清晰的分类：配置、状态、产物、模板
- ✅ 易于配置 .gitignore（按需选择）
- ✅ 符合 "点目录" 的工具配置惯例

**缺点**:
- ⚠️ 需要大规模代码重构
- ⚠️ 与现有两套系统都不同
- ⚠️ 迁移成本高

---

## 🔍 详细对比

### 目录用途分析

| 内容类型 | 是否版本控制 | 方案A位置 | 方案B位置 | 方案C位置 |
|---------|------------|----------|----------|----------|
| **配置文件** | ✅ 是 | `.aceflow/` | `.aceflow/` | `.aceflow/config/` |
| **工作流状态** | ⚠️ 可选 | `.aceflow/` | `.aceflow/` | `.aceflow/state/` |
| **OpenAPI 契约** | ✅ 是 | `aceflow_result/contracts/` | `.aceflow/contracts/` | `.aceflow/artifacts/contracts/` |
| **需求文档** | ✅ 是 | `aceflow_result/requirements/` | `.aceflow/requirements/` | `.aceflow/artifacts/requirements/` |
| **通用文档** | ✅ 是 | `aceflow_result/docs/` | `aceflow_result/docs/` | `.aceflow/artifacts/docs/` |
| **生成的代码** | ⚠️ 可选 | `aceflow_result/src/` | `aceflow_result/src/` | `.aceflow/artifacts/src/` |
| **Mock Server PID** | ❌ 否 | `aceflow_result/mock/` | `.aceflow/mock/` | `.aceflow/state/mock_pids/` |

---

## 💭 推荐方案

### 我的建议：**方案 A（改进版）**

```
project/
├── .aceflow/                        # 配置和状态（少量文件）
│   ├── config.yaml                  # 项目配置（版本控制）
│   ├── workflow.json                # 工作流状态（可选版本控制）
│   └── current_state.json           # 运行时状态（不版本控制）
│
├── aceflow_result/                  # 所有产物输出
│   ├── contracts/                   # OpenAPI 契约（版本控制）
│   ├── requirements/                # 需求文档（版本控制）
│   ├── docs/                        # 通用文档（版本控制）
│   ├── src/                         # 源代码（根据项目决定）
│   ├── tests/                       # 测试（根据项目决定）
│   └── .runtime/                    # 运行时文件（不版本控制）
│       └── mock_pids/               # Mock Server PID
│
├── .gitignore                       # Git 忽略配置
│   # .aceflow/current_state.json
│   # aceflow_result/.runtime/
│   # aceflow_result/src/            # 如果是生成的代码
│
└── README_ACEFLOW.md
```

### 理由：

1. **清晰分离**：
   - `.aceflow/` → 配置和状态（轻量级）
   - `aceflow_result/` → 所有产物（内容丰富）

2. **版本控制友好**：
   - 契约和需求文档应该版本控制（核心资产）
   - 运行时状态不需要版本控制
   - 生成的代码根据项目决定

3. **工具友好**：
   - 产物集中在一个目录，易于清理、部署
   - `.gitignore` 规则简单清晰
   - CI/CD 脚本容易编写

4. **向后兼容**：
   - 保持 `aceflow_result/` 作为主输出（tools.py 无需修改）
   - Contract-First 只需调整路径（contract_tools.py）

---

## 🚀 实施建议

### Phase 1: 立即实施（Contract-First）

修改 `contract_tools.py`，将契约产物移到 `aceflow_result/`:

```python
# 修改前
contracts_dir = Path.cwd() / ".aceflow" / "contracts"
requirements_dir = Path.cwd() / ".aceflow" / "requirements"

# 修改后
contracts_dir = Path.cwd() / "aceflow_result" / "contracts"
requirements_dir = Path.cwd() / "aceflow_result" / "requirements"
```

### Phase 2: 文档更新

- 更新所有文档中的目录结构说明
- 更新 Quick Start Guide
- 更新 Internal Network Deployment Guide

### Phase 3: 迁移工具

提供一个迁移脚本：

```python
# migrate_aceflow_structure.py
from pathlib import Path
import shutil

def migrate_project():
    """迁移现有项目到新结构"""
    old_contracts = Path(".aceflow/contracts")
    new_contracts = Path("aceflow_result/contracts")

    if old_contracts.exists():
        new_contracts.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_contracts), str(new_contracts))
        print(f"✅ 已迁移: {old_contracts} → {new_contracts}")
```

---

## ❓ 待讨论问题

1. **是否接受方案 A**？
   - 如果不接受，倾向于哪个方案？

2. **契约文件是否版本控制**？
   - 我认为应该（这是核心资产）

3. **生成的代码是否版本控制**？
   - 取决于项目类型
   - 建议：默认不控制，由用户决定

4. **Mock Server PID 文件位置**？
   - 建议：`aceflow_result/.runtime/mock_pids/`

5. **迁移策略**？
   - 立即迁移 vs 保持兼容 vs 新老并存

---

## 📝 决策记录

| 日期 | 决策者 | 决策内容 | 理由 |
|-----|-------|---------|-----|
| 2025-01-04 | - | 待定 | 待讨论 |

---

**创建者**: AceFlow Team
**最后更新**: 2025-01-04
