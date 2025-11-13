# AceFlow v3.1 规范文档

> **版本**: v3.1.0
> **更新时间**: 2025-01-13
> **类型**: AI驱动的合同优先软件开发工作流系统

---

## 1. 概述

### 核心定位
AceFlow 是一个 **AI驱动的 Contract-First 软件开发工作流管理系统**，专为 AI 代理设计，提供标准化、智能化的开发流程管理。

### 核心特性
- ✅ **Contract-First**: OpenAPI合同驱动的前后端协作
- ✅ **双模式流程**: Standard (7阶段) / Complete (10阶段)
- ✅ **AI优化设计**: 简洁高效的模板，专为AI代理设计
- ✅ **状态追踪**: 工作流状态管理和进度跟踪
- ✅ **MCP集成**: 通过MCP协议与AI工具无缝集成

### 适用场景

| 项目类型 | 团队规模 | 推荐模式 | 典型周期 |
|---------|---------|---------|---------|
| 常规功能开发、Bug修复 | 3-10人 | Standard | 5-10天 |
| 大型项目、关键系统 | 10+人 | Complete | 2-4周 |

---

## 2. 工作流模式

### 2.1 Standard 模式（标准流程）

**阶段数**: 7个
**适用**: 大多数项目的日常开发
**周期**: 5-10天

| # | 阶段ID | 名称 | 输出文件 | 核心目标 |
|---|--------|------|---------|---------|
| 1 | user_stories | 用户故事 | user_stories.md | 编写用户故事和验收标准 |
| 2 | task_breakdown | 任务分解 | task_breakdown.md | 分解开发任务 (≤8h/任务) |
| 3 | test_design | 测试设计 | test_design.md | 设计测试用例和策略 |
| 4 | implementation | 功能实现 | implementation.md | 实现功能代码 |
| 5 | unit_test | 单元测试 | unit_test.md | 执行单元测试 (覆盖率≥80%) |
| 6 | integration_test | 集成测试 | integration_test.md | 执行集成测试 (通过率≥95%) |
| 7 | code_review | 代码审查 | code_review.md | 代码质量评审 (评分≥8/10) |

### 2.2 Complete 模式（完整流程）

**阶段数**: 10个
**适用**: 大型项目、关键系统
**周期**: 2-4周

| # | 阶段ID | 名称 | 输出文件 | 核心目标 |
|---|--------|------|---------|---------|
| 1 | requirement_analysis | 需求分析 | requirement_analysis.md | 项目目标、功能需求、约束条件 |
| 2 | architecture_design | 架构设计 | architecture_design.md | 技术选型、系统架构、模块设计 |
| 3 | user_stories | 用户故事 | user_stories.md | 编写用户故事和验收标准 |
| 4 | task_breakdown | 任务分解 | task_breakdown.md | 分解开发任务 (≤8h/任务) |
| 5 | test_design | 测试设计 | test_design.md | 设计测试用例和策略 |
| 6 | implementation | 功能实现 | implementation.md | 实现功能代码 |
| 7 | unit_test | 单元测试 | unit_test.md | 执行单元测试 (覆盖率≥80%) |
| 8 | integration_test | 集成测试 | integration_test.md | 执行集成测试 (通过率≥95%) |
| 9 | performance_test | 性能测试 | performance_test.md | 性能测试和优化 (可选) |
| 10 | code_review | 代码审查 | code_review.md | 代码质量评审 (评分≥8/10) |

**Complete vs Standard 差异**:
- Complete 额外包含: requirement_analysis, architecture_design, performance_test
- Complete 适合需要详细需求分析和架构设计的大型项目

---

## 3. 目录结构

```
project_root/
├── .aceflow/                           # AceFlow配置目录
│   ├── config.yaml                     # 项目配置
│   ├── current_state.json              # 工作流状态
│   └── contract/                       # OpenAPI合同仓库配置
│
├── aceflow_result/                     # 执行结果目录
│   └── {iteration_id}/                 # 迭代目录
│       ├── {mode}/                     # standard 或 complete
│       │   ├── user_stories.md
│       │   ├── task_breakdown.md
│       │   ├── test_design.md
│       │   ├── implementation.md
│       │   ├── unit_test.md
│       │   ├── integration_test.md
│       │   └── code_review.md
│       └── contract/                   # 合同文件
│           └── {feature}_openapi.yaml
│
└── aceflow/                            # AceFlow核心
    └── templates/                      # 模板库
        ├── standard/                   # Standard模式7个模板
        │   ├── user_stories.md
        │   ├── task_breakdown.md
        │   ├── test_design.md
        │   ├── implementation.md
        │   ├── unit_test.md
        │   ├── integration_test.md
        │   └── code_review.md
        └── complete/                   # Complete模式10个模板
            ├── requirement_analysis.md
            ├── architecture_design.md
            ├── user_stories.md
            ├── task_breakdown.md
            ├── test_design.md
            ├── implementation.md
            ├── unit_test.md
            ├── integration_test.md
            ├── performance_test.md
            └── code_review.md
```

---

## 4. 配置说明

### 4.1 项目配置 (.aceflow/config.yaml)

```yaml
project:
  name: "项目名称"
  openapi_url: "https://api.example.com/openapi.yaml"

contract:
  repository_url: "git@github.com:org/contracts.git"
  repository_path: "contracts/backend"
  branch: "main"

smtp:
  enabled: false
  smtp_server: ""
  smtp_port: 587
```

### 4.2 工作流状态 (.aceflow/current_state.json)

```json
{
  "iteration_id": "iter_20250113_001",
  "mode": "standard",
  "current_stage": "implementation",
  "stages": {
    "user_stories": {"status": "completed", "progress": 100},
    "task_breakdown": {"status": "completed", "progress": 100},
    "test_design": {"status": "completed", "progress": 100},
    "implementation": {"status": "in_progress", "progress": 65}
  }
}
```

**状态值**:
- `pending`: 待开始
- `in_progress`: 进行中
- `completed`: 已完成
- `skipped`: 已跳过
- `blocked`: 被阻塞

---

## 5. MCP工具集成

AceFlow通过MCP (Model Context Protocol) 提供AI工具集成：

### 核心工具

| 工具名 | 功能 | 用途 |
|--------|------|------|
| `aceflow_init_workflow` | 初始化工作流 | 开始新迭代 |
| `aceflow_get_workflow_state` | 获取工作流状态 | 查看当前进度 |
| `aceflow_update_stage_status` | 更新阶段状态 | 标记阶段完成 |
| `aceflow_generate_stage_document` | 生成阶段文档 | 基于模板生成文档 |
| `aceflow_validate_workflow` | 验证工作流 | 检查流程完整性 |

### Contract工具

| 工具名 | 功能 | 用途 |
|--------|------|------|
| `aceflow_generate_contract` | 生成合同 | 从代码生成OpenAPI |
| `aceflow_push_contract` | 推送合同 | 推送到Git仓库 |
| `aceflow_start_mock_server` | 启动Mock服务 | 前端开发Mock |
| `aceflow_stop_mock_server` | 停止Mock服务 | 停止Mock服务 |

---

## 6. 使用流程

### 6.1 初始化项目

```bash
# 安装
pip install aceflow-mcp-server

# 初始化配置
aceflow init

# 配置项目信息（交互式）
```

### 6.2 启动工作流

通过AI工具（Cline/Claude Code）调用MCP工具：

```
AI: 我需要开始一个新的功能开发迭代
User: 功能名称是"用户认证"，使用Standard模式

[AI调用] aceflow_init_workflow(
  iteration_id="iter_20250113_001",
  mode="standard",
  feature_name="用户认证"
)

[AI生成] 基于模板生成各阶段文档
```

### 6.3 推进阶段

```
[阶段1完成]
AI: 用户故事已完成，更新状态

[AI调用] aceflow_update_stage_status(
  stage="user_stories",
  status="completed"
)

[AI调用] aceflow_generate_stage_document(
  stage="task_breakdown"
)

AI: 开始任务分解阶段...
```

---

## 7. 质量标准

### 代码质量
- 单元测试覆盖率 ≥ 80%
- 代码审查评分 ≥ 8/10
- 遵循项目编码规范

### 测试质量
- 单元测试通过率 = 100%
- 集成测试通过率 ≥ 95%
- 性能测试达标（Complete模式）

### 文档质量
- 每个阶段生成对应文档
- 文档内容完整、准确
- 合同文件符合OpenAPI规范

---

## 8. 模板设计原则

AceFlow v3.1 模板专为AI代理优化：

### ✅ 简洁高效
- 去除冗余的"示例占位"
- 每类内容保留1个示例+说明
- 用表格替代重复文本结构

### ✅ 表格驱动
- 核心内容使用表格组织
- 便于AI快速填充
- 减少提示词消耗

### ✅ 单例示范
- 保留1个完整示例
- 添加"_按需添加更多_"说明
- AI根据实际需求扩展

**示例对比**:

❌ **旧版（冗余）**:
```markdown
## US-001: [标题]
...详细内容...

## US-002: [标题]
...详细内容...

## US-003: [标题]
...详细内容...
```

✅ **新版（精简）**:
```markdown
## US-001: [标题]
...详细内容...

_按相同格式添加 US-002, US-003 等更多用户故事_
```

---

## 9. Contract-First工作流

### 9.1 核心理念
- OpenAPI合同作为前后端协作的"Single Source of Truth"
- 前端基于Mock Server开发，后端基于合同实现
- 合同变更触发通知和自动化流程

### 9.2 典型流程

```
1. [架构设计] → 设计API接口
2. [生成合同] → 从设计生成OpenAPI文件
3. [推送合同] → 推送到Git合同仓库
4. [通知前端] → 邮件/钉钉通知前端团队
5. [启动Mock] → 启动Mock Server (Prism)
6. [前端开发] → 前端基于Mock开发
7. [后端开发] → 后端基于合同实现
8. [集成测试] → 前后端集成验证
```

### 9.3 工具链
- **合同生成**: Spring Boot + Swagger / FastAPI自动生成
- **Mock Server**: Prism CLI
- **合同仓库**: Git独立仓库
- **通知**: SMTP邮件 / 钉钉Webhook

---

## 10. 版本历史

- **v3.1.0** (2025-01-13):
  - 精简模板设计 (减少24%冗余)
  - 移除Minimal和Smart模式
  - 更新为Standard/Complete双模式
  - 优化阶段定义（10/7阶段）
  - AI-First设计原则

- **v3.0.0** (2025-11-06):
  - Contract-First工作流
  - MCP协议集成
  - 模板系统重构

- **v2.0.0** (2025-07):
  - 基础PATEOAS流程
  - 8阶段Complete模式

---

**© 2025 AceFlow Team**
