# AceFlow v4.0 工作流模板库

## 📚 当前模板结构

本目录包含 **AceFlow v4.0** 的6种工作流模板。

> ⚠️ **重要**: v3.0的模板（minimal/standard/complete）已废弃，请使用v4.0工作流系统。

```
templates/
└── workflows/                           # v4.0 工作流模板
    ├── feature/                         # 功能开发 (5阶段)
    │   ├── requirement.md               # 需求分析
    │   ├── design.md                    # 设计方案
    │   ├── implementation.md            # 功能实现
    │   ├── testing.md                   # 测试验证
    │   └── delivery.md                  # 交付发布
    │
    ├── bugfix/                          # Bug修复 (5阶段)
    │   ├── analyze.md                   # Bug分析
    │   ├── locate.md                    # 问题定位
    │   ├── fix.md                       # 修复实现
    │   ├── verify.md                    # 修复验证
    │   └── release.md                   # 发布上线
    │
    ├── refactor/                        # 代码重构 (5阶段)
    │   ├── analyze.md                   # 重构分析
    │   ├── plan.md                      # 重构计划
    │   ├── refactor.md                  # 重构实现
    │   ├── test.md                      # 重构测试
    │   └── finalize.md                  # 完成收尾
    │
    ├── review/                          # 代码审查 (4阶段)
    │   ├── prepare.md                   # 审查准备
    │   ├── review.md                    # 进行审查
    │   ├── address.md                   # 处理反馈
    │   └── complete.md                  # 完成合并
    │
    ├── documentation/                   # 文档编写 (3阶段)
    │   ├── outline.md                   # 文档大纲
    │   ├── write.md                     # 编写文档
    │   └── review.md                    # 审查发布
    │
    └── performance/                     # 性能优化 (3阶段)
        ├── diagnose.md                  # 性能诊断
        ├── optimize.md                  # 优化实现
        └── verify.md                    # 效果验证
```

## 🎯 工作流类型说明

### 1. Feature Workflow - 功能开发
**适用场景**: 新功能开发、功能增强
**阶段**: requirement → design → implementation → testing → delivery
**典型周期**: 3-7天

### 2. Bugfix Workflow - Bug修复
**适用场景**: 紧急Bug修复、问题排查
**阶段**: analyze → locate → fix → verify → release
**典型周期**: 0.5-2天

### 3. Refactor Workflow - 代码重构
**适用场景**: 代码优化、架构调整
**阶段**: analyze → plan → refactor → test → finalize
**典型周期**: 2-5天

### 4. Review Workflow - 代码审查
**适用场景**: Pull Request审查、代码评审
**阶段**: prepare → review → address → complete
**典型周期**: 0.5-2天

### 5. Documentation Workflow - 文档编写
**适用场景**: 技术文档、用户手册
**阶段**: outline → write → review
**典型周期**: 1-3天

### 6. Performance Workflow - 性能优化
**适用场景**: 性能瓶颈优化、响应时间改善
**阶段**: diagnose → optimize → verify
**典型周期**: 2-5天

## 💡 使用方法

### 通过MCP工具使用（推荐）

```python
# 1. 开始工作项
aceflow_v4_start_work_item(
    type="feature",
    title="用户认证功能",
    description="实现JWT认证和授权"
)

# 2. 系统自动加载对应的模板
# 例如: workflows/feature/requirement.md

# 3. 完成阶段任务后推进
aceflow_v4_complete_stage(
    work_item_id="work_001",
    stage_id="requirement"
)
```

### 通过Python API使用

```python
from aceflow.workflow.core.engine import WorkflowEngine
from aceflow.workflow.models import WorkflowType

# 创建引擎
engine = WorkflowEngine(project_id="my_project")

# 开始功能开发工作流
result = engine.start_work_item(
    type=WorkflowType.FEATURE,
    title="用户登录",
    description="实现用户登录和会话管理"
)

# 获取当前阶段的模板路径
work_item = engine.get_current_work_item()
template_path = work_item.current_stage.checklist_template
# 例如: "workflows/feature/requirement.md"
```

## 🔧 模板开发

### 模板文件格式

所有模板使用Markdown格式，支持以下特性：

1. **任务检查清单**
```markdown
- [ ] 任务项1
- [ ] 任务项2
```

2. **记忆注入占位符**（v4.1即将支持）
```markdown
## 项目记忆

{{project_memory}}
```

3. **变量替换**
```markdown
# {{work_item_title}}

工作项ID: {{work_item_id}}
阶段: {{stage_name}}
```

### 添加新模板

1. 在对应的工作流目录下创建markdown文件
2. 在对应的Workflow类中注册阶段定义
3. 运行测试验证

## 📖 相关文档

- **工作流系统文档**: `docs/ACEFLOW_V4_IMPLEMENTATION_LOG.md`
- **API参考**: `docs/WORKFLOW_API_REFERENCE.md`
- **快速开始**: `docs/WORKFLOW_QUICK_START.md`

## 🔄 从v3.0迁移

如果你正在使用v3.0的模板系统，请参考迁移指南：

### v3.0 → v4.0 映射

| v3.0模式 | v4.0工作流 | 说明 |
|---------|-----------|------|
| Minimal (P→D→R) | BugfixWorkflow | 快速修复场景 |
| Standard (5阶段) | FeatureWorkflow | 标准功能开发 |
| Complete (8阶段) | FeatureWorkflow + 质量检查 | 严格流程场景 |
| Smart (自适应) | 根据type自动选择 | 由WorkflowEngine智能选择 |

### 迁移步骤

1. ✅ 停止使用 `MinimalWorkflow`, `StandardWorkflow`, `CompleteWorkflow`
2. ✅ 改用新的工作流类型: `WorkflowType.FEATURE`, `WorkflowType.BUGFIX` 等
3. ✅ 更新模板路径引用
4. ✅ 使用新的API接口

## 🆕 v4.0 新特性

- ✅ 更精细的工作流分类（6种类型）
- ✅ 动态阶段定义
- ✅ 任务依赖管理
- ✅ 记忆系统集成
- ✅ MCP工具完整支持
- 🔄 记忆自动注入（即将支持）
- 🔄 模板热重载（即将支持）

---

**版本**: v4.0.0
**最后更新**: 2025-11-17
**维护者**: AceFlow Team
