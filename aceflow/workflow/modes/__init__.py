"""
Workflow Modes - DEPRECATED (v3.0)

⚠️ 此模块已废弃，请使用 v4.0 工作流系统。

v3.0 工作流模式（已移除）:
- Minimal: 快速原型模式 → 已废弃
- Standard: 标准平衡模式 → 已废弃
- Complete: 完整严格模式 → 已废弃
- Smart: AI驱动自适应模式 → 已废弃

v4.0 工作流系统（推荐使用）:
位置: aceflow.workflow.workflows

可用工作流类型:
- FeatureWorkflow: 功能开发 (5阶段: requirement → design → implementation → testing → delivery)
- BugfixWorkflow: Bug修复 (5阶段: analyze → locate → fix → verify → release)
- RefactorWorkflow: 代码重构 (5阶段: analyze → plan → refactor → test → finalize)
- ReviewWorkflow: 代码审查 (4阶段: prepare → review → address → complete)
- DocumentationWorkflow: 文档编写 (3阶段: outline → write → review)
- PerformanceWorkflow: 性能优化 (3阶段: diagnose → optimize → verify)

使用示例:
```python
from aceflow.workflow.core.engine import WorkflowEngine
from aceflow.workflow.models import WorkflowType

# 创建引擎
engine = WorkflowEngine(project_id="my_project")

# 开始工作项
result = engine.start_work_item(
    type=WorkflowType.FEATURE,
    title="用户登录功能",
    description="实现用户登录和认证"
)

# 获取当前工作项
work_item = engine.get_current_work_item()

# 完成阶段
engine.state_manager.complete_stage(
    work_item_id=work_item.work_item_id,
    stage_id="requirement"
)
```

详见文档: docs/ACEFLOW_V4_IMPLEMENTATION_LOG.md
"""

# 为了向后兼容，提供错误提示
def __getattr__(name):
    """提供友好的错误消息"""
    if name in ['MinimalWorkflow', 'StandardWorkflow', 'CompleteWorkflow', 'SmartWorkflow']:
        raise ImportError(
            f"{name} has been deprecated in v4.0. "
            f"Please use the new workflow system: "
            f"from aceflow.workflow.workflows import FeatureWorkflow, BugfixWorkflow, etc."
        )
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = []  # 不再导出任何内容
