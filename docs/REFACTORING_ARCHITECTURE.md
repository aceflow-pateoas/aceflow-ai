# AceFlow v3.0 重构架构图

**版本**: v1.0
**日期**: 2025-11-08

---

## 📐 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        AceFlow v3.0                              │
│                   AI-Driven Development Workflow                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
      ┌─────────▼─────────┐         ┌──────────▼──────────┐
      │  aceflow (Core)   │         │ aceflow-mcp-server  │
      │   核心库           │◄────────│   MCP Server        │
      └───────────────────┘ Adapter └─────────────────────┘
                │                              │
    ┌───────────┼───────────┐                  │
    │           │           │                  │
┌───▼───┐ ┌────▼────┐ ┌────▼────┐      ┌──────▼──────┐
│Workflow│ │Templates│ │ Memory  │      │ stdio + http│
│  流程   │ │  模板   │ │  记忆   │      │   双协议     │
└────────┘ └─────────┘ └─────────┘      └─────────────┘
```

---

## 🏛️ 四大核心功能架构

### 1️⃣ Workflow 工作流流程定义

```
aceflow/workflow/
│
├── core/                        # 核心引擎层
│   ├── engine.py                # 工作流引擎
│   │   ├── WorkflowEngine       # 主引擎类
│   │   │   ├── initialize()     # 初始化迭代
│   │   │   ├── execute()        # 执行工作流
│   │   │   ├── transition()     # 状态转换
│   │   │   └── validate()       # 验证状态
│   │   │
│   ├── state.py                 # 状态管理
│   │   ├── StateManager         # 状态管理器
│   │   │   ├── get_state()      # 获取当前状态
│   │   │   ├── update()         # 更新状态
│   │   │   ├── persist()        # 持久化
│   │   │   └── load()           # 加载状态
│   │   │
│   ├── transitions.py           # 状态转换
│   │   ├── Transition           # 转换类
│   │   │   ├── validate()       # 验证转换合法性
│   │   │   ├── execute()        # 执行转换
│   │   │   └── rollback()       # 回滚转换
│   │   │
│   └── validators.py            # 验证器
│       ├── StageValidator       # 阶段验证器
│       ├── TaskValidator        # 任务验证器
│       └── GateValidator        # 质量门验证器
│
├── modes/                       # 4种模式定义
│   ├── minimal.py               # Minimal: P→D→R
│   │   ├── MinimalWorkflow      # Minimal工作流类
│   │   │   ├── stages = [P, D, R]
│   │   │   └── duration = "0.5-2天"
│   │
│   ├── standard.py              # Standard: P1→P2→D1→D2→R1
│   │   ├── StandardWorkflow     # Standard工作流类
│   │   │   ├── stages = [P1, P2, D1, D2, R1]
│   │   │   └── duration = "3-7天"
│   │
│   ├── complete.py              # Complete: S1→S2→...→S8
│   │   ├── CompleteWorkflow     # Complete工作流类
│   │   │   ├── stages = [S1..S8]
│   │   │   ├── gates = [DG1, DG2, DG3]
│   │   │   └── duration = "1-4周"
│   │
│   └── smart.py                 # Smart: AI驱动
│       ├── SmartWorkflow        # Smart工作流类
│       │   ├── analyze()        # 复杂度分析
│       │   ├── recommend()      # 模式推荐
│       │   ├── adjust()         # 动态调整
│       │   └── learn()          # 学习优化
│
├── stages/                      # 阶段定义
│   ├── base.py
│   │   └── BaseStage            # 基础阶段类
│   │       ├── enter()          # 进入阶段
│   │       ├── execute()        # 执行阶段
│   │       ├── exit()           # 退出阶段
│   │       └── validate()       # 验证完成
│   │
│   ├── planning.py              # P/P1/P2阶段
│   ├── development.py           # D/D1/S4阶段
│   └── review.py                # R/R1/S6阶段
│
├── gates/                       # Decision Gates
│   ├── dg1.py                   # DG1: Development Readiness
│   │   ├── check_user_stories() # 用户故事检查
│   │   ├── check_tasks()        # 任务拆分检查
│   │   └── check_tests()        # 测试用例检查
│   │
│   ├── dg2.py                   # DG2: Implementation Quality
│   │   ├── check_tests_pass()   # 测试通过率
│   │   ├── check_coverage()     # 代码覆盖率
│   │   └── check_performance()  # 性能基准
│   │
│   ├── dg3.py                   # DG3: Release Readiness
│   │   ├── check_uat()          # 用户验收测试
│   │   └── check_deployment()   # 部署就绪度
│   │
│   └── evaluator.py
│       └── GateEvaluator        # 质量门评估器
│           ├── evaluate()       # 评估质量门
│           ├── generate_report()# 生成报告
│           └── recommend()      # 推荐措施
│
└── models/                      # 数据模型
    ├── iteration.py
    │   └── Iteration            # 迭代模型
    │       ├── id: str
    │       ├── mode: str
    │       ├── stages: List[Stage]
    │       └── metadata: dict
    │
    ├── stage.py
    │   └── Stage                # 阶段模型
    │       ├── id: str
    │       ├── name: str
    │       ├── status: str
    │       └── progress: float
    │
    └── task.py
        └── Task                 # 任务模型
            ├── id: str
            ├── description: str
            ├── status: str
            └── estimated_hours: int
```

**数据流**:
```
用户请求
   │
   ▼
WorkflowEngine.initialize(mode="standard")
   │
   ├──► StateManager.create()
   ├──► modes/standard.py → 创建5个Stage
   └──► persist to state.json
   │
   ▼
WorkflowEngine.execute(stage="P1")
   │
   ├──► StateManager.get_current_stage() → P1
   ├──► stages/planning.py → 执行P1逻辑
   └──► TemplateManager.render("P1_requirements.md")
   │
   ▼
WorkflowEngine.transition(from="P1", to="P2")
   │
   ├──► Validator.validate_completion(P1)
   ├──► StateManager.update(current_stage="P2")
   └──► persist to state.json
```

---

### 2️⃣ Templates 模板管理

```
aceflow/templates/
│
├── manager.py                   # 模板管理器
│   └── TemplateManager
│       ├── load(mode, stage)    # 加载模板
│       ├── render(template, context) # 渲染模板
│       ├── validate(template)   # 验证模板
│       └── list_templates()     # 列出所有模板
│
├── renderer.py                  # 渲染引擎
│   └── Jinja2Renderer
│       ├── render()             # 渲染模板
│       ├── register_filter()    # 注册过滤器
│       └── register_function()  # 注册函数
│
├── loader.py                    # 加载器
│   └── TemplateLoader
│       ├── load_from_file()     # 从文件加载
│       ├── load_from_string()   # 从字符串加载
│       └── scan_directory()     # 扫描目录
│
├── validator.py                 # 验证器
│   └── TemplateValidator
│       ├── validate_syntax()    # 语法验证
│       ├── validate_variables() # 变量验证
│       └── validate_structure() # 结构验证
│
└── library/                     # 模板库
    ├── minimal/                 # Minimal模式模板
    │   ├── planning.md          # P阶段模板
    │   ├── development.md       # D阶段模板
    │   └── review.md            # R阶段模板
    │
    ├── standard/                # Standard模式模板
    │   ├── p1_requirements.md   # P1阶段模板
    │   ├── p2_design.md         # P2阶段模板
    │   ├── d1_implementation.md # D1阶段模板
    │   ├── d2_testing.md        # D2阶段模板
    │   └── r1_release.md        # R1阶段模板
    │
    ├── complete/                # Complete模式模板
    │   ├── s1_user_story.md     # S1阶段模板
    │   ├── s2_tasks_main.md     # S2阶段模板
    │   ├── ...                  # S3-S8模板
    │   └── s8_summary_report.md
    │
    └── smart/                   # Smart模式模板
        ├── dynamic_prompts.md   # 动态提示模板
        └── decision_engine.md   # 决策引擎模板
```

**使用流程**:
```
Workflow Engine请求渲染
   │
   ▼
TemplateManager.load(mode="standard", stage="P1")
   │
   ├──► TemplateLoader.load_from_file("library/standard/p1_requirements.md")
   ├──► TemplateValidator.validate_syntax()
   └──► 返回Template对象
   │
   ▼
TemplateManager.render(template, context={
    "iteration_id": "iter_001",
    "project_name": "用户管理系统",
    "start_time": "2025-11-06"
})
   │
   ├──► Jinja2Renderer.render()
   │       ├── 替换 {iteration_id} → "iter_001"
   │       ├── 替换 {project_name} → "用户管理系统"
   │       └── 替换 {start_time} → "2025-11-06"
   │
   └──► 返回渲染后的Markdown内容
   │
   ▼
输出到 aceflow_result/iter_001/standard/P1_requirements/requirements.md
```

---

### 3️⃣ Memory 记忆管理

```
aceflow/memory/
│
├── manager.py                   # 记忆管理器
│   └── MemoryManager
│       ├── store(memory)        # 存储记忆
│       ├── retrieve(query)      # 检索记忆
│       ├── update(memory_id)    # 更新记忆
│       ├── delete(memory_id)    # 删除记忆
│       └── smart_recall()       # 智能回忆
│
├── storage.py                   # 存储引擎
│   └── MemoryStorage
│       ├── FileStorage          # 文件存储(默认)
│       │   ├── save()
│       │   └── load()
│       └── DatabaseStorage      # 数据库存储(可选)
│           ├── save()
│           └── load()
│
├── retrieval.py                 # 检索引擎
│   └── MemoryRetrieval
│       ├── search_by_tag()      # 按标签检索
│       ├── search_by_keyword()  # 按关键词检索
│       ├── search_by_time()     # 按时间检索
│       └── smart_recall()       # 智能回忆(上下文感知)
│
├── indexer.py                   # 索引器
│   └── MemoryIndexer
│       ├── index()              # 建立索引
│       ├── update_index()       # 更新索引
│       └── rebuild_index()      # 重建索引
│
├── categories/                  # 5种记忆类型
│   ├── requirement.py           # REQ: 需求记忆
│   │   └── RequirementMemory
│   │       ├── original: str
│   │       ├── refined: str
│   │       ├── acceptance_criteria: List[str]
│   │       └── related_stories: List[str]
│   │
│   ├── decision.py              # DEC: 决策记忆
│   │   └── DecisionMemory
│   │       ├── context: str
│   │       ├── options: List[Option]
│   │       ├── decision: str
│   │       ├── reasoning: str
│   │       └── impact: List[str]
│   │
│   ├── pattern.py               # PATTERN: 模式记忆
│   │   └── PatternMemory
│   │       ├── name: str
│   │       ├── description: str
│   │       ├── code_example: str
│   │       └── use_cases: List[str]
│   │
│   ├── issue.py                 # ISSUE: 问题记忆
│   │   └── IssueMemory
│   │       ├── description: str
│   │       ├── root_cause: str
│   │       ├── solution: str
│   │       └── prevention: str
│   │
│   └── learning.py              # LEARN: 学习记忆
│       └── LearningMemory
│           ├── lesson: str
│           ├── context: str
│           └── recommendation: str
│
└── models/
    ├── base.py
    │   └── BaseMemory           # 基础记忆类
    │       ├── id: str
    │       ├── timestamp: datetime
    │       ├── tags: List[str]
    │       ├── iteration_id: str
    │       └── content: dict
    │
    └── schemas.py
        └── MemorySchema         # 记忆Schema
            ├── REQ_SCHEMA
            ├── DEC_SCHEMA
            ├── PATTERN_SCHEMA
            ├── ISSUE_SCHEMA
            └── LEARN_SCHEMA
```

**智能回忆流程**:
```
Workflow Engine进入新阶段(P2: 技术设计)
   │
   ▼
MemoryManager.smart_recall(
    context={
        "stage": "P2",
        "keywords": ["authentication", "API", "database"]
    }
)
   │
   ├──► MemoryIndexer.search_by_tag(["architecture", "design"])
   ├──► MemoryRetrieval.search_by_keyword(["authentication"])
   │
   ├──► 找到相关记忆:
   │    ├── DEC-003: "Use JWT for authentication"
   │    ├── PATTERN-002: "Authentication middleware pattern"
   │    └── ISSUE-004: "Session timeout edge case"
   │
   └──► 返回排序后的相关记忆列表
   │
   ▼
AI Agent在提示词中应用这些记忆:
```markdown
## 🧠 Memory Recall

**Found Relevant Memories**:

🎯 **Decisions** (1 item):
- DEC-003: Use JWT for authentication (chosen over session cookies)

🔧 **Patterns** (1 item):
- PATTERN-002: Authentication middleware pattern

⚠️ **Known Issues** (1 item):
- ISSUE-004: Session timeout edge case (resolved)

**Applying memories to current task...**
```
```

**存储结构**:
```
.aceflow/memory/
├── REQ/
│   ├── REQ-20251106-abc123.md
│   └── REQ-20251107-def456.md
├── DEC/
│   ├── DEC-20251106-ghi789.md
│   └── DEC-20251107-jkl012.md
├── PATTERN/
│   └── PATTERN-20251106-mno345.md
├── ISSUE/
│   └── ISSUE-20251106-pqr678.md
├── LEARN/
│   └── LEARN-20251106-stu901.md
└── index.json                   # 索引文件
```

---

### 4️⃣ MCP Server MCP工具管理

```
aceflow-mcp-server/
│
├── server/                      # MCP Server实现
│   ├── stdio.py                 # stdio协议
│   │   └── StdioServer
│   │       ├── start()          # 启动stdio服务
│   │       ├── handle_request() # 处理请求
│   │       └── shutdown()       # 关闭服务
│   │
│   ├── http.py                  # http协议
│   │   └── HttpServer
│   │       ├── start()          # 启动http服务(FastAPI)
│   │       ├── route_handler()  # 路由处理
│   │       └── shutdown()       # 关闭服务
│   │
│   └── unified.py               # 统一服务器
│       └── UnifiedServer
│           ├── start(protocol)  # 启动指定协议服务
│           ├── register_tool()  # 注册工具
│           └── register_resource() # 注册资源
│
├── tools/                       # MCP Tools定义
│   ├── workflow_tools.py        # 工作流工具
│   │   ├── workflow_init()      # 初始化工作流
│   │   ├── workflow_status()    # 查询状态
│   │   ├── workflow_advance()   # 推进工作流
│   │   └── workflow_rollback()  # 回滚
│   │
│   ├── template_tools.py        # 模板工具
│   │   ├── template_list()      # 列出模板
│   │   ├── template_render()    # 渲染模板
│   │   └── template_validate()  # 验证模板
│   │
│   ├── memory_tools.py          # 记忆工具
│   │   ├── memory_store()       # 存储记忆
│   │   ├── memory_retrieve()    # 检索记忆
│   │   └── memory_recall()      # 智能回忆
│   │
│   ├── contract_tools.py        # 契约工具
│   │   ├── contract_generate()  # 生成契约
│   │   ├── contract_push()      # 推送契约
│   │   └── mock_server_start()  # 启动Mock Server
│   │
│   └── analysis_tools.py        # 分析工具
│       ├── complexity_analyze() # 复杂度分析
│       ├── mode_recommend()     # 模式推荐
│       └── quality_assess()     # 质量评估
│
├── adapters/                    # 适配器层(关键!)
│   ├── workflow_adapter.py      # 工作流适配器
│   │   └── WorkflowAdapter
│   │       ├── __init__(workflow_engine)
│   │       ├── initialize()     # 调用aceflow.workflow
│   │       ├── get_status()
│   │       └── advance_stage()
│   │
│   ├── template_adapter.py      # 模板适配器
│   │   └── TemplateAdapter
│   │       ├── __init__(template_manager)
│   │       ├── list_templates()
│   │       └── render_template()
│   │
│   └── memory_adapter.py        # 记忆适配器
│       └── MemoryAdapter
│           ├── __init__(memory_manager)
│           ├── store_memory()
│           └── smart_recall()
│
├── resources/                   # MCP Resources
│   └── resources.py
│       ├── StateResource        # 状态资源
│       ├── TemplateResource     # 模板资源
│       └── MemoryResource       # 记忆资源
│
├── prompts/                     # MCP Prompts
│   ├── generator.py
│   │   └── PromptGenerator
│   │       ├── generate_stage_prompt()
│   │       └── generate_gate_prompt()
│   │
│   └── intelligent.py
│       └── IntelligentPromptGenerator
│           ├── analyze_context()
│           ├── enhance_prompt()
│           └── apply_memories()
│
├── cli/                         # CLI工具
│   ├── main.py                  # 主入口
│   │   └── aceflow              # CLI主命令
│   │       ├── init             # aceflow init
│   │       ├── status           # aceflow status
│   │       ├── contract         # aceflow contract
│   │       └── mock             # aceflow mock
│   │
│   ├── init.py                  # 初始化命令
│   ├── contract.py              # 契约管理
│   └── mock.py                  # Mock Server
│
└── config/
    └── settings.py
        └── Settings             # 配置类
            ├── mcp_port: int
            ├── protocols: List[str]
            └── tools_enabled: List[str]
```

**双协议架构**:
```
┌──────────────────────────────────────────┐
│         MCP Client (AI Agent)            │
│    (Claude Code / Cline / Cursor)        │
└──────────────┬───────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
   ┌───▼───┐       ┌────▼────┐
   │ stdio │       │  http   │
   │ 协议  │       │  协议   │
   └───┬───┘       └────┬────┘
       │                │
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │ UnifiedServer  │
       │  统一服务器     │
       └───────┬────────┘
               │
       ┌───────┴────────┐
       │   工具注册表    │
       │ Tool Registry  │
       └───────┬────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼──┐  ┌───▼──┐  ┌───▼──┐
│Workflow│ │Template│ │Memory│
│Adapter│ │Adapter │ │Adapter│
└───┬───┘ └───┬───┘ └───┬───┘
    │         │         │
┌───▼──────────▼─────────▼───┐
│   aceflow (核心库)          │
│  ┌─────────┐ ┌──────────┐  │
│  │Workflow │ │Templates │  │
│  └─────────┘ └──────────┘  │
│  ┌─────────┐                │
│  │ Memory  │                │
│  └─────────┘                │
└──────────────────────────────┘
```

**调用流程示例**:
```
AI Agent (Claude Code)
   │
   │ 调用MCP Tool: workflow_init
   ▼
UnifiedServer.handle_request({
    "tool": "workflow_init",
    "params": {"mode": "standard"}
})
   │
   ├──► 查找工具: tools/workflow_tools.py
   ├──► 执行: workflow_init(mode="standard")
   │
   └──► WorkflowAdapter.initialize(mode="standard")
           │
           └──► aceflow.workflow.core.engine.WorkflowEngine.initialize()
                   │
                   ├──► 创建5个Stage (P1, P2, D1, D2, R1)
                   ├──► 持久化到 .aceflow/state.json
                   └──► 返回Iteration对象
   │
   ▼
返回给AI Agent:
{
    "iteration_id": "iter_001",
    "mode": "standard",
    "stages": ["P1", "P2", "D1", "D2", "R1"],
    "current_stage": "P1",
    "status": "initialized"
}
```

---

## 🔄 组件交互图

### 完整工作流执行流程

```
┌─────────────────────────────────────────────────────────┐
│                  用户 / AI Agent                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ 1. aceflow init --mode standard
                     ▼
        ┌────────────────────────────┐
        │   MCP Server (CLI/stdio)   │
        └────────────┬───────────────┘
                     │
                     │ 2. 调用 workflow_init
                     ▼
        ┌────────────────────────────┐
        │    Workflow Adapter        │
        └────────────┬───────────────┘
                     │
                     │ 3. WorkflowEngine.initialize(mode)
                     ▼
        ┌────────────────────────────┐
        │   Workflow Engine (Core)   │
        │  ┌──────────────────────┐  │
        │  │ StandardWorkflow     │  │
        │  │  - P1: Requirements  │  │
        │  │  - P2: Design        │  │
        │  │  - D1: Impl          │  │
        │  │  - D2: Testing       │  │
        │  │  - R1: Release       │  │
        │  └──────────────────────┘  │
        └────────────┬───────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ State   │ │Template │ │ Memory  │
   │ Manager │ │ Manager │ │ Manager │
   └────┬────┘ └────┬────┘ └────┬────┘
        │           │           │
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │state.json│ │P1_req.md│ │REQ-001 │
   └─────────┘ └─────────┘ └─────────┘
        │
        │ 4. 返回状态
        ▼
┌───────────────────────────────────┐
│  AI Agent继续执行P1阶段           │
│  - 读取模板 P1_requirements.md    │
│  - 回忆相关记忆 (REQ, DEC)        │
│  - 生成需求文档                   │
└───────────────────────────────────┘
```

---

## 📦 模块依赖关系

```
┌──────────────────────────────────────┐
│         aceflow-mcp-server           │
│  ┌────────────────────────────────┐  │
│  │  Adapters (适配器层)           │  │
│  │  - 仅依赖aceflow核心接口       │  │
│  └───────────┬────────────────────┘  │
└──────────────┼───────────────────────┘
               │ depends on
               ▼
┌──────────────────────────────────────┐
│            aceflow                   │
│  ┌────────────────────────────────┐  │
│  │  Workflow   (独立模块)         │  │
│  │  - 无外部依赖                  │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  Templates  (独立模块)         │  │
│  │  - 依赖: Jinja2                │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  Memory     (独立模块)         │  │
│  │  - 无外部依赖                  │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

**依赖原则**:
- ✅ aceflow 核心库 **零外部依赖** (除Jinja2用于模板)
- ✅ aceflow-mcp-server **只依赖** aceflow核心库
- ✅ 单向依赖: MCP Server → aceflow (反之不可)
- ✅ 模块间通过接口通信,不直接依赖实现

---

## 🎯 关键设计决策

### 1. 为什么分离aceflow和aceflow-mcp-server?

**原因**:
- **关注点分离**: aceflow专注工作流逻辑,MCP Server专注协议和工具
- **可复用性**: aceflow可以被其他项目使用(不仅限于MCP)
- **可测试性**: 核心逻辑可以独立测试,不依赖MCP协议
- **可维护性**: 两个模块可以独立升级和发布

### 2. 为什么使用Adapter模式?

**原因**:
- **解耦**: MCP Server不直接依赖aceflow实现细节
- **灵活性**: 可以轻松切换aceflow的实现
- **扩展性**: 未来可以添加更多适配器(如GraphQL, gRPC)

### 3. 为什么统一stdin和http协议?

**原因**:
- **简化部署**: 一个服务器支持两种协议
- **代码复用**: 工具定义只需写一次
- **灵活性**: 用户可根据需求选择协议

---

**文档版本**: v1.0
**作者**: Claude Code
**最后更新**: 2025-11-08
