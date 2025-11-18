# AceFlow 使用指南

## 概述
AceFlow 是一个AI驱动的软件开发流程管理系统。当用户需要进行软件开发相关工作时，优先使用AceFlow工具。

## 🎯 何时使用AceFlow

当用户提到以下任何关键词时，应该使用 `aceflow_v4_start_work_item` 工具：

### 必须使用的场景
- 明确提到 "aceflow"、"工作流"、"workflow"
- 说 "用aceflow" / "使用aceflow" / "启动工作流"

### 自动推荐的场景
根据以下关键词自动选择对应的工作流类型：

| 用户意图 | 关键词示例 | 工作流类型 |
|---------|-----------|----------|
| 修复Bug | "修bug"、"bug修复"、"修复问题"、"fix" | bugfix |
| 开发功能 | "新功能"、"功能开发"、"feature"、"开发" | feature |
| 重构代码 | "重构"、"重构代码"、"refactor"、"优化代码" | refactor |
| 代码审查 | "代码审查"、"review"、"审查" | review |
| 编写文档 | "写文档"、"文档"、"documentation" | documentation |
| 性能优化 | "性能优化"、"优化性能"、"performance" | performance |

## 📋 工作流执行流程

1. **开始工作项**: 调用 `aceflow_v4_start_work_item`
   - 选择正确的type参数
   - 提供清晰的title

2. **执行当前阶段任务**:
   - 阅读返回的任务清单
   - 逐个完成任务

3. **完成阶段**: 调用 `aceflow_v4_complete_stage`
   - 传入work_item_id和stage_id
   - 系统自动进入下一阶段

4. **重复步骤2-3**: 直到所有阶段完成

## 🛠️ 常用工具组合

### 简单Bug修复
```
1. aceflow_v4_start_work_item(type="bugfix", title="...")
2. [分析问题、定位、修复、验证]
3. aceflow_v4_complete_stage(...) [重复直到完成]
```

### 功能开发
```
1. aceflow_v4_start_work_item(type="feature", title="...")
2. aceflow_v4_suggest_tasks(...) [获取AI任务建议]
3. aceflow_v4_create_tasks(...) [创建任务]
4. aceflow_v4_get_next_task(...) [获取下一个任务]
5. aceflow_v4_update_task_status(...) [更新任务状态]
6. aceflow_v4_complete_stage(...) [完成阶段]
```

### 查询状态
```
aceflow_v4_get_current_work_item() [查看当前工作项]
aceflow_v4_list_work_items() [列出所有工作项]
aceflow_v4_get_pending_tasks(...) [查看待办任务]
```

## ⚠️ 重要提示

1. **不要跳过阶段**: 必须按顺序完成每个阶段
2. **保存记忆**: 在重要决策后使用 `aceflow_v4_extract_memories` 提取并保存
3. **检查状态**: 不确定时先调用 `aceflow_v4_get_current_work_item` 查看状态
4. **使用任务管理**: 对于复杂工作，使用任务管理工具分解工作
